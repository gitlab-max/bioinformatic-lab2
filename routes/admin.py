# routes/admin.py

import os
from datetime import datetime
from flask import Blueprint, current_app, request, redirect, url_for, flash, render_template, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from extensions import db
from models import Request
from models import WorkshopRegistration

admin = Blueprint('admin', __name__)


@admin.route('/dashboard')
@login_required
def dashboard():
    if not current_user.role or current_user.role.lower() != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    all_requests = Request.query.order_by(Request.created_at.desc()).all()
    return render_template('admin/dashboard.html', requests=all_requests)


@admin.route('/request/<int:req_id>')
@login_required
def request_detail(req_id):
    if not current_user.role or current_user.role.lower() != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    req = Request.query.get_or_404(req_id)
    return render_template('admin/request_detail.html', req=req)


@admin.route('/upload_result/<int:req_id>', methods=['POST'])
@login_required
def upload_result(req_id):
    if not current_user.role or current_user.role.lower() != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.geo'))

    req = Request.query.get_or_404(req_id)
    if 'result_file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))

    file = request.files['result_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))

    if file:
        # ensure uploads folder exists
        upload_dir = os.path.join(current_app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)

        filename = secure_filename(f"{req_id}_{file.filename}")
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)

        req.result_file = filename
        req.status = 'Completed'
        req.completed_at = datetime.utcnow()
        db.session.commit()
        flash('Result file uploaded successfully.', 'success')

    return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))


@admin.route('/toggle_active/<int:req_id>', methods=['POST'])
@login_required
def toggle_active(req_id):
    if not current_user.role or current_user.role.lower() != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.geo'))

    req = Request.query.get_or_404(req_id)
    req.is_active = not req.is_active
    db.session.commit()
    flash(f"Request #{req.id} {'activated' if req.is_active else 'deactivated'}.", 'info')
    return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))


@admin.route('/download_result/<filename>')
@login_required
def download_result(filename):
    # Allow any logged-in user to download (or restrict to admin)
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(upload_dir, filename, as_attachment=True)


@admin.route('/workshop-registrations')
@login_required
def workshop_registrations():
    if not current_user.role or current_user.role.lower() != 'admin':
        flash('Access denied.', 'danger')
        return redirect(url_for('main.index'))
    registrations = WorkshopRegistration.query.order_by(WorkshopRegistration.registered_at.desc()).all()
    return render_template('admin/workshop_registrations.html', registrations=registrations)