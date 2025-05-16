from flask import Blueprint, render_template, redirect, url_for, flash, session
from model import db, Profile, Document
from forms import ProfileForm, DocumentUploadForm
import os
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    prof = Profile.query.filter_by(user_id=user_id).first() or Profile(user_id=user_id)
    form = ProfileForm(obj=prof)
    if form.validate_on_submit():
        form.populate_obj(prof)
        db.session.add(prof)
        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('profile.profile_view'))
    return render_template('edit_profile.html', form=form, profile=prof)

@profile_bp.route('/profile')
def profile_view():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    profile = Profile.query.filter_by(user_id=user_id).first()
    documents = Document.query.filter_by(user_id=user_id).all()
    return render_template('profile.html', profile=profile, documents=documents)

@profile_bp.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    form = DocumentUploadForm()
    if form.validate_on_submit():
        file = form.data_file.data
        if file and file.filename:
            filename = secure_filename(file.filename)
            save_path = os.path.join(os.getcwd(), 'uploads', filename)
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
        return redirect(url_for('profile.profile_view'))
    return render_template('upload_document.html', form=form)

@profile_bp.route('/delete_document/<int:doc_id>', methods=['POST'])
def delete_document(doc_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != user_id:
        flash("You are not authorized to delete this document.", "danger")
        return redirect(url_for('profile.profile_view'))
    try:
        os.remove(doc.file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
    db.session.delete(doc)
    db.session.commit()
    flash("Document deleted successfully.", "success")
    return redirect(url_for('profile.profile_view'))
