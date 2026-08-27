# routes/auth.py

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session
)

from flask_login import (
    login_user,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from extensions import db, mail
from models import User

from flask_mail import Message

from datetime import datetime, timedelta

import random


############################################################
# BLUEPRINT
############################################################

auth = Blueprint(
    "auth",
    __name__
)


############################################################
# HELPER
############################################################

def generate_verification_code():

    return str(
        random.randint(100000, 999999)
    )


############################################################
# SEND VERIFICATION EMAIL
############################################################
def send_verification_email(user):
    code = generate_verification_code()
    user.verification_code = code
    user.verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.session.commit()

    # Send the email
    message = Message(
        subject="Bioinformatic Lab - Email Verification",
        recipients=[user.email]
    )
    message.body = f"""Hello {user.username},

Thank you for registering with Bioinformatic Lab.

Your email verification code is:

{code}

This code is valid for 10 minutes.

If you did not create this account, please ignore this email.

Bioinformatic Lab
"""
    mail.send(message)


############################################################
# LOGIN
############################################################

@auth.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if current_user.is_authenticated:

        if current_user.role and current_user.role.lower() == "admin":

            return redirect(
                url_for("admin.dashboard")
            )

        return redirect(
            url_for("main.user_dashboard")
        )


    # --------------------------------------------------------
    # Login POST
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )


        # ----------------------------------------------------
        # Find user
        # ----------------------------------------------------

        user = User.query.filter_by(
            username=username
        ).first()


        # ----------------------------------------------------
        # Check username/password
        # ----------------------------------------------------

        if not user or not check_password_hash(
            user.password,
            password
        ):

            flash(
                "Invalid username or password.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ----------------------------------------------------
        # Check account status
        # ----------------------------------------------------

        if not user.status or user.status.lower() != "active":

            flash(
                "Your account is not active.",
                "error"
            )

            return redirect(
                url_for("auth.login")
            )


        # ----------------------------------------------------
        # Check email verification
        # ----------------------------------------------------

        if not user.email_verified:

            # Store user ID temporarily
            session["verification_user_id"] = user.id

            flash(
                "Please verify your email before logging in.",
                "error"
            )

            return redirect(
                url_for("auth.verify_email")
            )


        # ----------------------------------------------------
        # LOGIN USER
        # ----------------------------------------------------

        login_user(user)


        # ----------------------------------------------------
        # ADMIN
        # ----------------------------------------------------

        if user.role and user.role.lower() == "admin":

            return redirect(
                url_for("admin.dashboard")
            )


        # ----------------------------------------------------
        # NORMAL USER
        # ----------------------------------------------------

        return redirect(
            url_for("main.user_dashboard")
        )


    return render_template(
        "auth/login.html"
    )


############################################################
# REGISTER
############################################################

@auth.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    # --------------------------------------------------------
    # Already logged in
    # --------------------------------------------------------

    if current_user.is_authenticated:

        if current_user.role  and current_user.role.lower() == "admin":

            return redirect(
                url_for("admin.dashboard")
            )

        return redirect(
            url_for("main.user_dashboard")
        )


    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )


        # ----------------------------------------------------
        # Validate username
        # ----------------------------------------------------

        if not username:

            flash(
                "Username is required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Validate email
        # ----------------------------------------------------

        if not email:

            flash(
                "Email is required.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Validate password
        # ----------------------------------------------------

        if len(password) < 6:

            flash(
                "Password must be at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Confirm password
        # ----------------------------------------------------

        if password != confirm_password:

            flash(
                "Passwords do not match.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Check username
        # ----------------------------------------------------

        existing_username = User.query.filter_by(
            username=username
        ).first()

        if existing_username:

            flash(
                "Username already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Check email
        # ----------------------------------------------------

        existing_email = User.query.filter_by(
            email=email
        ).first()

        if existing_email:

            flash(
                "Email already exists.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Create user
        # ----------------------------------------------------

        user = User(

            username=username,

            email=email,

            password=generate_password_hash(
                password
            ),

            role="User",

            status="active",

            email_verified=False

        )


        db.session.add(user)

        db.session.commit()


        # ----------------------------------------------------
        # Send verification code
        # ----------------------------------------------------

        try:

            send_verification_email(user)

        except Exception as e:

            db.session.delete(user)

            db.session.commit()

            print(
                "EMAIL ERROR:",
                e
            )

            flash(
                "Could not send verification email. Please try again.",
                "error"
            )

            return redirect(
                url_for("auth.register")
            )


        # ----------------------------------------------------
        # Store user temporarily
        # ----------------------------------------------------

        session["verification_user_id"] = user.id


        flash(
            "Registration successful. A verification code has been sent to your email.",
            "success"
        )


        return redirect(
            url_for("auth.verify_email")
        )


    return render_template(
        "auth/register.html"
    )


############################################################
# VERIFY EMAIL
############################################################

@auth.route(
    "/verify-email",
    methods=["GET", "POST"]
)
def verify_email():

    user_id = session.get(
        "verification_user_id"
    )


    # --------------------------------------------------------
    # No user waiting for verification
    # --------------------------------------------------------

    if not user_id:

        flash(
            "No account is waiting for email verification.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    user = User.query.get(
        user_id
    )


    if not user:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "User account not found.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    # --------------------------------------------------------
    # Already verified
    # --------------------------------------------------------

    if user.email_verified:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "Your email is already verified. Please login.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )


    # --------------------------------------------------------
    # POST
    # --------------------------------------------------------

    if request.method == "POST":

        code = request.form.get(
            "verification_code",
            ""
        ).strip()


        # ----------------------------------------------------
        # Check code
        # ----------------------------------------------------

        if not user.verification_code:

            flash(
                "No verification code exists. Please request a new code.",
                "error"
            )

            return redirect(
                url_for("auth.verify_email")
            )


        # ----------------------------------------------------
        # Check expiration
        # ----------------------------------------------------

        if (
            not user.verification_expires_at
            or
            datetime.utcnow()
            > user.verification_expires_at
        ):

            flash(
                "Verification code has expired. Please request a new code.",
                "error"
            )

            return redirect(
                url_for("auth.verify_email")
            )


        # ----------------------------------------------------
        # Compare code
        # ----------------------------------------------------

        if code != user.verification_code:

            flash(
                "Invalid verification code.",
                "error"
            )

            return redirect(
                url_for("auth.verify_email")
            )


        # ----------------------------------------------------
        # Verification successful
        # ----------------------------------------------------

        user.email_verified = True

        user.verification_code = None

        user.verification_expires_at = None

        db.session.commit()


        # Remove temporary session
        session.pop(
            "verification_user_id",
            None
        )


        flash(
            "Email verified successfully. You can now login.",
            "success"
        )


        return redirect(
            url_for("auth.login")
        )


    return render_template(
        "auth/verify_email.html"
    )


############################################################
# RESEND VERIFICATION CODE
############################################################

@auth.route(
    "/resend-code",
    methods=["GET"]
)
def resend_code():

    user_id = session.get(
        "verification_user_id"
    )


    if not user_id:

        flash(
            "No account found for verification.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    user = User.query.get(
        user_id
    )


    if not user:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "User account not found.",
            "error"
        )

        return redirect(
            url_for("auth.register")
        )


    if user.email_verified:

        session.pop(
            "verification_user_id",
            None
        )

        flash(
            "Your email is already verified.",
            "success"
        )

        return redirect(
            url_for("auth.login")
        )


    # --------------------------------------------------------
    # Send new code
    # --------------------------------------------------------

    try:

        send_verification_email(user)

    except Exception as e:

        print(
            "EMAIL ERROR:",
            e
        )

        flash(
            "Could not send verification email.",
            "error"
        )

        return redirect(
            url_for("auth.verify_email")
        )


    flash(
        "A new verification code has been sent to your email.",
        "success"
    )


    return redirect(
        url_for("auth.verify_email")
    )


############################################################
# LOGOUT
############################################################

@auth.route(
    "/logout"
)
def logout():

    logout_user()

    session.pop(
        "verification_user_id",
        None
    )

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(
        url_for("main.index")
    )

