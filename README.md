
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
| 00115935   | Mengxi Li      | mengxi-dev       |
| [UWA ID]   | [Member 2]     | [GitHub2]        |
| [UWA ID]   | [Member 3]     | [GitHub3]        |
| [UWA ID]   | [Member 4]     | [GitHub4]        |

> Please replace placeholders with final group member information.

---

## 🚀 How to Launch

### 1. Clone the Repository
```bash
git clone https://github.com/your-team/pathfinder-app.git
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
/pathfinder-app/
│
├── app.py
├── /templates/
├── /static/
├── /tests/
├── /deliverables/
├── README.md
└── requirements.txt
```

---

## 📅 Milestones

- ✅ **Week 8 (Apr 28 – May 2)**: Static GUI design (HTML + CSS demo)
- ✅ **Week 9 (May 5 – 9)**: Working demo with minimal dynamic functionality
- ✅ **May 16, 11:59pm**: Final project submission
- ✅ **Week 12**: Project presentation (12-minute demo + Q&A)

---

## ✅ Submission Checklist

- [x] `README.md` with purpose, launch/test instructions, group table
- [x] Complete and commented source code
- [x] `requirements.txt` generated with `pip freeze > requirements.txt`
- [x] Deliverables folder with presentation/demo materials
- [x] No `.git` or virtual environment folders included in the final `.zip`
- [x] Repository made **public** before submission

---

*This project is submitted as part of the unit CITS3403/CITS5505 at the University of Western Australia. All work complies with the provided technical specifications and rubric.*
