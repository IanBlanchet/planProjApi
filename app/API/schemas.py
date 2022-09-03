from app.models import Contrat, Projet, User,\
                        Jalon, Events, Pti, Reglement, Subvention, \
                        Fonds, Ass_reglement_projet, Ass_fonds_projet, Ass_subvention_projet
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
        fields = ('id', 'no', 'princ', 'desc', 'estimation', 'statut', 'charge_contrat',  'projet_id')
        
    @post_load
    def make_contrat(self, data, **kwargs):
        return Contrat(**data)



class ProjetSchema(ma.Schema):
     class Meta:
        model = Projet
        include_fk = True
        unknown = EXCLUDE
        load_instance = True
        sqla_session = session
        fields = ('id', 'no_projet', 'desc', 'cat', 'immo', 'reglA', 'reglB', 'statut', 'affectation', 'prev_courante', 'nature', 'charge', 'anterieur', 'courante')
         

     @post_load
     def make_projet(self, data, **kwargs):
        #for index in range(len(data)):
            #anterieur, courante = data[index].calcDepense()   
            #data[index].anterieur = anterieur
            #data[index].courante = courante
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
    duree = fields.Integer()


    @post_load
    def make_jalon(self, data, **kwargs):
        return Jalon(**data)

class EventSchema(Schema):
    class meta:
        model = Events
        include_fk = True
        unknown = EXCLUDE
        load_instance = True
        sqla_session = session
        
    id = fields.Integer()
    title = fields.String()
    date = fields.String()
    
    @post_load
    def make_events(self, data, **kwargs):
        return Events(**data)

class PtiSchema(Schema):
    class meta:
        model = Pti
        include_fk = True
        unknown = EXCLUDE
        load_instance = True
        sqla_session = session
        
    id = fields.Integer()
    annee = fields.Integer()
    projet_id = fields.Integer()
    cycleCour = fields.Integer()
    cycle2 = fields.Integer()
    cycle3 = fields.Integer()
    cycle4 = fields.Integer()
    cycle5 = fields.Integer()   

    
    @post_load
    def make_pti(self, data, **kwargs):
        return Pti(**data)
        

class ReglementSchema(ma.Schema):
    class Meta:
        model = Reglement
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'numero', 'montant', 'ratioSecteur')
        
    @post_load
    def make_reglement(self, data, **kwargs):
        return Reglement(**data)

class SubventionSchema(ma.Schema):
    class Meta:
        model = Subvention
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'nomProg', 'no_id', 'montantAcc', 'montantFin')
        
    @post_load
    def make_subvention(self, data, **kwargs):
        return Subvention(**data)

class FondsSchema(ma.Schema):
    class Meta:
        model = Fonds
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'nom', 'montantDisp')
        
    @post_load
    def make_fonds(self, data, **kwargs):
        return Fonds(**data)

class AssReglementSchema(ma.Schema):
    class Meta:
        model = Ass_reglement_projet
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('montant', 'reglement_id', 'projet_id')
        
    @post_load
    def make_ass_reglement_projet(self, data, **kwargs):
        return Ass_reglement_projet(**data)

class AssFondsSchema(ma.Schema):
    class Meta:
        model = Ass_fonds_projet
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('montant', 'fonds_id', 'projet_id')
        
    @post_load
    def make_ass_fonds_projet(self, data, **kwargs):
        return Ass_fonds_projet(**data)

class AssSubventionSchema(ma.Schema):
    class Meta:
        model = Ass_subvention_projet
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('montant', 'subvention_id', 'projet_id')
        
    @post_load
    def make_ass_subvention_projet(self, data, **kwargs):
        return Ass_subvention_projet(**data)