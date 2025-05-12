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
from model import db, User, Profile, Document, PasswordResetToken, SharedWith, VizShare, JobHistory
from flask_mail import Mail, Message
from flask_migrate import Migrate  # ✅ Added
from datetime import datetime
import requests
from forms import JobHistoryForm

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
        flash("Invalid user or password.", "danger")
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

# Edit profile only
@application.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    prof = Profile.query.filter_by(user_id=user_id).first() or Profile(user_id=user_id)

    if request.method == 'POST':
        prof.full_name = request.form.get('full_name')
        prof.age       = request.form.get('age', type=int)
        bd = request.form.get('birth_date')
        if bd:
            prof.birth_date = datetime.strptime(bd, '%Y-%m-%d').date()

        prof.education = request.form.get('education')
        prof.gpa       = request.form.get('gpa')  # ← added

        prof.school          = request.form.get('school')
        gd = request.form.get('graduation_date')
        if gd:
            prof.graduation_date = datetime.strptime(gd, '%Y-%m-%d').date()

        prof.expected_company   = request.form.get('expected_company')
        prof.career_goal        = request.form.get('career_goal')
        prof.self_description   = request.form.get('self_description')
        prof.internship_experience = request.form.get('internship_experience')
        prof.is_shared            = 'is_shared' in request.form

        # ← new fields below
        prof.coding_c      = 'coding_c'      in request.form
        prof.coding_cpp    = 'coding_cpp'    in request.form
        prof.coding_java   = 'coding_java'   in request.form
        prof.coding_sql    = 'coding_sql'    in request.form
        prof.coding_python = 'coding_python' in request.form

        prof.communication_skill = request.form.get('communication_skill', type=int) or 0
        prof.working_experience  = request.form.get('working_experience',  type=int) or 0

        db.session.add(prof)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile_view'))

    return render_template('edit_profile.html', profile=prof)

# Upload document only
@application.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    if request.method == 'POST':
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
            flash('Document uploaded successfully.', 'success')
        else:
            flash('No file selected.', 'danger')

        return redirect(url_for('profile_view'))

    return render_template('upload_document.html')


