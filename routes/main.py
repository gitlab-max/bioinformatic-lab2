# routes/main.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models import Request
from utils.email import send_request_email, send_confirmation_email
from models import WorkshopRegistration   # add to imports
from utils.email import send_workshop_confirmation   # or email_sender

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("index.html")

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

    user_requests = Request.query.filter_by(
        user_id=current_user.id,
        module_type="transcriptomics"
    ).order_by(Request.created_at.desc()).all()
    return render_template("transcriptomics.html", requests=user_requests)

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

    user_requests = Request.query.filter_by(
        user_id=current_user.id,
        module_type="enrichment"
    ).order_by(Request.created_at.desc()).all()
    return render_template("enrichment.html", requests=user_requests)

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

    user_requests = Request.query.filter_by(
        user_id=current_user.id,
        module_type="targets"
    ).order_by(Request.created_at.desc()).all()
    return render_template("targets.html", requests=user_requests)

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

    user_requests = Request.query.filter_by(
        user_id=current_user.id,
        module_type="drug"
    ).order_by(Request.created_at.desc()).all()
    return render_template("drug.html", requests=user_requests)

# ------------------ User Dashboard ------------------
@main.route("/dashboard")
@login_required
def user_dashboard():
    user_requests = Request.query.filter_by(user_id=current_user.id).order_by(Request.created_at.desc()).all()
    return render_template("user/dashboard.html", requests=user_requests)


@main.route('/register-workshop', methods=['GET', 'POST'])
def register_workshop():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        date_pref = request.form.get('date')

        # Save to database
        new_reg = WorkshopRegistration(
            name=name,
            email=email,
            date_preference=date_pref
        )
        db.session.add(new_reg)
        db.session.commit()

        # Send confirmation email
        send_workshop_confirmation(name, email)

        flash(f'Registration successful for {name}! Check your email for confirmation.', 'success')
        return redirect(url_for('main.index'))
    return render_template('register_workshop.html')