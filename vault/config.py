import os


class Config:
    SECRET_KEY=os.environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI=os.environ.get("SQLALCHEMY_DATABASE_URI")
    MAIL_DEFAULT_SENDER=os.environ.get("MAIL_DEFAULT_SENDER")
    MAIL_USERNAME=os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD=os.environ.get("MAIL_PASSWORD")
    MAIL_PORT=587
    MAIL_SERVER='smtp.office365.com'
    MAIL_USE_TLS=True