# Delete document
@application.route('/delete_document/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != user_id:
        flash("You are not authorized to delete this document.", "danger")
        return redirect(url_for('profile_view'))

    try:
        os.remove(doc.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")

    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted successfully.", "success")
    return redirect(url_for('profile_view'))



# ---------------------------------
# Visualize, Share, Jobs
# ---------------------------------
@application.route('/visualize')
def visualize():
    # 1. Ensure user is logged in
    current_user_id = session.get('user_id')
    if not current_user_id:
        return redirect(url_for('login'))

    # 2. Determine whose dashboard to show (default = self)
    owner_id = request.args.get('user', type=int, default=current_user_id)

    # 3. If viewing someone else's, enforce VizShare permission
    if owner_id != current_user_id:
        allowed = VizShare.query.filter_by(
            owner_id=owner_id,
            shared_to_user_id=current_user_id
        ).first()
        if not allowed:
            flash("You’re not authorized to view that dashboard.", "danger")
            return redirect(url_for('dashboard'))

    # 4. Load the owner's profile and documents
    profile = Profile.query.filter_by(user_id=owner_id).first()
    if not profile:
        flash("No profile found. Please complete your profile before visualizing.", "warning")
        return redirect(url_for('edit_profile'))

    docs = Document.query.filter_by(user_id=owner_id).all()

    # 5. Compute Profile completeness (0.0–1.0)
    fields = [
        profile.full_name,
        profile.birth_date,
        profile.education,
        profile.school,
        profile.graduation_date,
        profile.career_goal,
        profile.self_description,
        profile.internship_experience
    ]
    completeness = sum(bool(f) for f in fields) / len(fields)

    # 6. Compute Document strength score (cap at 1.0)
    doc_score = min(len(docs) / 3, 1.0)

    # 7. Compute Skill-match (example logic)
    required_skills = {'Data Analysis', 'Python', 'Communication'}
    user_skills = set(profile.career_goal.split(',')) if profile.career_goal else set()
    skill_score = len(required_skills & user_skills) / len(required_skills)

    # 8. Aggregate into a single fit_score percentage
    fit_score = round((0.5 * completeness + 0.3 * skill_score + 0.2 * doc_score) * 100)

    # 9.compute values for radar (“star”) chart ---
    edu_map = {'Diploma': 1, 'Bachelor': 2, 'Master': 3, 'PhD': 4}
    education_val = edu_map.get(profile.education, 0)

    gpa_map = {'P': 2, 'CR': 3, 'D': 4, 'HD': 5}
    gpa_val = gpa_map.get(profile.gpa, 0)

    # --- safely count how many coding skills are True (None → 0) ---
    coding_val = sum([
        profile.coding_c      or 0,
        profile.coding_cpp    or 0,
        profile.coding_java   or 0,
        profile.coding_sql    or 0,
        profile.coding_python or 0
    ])

    # make sure missing ratings default to 0
    comm_val = profile.communication_skill or 0
    exp_val  = profile.working_experience   or 0

    star_labels = ['Education', 'GPA', 'Coding', 'Communication', 'Experience']
    star_values = [education_val, gpa_val, coding_val, comm_val, exp_val]

    # 10. pass into template ---
    return render_template(
        'visualize.html',
        completeness=int(completeness * 100),
        skill_score=int(skill_score * 100),
        doc_score=int(doc_score * 100),
        fit_score=fit_score,
        star_labels=star_labels,
        star_values=star_values
    )



@application.route('/share', methods=['GET', 'POST'])
def share():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # 1. Fetch the current user's documents and all other users
    entries   = Document.query.filter_by(user_id=user_id).all()
    all_users = User.query.filter(User.id != user_id).all()

    # 2. Build a map: document_id -> set(shared_to_user_ids)
    shared_map = {}
    for row in SharedWith.query.filter(
            SharedWith.document_id.in_([d.id for d in entries])
        ).all():
        shared_map.setdefault(row.document_id, set()).add(row.shared_to_user_id)

    # 3. Build a set of user_ids who can see this user's dashboard
    viz_shared = {
        row.shared_to_user_id
        for row in VizShare.query.filter_by(owner_id=user_id).all()
    }

    if request.method == 'POST':
        # 4a. Handle document sharing updates
        for doc in entries:
            # Update the public flag
            doc.is_shared = f'is_shared_{doc.id}' in request.form

            # Get selected user IDs for this document
            chosen = {
                int(uid)
                for uid in request.form.getlist(f'share_with_{doc.id}[]')
            }
            existing = shared_map.get(doc.id, set())

            # Remove de-selected shares
            for uid in existing - chosen:
                SharedWith.query.filter_by(
                    document_id=doc.id,
                    shared_to_user_id=uid
                ).delete()

            # Add newly selected shares
            for uid in chosen - existing:
                db.session.add(SharedWith(
                    document_id=doc.id,
                    shared_to_user_id=uid
                ))

        # 4b. Handle dashboard (visualize) sharing updates
        chosen_viz = {
            int(uid)
            for uid in request.form.getlist('share_viz[]')
        }

        # Remove de-selected dashboard shares
        for uid in viz_shared - chosen_viz:
            VizShare.query.filter_by(
                owner_id=user_id,
                shared_to_user_id=uid
            ).delete()

        # Add newly selected dashboard shares
        for uid in chosen_viz - viz_shared:
            db.session.add(VizShare(
                owner_id=user_id,
                shared_to_user_id=uid
            ))

        # 5. Commit all changes
        db.session.commit()
        flash("Sharing settings updated.", "success")
        return redirect(url_for('share'))

    # 6. Render the Manage Sharing template
    return render_template(
        'share.html',
        entries=entries,
        all_users=all_users,
        shared_map=shared_map,
        viz_shared=viz_shared
    )

@application.route('/shared')
def shared():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    # 1. Documents shared to me
    shared_docs = (
        db.session.query(Document, User.username.label('owner'))
        .join(User, Document.user_id == User.id)
        .join(SharedWith, SharedWith.document_id == Document.id)
        .filter(SharedWith.shared_to_user_id == user_id)
        .all()
    )

    # 2. Dashboards shared to me
    viz_owners = (
        db.session.query(User)
        .join(VizShare, VizShare.owner_id == User.id)
        .filter(VizShare.shared_to_user_id == user_id)
        .all()
    )

    return render_template(
        'shared.html',
        shared_docs=shared_docs,
        viz_owners=viz_owners
    )

@application.route('/jobs', methods=['GET', 'POST'])
def jobs():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    form = JobHistoryForm()

    if form.validate_on_submit():
        job = JobHistory(
            user_id=user_id,
            company_name=form.company_name.data,
            position=form.position.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            salary=form.salary.data,
            description=form.description.data
        )
        db.session.add(job)
        db.session.commit()
        flash("Job history uploaded successfully!", "success")
        return redirect(url_for('jobs'))

    history = JobHistory.query.filter_by(user_id=user_id).all()
    return render_template('jobs.html', form=form, history=history)


@application.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    user = User.query.get(user_id)
    profile = Profile.query.filter_by(user_id=user_id).first()
    documents = Document.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', user=user, profile=profile, documents=documents)

@application.route('/api/job_history/<int:user_id>')
def get_job_history(user_id):
    from model import JobHistory  # make sure it's imported if not already
    history = JobHistory.query.filter_by(user_id=user_id).all()
    return jsonify([
        {
            'company_name': h.company_name,
            'position': h.position,
            'start_date': h.start_date.strftime('%Y-%m-%d') if h.start_date else '',
            'end_date': h.end_date.strftime('%Y-%m-%d') if h.end_date else '',
            'description': h.description or ''
        }
        for h in history
    ])
    
# ---------------------------------
# Job History Upload
# ---------------------------------    
@application.route('/upload_job_history', methods=['POST'])
def upload_job_history():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))

    company_name = request.form.get('company_name')
    position = request.form.get('position')
    description = request.form.get('description')

    # Parse dates safely
    start_date_raw = request.form.get('start_date')
    end_date_raw = request.form.get('end_date')
    start_date = datetime.strptime(start_date_raw, '%Y-%m-%d').date() if start_date_raw else None
    end_date = datetime.strptime(end_date_raw, '%Y-%m-%d').date() if end_date_raw else None
    salary = request.form.get('salary')

    job = JobHistory(
        user_id=user_id,
        company_name=company_name,
        position=position,
        start_date=start_date,
        end_date=end_date,
        description=description,
        salary=salary
        
    )

    db.session.add(job)
    db.session.commit()

    flash("Job history uploaded successfully!", "success")
    return redirect(url_for('jobs'))

