from flask import Blueprint, render_template, redirect, url_for, flash, session, jsonify
from model import db, JobHistory
from forms import JobHistoryForm

jobs_bp = Blueprint('jobs', __name__)

@jobs_bp.route('/jobs', methods=['GET', 'POST'])
def jobs():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    form = JobHistoryForm()
    history = JobHistory.query.filter_by(user_id=user_id).all()
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
        return redirect(url_for('jobs.jobs'))
    return render_template('jobs.html', history=history, form=form)

@jobs_bp.route('/api/job_history/<int:user_id>')
def get_job_history(user_id):
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
