
# routes/admin.py

import os
from datetime import datetime
from functools import wraps

from flask import Blueprint, current_app, request, redirect, url_for, flash, render_template, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from extensions import db
from models import Request, WorkshopRegistration, User, Notification, News, Workshop

admin = Blueprint('admin', __name__, url_prefix='/admin')


# =========================================================
# ADMIN REQUIRED DECORATOR
# =========================================================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Please login first.', 'danger')
            return redirect(url_for('auth.login'))
        if not current_user.role or current_user.role.lower() != 'admin':
            flash('Access denied. Admin privileges required.', 'danger')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated


# =========================================================
# DASHBOARD
# =========================================================

@admin.route('/dashboard')
@admin_required
def dashboard():
    all_requests = Request.query.order_by(Request.created_at.desc()).all()
    user_count = User.query.count()
    request_count = Request.query.count()
    pending_count = Request.query.filter_by(status='Pending').count()
    completed_count = Request.query.filter_by(status='Completed').count()
    workshop_count = Workshop.query.count()

    return render_template('admin/dashboard.html',
                           requests=all_requests,
                           user_count=user_count,
                           request_count=request_count,
                           pending_count=pending_count,
                           completed_count=completed_count,
                           workshop_count=workshop_count)


# =========================================================
# REQUEST DETAIL
# =========================================================

@admin.route('/request/<int:req_id>')
@admin_required
def request_detail(req_id):
    req = Request.query.get_or_404(req_id)
    return render_template('admin/request_detail.html', req=req)


# =========================================================
# UPLOAD RESULT
# =========================================================

@admin.route('/upload_result/<int:req_id>', methods=['POST'])
@admin_required
def upload_result(req_id):
    req = Request.query.get_or_404(req_id)

    if 'result_file' not in request.files:
        flash('No file selected.', 'danger')
        return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))

    file = request.files['result_file']
    if file.filename == '':
        flash('No file selected.', 'danger')
        return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))

    if file:
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


# =========================================================
# TOGGLE ACTIVE
# =========================================================

@admin.route('/toggle_active/<int:req_id>', methods=['POST'])
@admin_required
def toggle_active(req_id):
    req = Request.query.get_or_404(req_id)
    req.is_active = not req.is_active
    db.session.commit()
    flash(f"Request #{req.id} {'activated' if req.is_active else 'deactivated'}.", 'info')
    return redirect(request.referrer or url_for('admin.request_detail', req_id=req.id))


# =========================================================
# DOWNLOAD RESULT
# =========================================================

@admin.route('/download_result/<filename>')
@login_required
def download_result(filename):
    upload_dir = os.path.join(current_app.root_path, 'uploads')
    return send_from_directory(upload_dir, filename, as_attachment=True)


# =========================================================
# WORKSHOP MANAGEMENT (CRUD)
# =========================================================

@admin.route('/workshops')
@admin_required
def workshop_list():
    workshops = Workshop.query.order_by(Workshop.date.desc()).all()
    return render_template('admin/workshop_list.html', workshops=workshops)

@admin.route('/workshops/add', methods=['GET', 'POST'])
@admin_required
def workshop_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        duration = request.form.get('duration', '2 hours').strip()
        capacity = request.form.get('capacity', 20)
        is_active = request.form.get('is_active') == 'on'
        image_url = request.form.get('image_url', '').strip() or None
        meet_link = request.form.get('meet_link', '').strip() or None

        # Validation
        if not title or not description or not date_str:
            flash('Title, description, and date are required.', 'danger')
            return render_template('admin/workshop_add.html')

        try:
            date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/workshop_add.html')

        # CREATE THE WORKSHOP OBJECT HERE
        workshop = Workshop(
            title=title,
            description=description,
            date=date,
            duration=duration,
            capacity=int(capacity) if capacity else 20,
            is_active=is_active,
            image_url=image_url,
            meet_link=meet_link      # <-- set directly in constructor
        )

        db.session.add(workshop)
        db.session.commit()
        flash('Workshop created successfully.', 'success')
        return redirect(url_for('admin.workshop_list'))

    return render_template('admin/workshop_add.html')
