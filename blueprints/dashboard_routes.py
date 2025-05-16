from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from model import db, Document, SharedWith, JobHistory, Profile, VizShare


dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    return render_template('index.html')

@dashboard_bp.route('/dashboard')
def dashboard():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    uploads = Document.query.filter_by(user_id=user_id).count()
    shared = (
        SharedWith.query
            .join(Document, SharedWith.document_id == Document.id)
            .filter(Document.user_id == user_id)
            .with_entities(SharedWith.document_id)
            .distinct()
            .count()
    )
    applications = JobHistory.query.filter_by(user_id=user_id).count()

    profile = Profile.query.filter_by(user_id=user_id).first() or Profile(user_id=user_id)
    docs = Document.query.filter_by(user_id=user_id).all()

    fields = [
        profile.full_name, profile.education,
        profile.school, profile.graduation_date,
        profile.career_goal
    ]
    completeness = sum(bool(f) for f in fields) / len(fields)
    doc_score = min(len(docs) / 3, 1.0)

    required_skills = {'Data Analysis', 'Python', 'Communication'}
    user_skills = set(profile.career_goal.split(',')) if profile.career_goal else set()
    skill_score = len(required_skills & user_skills) / len(required_skills)

    fit_score = round((0.5 * completeness + 0.3 * skill_score + 0.2 * doc_score) * 100)

    return render_template(
        'dashboard.html',
        stats={
            'uploads': uploads,
            'shared': shared,
            'applications': applications,
            'fit_score': fit_score
        },
        recent=[], job_apps=[]
    )


@dashboard_bp.route('/visualize')
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
            return redirect(url_for('dashboard.dashboard'))

    # 4. Load the owner's profile and documents
    profile = Profile.query.filter_by(user_id=owner_id).first()
    if not profile:
        flash("No profile found. Please complete your profile before visualizing.", "warning")
        return redirect(url_for('profile.edit_profile'))

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

    # 7. # map working_experience (years) to a 0–100% score (cap at 5 yrs → 100%)
    years = profile.working_experience or 0
    experience_frac  = min(years / 5.0, 1.0)
    experience_score = round(experience_frac * 100)

    # 8. Aggregate into a single fit_score percentage
    fit_score = round((0.5 * completeness + 0.3 * experience_frac + 0.2 * doc_score) * 100)

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
    completeness=round(completeness*100),
    experience_score= experience_score,
    doc_score=round(doc_score*100),
    fit_score=fit_score,
    star_labels=star_labels,
    star_values=star_values
    )
