#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""
import os
from datetime import datetime
from urllib.parse import urljoin
import secrets
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from flask import (
    Flask, render_template, request,
    redirect, url_for, flash,
    session, jsonify
)
from model import db, User, Profile, Document, PasswordResetToken
from flask_mail import Mail, Message
from flask_migrate import Migrate  # ✅ Added

# ---------------------------------
# App Initialization
# ---------------------------------
application = Flask(__name__)
DB_PATH = os.path.join(application.root_path, "pathfinder.db")
application.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', 'change_this_to_a_secure_random_key'),
    'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', f'sqlite:///{DB_PATH}'),
    'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    'UPLOAD_FOLDER': os.path.join(application.root_path, 'uploads')
})

# Mail configuration
application.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=587,
    MAIL_USERNAME='pathfinder.donotreply@gmail.com',
    MAIL_PASSWORD='lwzm kdun lziv ywfv',
    MAIL_DEFAULT_SENDER="PathFinder <pathfinder.donotreply@gmail.com>",
    MAIL_USE_TLS=True,
    MAIL_USE_SSL=False
)
mail = Mail(application)

os.makedirs(application.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(application)
migrate = Migrate(application, db)  # ✅ Added

# ---------------------------------
# User Registration
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
# Forgot Password
# ---------------------------------
def _send_reset_email(user, token_row):
    link   = urljoin(request.url_root, url_for('reset_get', token=token_row.token))
    expiry = token_row.expires_at.strftime("%H:%M UTC")

    html_body = render_template('email/reset_password.html', user=user, link=link, expiry=expiry)
    text_body = render_template('email/reset_password.txt', user=user, link=link, expiry=expiry)

    msg = Message(subject="Reset your PathFinder password", recipients=[user.email], html=html_body, body=text_body)
    mail.send(msg)

@application.route('/reset-link-sent')
def reset_link_sent():
    return render_template('reset_link_sent.html')

@application.route('/forgot-password', methods=['GET'])
def forgot_password_get():
    return render_template('forgot_password.html')

@application.route('/forgot-password', methods=['POST'])
def forgot_password_post():
    email = request.form['email'].strip()
    user  = User.query.filter_by(email=email).first()
    if user:
        token_row = PasswordResetToken.generate(user.id, ttl_minutes=30)
        db.session.add(token_row)
        db.session.commit()
        _send_reset_email(user, token_row)
    return redirect(url_for('reset_link_sent'))

@application.route('/reset/<token>', methods=['GET'])
def reset_get(token):
    tok = PasswordResetToken.query.filter_by(token=token).first()
    if not tok or not tok.is_valid():
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('login'))
    return render_template('reset_password.html', token=token)

@application.route('/reset/<token>', methods=['POST'])
def reset_post(token):
    tok = PasswordResetToken.query.filter_by(token=token, used=False).first()
    if not tok or not tok.is_valid():
        flash("Reset link invalid or expired.", "danger")
        return redirect(url_for('login'))

    pw  = request.form['password']
    cfm = request.form['confirm']
    if pw != cfm or len(pw) < 6:
        flash("Passwords must match and be at least 6 characters.", "danger")
        return redirect(url_for('reset_get', token=token))

    user = User.query.get(tok.user_id)
    user.password = generate_password_hash(pw)
    tok.used = True
    db.session.commit()

    flash("Password updated! Please log in.", "success")
    return redirect(url_for('login'))

# ---------------------------------
# Index and Dashboard
# ---------------------------------
@application.route('/')
def index():
    return render_template('index.html')

@application.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    uploads = Document.query.filter_by(user_id=user_id).count()
    shared  = Document.query.filter_by(user_id=user_id, is_shared=True).count()
    return render_template(
        'dashboard.html',
        stats={'uploads': uploads, 'shared': shared, 'applications': 0, 'fit_score': 0},
        recent=[], job_apps=[]
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
        prof = Profile.query.filter_by(user_id=user_id).first() or Profile(user_id=user_id)
        prof.full_name = request.form.get('full_name')
        prof.age = request.form.get('age', type=int)
        bd = request.form.get('birth_date')
        if bd:
            prof.birth_date = datetime.strptime(bd, '%Y-%m-%d').date()
        prof.education = request.form.get('education')
        prof.school = request.form.get('school')
        gd = request.form.get('graduation_date')
        if gd:
            prof.graduation_date = datetime.strptime(gd, '%Y-%m-%d').date()
        prof.expected_company = request.form.get('expected_company')
        prof.career_goal = request.form.get('career_goal')
        prof.self_description = request.form.get('self_description')
        prof.internship_experience = request.form.get('internship_experience')
        prof.is_shared = 'is_shared' in request.form
        db.session.add(prof)

        file = request.files.get('data_file')
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
            file.save(save_path)
            doc = Document(
                user_id=user_id,
                file_name=filename,
                file_path=save_path,
                file_type='resume',
                is_shared=False
            )
            db.session.add(doc)

        db.session.commit()
        flash('Profile and document saved successfully!', 'success')
        return redirect(url_for('dashboard'))
    return render_template('upload.html')

# ---------------------------------
# Visualize, Share, Jobs
# ---------------------------------
@application.route('/visualize')
def visualize():
    return render_template('visualize.html')

@application.route('/share', methods=['GET', 'POST'])
def share():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    entries = Document.query.filter_by(user_id=user_id).all()
    all_users = User.query.filter(User.id != user_id).all()
    if request.method == 'POST':
        flash("Sharing settings updated.", "success")
        return redirect(url_for('share'))
    return render_template('share.html', entries=entries, all_users=all_users)

@application.route('/jobs')
def jobs():
    return render_template('jobs.html')

@application.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    documents = Document.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=user, profile=profile, documents=documents)

# ---------------------------------
# App Entry Point
# ---------------------------------
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)
