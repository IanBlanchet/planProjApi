from app.config import Config
from app.config import session, Base, engine
import psycopg2
from flask import Flask
from flask_cors import CORS
#from flask_jwt_extended import JWTManager

from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView





#l'application FLASK
app = Flask(__name__)

app.config.from_object(Config)
CORS(app)
#jwt = JWTManager(app)
admin = Admin(app, name='planProjet', template_mode='bootstrap4')
#utilisation au besoin pour editer la BD manuellement;
#admin.add_view(ModelView(Contrat, session))
#admin.add_view(ModelView(Projet, session))
#admin.add_view(ModelView(Reglement, session))
#admin.add_view(ModelView(Subvention, session))
#admin.add_view(ModelView(Ass_reglement_projet, session))
#admin.add_view(ModelView(User, session))
from app.models import Depense
admin.add_view(ModelView(Depense, session))

from app.API import bp as API_bp
app.register_blueprint(API_bp)