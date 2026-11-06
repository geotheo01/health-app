# Smart Health Tracker

A web application for tracking nutrition and health, built as a diploma thesis at the
**University of West Attica (ΠΑΔΑ)**, Department of Informatics and Computer Engineering.

It combines a custom **YOLOv8 food-recognition model** (54 food classes) with a
**Google Gemini** AI advisor and chatbot. Users take a photo of their meal, the app
recognises the food, estimates calories and macronutrients, and gives personalised advice.

---

## Features

- **Meal photo recognition** with a YOLOv8 model trained on four merged Roboflow datasets
- **Nutrition estimates** (calories, protein, carbs, fat) from a built-in nutrition database
- **AI advisor and chatbot** powered by Google Gemini
- **Daily logs, goals and history** with charts
- **Wellness score and achievements**
- **Onboarding** with BMR / calorie target calculation
- **Admin panel** with user management and statistics
- **Graphical launcher** that installs everything and runs the app with one double-click

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| Database | SQLite via Flask-SQLAlchemy |
| Authentication | Flask-Login, Flask-WTF (CSRF) |
| Computer vision | Ultralytics YOLOv8, PyTorch |
| Generative AI | Google Gemini (`google-genai`) |
| Frontend | Jinja2 templates, HTML, CSS, JavaScript |

Architecture: **MVC** with a **service layer** and the **DAO** pattern.

---

## Quick start (Windows)

You only need **Python 3.12** installed
([python.org/downloads](https://www.python.org/downloads/), tick *"Add Python to PATH"*).

1. Download or clone this repository.
2. Double-click **`SmartHealth.bat`**.
3. In the launcher window:
   - **1. Libraries** → press *Install missing libraries* (first time only, downloads about 2-3 GB).
   - **2. Settings** → paste your Gemini API key and press *Save settings*.
   - **3. Run** → press *Start*. The browser opens automatically.

The launcher keeps all libraries in a private `venv` folder, so it does not affect other
Python programs on the computer. Next time, it checks everything in a second and goes
straight to *Start*.

> If the window does not appear, run `SmartHealth.bat debug` from a terminal to see the error.

## Manual setup (any OS)

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>

python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

# create your configuration
copy .env.example .env      # Windows
cp .env.example .env        # Linux / macOS
# then edit .env and add your GEMINI_API_KEY

python run.py
```

Open **http://localhost:3535** (or the port you set in `.env`).

---

## Configuration (`.env`)

| Variable | Required | Description |
|---|---|---|
| `GEMINI_API_KEY` | Yes, for AI features | Key from [Google AI Studio](https://aistudio.google.com/apikey) |
| `SECRET_KEY` | Recommended | Random string that signs login sessions |
| `PORT` | No | Web server port, default `3535` |
| `FLASK_ENV` | No | Set to `development` for debug mode |

`.env` is **never** committed to Git. Use `.env.example` as a template.

## Default admin account

On the first start an empty database (`health.db`) is created with an admin user:

- **Email:** `admin@smarthealth.local`
- **Password:** `123`

**Change this password** before using the app on a shared network
(launcher → *Settings* → *Change admin password*).

## Accessing from other computers

The server listens on all network interfaces. Other computers on the same network can
open `http://<this-computer's-IP>:3535`. On Windows the port must be allowed in the
firewall; the launcher can do this for you (*Settings* → *Allow other computers...*).

---

## Project structure

```
├── SmartHealth.bat          # double-click to open the launcher (Windows)
├── launcher.py              # graphical installer / runner (Tkinter, standard library only)
├── start_app.bat            # simple start without the launcher (after setup)
├── run.py                   # application entry point
├── config.py                # Flask configuration (reads .env)
├── init_db.py               # creates the database tables
├── requirements.txt
├── .env.example             # configuration template
├── app/
│   ├── __init__.py          # application factory
│   ├── controllers/         # Flask blueprints (routes)
│   ├── services/            # business logic
│   ├── dao/                 # data access objects
│   ├── models/              # SQLAlchemy models
│   ├── ai/                  # Gemini advisor and rule-based advisor
│   ├── utils/               # decorators, translations, achievements
│   ├── data/
│   │   └── nutrition_db.json
│   ├── templates/           # Jinja2 HTML templates
│   └── static/              # CSS, icons, uploaded meal photos
└── runs/detect/runs/detect/food_model_merged/weights/
    └── best.pt              # trained YOLOv8 food-recognition model
```

## Notes

- The YOLO model runs on the CPU; a graphics card is not required.
- On some Windows computers PyTorch needs the
  [Microsoft Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).
  The launcher detects this and shows the link.
- The built-in Flask server is meant for development and demonstration, not for
  production use on the public internet.

## Author

**Theocharis Georgios**
Diploma thesis, University of West Attica (ΠΑΔΑ)
