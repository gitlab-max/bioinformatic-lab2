from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="User")
    status = db.Column(db.String(30), nullable=False, default="Active")
    email_verified = db.Column(db.Boolean, nullable=False, default=False)
    verification_code = db.Column(db.String(20), nullable=True)
    verification_expires_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    requests = db.relationship("Request", back_populates="user", cascade="all, delete-orphan")
    notifications = db.relationship("Notification", back_populates="user", cascade="all, delete-orphan")


class Request(db.Model):
    __tablename__ = "requests"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_type = db.Column(db.String(50), nullable=False)
    disease = db.Column(db.String(200), nullable=True)
    gene_list = db.Column(db.Text, nullable=True)
    geo_dataset = db.Column(db.String(50), nullable=True)
    params = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    result_file = db.Column(db.String(300), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    user = db.relationship("User", back_populates="requests")


class Notification(db.Model):
    __tablename__ = "notifications"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship("User", back_populates="notifications")

class Workshop(db.Model):
    __tablename__ = "workshops"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    duration = db.Column(db.String(100), default="2 hours")
    capacity = db.Column(db.Integer, default=20)
    registered_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    image_url = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    meet_link = db.Column(db.String(500), nullable=True)   # Google Meet URL

    registrations = db.relationship("WorkshopRegistration", back_populates="workshop", cascade="all, delete-orphan")


class WorkshopRegistration(db.Model):
    __tablename__ = "workshop_registrations"
    id = db.Column(db.Integer, primary_key=True)
    workshop_id = db.Column(db.Integer, db.ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    affiliation = db.Column(db.String(200))
    status = db.Column(db.String(50), default="Pending")
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    workshop = db.relationship("Workshop", back_populates="registrations")

# models.py

class News(db.Model):
    __tablename__ = "news"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    summary = db.Column(db.String(500))
    content = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300))
    published_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
