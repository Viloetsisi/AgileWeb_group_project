#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash,
    session, jsonify
)
from model import db, User, Profile, Document

# ---------------------------------
# Application Initialization
# ---------------------------------
application = Flask(__name__)
application.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'change_this_to_a_secure_random_key'),
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///pathfinder.db'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'UPLOAD_FOLDER': os.path.join(application.root_path, 'uploads')
})
os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)

# bind SQLAlchemy to our Flask app
db.init_app(application)

# ---------------------------------
# Signup
# ---------------------------------
@application.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username'].strip()
        email    = request.form['email'].strip()
        pwd      = request.form['password']
        confirm  = request.form['confirm_password']
        if pwd != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for('signup'))
        if User.query.filter((User.username==username)|(User.email==email)).first():
            flash("Username or email already taken.", "danger")
            return redirect(url_for('signup'))
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(pwd)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('login'))
    return render_template('signup.html')

# ---------------------------------
# Login / Logout
# ---------------------------------
@application.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        ident = request.form['username'].strip()
        pwd   = request.form['password']
        user  = User.query.filter(
            (User.username==ident)|(User.email==ident)
        ).first()
        if user and check_password_hash(user.password, pwd):
            session.clear()
            session['user_id'] = user.id
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard'))
        flash("Invalid credentials.", "danger")
        return redirect(url_for('login'))
    return render_template('login.html')

@application.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------------------------------
# Introductory / Home
# ---------------------------------
@application.route('/')
def index():
    return render_template('index.html')

# ---------------------------------
# Dashboard
# ---------------------------------
@application.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    # Compute stats
    uploads      = Document.query.filter_by(user_id=user_id).count()
    shared       = Document.query.filter_by(user_id=user_id, is_shared=True).count()
    # No JobApplication model here; omit that card or repurpose:
    return render_template(
        'dashboard.html',
        stats={
            'uploads': uploads,
            'shared': shared,
            'applications': 0,
            'fit_score': 0
        },
        recent=[],
        job_apps=[]
    )

# ---------------------------------
# Upload (Profile + Document)
# ---------------------------------
@application.route('/upload', methods=['GET', 'POST'])
def upload():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    if request.method == 'POST':
        # Load or create Profile
        prof = Profile.query.filter_by(user_id=user_id).first() or Profile(user_id=user_id)
        prof.full_name           = request.form.get('full_name')
        prof.age                 = request.form.get('age', type=int)
        bd = request.form.get('birth_date')
        if bd:
            prof.birth_date = datetime.strptime(bd, '%Y-%m-%d').date()
        prof.education           = request.form.get('education')
        prof.school              = request.form.get('school')
        gd = request.form.get('graduation_date')
        if gd:
            prof.graduation_date = datetime.strptime(gd, '%Y-%m-%d').date()
        prof.expected_company    = request.form.get('expected_company')
        prof.career_goal         = request.form.get('career_goal')
        prof.self_description    = request.form.get('self_description')
        prof.internship_experience = request.form.get('internship_experience')
        prof.is_shared           = 'is_shared' in request.form
        db.session.add(prof)

        # Handle file upload
        file = request.files.get('data_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            doc = Document(
                user_id   = user_id,
                file_name = filename,
                file_path = save_path,
                file_type = 'resume',
                is_shared = False
            )
            db.session.add(doc)

        db.session.commit()
        flash('Profile and document saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

# ---------------------------------
# Visualise Data
# ---------------------------------
@application.route('/visualize')
def visualize():
    return render_template('visualize.html')

# ---------------------------------
# Share Data
# ---------------------------------
@application.route('/share', methods=['GET', 'POST'])
def share():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    entries   = Document.query.filter_by(user_id=user_id).all()
    all_users = User.query.filter(User.id!=user_id).all()
    if request.method == 'POST':
        # TODO: implement share logic
        flash("Sharing settings updated.", "success")
        return redirect(url_for('share'))
    return render_template('share.html', entries=entries, all_users=all_users)

# ---------------------------------
# Job Market Page (static)
# ---------------------------------
@application.route('/jobs')
def jobs():
    return render_template('jobs.html')

# ---------------------------------
# User Profile View
# ---------------------------------
@application.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    user     = User.query.get(user_id)
    profile  = Profile.query.filter_by(user_id=user_id).first()
    documents= Document.query.filter_by(user_id=user_id).all()

    return render_template(
      'profile.html',
      user=user,
      profile=profile,
      documents=documents
    )
# ---------------------------------
# CLI: Create tables & run
# ---------------------------------
if __name__ == '__main__':
    with application.app_context():
        db.create_all()
    application.run(host='0.0.0.0', port=5000, debug=True)
