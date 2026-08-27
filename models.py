# models.py

from extensions import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)          # plain text (temporary)
    password_hash = db.Column(db.String(128), nullable=True)      # for future hashing
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='active')
    email_verified = db.Column(db.Boolean, default=False)
    verification_code = db.Column(db.String(100), nullable=True)
    verification_expires_at = db.Column(db.DateTime, nullable=True)   # <-- added
    full_name = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship
    requests = db.relationship('Request', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Request(db.Model):
    __tablename__ = 'request'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_type = db.Column(db.String(50), nullable=False)   # 'geo', 'transcriptomics', ...
    disease = db.Column(db.String(200), nullable=True)
    geo_dataset = db.Column(db.String(100), nullable=True)
    gene_list = db.Column(db.Text, nullable=True)
    params = db.Column(db.JSON, nullable=True, default={})
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    result_file = db.Column(db.String(200), nullable=True)   # filename in uploads/
    is_active = db.Column(db.Boolean, default=True)           # admin can toggle

    @property
    def display_query(self):
        if self.module_type == 'geo':
            return self.disease
        elif self.module_type == 'transcriptomics':
            return self.geo_dataset
        elif self.module_type in ('enrichment', 'targets'):
            if self.gene_list:
                return self.gene_list[:50] + ('...' if len(self.gene_list) > 50 else '')
            return ''
        elif self.module_type == 'drug':
            return self.disease
        return 'N/A'

    def __repr__(self):
        return f'<Request {self.id} ({self.module_type})>'
class WorkshopRegistration(db.Model):
    __tablename__ = 'workshop_registration'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    date_preference = db.Column(db.String(50), nullable=True)  # 'today', 'tomorrow', etc.
    registered_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<WorkshopRegistration {self.name} ({self.email})>'