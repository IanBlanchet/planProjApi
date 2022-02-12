from app.config import Config
from app.config import session, Base, engine
from app.models import Contrat
import psycopg2
from flask import Flask
from flask_cors import CORS


from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView





#l'application FLASK
app = Flask(__name__)

app.config.from_object(Config)
CORS(app)
admin = Admin(app, name='contratGref', template_mode='bootstrap4')
admin.add_view(ModelView(Contrat, session))



from app.API import bp as API_bp
app.register_blueprint(API_bp)