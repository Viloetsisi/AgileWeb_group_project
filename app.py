#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""

from werkzeug.utils import secure_filename
import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask application
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
# Database Models (examples)
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
    data_id = db.Column(
        db.Integer, db.ForeignKey('data_entry.id'), nullable=False
    )
    shared_with_user_id = db.Column(
        db.Integer, db.ForeignKey('user.id'), nullable=False
    )


# ---------------------------------
# Application Routes
# ---------------------------------

@application.route('/')
def index():
    """Introductory view: homepage with signup/login links"""
    return render_template('index.html')


@application.route('/signup', methods=['GET', 'POST'])
def signup():
    """Signup view (placeholder)"""
    if request.method == 'POST':
        # TODO: process signup form
        return redirect(url_for('index'))
    return render_template('signup.html')


@application.route('/login', methods=['GET', 'POST'])
def login():
    """Login view (placeholder)"""
    if request.method == 'POST':
        # TODO: process login form
        return redirect(url_for('index'))
    return render_template('login.html')


@application.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('data_file')
        desc = request.form.get('description', '')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(save_path)

            # persist to DB:
            entry = DataEntry(user_id=1, filename=save_path)  # replace user_id
            db.session.add(entry)
            db.session.commit()

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('dashboard'))

        flash('Please select a file to upload', 'error')

    return render_template('upload.html')


@application.route('/visualize')
def visualize():
    """Visualise Data view: show analysis results"""
    # TODO: query DataEntry and run analysis
    return render_template('visualize.html')


@application.route('/share', methods=['GET', 'POST'])
def share():
    """Share Data view: allow user to share entries"""
    if request.method == 'POST':
        # TODO: handle share logic
        return redirect(url_for('share'))
    return render_template('share.html')

@application.route('/dashboard')
def dashboard():
    """Dashboard view: user’s control center post‑login."""
    # In a real app, you’d fetch counts/stats from the database:
    stats = {
        'uploads': DataEntry.query.count(),
        'shared': SharedEntry.query.count(),
    }
    # Recent activity stub:
    recent = [
        "Uploaded grades.csv 10 minutes ago",
        "Shared 'Resume v1' with alice@example.com",
    ]
    return render_template('dashboard.html', stats=stats, recent=recent)


@application.route('/profile', methods=['GET', 'POST'])
def profile():
    """Profile view: manage user settings."""
    # In a real app, you’d load the current user from session/db
    user = User.query.first()  # placeholder
    if user is None:
        return redirect(url_for('signup'))
    if request.method == 'POST':
        # example update logic:
        user.username = request.form['username']
        user.email = request.form['email']
        # TODO: handle password change
        db.session.commit()
        return redirect(url_for('profile'))
    return render_template('profile.html', user=user)


# ---------------------------------
# CLI & App Launch
# ---------------------------------
if __name__ == '__main__':
    # Create database tables if they don't exist
    with application.app_context():
        db.create_all()
    application.run(host='0.0.0.0', port=5000, debug=True)
