#!/usr/bin/env python3
"""
app.py: Main Flask application for PathFinder.
"""
import os
from flask import Flask, render_template, request, redirect, url_for
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
    """Upload Data view: handle file or form uploads"""
    if request.method == 'POST':
        # TODO: process uploaded file or data
        return redirect(url_for('visualize'))
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


# ---------------------------------
# CLI & App Launch
# ---------------------------------
if __name__ == '__main__':
    # Create database tables if they don't exist
    with application.app_context():
        db.create_all()
    application.run(host='0.0.0.0', port=5000, debug=True)
