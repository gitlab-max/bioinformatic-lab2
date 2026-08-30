# utils/email.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config
from flask_mail import Message
from extensions import mail
from flask import current_app, url_for

# Get email credentials from the Config class
EMAIL_USER = Config.MAIL_USERNAME
EMAIL_PASSWORD = Config.MAIL_PASSWORD
ADMIN_EMAIL = Config.ADMIN_EMAIL


def send_request_email(module_name, query, user_email, request_id):
    """Notify admin about a new analysis request."""
    subject = f"New {module_name} Request"
    body = f"""
A new request has been submitted.

Module: {module_name}
Query: {query}
User: {user_email}
Request ID: {request_id}

Please process this request and upload the results.
"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = ADMIN_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("Admin notification sent.")
    except Exception as e:
        print(f"Failed to send admin email: {e}")


def send_confirmation_email(module_name, query, user_email, request_id):
    """Send confirmation to the user who submitted a request."""
    subject = f"{module_name} Request Received"
    body = f"""
Dear Researcher,

Thank you for using the Integrated Bioinformatics & AI Drug Discovery Workflow.

We have received your {module_name} request.

Request: {query}
Request ID: {request_id}

The results will be sent to this email address once completed.

Best regards,
Bioinformatics Lab Team
"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = user_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Confirmation sent to {user_email}")
    except Exception as e:
        print(f"Failed to send confirmation email: {e}")


def send_workshop_confirmation(name, email):
    """Send a confirmation email to a workshop registrant."""
    subject = "Workshop Registration Confirmed – Bioinformatics Lab"
    body = f"""
Dear {name},

Thank you for registering for our free daily bioinformatics workshop!

📅 When: Every weekday at 10:00 AM (UTC)
🔗 Link: You will receive the meeting link shortly before the session.

We look forward to seeing you there!

Best regards,
Bioinformatics Lab Team
"""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_USER
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"Workshop confirmation sent to {email}")
        return True
    except Exception as e:
        print(f"Failed to send workshop email: {e}")
        return False
def send_workshop_confirmation_email(registration, workshop):
    """Send a confirmation email to a workshop registrant."""
    subject = f"Workshop Confirmation: {workshop.title}"

    body = f"""
Dear {registration.name},

Thank you for registering for the workshop "{workshop.title}".

📅 Date: {workshop.date.strftime('%A, %B %d, %Y at %H:%M %Z')}
⏰ Duration: {workshop.duration}

🔗 Join the workshop here:
{workshop.meet_link or 'The link will be sent separately.'}

If you have any questions, please reply to this email.

Best regards,
Bioinformatic Lab Team
"""

    msg = Message(subject=subject, recipients=[registration.email])
    msg.body = body
    mail.send(msg)