@admin.route('/workshops/<int:workshop_id>/edit', methods=['GET', 'POST'])
@admin_required
def workshop_edit(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)

    if request.method == 'POST':
        workshop.title = request.form.get('title', '').strip()
        workshop.description = request.form.get('description', '').strip()
        date_str = request.form.get('date', '').strip()
        workshop.duration = request.form.get('duration', '2 hours').strip()
        workshop.capacity = int(request.form.get('capacity', 20))
        workshop.is_active = request.form.get('is_active') == 'on'
        workshop.image_url = request.form.get('image_url', '').strip() or None
        workshop.meet_link = request.form.get('meet_link', '').strip() or None

        if not workshop.title or not workshop.description or not date_str:
            flash('Title, description, and date are required.', 'danger')
            return render_template('admin/workshop_edit.html', workshop=workshop)

        try:
            workshop.date = datetime.strptime(date_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Invalid date format.', 'danger')
            return render_template('admin/workshop_edit.html', workshop=workshop)

        db.session.commit()
        flash('Workshop updated successfully.', 'success')
        return redirect(url_for('admin.workshop_list'))

    # For GET, format the date
    date_str = workshop.date.strftime('%Y-%m-%dT%H:%M') if workshop.date else ''
    return render_template('admin/workshop_edit.html', workshop=workshop, date_str=date_str)

@admin.route('/workshops/<int:workshop_id>/delete', methods=['POST'])
@admin_required
def workshop_delete(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    db.session.delete(workshop)
    db.session.commit()
    flash('Workshop deleted successfully.', 'success')
    return redirect(url_for('admin.workshop_list'))


@admin.route('/workshops/<int:workshop_id>/registrations')
@admin_required
def workshop_registrations(workshop_id):
    workshop = Workshop.query.get_or_404(workshop_id)
    registrations = workshop.registrations
    return render_template('admin/workshop_registrations.html', workshop=workshop, registrations=registrations)


@admin.route('/workshop-registrations/update/<int:reg_id>', methods=['POST'])
@admin_required
def update_registration_status(reg_id):
    reg = WorkshopRegistration.query.get_or_404(reg_id)
    new_status = request.form.get('status', 'Pending').strip()
    valid_statuses = ['Pending', 'Confirmed', 'Attended', 'Cancelled', 'Waitlist']
    if new_status in valid_statuses:
        reg.status = new_status
        db.session.commit()
        flash(f"Registration for {reg.name} updated to {new_status}.", 'success')
    else:
        flash('Invalid status.', 'danger')
    return redirect(request.referrer or url_for('admin.workshop_list'))


@admin.route('/workshop-registrations/delete/<int:reg_id>', methods=['POST'])
@admin_required
def delete_registration(reg_id):
    reg = WorkshopRegistration.query.get_or_404(reg_id)
    workshop_id = reg.workshop_id
    db.session.delete(reg)
    db.session.commit()
    flash('Registration deleted.', 'success')
    return redirect(url_for('admin.workshop_registrations', workshop_id=workshop_id))

# =========================================================
# USER MANAGEMENT
# =========================================================

@admin.route('/users')
@admin_required
def users():
    """View all registered users."""
    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)


@admin.route('/users/<int:user_id>/role', methods=['POST'])
@admin_required
def update_user_role(user_id):
    """Update a user's role (User/Admin)."""
    user = User.query.get_or_404(user_id)
    
    # Prevent changing the main admin account's role
    if user.username == 'admin':
        flash('Cannot change the main admin account role.', 'danger')
        return redirect(url_for('admin.users'))
    
    new_role = request.form.get('role', 'User').strip()
    if new_role in ['User', 'Admin']:
        user.role = new_role
        db.session.commit()
        flash(f"User '{user.username}' role updated to {new_role}.", 'success')
    else:
        flash('Invalid role.', 'danger')
    
    return redirect(url_for('admin.users'))


@admin.route('/users/<int:user_id>/status', methods=['POST'])
@admin_required
def update_user_status(user_id):
    """Update a user's account status (Active/Inactive/Pending/Suspended)."""
    user = User.query.get_or_404(user_id)
    
    # Prevent disabling the main admin account
    if user.username == 'admin':
        flash('Cannot change the main admin account status.', 'danger')
        return redirect(url_for('admin.users'))
    
    new_status = request.form.get('status', 'Active').strip()
    valid_statuses = ['Active', 'Inactive', 'Pending', 'Suspended']
    
    if new_status in valid_statuses:
        user.status = new_status
        db.session.commit()
        flash(f"User '{user.username}' status updated to {new_status}.", 'success')
    else:
        flash('Invalid status.', 'danger')
    
    return redirect(url_for('admin.users'))


@admin.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    """Delete a user from the system."""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the main admin account
    if user.username == 'admin':
        flash('Cannot delete the main admin account.', 'danger')
        return redirect(url_for('admin.users'))
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    flash(f"User '{user.username}' has been deleted.", 'success')
    return redirect(url_for('admin.users'))


@admin.route('/users/<int:user_id>/notify', methods=['GET', 'POST'])
@admin_required
def notify_user(user_id):
    """Send a notification to a specific user."""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        message = request.form.get('message', '').strip()
        
        if not title or not message:
            flash('Title and message are required.', 'danger')
            return render_template('admin/notify_user.html', user=user)
        
        # Create notification record
        notification = Notification(
            user_id=user.id,
            title=title,
            message=message,
            read=False
        )
        db.session.add(notification)
        db.session.commit()
        
        flash(f"Notification sent to {user.username}.", 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/notify_user.html', user=user)
# In admin.py – add these routes

# routes/admin.py – add these functions

@admin.route('/news')
@admin_required
def news_list():
    all_news = News.query.order_by(News.published_at.desc()).all()
    return render_template('admin/news_list.html', news=all_news)

@admin.route('/news/add', methods=['GET', 'POST'])
@admin_required
def news_add():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        summary = request.form.get('summary', '').strip()
        image_url = request.form.get('image_url', '').strip()

        if not title or not content:
            flash('Title and content are required.', 'danger')
            return render_template('admin/news_add.html')

        news = News(
            title=title,
            content=content,
            summary=summary or None,
            image_url=image_url or None,
            is_published=request.form.get('is_published') == 'on'
        )
        db.session.add(news)
        db.session.commit()
        flash('News article created successfully.', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_add.html')

@admin.route('/news/<int:news_id>/edit', methods=['GET', 'POST'])
@admin_required
def news_edit(news_id):
    news = News.query.get_or_404(news_id)

    if request.method == 'POST':
        news.title = request.form.get('title', '').strip()
        news.content = request.form.get('content', '').strip()
        news.summary = request.form.get('summary', '').strip() or None
        news.image_url = request.form.get('image_url', '').strip() or None
        news.is_published = request.form.get('is_published') == 'on'
        db.session.commit()
        flash('News article updated successfully.', 'success')
        return redirect(url_for('admin.news_list'))

    return render_template('admin/news_edit.html', news=news)

@admin.route('/news/<int:news_id>/delete', methods=['POST'])
@admin_required
def news_delete(news_id):
    news = News.query.get_or_404(news_id)
    db.session.delete(news)
    db.session.commit()
    flash('News article deleted.', 'success')
    return redirect(url_for('admin.news_list'))
