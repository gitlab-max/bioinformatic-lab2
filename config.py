import os

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "BioLabSecretKey_2026")
    SQLALCHEMY_DATABASE_URI = "sqlite:///biolab.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "BIBIMEDICIN@gmail.com")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "ulcn vigq hitm zcnh")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", "BIBIMEDICIN@gmail.com")

    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL", "BIBIMEDICIN@gmail.com")