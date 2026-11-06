"""
Smart Health Tracker - Launcher
================================

A small graphical tool that prepares and runs the Smart Health Tracker web app
on any computer that already has Python installed.

What it does
------------
1. Libraries tab : checks every library listed in requirements.txt inside a
                   private virtual environment (venv), shows what is missing or
                   has the wrong version, installs only those, and finally runs
                   a self-test that really imports each library.
2. Settings tab  : writes the .env file (Gemini API key, port, secret key),
                   tests the Gemini key, opens the Windows firewall port,
                   changes the admin password, starts with an empty database.
3. Run tab       : starts / stops the web server and shows its addresses.

It uses ONLY the Python standard library (tkinter), so the window opens even
before any of the app's libraries are installed.
"""

import datetime
import json
import os
import queue
import re
import secrets
import socket
import subprocess
import sys
import threading
import traceback
import webbrowser

import tkinter as tk
from tkinter import messagebox, scrolledtext, ttk

# ---------------------------------------------------------------------------
# Paths and constants
# ---------------------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
IS_WIN = os.name == "nt"
VENV = os.path.join(BASE, "venv")
VENV_PY = (os.path.join(VENV, "Scripts", "python.exe") if IS_WIN
           else os.path.join(VENV, "bin", "python"))
REQ_FILE = os.path.join(BASE, "requirements.txt")
ENV_FILE = os.path.join(BASE, ".env")
DB_FILE = os.path.join(BASE, "health.db")
MARKER_FILE = os.path.join(VENV, ".smarthealth_selftest")
MODEL_FILE = os.path.join(BASE, "runs", "detect", "runs", "detect",
                          "food_model_merged", "weights", "best.pt")
NUTRITION_FILE = os.path.join(BASE, "app", "data", "nutrition_db.json")
RUN_FILE = os.path.join(BASE, "run.py")

DEFAULT_PORT = "3535"
FIREWALL_RULE = "Smart Health Tracker"
NO_WINDOW = 0x08000000 if IS_WIN else 0  # CREATE_NO_WINDOW: no black console pop-ups
VC_REDIST_URL = "https://aka.ms/vs/17/release/vc_redist.x64.exe"
GEMINI_KEY_URL = "https://aistudio.google.com/apikey"
PYTHON_URL = "https://www.python.org/downloads/"

# pip package name -> name used in "import ..." (they are not always the same)
IMPORT_NAMES = {
    "flask": "flask",
    "flask-sqlalchemy": "flask_sqlalchemy",
    "flask-login": "flask_login",
    "flask-wtf": "flask_wtf",
    "python-dotenv": "dotenv",
    "google-genai": "google.genai",
    "pillow": "PIL",
    "torch": "torch",
    "torchvision": "torchvision",
    "ultralytics": "ultralytics",
}
# Needed only for running the automated tests, not for the app itself
OPTIONAL = {"pytest"}

# ---------------------------------------------------------------------------
# Small scripts executed INSIDE the venv's Python
# ---------------------------------------------------------------------------
CHECK_SCRIPT = (
    "import sys, json\n"
    "from importlib.metadata import version, PackageNotFoundError\n"
    "out = {}\n"
    "for n in sys.argv[1:]:\n"
    "    try:\n"
    "        out[n] = version(n)\n"
    "    except PackageNotFoundError:\n"
    "        out[n] = None\n"
    "print('@@' + json.dumps(out))\n"
)

SELFTEST_SCRIPT = (
    "import sys, json, importlib\n"
    "res = {}\n"
    "for m in sys.argv[1:]:\n"
    "    try:\n"
    "        importlib.import_module(m)\n"
    "        res[m] = None\n"
    "    except BaseException as e:\n"
    "        res[m] = type(e).__name__ + ': ' + str(e)\n"
    "print('@@' + json.dumps(res))\n"
)

GEMINI_TEST_SCRIPT = (
    "import sys\n"
    "from google import genai\n"
    "key = sys.stdin.readline().strip()\n"
    "client = genai.Client(api_key=key)\n"
    "r = client.models.generate_content(model=sys.argv[1], contents='Reply with the word OK')\n"
    "print('@@OK ' + (r.text or '').strip()[:40])\n"
)

ADMIN_PASSWORD_SCRIPT = (
    "import sys\n"
    "from werkzeug.security import generate_password_hash\n"
    "from app import create_app, db\n"
    "from app.models.user import User\n"
    "pw = sys.stdin.readline().rstrip('\\r\\n')\n"
    "app = create_app()\n"
    "with app.app_context():\n"
    "    u = (User.query.filter_by(username='admin').first()\n"
    "         or User.query.filter_by(role='admin').first())\n"
    "    if not u:\n"
    "        print('@@NOADMIN')\n"
    "    else:\n"
    "        u.password_hash = generate_password_hash(pw)\n"
    "        db.session.commit()\n"
    "        print('@@OK ' + u.email)\n"
)


