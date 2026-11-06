"""
Localization & Translation Utility
----------------------------------
This module provides a lightweight internationalization (i18n) dictionary system
for our Flask application. It supports Greek ('el') and English ('en', default).
It contains helper functions to detect the user's active language from their session
or HTTP headers (get_locale) and look up translated phrases with string interpolation (translate).
"""

from flask import session

# Dictionary mapping language codes to key-value translation dictionaries.
# English ('en') is the base language of the UI and serves as the default fallback.
TRANSLATIONS = {
    'el': {
        # General / Layout
        "Smart Health Tracker": "Έξυπνος Καταγραφέας Υγείας",
        "Health Tracker": "Καταγραφέας Υγείας",
        "Admin Panel": "Πίνακας Διαχειριστή",
        "Users": "Χρήστες",
        "Dashboard": "Πίνακας Ελέγχου",
        "Meals": "Γεύματα",
        "Health Logs": "Καταγραφές Υγείας",
        "History": "Ιστορικό",
        "AI Advisor": "Σύμβουλος AI",
        "AI Chatbot": "Συνομιλία AI",
        "My Goals": "Οι Στόχοι Μου",
        "Profile": "Προφίλ",
        "Light Mode": "Λειτουργία Φωτός",
        "Dark Mode": "Σκοτεινή Λειτουργία",
        "Logout": "Αποσύνδεση",
        "Login": "Σύνδεση",
        "Register": "Εγγραφή",
        
        # Index
        "Welcome to Smart Health Tracker": "Καλώς ορίσατε στο Smart Health Tracker",
        "Your personal companion for tracking nutrition, hydration, and wellness. Start your journey to a healthier lifestyle today.": "Ο προσωπικός σας σύντροφος για την παρακολούθηση της διατροφής, της ενυδάτωσης και της ευεξίας σας. Ξεκινήστε το ταξίδι σας προς έναν πιο υγιεινό τρόπο ζωής σήμερα.",
        "Join Now": "Εγγραφείτε Τώρα",
        
        # Dashboard Overview
        "Dashboard Overview": "Επισκόπηση Πίνακα Ελέγχου",
        "Welcome back, {name}!": "Καλώς ήρθες πίσω, {name}!",
        "Today is": "Σήμερα είναι",
        "Day Streak!": "Ημέρες Σερί!",
        "Keep pushing towards your goals!": "Συνεχίστε την προσπάθεια για τους στόχους σας!",
        "Wellness Score": "Σκορ Ευεξίας",
        "Quick Actions": "Γρήγορες Ενέργειες",
        "Log a Meal": "Καταγραφή Γεύματος",
        "Daily Health Log": "Ημερήσια Καταγραφή",
        "Get AI Advice": "Λήψη Συμβουλής AI",
        "Quick Hydration": "Γρήγορη Ενυδάτωση",
        "Current:": "Τρέχων:",
        "+250ml": "+250ml",
        "+500ml": "+500ml",
        "Calories": "Θερμίδες",
        "Goal:": "Στόχος:",
        "Water Intake": "Πρόσληψη Νερού",
        "Sleep": "Ύπνος",
        "Exercise": "Άσκηση",
        "Daily Target:": "Ημερήσιος Στόχος:",
        "Macros Distribution": "Κατανομή Μακροστοιχείων",
        "Protein (g)": "Πρωτεΐνη (g)",
        "Carbs (g)": "Υδατάνθρακες (g)",
        "Fat (g)": "Λίπος (g)",
        "No meals logged today": "Δεν καταγράφηκαν γεύματα σήμερα",
        "Calories History": "Ιστορικό Θερμίδων",
        "Weight Trend (kg)": "Τάση Βάρους (kg)",
        "Weight (kg)": "Βάρος (kg)",
        
        # Meals List/Form
        "Meal Logs": "Καταγραφές Γευμάτων",
        "Logged Meals": "Καταγεγραμμένα Γεύματα",
        "Add Meal": "Προσθήκη Γεύματος",
        "Meal Name": "Όνομα Γεύματος",
        "Time": "Ώρα",
        "Calories (kcal)": "Θερμίδες (kcal)",
        "Protein": "Πρωτεΐνη",
        "Carbohydrates": "Υδατάνθρακες",
        "Fats": "Λίπη",
        "Actions": "Ενέργειες",
        "View": "Προβολή",
        "Delete": "Διαγραφή",
        "Edit Meal": "Επεξεργασία Γεύματος",
        "Log New Meal": "Καταγραφή Νέου Γεύματος",
        "Save Meal": "Αποθήκευση Γεύματος",
        "Cancel": "Ακύρωση",
        "Meal Details": "Λεπτομέρειες Γεύματος",
        "Back to List": "Επιστροφή στη Λίστα",
        "Edit": "Επεξεργασία",
        "Nutrition Info (per serving)": "Διατροφικές Πληροφορίες (ανά μερίδα)",
        "g": "γρ.",
        "Meal Components / Ingredients": "Συστατικά Γεύματος",
        "No ingredients listed.": "Δεν αναφέρονται συστατικά.",
        "Add Ingredient": "Προσθήκη Συστατικού",
        "Ingredient Name": "Όνομα Συστατικού",
        "Amount (g)": "Ποσότητα (γρ.)",
        "Remove": "Αφαίρεση",
        "Nutrition Estimates": "Εκτιμήσεις Διατροφής",
        
        # Health Logs List/Form
        "Health & Wellness Logs": "Καταγραφές Υγείας & Ευεξίας",
        "Log Health Metrics": "Καταγραφή Δεικτών Υγείας",
        "Date": "Ημερομηνία",
        "Water": "Νερό",
        "Exercise (mins)": "Άσκηση (λεπτά)",
        "Sleep (hours)": "Ύπνος (ώρες)",
        "Weight": "Βάρος",
        "Mood": "Διάθεση",
        "Log Daily Metrics": "Καταγραφή Ημερήσιων Δεικτών",
        "Edit Daily Metrics": "Επεξεργασία Ημερήσιων Δεικτών",
        "Save Log": "Αποθήκευση Καταγραφής",
        "Water Intake (Liters)": "Πρόσληψη Νερού (Λίτρα)",
        "Sleep Duration (Hours)": "Διάρκεια Ύπνου (Ώρες)",
        "Exercise Duration (Minutes)": "Διάρκεια Άσκησης (Λεπτά)",
        "Weight (kg)": "Βάρος (kg)",
        "How are you feeling today?": "Πώς αισθάνεστε σήμερα;",
        "Excellent": "Εξαιρετικά",
        "Good": "Καλά",
        "Okay": "Μέτρια",
        "Tired": "Κουρασμένος/η",
        "Stressed": "Αγχωμένος/η",
        "Poor": "Χάλια",
        
        # History
        "Historical Progress": "Ιστορική Πρόοδος",
        "Your Health & Fitness Journey": "Το Ταξίδι Υγείας & Φυσικής Κατάστασης",
        "Metric Overview": "Επισκόπηση Δεικτών",
        "Select Metric:": "Επιλογή Δείκτη:",
        "Sleep (Hours)": "Ύπνος (Ώρες)",
        "Exercise (Minutes)": "Άσκηση (Λεπτά)",
        "Select Range:": "Επιλογή Εύρους:",
        "Last 7 Days": "Τελευταίες 7 Ημέρες",
        "Last 30 Days": "Τελευταίες 30 Ημέρες",
        "Detailed Log History": "Λεπτομερές Ιστορικό Καταγραφών",
        "No health logs found for this period.": "Δεν βρέθηκαν καταγραφές υγείας για αυτήν την περίοδο.",
        
        # AI Advisor / Chatbot
        "Personal AI Wellness Advisor": "Προσωπικός Σύμβουλος Ευεξίας AI",
        "Get personalized insights and recommendations based on your health logs.": "Λάβετε εξατομικευμένες πληροφορίες και προτάσεις με βάση τις καταγραφές υγείας σας.",
        "Generate Advice": "Δημιουργία Συμβουλής",
        "Generating advice...": "Δημιουργία συμβουλής...",
        "AI Health Chatbot": "Συνομιλία Υγείας AI",
        "Ask me anything about fitness, nutrition, or sleep!": "Ρωτήστε με ό,τι θέλετε για τη φυσική κατάσταση, τη διατροφή ή τον ύπνο!",
        "Type your message here...": "Πληκτρολογήστε το μήνυμά σας εδώ...",
        "Send": "Αποστολή",
        "Weekly Trend Insight": "Εβδομαδιαία Τάση & Συμβουλή",
        "Your Daily Action Plan": "Το Ημερήσιο Πλάνο Δράσης Σας",
        "Food Quality Assessment": "Αξιολόγηση Ποιότητας Διατροφής",
        
        # Goals
        "My Health Goals": "Οι Στόχοι Υγείας Μου",
        "Track and manage your daily and weekly health targets.": "Παρακολουθήστε και διαχειριστείτε τους ημερήσιους και εβδομαδιαίους στόχους υγείας σας.",
        "Edit Goals": "Επεξεργασία Στόχων",
        "Daily Calorie Goal (kcal)": "Ημερήσιος Στόχος Θερμίδων (kcal)",
        "Daily Water Goal (Liters)": "Ημερήσιος Στόχος Νερού (Λίτρα)",
        "Daily Sleep Goal (Hours)": "Ημερήσιος Στόχος Ύπνου (Ώρες)",
        "Weekly Exercise Goal (Minutes)": "Εβδομαδιαίος Στόχος Άσκησης (Λεπτά)",
        "Target Weight (kg)": "Στόχος Βάρους (kg)",
        "Save Goals": "Αποθήκευση Στόχων",
        "Save Changes": "Αποθήκευση Αλλαγών",
        
        # Profile
        "User Profile": "Προφίλ Χρήστη",
        "Manage your account details and physical metrics.": "Διαχειριστείτε τις λεπτομέρειες του λογαριασμού σας και τις φυσικές μετρήσεις.",
        "Full Name": "Ονοματεπώνυμο",
        "Username": "Όνομα χρήστη",
        "Email": "Email",
        "Physical Metrics": "Φυσικές Μετρήσεις",
        "Age": "Ηλικία",
        "years": "ετών",
        "Height": "Ύψος",
        "cm": "εκ.",
        "Current Weight": "Τρέχον Βάρος",
        "Biological Sex": "Βιολογικό Φύλο",
        "Activity Level": "Επίπεδο Δραστηριότητας",
        "Sedentary": "Καθιστική ζωή",
        "Lightly Active": "Ελαφρώς δραστήριος/α",
        "Moderately Active": "Μέτρια δραστήριος/α",
        "Very Active": "Πολύ δραστήριος/α",
        "Extremely Active": "Εξαιρετικά δραστήριος/α",
        "Male": "Άνδρας",
        "Female": "Γυναίκα",
        "Other": "Άλλο",
        "Edit Profile": "Επεξεργασία Προφίλ",
        "Update Profile": "Ενημέρωση Προφίλ",
        
        # Onboarding
        "Welcome to Smart Health Tracker!": "Καλώς ορίσατε στο Smart Health Tracker!",
        "Let's customize the app for your personal health journey.": "Ας προσαρμόσουμε την εφαρμογή για το προσωπικό σας ταξίδι υγείας.",
        "Get Started": "Ξεκινήστε",
        "Step 1: Account Details": "Βήμα 1: Λεπτομέρειες Λογαριασμού",
        "Step 2: Physical Profile": "Βήμα 2: Φυσικό Προφίλ",
        "Step 3: Goals": "Βήμα 3: Στόχοι",
        "Step 4: AI Assessment": "Βήμα 4: Αξιολόγηση AI",
        "Step 5: Setup Complete": "Βήμα 5: Η Εγκατάσταση Ολοκληρώθηκε",
        "Next": "Επόμενο",
        "Back": "Πίσω",
        "Complete": "Ολοκλήρωση",
        "Set up your basic account details.": "Ορίστε τις βασικές λεπτομέρειες του λογαριασμού σας.",
        "Enter your height, weight, age, and activity level so we can calculate your personalized goals.": "Εισαγάγετε το ύψος, το βάρος, την ηλικία και το επίπεδο δραστηριότητάς σας για να υπολογίσουμε τους εξατομικευμένους στόχους σας.",
        "Set your health targets.": "Ορίστε τους στόχους υγείας σας.",
        "Analyzing your profile to generate personalized goals...": "Ανάλυση του προφίλ σας για τη δημιουργία εξατομικευμένων στόχων...",
        "Your personalized health tracker is ready. Let's start tracking your health journey!": "Ο εξατομικευμένος καταγραφέας υγείας σας είναι έτοιμος. Ας ξεκινήσουμε την παρακολούθηση της υγείας σας!",
        "Go to Dashboard": "Μετάβαση στον Πίνακα Ελέγχου",
        
        # Login / Register
        "Sign In to Your Account": "Συνδεθείτε στον Λογαριασμό Σας",
        "Email Address": "Διεύθυνση Email",
        "Password": "Κωδικός Πρόσβασης",
        "Sign In": "Σύνδεση",
        "Don't have an account?": "Δεν έχετε λογαριασμό;",
        "Create an Account": "Δημιουργήστε έναν Λογαριασμό",
        "Get started with your personal health tracker today.": "Ξεκινήστε με τον προσωπικό σας καταγραφέα υγείας σήμερα.",
        "Already have an account?": "Έχετε ήδη λογαριασμό;",
        "Confirm Password": "Επιβεβαίωση Κωδικού",
        "Welcome Back": "Καλώς Ήρθατε Πίσω",
        "Login to your health dashboard": "Συνδεθείτε στον πίνακα ελέγχου υγείας σας",
        "Username or Email": "Όνομα χρήστη ή Email",
        "Username or email": "Όνομα χρήστη ή email",
        "Create Account": "Δημιουργία Λογαριασμού",
        "Join Smart Health Tracker": "Γίνετε μέλος του Smart Health Tracker",
        "Fill out the form below to create your account.": "Συμπληρώστε την παρακάτω φόρμα για να δημιουργήσετε τον λογαριασμό σας.",
        
        # Admin
        "System Statistics": "Στατιστικά Συστήματος",
        "Total Users": "Σύνολο Χρηστών",
        "Total Meals Logged": "Σύνολο Γευμάτων",
        "Total Health Logs": "Σύνολο Καταγραφών",
        "Registered Users": "Εγγεγραμμένοι Χρήστες",
        "Role": "Ρόλος",
        "Onboarding": "Εισαγωγή",
        "Admin": "Διαχειριστής",
        "User": "Χρήστης",
        "Completed": "Ολοκληρώθηκε",
        "Pending": "Σε εκκρεμότητα",
        "Manage Users": "Διαχείριση Χρηστών",
        "System Admin Panel": "Πίνακας Διαχειριστή Συστήματος",
        "Overview of application performance and users.": "Επισκόπηση της απόδοσης και των χρηστών της εφαρμογής.",
        "All Registered Users": "Όλοι οι Εγγεγραμμένοι Χρήστες",
        "List of all users in the system.": "Λίστα όλων των χρηστών στο σύστημα.",
        
        # Flashes / Messages
        "Meal added successfully!": "Το γεύμα προστέθηκε με επιτυχία!",
        "Meal deleted successfully!": "Το γεύμα διαγράφηκε με επιτυχία!",
        "Meal updated successfully!": "Το γεύμα ενημερώθηκε με επιτυχία!",
        "Health log saved successfully!": "Η καταγραφή υγείας αποθηκεύτηκε με επιτυχία!",
        "Goals saved successfully!": "Οι στόχοι αποθηκεύτηκαν με επιτυχία!",
        "Profile updated successfully!": "Το προφίλ ενημερώθηκε με επιτυχία!",
        "Logged in successfully.": "Συνδεθήκατε με επιτυχία.",
        "Invalid username or password.": "Μη έγκυρο όνομα χρήστη ή κωδικός πρόσβασης.",
        "You must complete onboarding first.": "Πρέπει πρώτα να ολοκληρώσετε την εισαγωγική διαδικασία.",
        "Registration successful! Please log in.": "Η εγγραφή ήταν επιτυχής! Παρακαλώ συνδεθείτε.",
        "Account created! Please complete onboarding.": "Ο λογαριασμός δημιουργήθηκε! Παρακαλώ ολοκληρώστε την εισαγωγική διαδικασία.",
        
        # Errors
        "Access Denied": "Άρνηση Πρόσβασης",
        "You do not have permission to access this page.": "Δεν έχετε άδεια πρόσβασης σε αυτή τη σελίδα.",
        "Page Not Found": "Η Σελίδα Δεν Βρέθηκε",
        "The page you are looking for does not exist.": "Η σελίδα που αναζητάτε δεν υπάρχει.",
        "Server Error": "Σφάλμα Διακομιστή",
        "Something went wrong on our end. Please try again later.": "Κάτι πήγε στραβά από την πλευρά μας. Παρακαλώ δοκιμάστε ξανά αργότερα.",

        # AI Advisor page & recommendations
        "AI Advisor": "Σύμβουλος AI",
        "Your Smart Health Partner": "Ο Έξυπνος Σύντροφος Υγείας Σας",
        "I've analyzed your recent logs and goals to provide personalized wellness insights.": "Ανέλυσα τις πρόσφατες καταγραφές και τους στόχους σας για να παρέχω εξατομικευμένες συμβουλές ευεξίας.",
        "Daily Recommendations": "Ημερήσιες Προτάσεις",
        "All Caught Up!": "Όλα έτοιμα!",
        "You're doing great! There are no areas requiring immediate attention today, or you haven't logged enough data yet.": "Τα πάτε εξαιρετικά! Δεν υπάρχουν τομείς που απαιτούν άμεση προσοχή σήμερα ή δεν έχετε καταγράψει αρκετά δεδομένα ακόμη.",
        "Add Health Log": "Προσθήκη Καταγραφής",
        "Disclaimer:": "Αποποίηση ευθύνης:",
        "The AI Wellness Advisor provides general wellness suggestions based on your input. It is a rule-based system and does not provide medical diagnosis, treatment, or advice. Always consult a healthcare professional for medical concerns.": "Ο Σύμβουλος Ευεξίας AI παρέχει γενικές προτάσεις ευεξίας με βάση τα δεδομένα σας. Είναι ένα σύστημα βασισμένο σε κανόνες και δεν παρέχει ιατρική διάγνωση, θεραπεία ή συμβουλές. Πάντα να συμβουλεύεστε έναν επαγγελματία υγείας για ιατρικά θέματα.",
        "Improve your sleep schedule.": "Βελτιώστε το πρόγραμμα ύπνου σας.",
        "You slept {actual_sleep}h, which is below your goal of {target_sleep}h. Try going to bed 30 minutes earlier tonight.": "Κοιμηθήκατε {actual_sleep} ώρες, που είναι κάτω από το στόχο σας των {target_sleep} ωρών. Δοκιμάστε να κοιμηθείτε 30 λεπτά νωρίτερα απόψε.",
        "Drink more water.": "Πιείτε περισσότερο νερό.",
        "You drank {actual_water}L, which is below your goal of {target_water}L. Keep a water bottle nearby.": "Ήπιατε {actual_water}L, που είναι κάτω από το στόχο σας των {target_water}L. Κρατήστε ένα μπουκάλι νερό κοντά σας.",
        "Get moving today.": "Δραστηριοποιηθείτε σήμερα.",
        "You exercised {actual_exercise} mins, below your target of {round_target_exercise} mins. Consider a short walk.": "Ασκηθήκατε {actual_exercise} λεπτά, κάτω από το στόχο σας των {round_target_exercise} λεπτών. Σκεφτείτε να κάνετε μια σύντομη βόλτα.",
        "Consider a lighter next meal.": "Σκεφτείτε ένα πιο ελαφρύ επόμενο γεύμα.",
        "You consumed {total_calories} kcal, exceeding your daily target of {target_calories} kcal. Focus on protein and vegetables for the rest of the day.": "Καταναλώσατε {total_calories} kcal, υπερβαίνοντας τον ημερήσιο στόχο σας των {target_calories} kcal. Εστιάστε σε πρωτεΐνες και λαχανικά για το υπόλοιπο της ημέρας.",
        "Take some time for yourself.": "Αφιερώστε λίγο χρόνο στον εαυτό σας.",
        "Your mood is low today. Taking a few minutes to breathe deeply or do something you enjoy might help.": "Η διάθεσή σας είναι χαμηλή σήμερα. Αφιερώστε λίγα λεπτά για να αναπνεύσετε βαθιά ή να κάνετε κάτι που σας ευχαριστεί.",
        "sleep": "ύπνος",
        "water": "νερό",
        "exercise": "άσκηση",
        "nutrition": "διατροφή",
        "mood": "διάθεση",

        # Chatbot translations
        "Today you've consumed {total_calories} calories, drank {water}L of water, and did {exercise} minutes of exercise.": "Σήμερα έχετε καταναλώσει {total_calories} θερμίδες, ήπιατε {water}L νερό και κάνατε {exercise} λεπτά άσκησης.",
        "Keep it up! You're on a {streak}-day streak! 🔥 ": "Συνεχίστε έτσι! Είστε σε σερί {streak} ημερών! 🔥 ",
        " ✨ You've reached your hydration goal for today!": " ✨ Φτάσατε τον στόχο ενυδάτωσης για σήμερα!",
        " You need about {rem}L more to hit your goal.": " Χρειάζεστε περίπου {rem}L ακόμη για να φτάσετε τον στόχο σας.",
        "Hello! I'm your AI health coach. ": "Γεια σας! Είμαι ο AI προπονητής υγείας σας. ",
        " I noticed you're over your calorie goal. Maybe try a light walk this evening?": " Παρατήρησα ότι ξεπεράσατε τον στόχο θερμίδων σας. Ίσως να δοκιμάσετε έναν ελαφρύ περίπατο απόψε;",
        " Try drinking a large glass of water now to stay hydrated.": " Δοκιμάστε να πιείτε ένα μεγάλο ποτήρι νερό τώρα για να παραμείνετε ενυδατωμένοι.",

        # Admin Actions
        "System Users": "Χρήστες Συστήματος",
        "Joined": "Εγγραφή",
        "Deactivate": "Απενεργοποίηση",
        "Activate": "Ενεργοποίηση",
        "Make User": "Ορισμός ως Χρήστη",
        "Make Admin": "Ορισμός ως Διαχειριστή",
        "Are you sure you want to delete this user?": "Είστε βέβαιοι ότι θέλετε να διαγράψετε αυτόν τον χρήστη;",
        "Deactivated successfully.": "Απενεργοποιήθηκε με επιτυχία.",
        "Activated successfully.": "Ενεργοποιήθηκε με επιτυχία.",
        "Role changed successfully.": "Ο ρόλος άλλαξε με επιτυχία.",
        "User deleted successfully.": "Ο χρήστης διαγράφηκε με επιτυχία.",
        "Return Home": "Επιστροφή στην Αρχική",
        
        # Admin Advanced Analytics
        "System Activity Heatmap (Last 30 Days)": "Ημερολόγιο Δραστηριότητας Συστήματος (Τελευταίες 30 Ημέρες)",
        "Visualizing system-wide daily logs and meal entries.": "Οπτικοποίηση των ημερήσιων καταγραφών και των γευμάτων σε όλο το σύστημα.",
        "User Role Distribution": "Κατανομή Ρόλων Χρηστών",
        "Peak Activity Hours": "Ώρες Αιχμής Δραστηριότητας",
        "Less": "Λιγότερο",
        "More": "Περισσότερο",
        "activities": "δραστηριότητες",


        # Wellness Score Explanations
        "you haven't filled out your daily health log": "δεν έχετε συμπληρώσει την ημερήσια καταγραφή υγείας σας",
        "sleep was below your goal": "ο ύπνος ήταν κάτω από τον στόχο σας",
        "water intake was low": "η πρόσληψη νερού ήταν χαμηλή",
        "exercise was below your daily average target": "η άσκηση ήταν κάτω από τον μέσο ημερήσιο στόχο σας",
        "your mood was reported as low": "η διάθεσή σας αναφέρθηκε ως χαμηλή",
        "no meals were logged": "δεν καταγράφηκαν γεύματα",
        "calories exceeded your daily target": "οι θερμίδες ξεπέρασαν τον ημερήσιο στόχο σας",
        "calories were well below your daily target": "οι θερμίδες ήταν πολύ κάτω από τον ημερήσιο στόχο σας",
        "Great job! You are hitting all your wellness goals today.": "Εξαιρετική δουλειά! Πετυχαίνετε όλους τους στόχους ευεξίας σας σήμερα.",
        "Your score could improve because: ": "Το σκορ σας θα μπορούσε να βελτιωθεί επειδή: ",

        # Achievements & Gamification
        "My Achievements": "Τα Επιτεύγματά Μου",
        "Achievements": "Επιτεύγματα",
        "Keep it up, {name}!": "Συνέχισε έτσι, {name}!",
        "You have unlocked {unlocked} out of {total} badges. Compete in challenges to establish healthy habits.": "Έχετε ξεκλειδώσει {unlocked} από τα {total} σήματα. Συμμετάσχετε σε προκλήσεις για να χτίσετε υγιεινές συνήθειες.",
        "Current Streak": "Τρέχον Σερί",
        "Progress": "Πρόοδος",
        "Achievements & Badges": "Επιτεύγματα & Σήματα",
        "Streak Master": "Πρωταθλητής Σερί",
        "Log logs or meals for 3+ consecutive days": "Καταγράψτε logs ή γεύματα για 3+ συνεχόμενες ημέρες",
        "3 consecutive days active (Current: {streak} days)": "3 συνεχόμενες ημέρες ενεργός (Τρέχον: {streak} ημέρες)",
        "Hydration Hero": "Ήρωας Ενυδάτωσης",
        "Meet your daily water goal at least once": "Πιάστε τον ημερήσιο στόχο νερού τουλάχιστον μία φορά",
        "Log >= {target}L of water in one day": "Καταγράψτε >= {target}L νερού σε μία ημέρα",
        "Sleep King": "Βασιλιάς του Ύπνου",
        "Meet your daily sleep goal of 8+ hours": "Πιάστε τον ημερήσιο στόχο ύπνου των 8+ ωρών",
        "Log >= {target}h of sleep in one day": "Καταγράψτε >= {target}h ύπνου σε μία ημέρα",
        "Early Bird": "Πρωινό Πουλί",
        "Log breakfast early in the morning": "Καταγράψτε πρωινό νωρίς το πρωί",
        "Log breakfast before 10:00 AM": "Καταγράψτε πρωινό πριν από τις 10:00 π.μ.",
        "Mindfulness": "Ενσυνειδητότητα",
        "Report an excellent mood score of 8 or above": "Καταγράψτε εξαιρετικό σκορ διάθεσης 8 ή παραπάνω",
        "Mood score >= 8/10": "Σκορ διάθεσης >= 8/10",
        "Consistency": "Συνέπεια",
        "Log 5 or more total activities": "Καταγράψτε 5 ή περισσότερες συνολικές δραστηριότητες",
        "Total logs + meals >= 5 (Current: {total})": "Συνολικές καταγραφές + γεύματα >= 5 (Τρέχον: {total})",
        "Hydration Challenge": "Πρόκληση Ενυδάτωσης",
        "Drink water for 3 consecutive days to establish a habit.": "Πιείτε νερό για 3 συνεχόμενες ημέρες για να χτίσετε τη συνήθεια.",
        "Consistency Challenge": "Πρόκληση Συνέπειας",
        "Build consistent logging habits by logging 5 meals or logs.": "Χτίστε συνέπεια καταγράφοντας 5 γεύματα ή ημερολόγια.",
        "Challenge Progress": "Πρόοδος Πρόκλησης",

        # Recipes & Custom Meals
        "My Recipes": "Οι Συνταγές Μου",
        "Save this meal as a Favorite Recipe": "Αποθήκευση ως αγαπημένη συνταγή",
        "Favorite Recipes": "Αγαπημένες Συνταγές",
        "Quick Log": "Γρήγορη Καταγραφή",
        "Recipe Logged Successfully!": "Η συνταγή καταγράφηκε με επιτυχία!",
        "Recipe matches your remaining targets perfectly!": "Η συνταγή ταιριάζει απόλυτα με τους στόχους που απομένουν!",
        "AI Recipe Suggestions": "Προτάσεις Συνταγών AI",
        "Remaining Calories Target:": "Στόχος Θερμίδων που Απομένει:",
        "No recipes match your criteria. Try updating your goals!": "Δεν βρέθηκαν συνταγές. Δοκιμάστε να ενημερώσετε τους στόχους σας!",
        "Meal Saved to Favorites!": "Το γεύμα αποθηκεύτηκε στα Αγαπημένα!",

        # Reports & Analytics
        "Download PDF Report": "Λήψη Αναφοράς PDF",
        "Health & Nutrition Report": "Αναφορά Υγείας & Διατροφής",
        "Report generated on": "Η αναφορά δημιουργήθηκε στις",
        "Weekly Summary": "Εβδομαδιαία Σύνοψη",
        "Monthly Summary": "Μηνιαία Σύνοψη",
        "Averages": "Μέσοι Όροι",
        "Daily Averages": "Ημερήσιοι Μέσοι Όροι",
        "Total Calories Burned": "Συνολικές Θερμίδες",
        "Total Water Consumed": "Συνολικό Νερό",
        "Print Report": "Εκτύπωση Αναφοράς",
        "Close Preview": "Κλείσιμο Προεπισκόπησης",
        "Correlation Dashboard": "Πίνακας Συσχετίσεων",
        "Sleep vs Mood": "Ύπνος vs Διάθεση",
        "Exercise vs Sleep": "Άσκηση vs Ύπνος",
    },
    'en': {}  # Fallback: English strings are defined directly in template/code keys
}


