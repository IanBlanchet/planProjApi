
from builtins import print
from os import access
from flask.wrappers import Request
from sqlalchemy import delete, false, true
from app.API import bp
from app.models import Projet, Contrat, User, Jalon, Events, Pti
from app import app
from app.config import session, engine, Config
from flask_restful import Resource, Api, abort
from datetime import datetime, timedelta
from flask import Response, redirect, request, url_for
from flask_apispec.views import MethodResource
from apispec import APISpec
from flask_apispec.extension import FlaskApiSpec
from apispec.ext.marshmallow import MarshmallowPlugin
from flask_apispec import marshal_with
import secrets
import jwt
#from flask_jwt_extended import create_access_token
from time import time
from app.API.schemas import ContratSchema, UserSchema, ProjetSchema, JalonSchema, EventSchema, PtiSchema
import json
import msal




appGraph = msal.ConfidentialClientApplication(
        client_id=Config.client_id, authority=Config.tenant,
        client_credential=Config.secret)



api = Api(app)

def isAutorize(encodeToken):
    """
    function to validate token comming from route
    """   
    try:
        user = jwt.decode(encodeToken, Config.SECRET_KEY, algorithms='HS256')        
        return True
    except:    
        return False
 

# Serialize the data for the response
contrats_schema = ContratSchema(many=True)
users_schema = UserSchema(many=True)
projets_schema = ProjetSchema(many=True)
projet_schema = ProjetSchema()
jalons_schema = JalonSchema(many=True)
events_schema = EventSchema(many=True)
event_schema = EventSchema()
jalon_schema = JalonSchema()
pti_schema = PtiSchema()
ptis_schema = PtiSchema(many=True)


class AuthApi(MethodResource,Resource):
    '''
    route to log user and return Token
    '''
    def get(self):
        
        return

    def post(self):
        "validate user et return token"
        data = request.get_json(force=True)
        
        user = session.query(User).filter_by(username = data['username']).first()
        msToken = appGraph.acquire_token_by_username_password('blanchia@ville.valleyfield.qc.ca', password=Config.office_pass, scopes=['https://graph.microsoft.com/.default'])
        if user:
            if user.check_password(data['password']):
                expires = timedelta(days=1)
                access_token = jwt.encode({"exp":datetime.now() + expires}, Config.SECRET_KEY)
                #access_token = create_access_token(identity=str(user.id), expires_delta=expires)
                
                return ({
                    'isUser':'true',
                    'isLogged' : 'true',
                    'token':access_token,
                    'msToken': msToken['access_token'],
                    'message':'successfull login'}, 200)
            else:
                return ({
                'isUser':'true',
                'isLogged':'false',
                'token':"",
                'message':'error'})

        
        else:
            return ({
                'isUser':'false',
                'isLogged':'false',
                'token':"",
                'message':'error'})
        

api.add_resource(AuthApi, '/api/v1/autorize')

class ContratApi(MethodResource,Resource):
    @marshal_with(contrats_schema)    
    def get(self):
        "GET all contrat"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            contrat = session.query(Contrat).all()
            return contrats_schema.dump(contrat)
        else:
            return ({'message':'token not valid or expired'}, 400)
        
    
    def post(self):
        "Get all contrats"
        contrat = session.query(Contrat).all()
        return contrats_schema.dump(contrat)
        

api.add_resource(ContratApi, '/api/v1/contrat')



class ProjetApi(MethodResource,Resource):
    @marshal_with(projets_schema)    
    def get(self):
        "GET all projet"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            projet = session.query(Projet).all()
            return projets_schema.dump(projet)
        else:
            return ({'message':'token not valid or expired'}, 400)   
    

api.add_resource(ProjetApi, '/api/v1/projet')

class EditProjetApi(MethodResource,Resource):     
    def get(self, projet_id):
        "GET a projet"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            projet = session.query(Projet).filter_by(id= projet_id).first()            
            return projet_schema.dump(projet)
        else:
            return ({'message':'token not valid or expired'}, 400)

    def put(self, projet_id):
        "edit projet"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            data = request.get_json(force=True)            
            projet = session.query(Projet).filter_by(id= projet_id).first()
            for key in data:                
                setattr(projet, key, data[key])                               
                session.commit()                
            return projet_schema.dump(projet)   
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(EditProjetApi, '/api/v1/projet/<int:projet_id>')

class FinanceApi(MethodResource,Resource):
    def get(self, projet_id):
        "extract source financement"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            projet = session.query(Projet).filter_by(id = projet_id).first() 
            reglements, subventions, fonds = projet.extractFinance()
            
            return ({'reglements':reglements, 'subventions': subventions, 'fonds':fonds}, 200)
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(FinanceApi, '/api/v1/finance/<int:projet_id>')


class DepenseApi(MethodResource,Resource):
    def get(self, projet_id):
        "extract depense"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            projet = session.query(Projet).filter_by(id = projet_id).first() 
            anterieur, courante = projet.calcDepense()

            return ({'anterieur':anterieur, 'courante':courante}, 200)
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(DepenseApi, '/api/v1/depense/<int:projet_id>')


