import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base



load_dotenv()


class Config(object):
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'tu le devinera pas'
	token = os.environ.get('token')
	DATABASE_URI = os.environ.get('DATABASE_URI') or 'sqlite:///pos.db'
	FLASK_APP = os.environ.get('FLASK_APP')
	SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY')


	client_id = os.environ.get('CLIENT_ID')
	tenant = os.environ.get('TENANT')
	secret = os.environ.get('CLIENT_SECRET')
	office_pass = os.environ.get('OFFICE_PASS')
	

#connection with bd
Base = declarative_base()
engine = create_engine(Config.DATABASE_URI)
Session = sessionmaker(bind=engine)
session= Session()
