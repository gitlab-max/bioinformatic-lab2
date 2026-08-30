# routes/main.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Request,News,Notification,Workshop,WorkshopRegistration
from utils.email import send_request_email, send_confirmation_email
from utils.email import send_workshop_confirmation   # or email_sender

main = Blueprint("main", __name__)

@main.route("/")
def index():
    # Fetch published news articles from database (most recent first)
    news_articles = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(6).all()
    return render_template("index.html", news_articles=news_articles)

# ------------------ GEO ------------------
@main.route("/geo", methods=["GET", "POST"])
@login_required
def geo():
    if request.method == "POST":
        disease = request.form.get("disease", "").strip()
        if not disease:
            flash("Disease name is required.", "error")
            return redirect(url_for("main.geo"))
        new_req = Request(
            user_id=current_user.id,
            module_type="geo",
            disease=disease,
            params={"email": current_user.email}
        )
        db.session.add(new_req)
        db.session.commit()
        send_request_email("GEO Prioritization", disease, current_user.email, new_req.id)
        send_confirmation_email("GEO Prioritization", disease, current_user.email, new_req.id)
        flash("Your GEO analysis request has been submitted.", "success")
        return redirect(url_for("main.geo"))  # stay on the same page

    
    # GET: show all (active for users, all for admin)
    if current_user.role == 'admin':
        requests = Request.query.filter_by(module_type='geo').order_by(Request.created_at.desc()).all()
    else:
        requests = Request.query.filter_by(module_type='geo', is_active=True).order_by(Request.created_at.desc()).all()
    return render_template("geo.html", requests=requests, is_admin=(current_user.role == 'admin'))

# ------------------ Transcriptomics ------------------
@main.route("/transcriptomics", methods=["GET", "POST"])
@login_required
def transcriptomics():
    if request.method == "POST":
        geo_dataset = request.form.get("geo_dataset", "").strip()
        if not geo_dataset:
            flash("GEO dataset ID is required.", "error")
            return redirect(url_for("main.transcriptomics"))
        new_req = Request(
            user_id=current_user.id,
            module_type="transcriptomics",
            geo_dataset=geo_dataset,
            params={"email": current_user.email}
        )
        db.session.add(new_req)
        db.session.commit()
        send_request_email("Transcriptomics", geo_dataset, current_user.email, new_req.id)
        send_confirmation_email("Transcriptomics", geo_dataset, current_user.email, new_req.id)
        flash("Your transcriptomics request has been submitted.", "success")
        return redirect(url_for("main.transcriptomics"))

    # GET: show all (active for users, all for admin)
    if current_user.role == 'admin':
           requests = Request.query.filter_by(module_type='trancriptomics').order_by(Request.created_at.desc()).all()
    else:
           requests = Request.query.filter_by(module_type='transcriptomics', is_active=True).order_by(Request.created_at.desc()).all()
    return render_template("transcriptomics.html", requests=requests, is_admin=(current_user.role == 'admin'))

# ------------------ Enrichment ------------------
@main.route("/enrichment", methods=["GET", "POST"])
@login_required
def enrichment():
    if request.method == "POST":
        gene_list = request.form.get("gene_list", "").strip()
        if not gene_list:
            flash("Gene list is required.", "error")
            return redirect(url_for("main.enrichment"))
        new_req = Request(
            user_id=current_user.id,
            module_type="enrichment",
            gene_list=gene_list,
            params={"email": current_user.email}
        )
        db.session.add(new_req)
        db.session.commit()
        send_request_email("Functional Enrichment", gene_list[:50], current_user.email, new_req.id)
        send_confirmation_email("Functional Enrichment", gene_list[:50], current_user.email, new_req.id)
        flash("Your enrichment request has been submitted.", "success")
        return redirect(url_for("main.enrichment"))

     # GET: show all (active for users, all for admin)
    if current_user.role == 'admin':
            requests = Request.query.filter_by(module_type='enrichment').order_by(Request.created_at.desc()).all()
    else:
            requests = Request.query.filter_by(module_type='enrichment', is_active=True).order_by(Request.created_at.desc()).all()
    return render_template("enrichment.html", requests=requests, is_admin=(current_user.role == 'admin'))

