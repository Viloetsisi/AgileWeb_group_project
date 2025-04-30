# model.py

from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize the shared SQLAlchemy object
db = SQLAlchemy()

# ------------------------------
# User account model
# ------------------------------
class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer,    primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    registered_at = db.Column(db.DateTime,   default=datetime.utcnow)

    def set_password(self, pwd: str):
        self.password_hash = generate_password_hash(pwd)
    
    def check_password(self, pwd: str):
        return check_password_hash(self.password_hash, pwd)
    
    # One-to-one relationship to Profile, one-to-many to Document
    profile   = db.relationship("Profile",  back_populates="user", uselist=False)
    documents = db.relationship("Document", back_populates="user", lazy=True)

    def __repr__(self):
        return f"<User {self.username!r}>"

# ------------------------------
# Detailed profile information entered by the user
# ------------------------------
class Profile(db.Model):
    __tablename__ = 'profiles'

    id                    = db.Column(db.Integer, primary_key=True)
    user_id               = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    full_name             = db.Column(db.String(120))    # Full name
    age                   = db.Column(db.Integer)        # Age
    birth_date            = db.Column(db.Date)           # Date of birth
    education             = db.Column(db.String(100))    # Highest education level
    graduation_date       = db.Column(db.Date)           # Graduation date
    school                = db.Column(db.String(200))    # University or school
    expected_company      = db.Column(db.String(200))    # Desired company
    career_goal           = db.Column(db.String(200))    # Target career path
    self_description      = db.Column(db.Text)          # Personal bio or summary
    internship_experience = db.Column(db.Text)          # Internship details

    is_shared             = db.Column(db.Boolean, default=False)  # Whether profile is shareable

    user = db.relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<Profile user_id={self.user_id}>"

# ------------------------------
# User-uploaded documents (certificates, awards, etc.)
# ------------------------------
class Document(db.Model):
    __tablename__ = 'documents'

    id          = db.Column(db.Integer,    primary_key=True)
    user_id     = db.Column(db.Integer,    db.ForeignKey('users.id'), nullable=False)

    file_name   = db.Column(db.String(200))  # Display name of the file
    file_path   = db.Column(db.String(300))  # Actual storage path on disk
    file_type   = db.Column(db.String(50))   # Type (e.g., certificate, award)
    upload_time = db.Column(db.DateTime,     default=datetime.utcnow)

    is_shared   = db.Column(db.Boolean,      default=False)  # Whether document is shareable

    user = db.relationship("User", back_populates="documents")

    def __repr__(self):
        return f"<Document {self.file_name!r} of user {self.user_id}>"
