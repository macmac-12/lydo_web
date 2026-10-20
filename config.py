import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bula-youth-secret-2026'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///lydo.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False