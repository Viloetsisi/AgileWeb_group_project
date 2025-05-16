



# PathFinder – Student Career Companion

## 📌 Project Overview
PathFinder is a data-driven web application designed to help undergraduate students at UWA prepare for their careers. The platform allows users to upload personal academic data (e.g., resumes, transcripts, and interests), receive automated career insights, and selectively share their profile with mentors, peers, or potential employers.

This application satisfies all required project criteria:
- **Engaging**: Clean UI and personalized results
- **Effective**: Offers skill gap analysis, job fit recommendations
- **Intuitive**: Simple navigation with four structured views

## 🌐 Views Implemented
1. **Introductory View** – Homepage with overview, sign-up/login interface
2. **Upload Data View** – Allows users to submit resumes, transcripts, and skill tags
3. **Visualise Data View** – Displays career fit metrics, skill gaps, and personalized insights
4. **Share Data View** – Enables secure and selective profile sharing with other users

## 🛠️ Technologies Used

### Core Technologies
- Python (Flask)
- HTML
- CSS (Bootstrap 5)
- JavaScript (vanilla & Chart.js)
- SQLAlchemy (with SQLite)
- AJAX for asynchronous updates

### Optional Libraries
- Flask-WTF, Flask-Mail
- Chart.js – for visualizing data
- python-dotenv – for environment variables
- Font Awesome – for icons

*Only technologies permitted by the project specification are used.*

## 👥 Group Members

| UWA ID     | Name           | GitHub Username |
|------------|----------------|----------------|
| 24194872   | Mengxi Li      | Viloetsisi     |
| 23723494   | Lucy Zhi       | Yutong Zhi     |
| 23734789   | Feiyue Zhang   | Feiyue222      |
| 23723494   | Kean Scott     | keanscott      |

## 🚀 How to Launch

### 1. Clone the Repository
```bash
git clone https://github.com/Viloetsisi/AgileWeb_group_project.git
cd AgileWeb_group_project

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4.Database Migration & Initialization
```bash
# Initialize migrations folder (only if not exists)
flask db init

# Generate migration scripts (only if there are model changes)
flask db migrate -m "Initial migration"

# Apply migrations and create tables
flask db upgrade
```
### 5. Run the Application
```bash
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🧪 How to Run Tests

```bash
python -m unittest discover tests
```

> Ensure your virtual environment is activated and Flask environment is properly set.

---

## 📂 Project Structure

```
AgileWeb_group_project/
├── app.py                   # Main Flask application
├── config.py                # Configuration settings
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (DO NOT COMMIT)
├── .gitignore
├── uploads                  # store the upload files
│
├── blueprints/              # Modular route handlers (Flask Blueprints)
│   ├── auth_routes.py
│   ├── profile_routes.py
│   ├── jobs_routes.py
│   ├── share_routes.py
│   ├── market_routes.py
│   └── dashboard_routes.py
│
├── templates/               # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── upload_document.html
│   ├── visualize.html
│   ├── login.html
│   ├── signup.html
│   ├── profile.html
│   ├── dashboard.html
│   ├── jobs.html
│   └── share.html
│
├── static/                  # Static assets (CSS, JS, images)
│   ├── css/
│   ├── js/
│   └── images/
│
├── tests/                   # Automated tests
│   ├── test_auth.py
│   ├── test_dashboard.py
│   ├── test_jobs.py
|   ├── test_profile.py
│   └── test_share.py


