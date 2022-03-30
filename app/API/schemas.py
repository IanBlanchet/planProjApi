from app.models import Contrat, Projet, User, Jalon
from flask_marshmallow import Marshmallow
from marshmallow import post_load, INCLUDE, EXCLUDE, fields, Schema
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from app import app
from app.config import session


ma = Marshmallow(app)


class ContratSchema(ma.Schema):
    class Meta:
        model = Contrat
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'no', 'desc', 'projet_id')
        
    @post_load
    def make_contrat(self, data, **kwargs):
        return Contrat(**data)



class ProjetSchema(ma.Schema):
     class Meta:
        model = Projet
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'no_projet', 'desc', 'cat', 'immo', 'reglA', 'reglB', 'statut', 'affectation', 'prev_courante', 'nature', 'charge')
     
     @post_load
     def make_projet(self, data, **kwargs):
         return Projet(**data)
    
    


class UserSchema(Schema):
    class meta:
        model = User
        include_fk = True
        unknown = EXCLUDE
        load_instance = True      
        sqla_session = session        

    id = fields.Integer()
    username = fields.String()
    email = fields.String()
    statut = fields.String()
    service = fields.String()

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


#utilsation du schema direct de marshmallow pour éviter erreur
class JalonSchema(Schema):
    class meta:
        model = Jalon
        include_fk = True
        unknown = EXCLUDE
        load_instance = True
        sqla_session = session
        
    id = fields.Integer()
    date = fields.String()
    jalon = fields.String()
    commentaire = fields.String()
    etat = fields.String()
    charge_jalon = fields.Integer()
    projet_id =  fields.Integer()
    contrat_id =  fields.Integer()


    @post_load
    def make_jalon(self, data, **kwargs):
        return Jalon(**data)


        

