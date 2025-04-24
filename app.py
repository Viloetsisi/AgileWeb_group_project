#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy

# ---------------------------------
# Application Initialization
# ---------------------------------

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY', 'change_this_to_a_secure_random_key'
)
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///pathfinder.db'
)
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)

# ---------------------------------
# Database Models
# ---------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password = db.Column(db.String(120), nullable=False)

class DataEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(120), nullable=False)

class SharedEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data_id = db.Column(db.Integer, db.ForeignKey('data_entry.id'), nullable=False)
    shared_with_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Job application model (added by Feiyue)
class JobApplication(db.Model):
    __tablename__ = 'job_applications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_title = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    application_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)

    user = db.relationship('User', backref='applications')

# ---------------------------------
# Application Routes
# ---------------------------------

@application.route('/')
def index():
    """Introductory view: homepage with signup/login links"""
    return render_template('index.html')

@application.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup view"""
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('signup.html')

@application.route('/login', methods=['GET', 'POST'])
def login():
    """Login view"""
    if request.method == 'POST':
        return redirect(url_for('index'))
    return render_template('login.html')

@application.route('/upload', methods=['GET', 'POST'])
def upload():
    """Upload view"""
    if request.method == 'POST':
        file = request.files.get('data_file')
        desc = request.form.get('description', '')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(save_path)
            entry = DataEntry(user_id=1, filename=save_path)
            db.session.add(entry)
            db.session.commit()
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))
        flash('Please select a file to upload', 'error')
    return render_template('upload.html')

@application.route('/visualize')
def visualize():
    """Visualise Data view"""
    return render_template('visualize.html')

@application.route('/share', methods=['GET', 'POST'])
def share():
    """Share Data view"""
    entries = [
        type('E', (), {'id': 1, 'filename': 'grades.csv', 'upload_date': datetime.today(), 'shared_with_ids': [2]}),
        type('E', (), {'id': 2, 'filename': 'resume.pdf', 'upload_date': datetime.today(), 'shared_with_ids': []}),
    ]
    all_users = [
        type('U', (), {'id': 1, 'username': 'alice'}),
        type('U', (), {'id': 2, 'username': 'bob'}),
        type('U', (), {'id': 3, 'username': 'carol'}),
    ]
    if request.method == 'POST':
        pass
    return render_template('share.html', entries=entries, all_users=all_users)

@application.route('/dashboard')
def dashboard():
    """Dashboard view"""
    stats = {
        'uploads': DataEntry.query.count(),
        'shared': SharedEntry.query.count(),
    }
    recent = [
        "Uploaded grades.csv 10 minutes ago",
        "Shared 'Resume v1' with alice@example.com",
    ]
    return render_template('dashboard.html', stats=stats, recent=recent)

@application.route('/profile', methods=['GET', 'POST'])
def profile():
    """Profile view"""
    user = User.query.first()
    if user is None:
        return redirect(url_for('signup'))
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)

# ---------------------------------
# Job Application API Routes
# ---------------------------------

@application.route('/api/jobs', methods=['POST'])
def create_job():
    """API: Add a new job application"""
    data = request.get_json()
    try:
        job = JobApplication(
            user_id=data['user_id'],
            job_title=data['job_title'],
            company_name=data['company_name'],
            application_date=datetime.strptime(data['application_date'], "%Y-%m-%d"),
            status=data['status'],
            notes=data.get('notes', '')
        )
        db.session.add(job)
        db.session.commit()
        return jsonify({'message': 'Job added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@application.route('/api/jobs/<int:user_id>', methods=['GET'])
def get_jobs(user_id):
    """API: Get all job applications for a user"""
    jobs = JobApplication.query.filter_by(user_id=user_id).all()
    result = []
    for job in jobs:
        result.append({
            'id': job.id,
            'job_title': job.job_title,
            'company_name': job.company_name,
            'application_date': job.application_date.strftime("%Y-%m-%d"),
            'status': job.status,
            'notes': job.notes
        })
    return jsonify(result)

# ---------------------------------
# CLI & App Launch
# ---------------------------------

if __name__ == '__main__':
    with application.app_context():
        db.create_all()
    application.run(host='0.0.0.0', port=5000, debug=True)