# ---------------------------------
# Career Market
# ---------------------------------

@application.route('/career_market', methods=['GET'])
def career_market():
    job_title = request.args.get('job_title', '')  # default to empty if no input
    location = request.args.get('location', '')  # default to empty if no input

    # Check if both job title and location are provided
    if job_title and location:
        query = f"{job_title} jobs in {location}"  # Construct query like "developer jobs in chicago"
    elif job_title:
        query = f"{job_title} jobs"  # If only job title is provided, search for jobs with that title
    elif location:
        query = f"jobs in {location}"  # If only location is provided, search for jobs in that location
    else:
        query = "developer jobs"  # Default search if neither job title nor location is provided

    # Construct the query parameters
    querystring = {
        "query": query,
        "page": "1",
        "num_pages": "1",
        "date_posted": "all",
        "country": "us",  # Specify the country as 'us'
        "language": "en"  # English language preference
    }

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        'x-rapidapi-key': "4797b66196msh6bc26e180733e9ap1277d3jsn7f80a962b427",
        'x-rapidapi-host': "jsearch.p.rapidapi.com"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()
        jobs = response.json().get("data", [])
    except Exception as e:
        jobs = []
        print(f"Error fetching job data: {e}")

    return render_template("career_market.html", jobs=jobs, job_title=job_title, location=location)

# ---------------------------------
# App Entry Point
# ---------------------------------
if __name__ == '__main__':
    application.run(host='0.0.0.0', port=5000, debug=True)

