
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
- HTML
- CSS via Tailwind
- JavaScript with jQuery
- Flask (Python)
- SQLite via SQLAlchemy
- AJAX for asynchronous updates

### Optional Libraries
- Chart.js – for visualizing data
- Font Awesome – for icons
- (Optional) NLP tools such as spaCy or NLTK – for resume processing

*Only technologies permitted by the project specification are used.*

## 👥 Group Members

| UWA ID     | Name           | GitHub Username |
|------------|----------------|------------------|
| 24194872   | Mengxi Li      | Viloetsisi       |
| 23723494   | Lucy Zhi       | Yutong Zhi       |
| 23734789   | Feiyue Zhang   | Feiyue222        |
| 23723494   | Kean Scott     | keanscott        |




## 🚀 How to Launch

### 1. Clone the Repository
```bash

git clone https://github.com/Viloetsisi/AgileWeb_group_project/pathfinder-app.git

cd pathfinder-app
```

### 2. Set Up Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
flask run
```
Visit `http://127.0.0.1:5000` in your browser.

---

## 🧪 How to Run Tests

```bash
pytest tests/
```

> Ensure your virtual environment is activated and Flask environment is properly set.

---

## 📂 Project Structure

```


pathfinder-app/
├── app.py                   # Main Flask application
├── project-signup.py        # Entry point for running the app
├── requirements.txt         # Python dependencies
├── README.md                # Project overview & instructions
├── .gitignore               # Files/folders to ignore in Git
├── LICENSE                  # MIT License
│
├── templates/               # HTML templates
│   ├── base.html            # Base layout (navbar, footer, etc.)
│   ├── index.html           # Introductory view
│   ├── upload.html          # Upload Data view
│   ├── visualize.html       # Visualise Data view
│   └── share.html           # Share Data view
│
├── static/                  # Static assets
│   ├── css/
│   │   └── styles.css       # Tailwind overrides or custom styles
│   ├── js/
│   │   └── scripts.js       # AJAX calls, interactivity
│   └── images/              # Logo, placeholders, etc.
│
├── tests/                   # Automated tests
│   ├── conftest.py          # pytest fixtures (e.g. test client)
│   ├── test_auth.py         # Signup/Login tests
│   ├── test_upload.py       # Data upload tests
│   ├── test_visualize.py    # Visualization logic tests
│   └── test_share.py        # Sharing functionality tests
│
└── deliverables/            # Materials for lab presentations
    ├── gui_design/          # Static HTML/CSS mockups
    └── demo_prototype/      # Screenshots or small demo notes

