from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from werkzeug.security import generate_password_hash, check_password_hash
from model import db, User, PasswordResetToken
from forms import SignupForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from flask_mail import Message
from urllib.parse import urljoin

auth_bp = Blueprint('auth', __name__)

def _send_reset_email(user, token_row):
    link = urljoin(request.url_root, url_for('auth.reset', token=token_row.token))
    expiry = token_row.expires_at.strftime("%H:%M UTC")
    html_body = render_template('email/reset_password.html', user=user, link=link, expiry=expiry)
    text_body = render_template('email/reset_password.txt', user=user, link=link, expiry=expiry)
    from app import mail
    msg = Message(subject="Reset your PathFinder password", recipients=[user.email], html=html_body, body=text_body)
    mail.send(msg)

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        username = form.username.data.strip()
        email = form.email.data.strip()
        pwd = form.password.data
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already taken.", "danger")
            return redirect(url_for('auth.signup'))
        user = User(
            username=username,
            email=email,
            password=generate_password_hash(pwd)
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('signup.html', form=form)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        ident = form.username.data.strip()
        pwd   = form.password.data
        user  = User.query.filter((User.username==ident)|(User.email==ident)).first()
        if user and check_password_hash(user.password, pwd):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Logged in successfully.", "success")
            return redirect(url_for('dashboard.dashboard'))
        flash("Invalid user or password.", "danger")
        return redirect(url_for('auth.login'))
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data.strip()
        user  = User.query.filter_by(email=email).first()
        if user:
            token_row = PasswordResetToken.generate(user.id, ttl_minutes=30)
            db.session.add(token_row)
            db.session.commit()
            _send_reset_email(user, token_row)
        return redirect(url_for('auth.reset_link_sent'))
    return render_template('forgot_password.html', form=form)

@auth_bp.route('/reset-link-sent')
def reset_link_sent():
    return render_template('reset_link_sent.html')

@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset(token):
    tok = PasswordResetToken.query.filter_by(token=token).first()
    if not tok or not tok.is_valid():
        flash("Invalid or expired reset link.", "danger")
        return redirect(url_for('auth.login'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        pw  = form.password.data
        user = User.query.get(tok.user_id)
        user.password = generate_password_hash(pw)
        tok.used = True
        db.session.commit()
        flash("Password updated! Please log in.", "success")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html', form=form, token=token)
