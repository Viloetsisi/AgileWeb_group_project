from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from model import db, User, Document, SharedWith, VizShare
from forms import JobHistoryForm
from sqlalchemy.orm import joinedload

share_bp = Blueprint('share', __name__)

@share_bp.route('/share', methods=['GET', 'POST'])
def share():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    entries = Document.query.filter_by(user_id=user_id).all()
    all_users = User.query.filter(User.id != user_id).all()

    shared_map = {}
    for row in SharedWith.query.filter(
        SharedWith.document_id.in_([d.id for d in entries])
    ).all():
        shared_map.setdefault(row.document_id, set()).add(row.shared_to_user_id)

    viz_shared = {
        row.shared_to_user_id
        for row in VizShare.query.filter_by(owner_id=user_id).all()
    }

    if request.method == 'POST':
        # Document sharing
        for doc in entries:
            doc.is_shared = f'is_shared_{doc.id}' in request.form
            chosen = {
                int(uid)
                for uid in request.form.getlist(f'share_with_{doc.id}[]')
            }
            existing = shared_map.get(doc.id, set())

            for uid in existing - chosen:
                SharedWith.query.filter_by(
                    document_id=doc.id,
                    shared_to_user_id=uid
                ).delete()

            for uid in chosen - existing:
                db.session.add(SharedWith(
                    document_id=doc.id,
                    shared_to_user_id=uid
                ))

        # Dashboard sharing
        chosen_viz = {
            int(uid)
            for uid in request.form.getlist('share_viz[]')
        }

        for uid in viz_shared - chosen_viz:
            VizShare.query.filter_by(
                owner_id=user_id,
                shared_to_user_id=uid
            ).delete()

        for uid in chosen_viz - viz_shared:
            db.session.add(VizShare(
                owner_id=user_id,
                shared_to_user_id=uid
            ))

        db.session.commit()
        flash("Sharing settings updated.", "success")
        return redirect(url_for('share.share'))

    return render_template(
        'share.html',
        entries=entries,
        all_users=all_users,
        shared_map=shared_map,
        viz_shared=viz_shared
    )

@share_bp.route('/shared')
def shared():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.login'))

    shared_docs = (
        db.session.query(Document, User.username.label('owner'))
        .join(User, Document.user_id == User.id)
        .join(SharedWith, SharedWith.document_id == Document.id)
        .filter(SharedWith.shared_to_user_id == user_id)
        .all()
    )

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