def get_locale():
    """
    Determines the current language preference of the user.

    Priority order:
    1. Explicit session preference ('session['lang']') chosen by user via language switcher.
    2. Best matching language from the browser's HTTP Accept-Language request header.
    3. Fallback to English ('en') if neither is available or if outside a request context.

    Returns:
        str: Active language code, e.g. 'el' or 'en'.
    """
    from flask import request
    try:
        # Check 1: User explicitly changed language in their session cookie
        if session and 'lang' in session:
            return session['lang']
        # Check 2: Detect browser preferred language from request headers
        elif request:
            best = request.accept_languages.best_match(['en', 'el'])
            if best:
                return best
    except RuntimeError:
        # Raised if accessed outside of an active Flask application or request context
        pass
    except Exception:
        # Fall back safely on any unexpected exception
        pass
    
    # Default fallback language
    return 'en'


def translate(text, **kwargs):
    """
    Translates a source English text string into the currently active locale.

    Supports keyword formatting placeholders, e.g.:
        translate("Welcome back, {name}!", name="Alex")

    Parameters:
        text (str): The English base string acting as the lookup key.
        **kwargs: Optional dynamic arguments to substitute into the translated string.

    Returns:
        str: The translated and formatted string, or the original string if no translation is found.
    """
    # Find out whether the user is browsing in Greek or English
    lang = get_locale()
    
    # Look up translation for the active language. If not found, default to the original English text
    translation = TRANSLATIONS.get(lang, {}).get(text, text)
    
    # Safely interpolate any provided dynamic keyword arguments
    try:
        return translation.format(**kwargs)
    except Exception:
        # If string formatting fails (e.g., mismatched brackets or keys), return raw translation
        return translation