# ------------------ Targets ------------------
@main.route("/targets", methods=["GET", "POST"])
@login_required
def targets():
    if request.method == "POST":
        gene_list = request.form.get("gene_list", "").strip()
        if not gene_list:
            flash("Gene list is required.", "error")
            return redirect(url_for("main.targets"))
        new_req = Request(
            user_id=current_user.id,
            module_type="targets",
            gene_list=gene_list,
            params={"email": current_user.email}
        )
        db.session.add(new_req)
        db.session.commit()
        send_request_email("Target Identification", gene_list[:50], current_user.email, new_req.id)
        send_confirmation_email("Target Identification", gene_list[:50], current_user.email, new_req.id)
        flash("Your target identification request has been submitted.", "success")
        return redirect(url_for("main.targets"))

     # GET: show all (active for users, all for admin)
    if current_user.role == 'admin':
            requests = Request.query.filter_by(module_type='targets').order_by(Request.created_at.desc()).all()
    else:
            requests = Request.query.filter_by(module_type='targets', is_active=True).order_by(Request.created_at.desc()).all()
    return render_template("targets.html", requests=requests, is_admin=(current_user.role == 'admin'))

# ------------------ Drug Discovery ------------------
@main.route("/drug", methods=["GET", "POST"])
@login_required
def drug():
    if request.method == "POST":
        target = request.form.get("target", "").strip()
        if not target:
            flash("Target name is required.", "error")
            return redirect(url_for("main.drug"))
        new_req = Request(
            user_id=current_user.id,
            module_type="drug",
            disease=target,  # store target in disease field
            params={"email": current_user.email}
        )
        db.session.add(new_req)
        db.session.commit()
        send_request_email("Drug Discovery", target, current_user.email, new_req.id)
        send_confirmation_email("Drug Discovery", target, current_user.email, new_req.id)
        flash("Your drug discovery request has been submitted.", "success")
        return redirect(url_for("main.drug"))

     # GET: show all (active for users, all for admin)
    if current_user.role == 'admin':
            requests = Request.query.filter_by(module_type='drug').order_by(Request.created_at.desc()).all()
    else:
            requests = Request.query.filter_by(module_type='drug', is_active=True).order_by(Request.created_at.desc()).all()
    return render_template("drug.html", requests=requests, is_admin=(current_user.role == 'admin'))

# ------------------ User Dashboard ------------------
@main.route("/dashboard")
@login_required
def user_dashboard():
    user_requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    return render_template("user/dashboard.html", requests=user_requests)


@main.route('/register-workshop', methods=['GET', 'POST'])
def register_workshop():
    workshops = Workshop.query.filter_by(is_active=True).order_by(Workshop.date.asc()).all()

    if request.method == 'POST':
        workshop_id = request.form.get('workshop_id', '').strip()
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        affiliation = request.form.get('affiliation', '').strip()

        if not workshop_id:
            flash('Please select a workshop.', 'danger')
            return render_template('register_workshop.html', workshops=workshops)

        if not name or not email:
            flash('Name and email are required.', 'danger')
            return render_template('register_workshop.html', workshops=workshops)

        workshop = Workshop.query.get_or_404(int(workshop_id))

        # Check capacity
        if workshop.registered_count >= workshop.capacity:
            flash('This workshop is full. Please select another.', 'danger')
            return render_template('register_workshop.html', workshops=workshops)

        # Save registration
        reg = WorkshopRegistration(
            workshop_id=workshop.id,
            name=name,
            email=email,
            affiliation=affiliation,
            status='Pending'
        )
        db.session.add(reg)
        workshop.registered_count += 1
        db.session.commit()

        flash(f'Registration successful for "{workshop.title}"!', 'success')
        return redirect(url_for('main.index'))

    return render_template('register_workshop.html', workshops=workshops)

@main.route('/news/<int:news_id>')
def news_detail(news_id):
    news = News.query.get_or_404(news_id)
    return render_template('news_detail.html', news=news)

@main.route("/notifications")
@login_required
def notifications():
    user_notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    return render_template("user/notifications.html", notifications=user_notifications)
