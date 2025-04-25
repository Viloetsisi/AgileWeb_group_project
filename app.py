#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""

import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

# ---------------------------------
# Application Initialization
# ---------------------------------

application = Flask(__name__)
application.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'change_this_to_a_secure_random_key')
application.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///pathfinder.db')
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
application.config['UPLOAD_FOLDER'] = 'uploads'

os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)

db = SQLAlchemy(application)

# ---------------------------------
# Database Models
# ---------------------------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    profile = db.relationship("Profile", backref="user", uselist=False)
    documents = db.relationship("Document", backref="user", lazy=True)

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, unique=True)

    full_name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    birth_date = db.Column(db.Date)
    education = db.Column(db.String(100))
    graduation_date = db.Column(db.Date)
    school = db.Column(db.String(200))
    expected_company = db.Column(db.String(200))
    career_goal = db.Column(db.String(200))
    self_description = db.Column(db.Text)
    internship_experience = db.Column(db.Text)
    is_shared = db.Column(db.Boolean, default=False)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    file_name = db.Column(db.String(200))
    file_path = db.Column(db.String(300))
    file_type = db.Column(db.String(50))
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    is_shared = db.Column(db.Boolean, default=False)

# ------------------------------
# Signup Route
# ------------------------------
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))

        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            flash("Username or email already exists.", "danger")
            return redirect(url_for('signup'))

        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('signup.html')

# ------------------------------
# Login Route
# ------------------------------
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        user = User.query.filter((User.username == identifier) | (User.email == identifier)).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Login successful.", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid username/email or password.", "danger")
            return redirect(url_for('login'))

    return render_template('login.html')

# ------------------------------
# Combined Profile and File Upload API
# ------------------------------
@application.route('/api/profile-and-documents', methods=['POST'])
def profile_and_documents():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'User not logged in'}), 401

    profile = Profile.query.filter_by(user_id=user_id).first()
    if not profile:
        profile = Profile(user_id=user_id)

    profile.full_name = request.form.get('full_name')
    profile.age = request.form.get('age', type=int)
    profile.birth_date = request.form.get('birth_date')
    profile.education = request.form.get('education')
    profile.graduation_date = request.form.get('graduation_date')
    profile.school = request.form.get('school')
    profile.expected_company = request.form.get('expected_company')
    profile.career_goal = request.form.get('career_goal')
    profile.self_description = request.form.get('self_description')
    profile.internship_experience = request.form.get('internship_experience')
    profile.is_shared = request.form.get('is_shared') == 'true'

    db.session.add(profile)

    files = request.files.getlist('files')
    file_types = request.form.getlist('file_type')
    shares = request.form.getlist('file_shared')

    for i, file in enumerate(files):
        if file.filename:
            filename = secure_filename(file.filename)
            path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(path)

            document = Document(
                user_id=user_id,
                file_name=filename,
                file_path=path,
                file_type=file_types[i] if i < len(file_types) else 'unknown',
                is_shared=(shares[i] == 'true') if i < len(shares) else False
            )
            db.session.add(document)

    db.session.commit()
    return jsonify({'message': 'Profile and documents saved successfully'}), 201

# ------------------------------
# API for Matching System to Fetch User Data
# ------------------------------
@application.route('/api/profile-data/<int:user_id>', methods=['GET'])
def get_profile_data(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    profile = Profile.query.filter_by(user_id=user_id).first()
    documents = Document.query.filter_by(user_id=user_id).all()

    profile_data = {
        'full_name': profile.full_name if profile else '',
        'age': profile.age if profile else '',
        'education': profile.education if profile else '',
        'expected_company': profile.expected_company if profile else '',
        'career_goal': profile.career_goal if profile else '',
        'self_description': profile.self_description if profile else '',
        'internship_experience': profile.internship_experience if profile else '',
        'is_shared': profile.is_shared if profile else False
    }

    docs = [
        {
            'file_name': d.file_name,
            'file_type': d.file_type,
            'is_shared': d.is_shared
        }
        for d in documents
    ]

    return jsonify({
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'profile': profile_data,
        'documents': docs
    })

# ------------------------------
# User Profile Display Page
# ------------------------------
@application.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    documents = Document.query.filter_by(user_id=user_id).all()

    return render_template('profile.html', user=user, profile=profile, documents=documents)

# ------------------------------
# Home / Dashboard
# ------------------------------
@application.route('/')
def index():
    return redirect(url_for('login'))

@application.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    return f"Welcome, {user.username}! (dashboard content to be implemented)"

# ------------------------------
# Initialize Database
# ------------------------------
if __name__ == '__main__':
    with application.app_context():
        db.create_all()
    application.run(host='0.0.0.0', port=5000, debug=True)