class PtiApi(MethodResource,Resource):
    def get(self, projet_id):
        "extract PTI"        
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            projet = session.query(Projet).filter_by(id = projet_id).first()
            ptiCourant, ptiEnPrep = projet.extractPtiCourant()                      
            return {'ptiCourant':pti_schema.dump(ptiCourant), 'ptiEnPrep':pti_schema.dump(ptiEnPrep), 'prev_courante':projet.prev_courante}
            
        else:
            return ({'message':'token not valid or expired'}, 400)

    def post(self, projet_id):
        "add or edit PTI"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            data = request.get_json(force=True)
            projet = session.query(Projet).filter_by(id = projet_id).first()
            ptiCourant, ptiEnPrep = projet.extractPtiCourant()
            if ptiEnPrep:
                pti = session.query(Pti).filter(Pti.projet_id==projet.id, Pti.annee==ptiEnPrep.annee).first()            
                
                pti.cycleCour= data['cycleCour']
                pti.cycle2 = data['cycle2']
                pti.cycle3 = data['cycle3']
                pti.cycle4 = data['cycle4']
                pti.cycle5 = data['cycle5']
                session.commit()                
            else:                
                newPti = ptis_schema.make_pti(data)
                session.add(newPti)
                session.commit()

            
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(PtiApi, '/api/v1/pti/<int:projet_id>')


class AllPtiApi(MethodResource, Resource):
    def get(self, annee):
        "extract all PTI for given year"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            pti = session.query(Pti).filter_by(annee = annee).all()            
                      
            return ptis_schema.dump(pti)
            
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(AllPtiApi, '/api/v1/pti/all/<int:annee>')


class JalonApi(MethodResource,Resource):
    @marshal_with(jalons_schema)    
    def get(self):
        "GET all jalons"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            jalon = session.query(Jalon).all()
                     
            return jalons_schema.dump(jalon)
        else:
            return ({'message':'token not valid or expired'}, 400)   
    
    def post(self):
        "ADD jalons"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            data = request.get_json(force=True)
            jalon = data['jalon']
            charge_jalon = data['charge_jalon']
            date = data['date']
            if data['projet_id'] == '':
                projet_id = None
                contrat_id = data['contrat_id']
            else:
                projet_id = data['projet_id']
                contrat_id = None
            
            commentaire = data['commentaire']
            newJalon = Jalon(jalon=jalon, charge_jalon=charge_jalon, date=date, projet_id=projet_id, 
            contrat_id=contrat_id, commentaire=commentaire)
            session.add(newJalon)
            session.commit()  
            return jalons_schema.dump(data)
        else:
            return ({'message':'token not valid or expired'}, 400) 

api.add_resource(JalonApi, '/api/v1/jalon')

class EditJalonApi(MethodResource,Resource):      
    def put(self, jalon_id):
        "edit jalons"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            jalon = session.query(Jalon).filter_by(id = jalon_id).first()
            if request.args.get('etat'):
                jalon.etat = "complet"
                session.commit()
                return jalon_schema.dump(jalon)
            data = request.get_json(force=True)
            
            if not jalon:
                return ({'message':'there no jalon with this id'}, 400)
            jalon.date = data.get('date')
            jalon.commentaire = data.get('commentaire')
            jalon.etat = data.get('etat')
            jalon.charge_jalon = data.get('charge_jalon')
            jalon.duree = data.get('duree')
            session.commit()
            return jalon_schema.dump(jalon)
        else:
            return ({'message':'token not valid or expired'}, 400)

    def delete(self, jalon_id) :
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            jalon = session.query(Jalon).filter_by(id = jalon_id).first()
            session.delete(jalon)
            session.commit()
            return {'message':f'jalon {jalon_id} successfull deleted'}
        else:
            return ({'message':'token not valid or expired'}, 400)


api.add_resource(EditJalonApi, '/api/v1/jalon/<int:jalon_id>')


class UserApi(MethodResource,Resource):
    @marshal_with(users_schema)    
    def get(self):
        "GET all user"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            user = session.query(User).all()
            return users_schema.dump(user) 
        else:            
            return ({'message':'token not valid or expired'}, 400)
        

    def post(self):
                  
        return 
        

api.add_resource(UserApi, '/api/v1/user')

class EventApi(MethodResource,Resource):
    @marshal_with(events_schema)    
    def get(self):
        "GET all events"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            events = session.query(Events).all()
            return events_schema.dump(events)
        else:            
            return ({'message':'token not valid or expired'}, 400)
        

    def post(self):
        "POST a new Event"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            data = request.get_json(force=True)   
            newEvents = events_schema.make_events(data)
            session.add(newEvents)
            session.commit()
        return events_schema.dump(data)

api.add_resource(EventApi, '/api/v1/event')

class EditEventApi(MethodResource,Resource):
    def put(self, event_id):
        "Edit the date of Events"
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            event = session.query(Events).filter_by(id=event_id).first()
            if not event:
                return ({'message':'there no event with this id'}, 400)
            event.date = request.args.get('date')
            session.commit()
            return event_schema.dump(event)
        return ({'message':'token not valid or expired'}, 400)

    def delete(self, event_id):
        token = request.headers.get('HTTP_AUTHORIZATION')        
        if isAutorize(token):
            event = session.query(Events).filter_by(id=event_id).first()
            if not event:
                return ({'message':'there no event with this id'}, 400)
            session.delete(event)
            session.commit()
            return event_schema.dump(event)
        return ({'message':'token not valid or expired'}, 400)

api.add_resource(EditEventApi, '/api/v1/event/<int:event_id>')


app.config.update({
    'APISPEC_SPEC': APISpec(
        title='planproj',
        version='v1',
        plugins=[MarshmallowPlugin()],
        openapi_version='2.0'
    ),
    'APISPEC_SWAGGER_URL': '/swagger/',  # URI to access API Doc JSON 
    'APISPEC_SWAGGER_UI_URL': '/swagger-ui/'  # URI to access UI of API Doc
})
docs = FlaskApiSpec(app)

docs.register(ContratApi)
docs.register(UserApi)
docs.register(ProjetApi)
docs.register(JalonApi)
docs.register(EditJalonApi)
docs.register(EventApi)
docs.register(EditEventApi)
docs.register(DepenseApi)
docs.register(PtiApi)
docs.register(AllPtiApi)