# ---------------------------------------------------------------------------
# Helper functions (no GUI)
# ---------------------------------------------------------------------------
def base_python():
    """The python.exe that is running this launcher (not pythonw.exe)."""
    exe = sys.executable
    if IS_WIN and exe.lower().endswith("pythonw.exe"):
        candidate = exe[: -len("pythonw.exe")] + "python.exe"
        if os.path.exists(candidate):
            return candidate
    return exe


def child_env():
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUNBUFFERED"] = "1"
    return env


def run(cmd, stdin_text=None, timeout=600):
    """Run a command and wait. Returns (exit_code, combined_output)."""
    try:
        p = subprocess.run(
            cmd, cwd=BASE, env=child_env(), input=stdin_text,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
            timeout=timeout, creationflags=NO_WINDOW,
        )
        return p.returncode, p.stdout or ""
    except subprocess.TimeoutExpired:
        return -1, "Timed out."
    except OSError as e:
        return -1, str(e)


def stream(cmd, on_line):
    """Run a command and send each output line to on_line(). Returns exit code."""
    try:
        p = subprocess.Popen(
            cmd, cwd=BASE, env=child_env(),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace", bufsize=1,
            creationflags=NO_WINDOW,
        )
    except OSError as e:
        on_line(f"Could not start process: {e}")
        return -1
    for line in p.stdout:
        line = line.rstrip()
        if line:
            on_line(line)
    return p.wait()


def marker_payload(output):
    """Find the line our helper scripts print with the '@@' prefix."""
    for line in reversed(output.splitlines()):
        if line.startswith("@@"):
            return line[2:]
    return None


REQ_RE = re.compile(r"^\s*([A-Za-z0-9_.\-]+)\s*(==|>=|<=|~=|>|<)?\s*([^\s;,]*)")


def parse_requirements():
    reqs = []
    if not os.path.exists(REQ_FILE):
        return reqs
    with open(REQ_FILE, encoding="utf-8") as f:
        for raw in f:
            line = raw.split("#")[0].strip()
            if not line or line.startswith("-"):
                continue
            m = REQ_RE.match(line)
            if m:
                reqs.append({
                    "name": m.group(1),
                    "key": m.group(1).lower().replace("_", "-"),
                    "op": m.group(2) or "",
                    "ver": m.group(3) or "",
                    "spec": line,
                })
    return reqs


def vtuple(v):
    """'2.5.1+cpu' -> (2, 5, 1). Trailing zeros removed so 2.0 == 2.0.0."""
    v = v.split("+")[0]
    parts = []
    for p in v.split("."):
        m = re.match(r"\d+", p)
        parts.append(int(m.group()) if m else 0)
    while parts and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def satisfies(installed, op, required):
    if not op or not required:
        return True
    a, b = vtuple(installed), vtuple(required)
    return {
        "==": a == b, ">=": a >= b, "<=": a <= b,
        ">": a > b, "<": a < b, "~=": a >= b,
    }.get(op, True)


def read_env():
    data = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def write_env(updates):
    """Update keys in .env, keeping every other line exactly as it was."""
    lines, seen = [], set()
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, encoding="utf-8") as f:
            for line in f.read().splitlines():
                key = line.split("=", 1)[0].strip() if "=" in line else None
                if key in updates:
                    lines.append(f"{key}={updates[key]}")
                    seen.add(key)
                else:
                    lines.append(line)
    for k, v in updates.items():
        if k not in seen:
            lines.append(f"{k}={v}")
    with open(ENV_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def gemini_model_name():
    """Use the same Gemini model the app uses (read from its source)."""
    path = os.path.join(BASE, "app", "services", "chatbot_service.py")
    try:
        with open(path, encoding="utf-8") as f:
            m = re.search(r"model\s*=\s*['\"]([^'\"]+)['\"]", f.read())
            if m:
                return m.group(1)
    except OSError:
        pass
    return "gemini-3.8-flash"


def local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def port_is_free(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("0.0.0.0", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def open_firewall(port):
    """Ask Windows for admin rights (UAC prompt) and open the TCP port."""
    import ctypes
    cmd = (f'/c netsh advfirewall firewall delete rule name="{FIREWALL_RULE}" >nul 2>&1 & '
           f'netsh advfirewall firewall add rule name="{FIREWALL_RULE}" dir=in '
           f'action=allow protocol=TCP localport={port}')
    r = ctypes.windll.shell32.ShellExecuteW(None, "runas", "cmd.exe", cmd, None, 0)
    return r > 32


# ---------------------------------------------------------------------------
# The window
# ---------------------------------------------------------------------------
class Launcher(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart Health Tracker - Launcher")
        self.geometry("940x700")
        self.minsize(840, 620)

        self.q = queue.Queue()          # work for the GUI thread
        self.busy = False
        self.busy_widgets = []
        self.server = None
        self.reqs = []
        self.missing = []
        self.versions = {}
        self.selftest_ok = False
        self.files_ok = False

        self._style()
        self._build()
        self._load_settings()
        self.after(100, self._poll)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self.after(300, lambda: self.run_task(self.task_check, auto_selftest=True))

    # ----- thread helpers ---------------------------------------------------
    def ui(self, fn, *args):
        """Run fn(*args) on the GUI thread (tkinter is not thread-safe)."""
        self.q.put((fn, args))

    def _poll(self):
        try:
            while True:
                fn, args = self.q.get_nowait()
                fn(*args)
        except queue.Empty:
            pass
        self.after(100, self._poll)

    def log(self, msg):
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.ui(self._append_log, f"[{stamp}] {msg}\n")

    def _append_log(self, text):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", text)
        lines = int(self.log_box.index("end-1c").split(".")[0])
        if lines > 4000:
            self.log_box.delete("1.0", f"{lines - 4000}.0")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def run_task(self, fn, **kwargs):
        """Run a long job in a background thread so the window never freezes."""
        if self.busy:
            messagebox.showinfo("Please wait", "Another operation is still running.")
            return
        self._set_busy(True)

        def worker():
            try:
                fn(**kwargs)
            except Exception:
                self.log("Unexpected error:\n" + traceback.format_exc())
            finally:
                self.ui(self._set_busy, False)

        threading.Thread(target=worker, daemon=True).start()

    def _set_busy(self, busy):
        self.busy = busy
        for w in self.busy_widgets:
            w.configure(state="disabled" if busy else "normal")
        if busy:
            self.progress.start(12)
        else:
            self.progress.stop()
            self._update_ready()

    # ----- layout -----------------------------------------------------------
    def _style(self):
        style = ttk.Style(self)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"))
        style.configure("Sub.TLabel", foreground="#555")
        style.configure("Big.TButton", font=("Segoe UI", 11, "bold"), padding=8)

    def _build(self):
        header = ttk.Frame(self, padding=(14, 10, 14, 4))
        header.pack(fill="x")
        ttk.Label(header, text="Smart Health Tracker", style="Title.TLabel").pack(anchor="w")
        pyver = ".".join(map(str, sys.version_info[:3]))
        ttk.Label(header, style="Sub.TLabel",
                  text=f"Python {pyver}   |   Folder: {BASE}").pack(anchor="w")

        self.ready_label = ttk.Label(header, text="Checking...", font=("Segoe UI", 10, "bold"))
        self.ready_label.pack(anchor="w", pady=(4, 0))

        paned = ttk.PanedWindow(self, orient="vertical")
        paned.pack(fill="both", expand=True, padx=10, pady=4)

        self.nb = ttk.Notebook(paned)
        paned.add(self.nb, weight=3)
        self._build_libraries_tab()
        self._build_settings_tab()
        self._build_run_tab()

        log_frame = ttk.LabelFrame(paned, text="Log", padding=4)
        paned.add(log_frame, weight=2)
        self.log_box = scrolledtext.ScrolledText(log_frame, height=10, state="disabled",
                                                 font=("Consolas", 9), wrap="word")
        self.log_box.pack(fill="both", expand=True)

        bottom = ttk.Frame(self, padding=(10, 0, 10, 8))
        bottom.pack(fill="x")
        self.progress = ttk.Progressbar(bottom, mode="indeterminate")
        self.progress.pack(fill="x")

        if sys.version_info < (3, 9):
            messagebox.showerror("Python too old",
                                 f"Python {pyver} is too old. Please install Python 3.12 "
                                 f"from {PYTHON_URL}")

    def _build_libraries_tab(self):
        tab = ttk.Frame(self.nb, padding=10)
        self.nb.add(tab, text="  1. Libraries  ")

        cols = ("required", "installed", "status")
        self.tree = ttk.Treeview(tab, columns=cols, height=12)
        self.tree.heading("#0", text="Library / file")
        self.tree.heading("required", text="Required")
        self.tree.heading("installed", text="Installed")
        self.tree.heading("status", text="Status")
        self.tree.column("#0", width=260)
        self.tree.column("required", width=140, anchor="center")
        self.tree.column("installed", width=140, anchor="center")
        self.tree.column("status", width=220)
        self.tree.tag_configure("ok", foreground="#1a7f37")
        self.tree.tag_configure("bad", foreground="#c62828")
        self.tree.tag_configure("warn", foreground="#d97706")
        self.tree.tag_configure("opt", foreground="#777")
        self.tree.pack(fill="both", expand=True)

        btns = ttk.Frame(tab)
        btns.pack(fill="x", pady=(8, 0))
        b1 = ttk.Button(btns, text="Check again",
                        command=lambda: self.run_task(self.task_check, auto_selftest=True))
        self.install_btn = ttk.Button(btns, text="Install missing libraries",
                                      style="Big.TButton",
                                      command=lambda: self.run_task(self.task_install))
        b3 = ttk.Button(btns, text="Run self-test",
                        command=lambda: self.run_task(self.task_selftest))
        b1.pack(side="left")
        self.install_btn.pack(side="left", padx=8)
        b3.pack(side="left")
        self.busy_widgets += [b1, self.install_btn, b3]
        ttk.Label(tab, style="Sub.TLabel", wraplength=820, justify="left",
                  text="Libraries are installed in a private 'venv' folder next to this "
                       "launcher, so other Python programs on this computer are not affected. "
                       "The first installation downloads about 2-3 GB (PyTorch) and can take "
                       "several minutes.").pack(anchor="w", pady=(8, 0))

    def _build_settings_tab(self):
        tab = ttk.Frame(self.nb, padding=12)
        self.nb.add(tab, text="  2. Settings  ")
        tab.columnconfigure(1, weight=1)
        r = 0

        # --- AI -------------------------------------------------------------
        ttk.Label(tab, text="AI (Google Gemini)", font=("Segoe UI", 10, "bold")).grid(
            row=r, column=0, columnspan=3, sticky="w"); r += 1
        ttk.Label(tab, text="Gemini API key").grid(row=r, column=0, sticky="w", pady=3)
        self.key_var = tk.StringVar()
        self.key_entry = ttk.Entry(tab, textvariable=self.key_var, show="•")
        self.key_entry.grid(row=r, column=1, sticky="ew", padx=6)
        kb = ttk.Frame(tab)
        kb.grid(row=r, column=2, sticky="w")
        self.show_key = tk.BooleanVar()
        ttk.Checkbutton(kb, text="Show", variable=self.show_key,
                        command=lambda: self.key_entry.configure(
                            show="" if self.show_key.get() else "•")).pack(side="left")
        tb = ttk.Button(kb, text="Test key", command=lambda: self.run_task(self.task_test_key, key=self.key_var.get().strip()))
        tb.pack(side="left", padx=4)
        self.busy_widgets.append(tb)
        r += 1
        link = ttk.Label(tab, text=f"Get a free key at {GEMINI_KEY_URL}",
                         foreground="#1565c0", cursor="hand2")
        link.grid(row=r, column=1, sticky="w", padx=6)
        link.bind("<Button-1>", lambda e: webbrowser.open(GEMINI_KEY_URL))
        r += 1

        # --- Network ----------------------------------------------------------
        ttk.Separator(tab).grid(row=r, column=0, columnspan=3, sticky="ew", pady=10); r += 1
        ttk.Label(tab, text="Network", font=("Segoe UI", 10, "bold")).grid(
            row=r, column=0, columnspan=3, sticky="w"); r += 1
        ttk.Label(tab, text="Port").grid(row=r, column=0, sticky="w", pady=3)
        self.port_var = tk.StringVar(value=DEFAULT_PORT)
        ttk.Entry(tab, textvariable=self.port_var, width=8).grid(row=r, column=1, sticky="w", padx=6)
        r += 1
        self.lan_var = tk.BooleanVar()
        ttk.Checkbutton(tab, variable=self.lan_var,
                        text="Allow other computers on the network to connect "
                             "(opens the port in Windows Firewall, asks for admin rights)").grid(
            row=r, column=0, columnspan=3, sticky="w", pady=3); r += 1
        self.secret_label = ttk.Label(tab, style="Sub.TLabel")
        self.secret_label.grid(row=r, column=0, columnspan=3, sticky="w"); r += 1

        save = ttk.Button(tab, text="Save settings", style="Big.TButton", command=self.save_settings)
        save.grid(row=r, column=0, columnspan=3, sticky="w", pady=(8, 0)); r += 1
        self.busy_widgets.append(save)

        # --- Database ---------------------------------------------------------
        ttk.Separator(tab).grid(row=r, column=0, columnspan=3, sticky="ew", pady=10); r += 1
        ttk.Label(tab, text="Database and admin account", font=("Segoe UI", 10, "bold")).grid(
            row=r, column=0, columnspan=3, sticky="w"); r += 1
        self.db_label = ttk.Label(tab, style="Sub.TLabel")
        self.db_label.grid(row=r, column=0, columnspan=3, sticky="w"); r += 1

        ttk.Label(tab, text="New admin password").grid(row=r, column=0, sticky="w", pady=3)
        self.pw1 = tk.StringVar()
        ttk.Entry(tab, textvariable=self.pw1, show="•").grid(row=r, column=1, sticky="ew", padx=6)
        r += 1
        ttk.Label(tab, text="Repeat password").grid(row=r, column=0, sticky="w", pady=3)
        self.pw2 = tk.StringVar()
        ttk.Entry(tab, textvariable=self.pw2, show="•").grid(row=r, column=1, sticky="ew", padx=6)
        pwb = ttk.Button(tab, text="Change admin password",
                         command=lambda: self.run_task(self.task_admin_password,
                                                             p1=self.pw1.get(), p2=self.pw2.get()))
        pwb.grid(row=r, column=2, sticky="w")
        r += 1
        emb = ttk.Button(tab, text="Start with an empty database...", command=self.empty_database)
        emb.grid(row=r, column=0, columnspan=3, sticky="w", pady=(8, 0))
        self.busy_widgets += [pwb, emb]

    def _build_run_tab(self):
        tab = ttk.Frame(self.nb, padding=16)
        self.nb.add(tab, text="  3. Run  ")

        top = ttk.Frame(tab)
        top.pack(fill="x")
        self.dot = tk.Canvas(top, width=22, height=22, highlightthickness=0)
        self.dot.pack(side="left")
        self.dot_item = self.dot.create_oval(3, 3, 19, 19, fill="#c62828", outline="")
        self.server_label = ttk.Label(top, text="Server stopped", font=("Segoe UI", 12, "bold"))
        self.server_label.pack(side="left", padx=8)

        btns = ttk.Frame(tab)
        btns.pack(fill="x", pady=14)
        self.start_btn = ttk.Button(btns, text="▶  Start", style="Big.TButton",
                                    command=self.start_server)
        self.stop_btn = ttk.Button(btns, text="■  Stop", style="Big.TButton",
                                   command=self.stop_server, state="disabled")
        self.open_btn = ttk.Button(btns, text="Open in browser", command=self.open_browser)
        self.start_btn.pack(side="left")
        self.stop_btn.pack(side="left", padx=8)
        self.open_btn.pack(side="left")

        self.auto_open = tk.BooleanVar(value=True)
        ttk.Checkbutton(tab, text="Open the browser automatically when the server is ready",
                        variable=self.auto_open).pack(anchor="w")

        addr = ttk.LabelFrame(tab, text="Addresses", padding=10)
        addr.pack(fill="x", pady=14)
        self.url_local = ttk.Label(addr, foreground="#1565c0", cursor="hand2",
                                   font=("Segoe UI", 11))
        self.url_lan = ttk.Label(addr, foreground="#1565c0", cursor="hand2",
                                 font=("Segoe UI", 11))
        ttk.Label(addr, text="This computer:").grid(row=0, column=0, sticky="w")
        self.url_local.grid(row=0, column=1, sticky="w", padx=8)
        ttk.Label(addr, text="Other computers:").grid(row=1, column=0, sticky="w", pady=(4, 0))
        self.url_lan.grid(row=1, column=1, sticky="w", padx=8, pady=(4, 0))
        self.url_local.bind("<Button-1>", lambda e: webbrowser.open(self.url_local.cget("text")))
        self.url_lan.bind("<Button-1>", lambda e: webbrowser.open(self.url_lan.cget("text")))
        ttk.Label(tab, style="Sub.TLabel",
                  text="Default admin login if never changed: admin@smarthealth.local / 123").pack(
            anchor="w")
        self._refresh_urls()

    # ----- state ------------------------------------------------------------
    def _update_ready(self):
        ready = self.is_ready()
        running = self.server is not None and self.server.poll() is None
        if ready:
            self.ready_label.configure(text="✔  Everything is ready. Go to '3. Run' and press Start.",
                                       foreground="#1a7f37")
        elif self.missing:
            self.ready_label.configure(
                text=f"✘  {len(self.missing)} required libraries are missing or outdated. "
                     f"Press 'Install missing libraries'.", foreground="#c62828")
        elif not self.files_ok:
            self.ready_label.configure(text="✘  Some application files are missing (see table).",
                                       foreground="#c62828")
        elif not self.selftest_ok:
            self.ready_label.configure(text="⚠  Libraries found but the self-test has not passed.",
                                       foreground="#d97706")
        self.install_btn.configure(
            state="normal" if (self.missing and not self.busy) else "disabled")
        self.start_btn.configure(state="normal" if (ready and not running and not self.busy)
                                 else "disabled")
        self.stop_btn.configure(state="normal" if running else "disabled")

        env = read_env()
        self.secret_label.configure(
            text="Session secret key: set ✔" if env.get("SECRET_KEY")
            else "Session secret key: not set yet, it will be generated automatically when you save.")
        if os.path.exists(DB_FILE):
            size = os.path.getsize(DB_FILE) / 1024
            self.db_label.configure(text=f"Database: health.db ({size:.0f} KB)")
        else:
            self.db_label.configure(text="Database: none yet, an empty one will be created "
                                         "on first start (admin / 123).")

    def is_ready(self):
        return bool(self.reqs) and not self.missing and self.selftest_ok and self.files_ok

    # ----- tasks (run in background threads) --------------------------------
    def task_check(self, auto_selftest=False):
        self.log("Checking libraries...")
        self.reqs = parse_requirements()
        if not self.reqs:
            self.log("requirements.txt not found or empty!")
        names = [r["name"] for r in self.reqs]

        if not os.path.exists(VENV_PY):
            self.log("No virtual environment yet. 'Install missing libraries' will create it.")
            versions = {n: None for n in names}
        else:
            code, out = run([VENV_PY, "-c", CHECK_SCRIPT] + names, timeout=120)
            payload = marker_payload(out)
            if code != 0 or payload is None:
                self.log("Could not read installed libraries:\n" + out)
                versions = {n: None for n in names}
            else:
                versions = json.loads(payload)

        rows, missing = [], []
        for r in self.reqs:
            inst = versions.get(r["name"])
            optional = r["key"] in OPTIONAL
            required_txt = f"{r['op']} {r['ver']}".strip() or "any"
            if inst is None:
                status, tag = ("Optional (only for tests)", "opt") if optional else ("✘ Missing", "bad")
            elif satisfies(inst, r["op"], r["ver"]):
                status, tag = "✔ OK", "ok"
            else:
                status, tag = (("Optional, other version", "opt") if optional
                               else ("⚠ Wrong version", "warn"))
            if tag in ("bad", "warn"):
                missing.append(r)
            rows.append((r["name"], required_txt, inst or "-", status, tag))

        files_ok = True
        for label, path in (("[file] YOLO food model (best.pt)", MODEL_FILE),
                            ("[file] Nutrition data (nutrition_db.json)", NUTRITION_FILE),
                            ("[file] run.py", RUN_FILE)):
            ok = os.path.exists(path)
            files_ok &= ok
            rows.append((label, "file", "found" if ok else "-",
                         "✔ OK" if ok else "✘ Missing", "ok" if ok else "bad"))

        self.versions, self.missing, self.files_ok = versions, missing, files_ok
        self.ui(self._fill_table, rows)

        if missing:
            self.selftest_ok = False
            self.log(f"{len(missing)} required libraries missing or outdated: "
                     + ", ".join(r["name"] for r in missing))
            return
        self.log("All required libraries are installed.")
        if self._marker_matches():
            self.selftest_ok = True
            self.log("Self-test already passed for these versions.")
        elif auto_selftest:
            self.task_selftest()

    def _fill_table(self, rows):
        self.tree.delete(*self.tree.get_children())
        for name, req, inst, status, tag in rows:
            self.tree.insert("", "end", text=name, values=(req, inst, status), tags=(tag,))

    def task_install(self):
        fresh = not os.path.exists(VENV_PY)
        if fresh:
            self.log("Creating virtual environment (venv)...")
            code = stream([base_python(), "-m", "venv", VENV], self.log)
            if code != 0 or not os.path.exists(VENV_PY):
                self.log("Could not create the virtual environment.")
                self.ui(messagebox.showerror, "Error", "Could not create the virtual environment. "
                                                      "See the log for details.")
                return
            self.log("Updating pip...")
            stream([VENV_PY, "-m", "pip", "install", "--upgrade", "pip"], self.log)
            specs = [r["spec"] for r in self.reqs if r["key"] not in OPTIONAL]
        else:
            specs = [r["spec"] for r in self.missing]
        if not specs:
            self.log("Nothing to install.")
            return

        self.log("Installing: " + ", ".join(specs))
        self.log("This can take several minutes, please keep the window open...")
        code = stream([VENV_PY, "-m", "pip", "install"] + specs, self.log)
        if code != 0:
            self.log("pip reported an error (see above).")
            self.ui(messagebox.showerror, "Installation failed",
                    "Some libraries could not be installed. Check your internet connection "
                    "and look at the log for the exact error.")
        else:
            self.log("Installation finished.")
        self.task_check(auto_selftest=True)

    def task_selftest(self):
        if not os.path.exists(VENV_PY):
            self.log("Install the libraries first.")
            return
        mods = [IMPORT_NAMES[r["key"]] for r in self.reqs if r["key"] in IMPORT_NAMES]
        self.log("Self-test: importing every library (PyTorch can take ~30 seconds)...")
        code, out = run([VENV_PY, "-c", SELFTEST_SCRIPT] + mods, timeout=600)
        payload = marker_payload(out)
        if payload is None:
            self.log("Self-test crashed:\n" + out)
            self.selftest_ok = False
            return
        failures = {m: err for m, err in json.loads(payload).items() if err}
        if not failures:
            self.selftest_ok = True
            self._write_marker()
            self.log("✔ Self-test passed. All libraries load correctly.")
            return
        self.selftest_ok = False
        hints = []
        for m, err in failures.items():
            self.log(f"✘ {m}: {err}")
            if "DLL" in err or "c10" in err or "WinError 126" in err:
                hints.append("PyTorch needs the Microsoft Visual C++ Redistributable.\n"
                             f"Download and install it from:\n{VC_REDIST_URL}\n"
                             "then press 'Run self-test' again.")
        msg = "These libraries are installed but fail to load:\n\n" + "\n".join(failures)
        if hints:
            msg += "\n\n" + hints[0]
            self.log(hints[0])
        self.ui(messagebox.showwarning, "Self-test failed", msg)

    def _marker_matches(self):
        try:
            with open(MARKER_FILE, encoding="utf-8") as f:
                return f.read() == json.dumps(self.versions, sort_keys=True)
        except OSError:
            return False

    def _write_marker(self):
        try:
            with open(MARKER_FILE, "w", encoding="utf-8") as f:
                f.write(json.dumps(self.versions, sort_keys=True))
        except OSError:
            pass

    def task_test_key(self, key):
        if not key:
            self.ui(messagebox.showinfo, "Gemini", "Please type an API key first.")
            return
        if not self.selftest_ok:
            self.ui(messagebox.showinfo, "Gemini", "Install the libraries first (tab 1).")
            return
        model = gemini_model_name()
        self.log(f"Testing Gemini key with model {model}...")
        code, out = run([VENV_PY, "-c", GEMINI_TEST_SCRIPT, model], stdin_text=key + "\n",
                        timeout=90)
        payload = marker_payload(out)
        if payload and payload.startswith("OK"):
            self.log("✔ Gemini key works.")
            self.ui(messagebox.showinfo, "Gemini", "The key works!")
        else:
            last = out.strip().splitlines()[-1] if out.strip() else "no answer"
            self.log("✘ Gemini test failed: " + last)
            self.ui(messagebox.showerror, "Gemini", "The key did not work:\n\n" + last[:400])

    def task_admin_password(self, p1, p2):
        if len(p1) < 4:
            self.ui(messagebox.showinfo, "Password", "Use at least 4 characters.")
            return
        if p1 != p2:
            self.ui(messagebox.showinfo, "Password", "The two passwords are not the same.")
            return
        if not self.selftest_ok:
            self.ui(messagebox.showinfo, "Password", "Install the libraries first (tab 1).")
            return
        self.log("Changing admin password...")
        code, out = run([VENV_PY, "-c", ADMIN_PASSWORD_SCRIPT], stdin_text=p1 + "\n", timeout=120)
        payload = marker_payload(out) or ""
        if payload.startswith("OK"):
            self.log("✔ Admin password changed for " + payload[3:])
            self.ui(self.pw1.set, "")
            self.ui(self.pw2.set, "")
            self.ui(messagebox.showinfo, "Password", "Admin password changed.")
        elif payload == "NOADMIN":
            self.ui(messagebox.showinfo, "Password",
                    "No admin account exists yet. Start the server once (it creates "
                    "admin / 123) and then change the password here.")
        else:
            self.log("Could not change the password:\n" + out)
            self.ui(messagebox.showerror, "Password", "Could not change the password. See the log.")

    # ----- settings (quick, run on GUI thread) -------------------------------
    def _load_settings(self):
        env = read_env()
        self.key_var.set(env.get("GEMINI_API_KEY", ""))
        self.port_var.set(env.get("PORT", DEFAULT_PORT))
        self.lan_var.set(env.get("LAUNCHER_ALLOW_LAN", "0") == "1")
        if not env.get("GEMINI_API_KEY"):
            self.after(800, lambda: self.log("No Gemini API key yet. The AI advisor and chatbot "
                                             "need one (tab 2)."))

    def _port(self):
        p = self.port_var.get().strip()
        if not p.isdigit() or not 1 <= int(p) <= 65535:
            raise ValueError
        return int(p)

    def save_settings(self):
        try:
            port = self._port()
        except ValueError:
            messagebox.showerror("Settings", "The port must be a number between 1 and 65535.")
            return
        env = read_env()
        updates = {
            "GEMINI_API_KEY": self.key_var.get().strip(),
            "PORT": str(port),
            "LAUNCHER_ALLOW_LAN": "1" if self.lan_var.get() else "0",
        }
        if not env.get("SECRET_KEY"):
            updates["SECRET_KEY"] = secrets.token_hex(32)
        write_env(updates)
        self.log("Settings saved to .env")

        lan_before = env.get("LAUNCHER_ALLOW_LAN") == "1" and env.get("PORT") == str(port)
        if self.lan_var.get() and IS_WIN and not lan_before:
            if open_firewall(port):
                self.log(f"Firewall rule '{FIREWALL_RULE}' added for port {port}.")
            else:
                self.log("Firewall change was cancelled or failed.")
                messagebox.showwarning("Firewall", "The firewall port was not opened "
                                                   "(admin permission was refused).")
        self._refresh_urls()
        self._update_ready()
        messagebox.showinfo("Settings", "Settings saved. Restart the server if it is running.")

    def empty_database(self):
        if self.server and self.server.poll() is None:
            messagebox.showinfo("Database", "Stop the server first.")
            return
        if not os.path.exists(DB_FILE):
            messagebox.showinfo("Database", "There is no database yet; it will be created empty.")
            return
        if not messagebox.askyesno("Empty database",
                                   "The current database will be renamed to a backup file and a "
                                   "new empty one will be created on the next start "
                                   "(admin / 123).\n\nContinue?"):
            return
        stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = os.path.join(BASE, f"health_backup_{stamp}.db")
        os.rename(DB_FILE, backup)
        self.log(f"Database moved to {os.path.basename(backup)}")
        self._update_ready()

    # ----- server -----------------------------------------------------------
    def _refresh_urls(self):
        port = self.port_var.get().strip() or DEFAULT_PORT
        self.url_local.configure(text=f"http://localhost:{port}")
        self.url_lan.configure(text=f"http://{local_ip()}:{port}")

    def start_server(self):
        if not self.is_ready():
            messagebox.showinfo("Not ready", "Please complete tab 1 first.")
            return
        env = read_env()
        if not env.get("SECRET_KEY"):
            write_env({"SECRET_KEY": secrets.token_hex(32)})
        port = int(env.get("PORT", DEFAULT_PORT) or DEFAULT_PORT)
        if not port_is_free(port):
            messagebox.showerror("Port busy", f"Port {port} is already in use (maybe the app is "
                                              f"already running in another window). Choose another "
                                              f"port in Settings.")
            return
        self.port_var.set(str(port))
        self._refresh_urls()
        self.log(f"Starting server on port {port}...")
        try:
            self.server = subprocess.Popen(
                [VENV_PY, RUN_FILE], cwd=BASE, env=child_env(),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace", bufsize=1,
                creationflags=NO_WINDOW,
            )
        except OSError as e:
            messagebox.showerror("Error", f"Could not start the server:\n{e}")
            return
        self._set_server_state("starting")
        threading.Thread(target=self._read_server, args=(self.server,), daemon=True).start()

    def _read_server(self, proc):
        opened = False
        for line in proc.stdout:
            line = line.rstrip()
            if not line:
                continue
            self.log("server | " + line)
            if not opened and "Running on" in line:
                opened = True
                self.ui(self._set_server_state, "running")
                self.ui(self._auto_open_browser)
        code = proc.wait()
        self.log(f"Server stopped (exit code {code}).")
        self.ui(self._set_server_state, "stopped")

    def _set_server_state(self, state):
        colors = {"starting": "#d97706", "running": "#1a7f37", "stopped": "#c62828"}
        texts = {"starting": "Server starting...", "running": "Server running",
                 "stopped": "Server stopped"}
        self.dot.itemconfigure(self.dot_item, fill=colors[state])
        self.server_label.configure(text=texts[state])
        if state == "stopped":
            self.server = None
        self._update_ready()

    def stop_server(self):
        if self.server and self.server.poll() is None:
            self.log("Stopping server...")
            self.server.terminate()
            try:
                self.server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.server.kill()

    def _auto_open_browser(self):
        if self.auto_open.get():
            self.open_browser()

    def open_browser(self):
        webbrowser.open(self.url_local.cget("text"))

    def _on_close(self):
        if self.server and self.server.poll() is None:
            if not messagebox.askyesno("Exit", "The server is running. Stop it and exit?"):
                return
            self.stop_server()
        self.destroy()


def main():
    if IS_WIN:
        try:  # sharp text on high-DPI screens
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass
    Launcher().mainloop()


if __name__ == "__main__":
    main()
