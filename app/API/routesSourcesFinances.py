from builtins import print

from flask.wrappers import Request
from sqlalchemy import delete, false, true
from app.models import Projet, Reglement, Subvention, \
                        Fonds, Ass_subvention_projet, Ass_reglement_projet, Ass_fonds_projet
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
import time
from app.API.schemas import ProjetSchema, ReglementSchema, SubventionSchema, FondsSchema, AssReglementSchema
import json


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
projets_schema = ProjetSchema(many=True)
projet_schema = ProjetSchema()
reglements_schema = ReglementSchema(many=True)
subventions_schema = SubventionSchema(many=True)
fonds_schema = FondsSchema(many=True)
ass_reglement_schema = AssReglementSchema(many=True)

class ReglementApi(MethodResource,Resource):
    def get(self):
        "extract reglements"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            reglements = session.query(Reglement).all()    

            return reglements_schema.dump(reglements)
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(ReglementApi, '/api/v1/reglement')

class SubventionApi(MethodResource,Resource):
    def get(self):
        "extract subvention"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            subventions = session.query(Subvention).all()        
            return subventions_schema.dump(subventions)
        else:
            return ({'message':'token not valid or expired'}, 400)

api.add_resource(SubventionApi, '/api/v1/subvention')

class FondsApi(MethodResource,Resource):
    def get(self):
        "extract Fonds"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            fonds = session.query(Fonds).all()        
            return fonds_schema.dump(fonds)
        else:
            return ({'message':'token not valid or expired'}, 400)
    

api.add_resource(FondsApi, '/api/v1/fonds')


class AffecteFinancement(MethodResource,Resource):
    def post(self):
        "affecte une source de financement"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            
            data = request.get_json(force=True)
            
            for item in data :
                if item == 'reglements':                    
                    newAffecte = Ass_reglement_projet(montant=data['reglements']['montant'], 
                                    reglement_id=data['reglements']['id'], 
                                    projet_id=data['reglements']['projet'])
                    session.add(newAffecte)
                    session.commit()
                elif item == 'subventions':
                    newAffecte = Ass_subvention_projet(montant=data['subventions']['montant'], 
                                    subvention_id=data['subventions']['id'], 
                                    projet_id=data['subventions']['projet'])
                    session.add(newAffecte)
                    session.commit()
                elif item == 'fonds':
                    newAffecte = Ass_fonds_projet(montant=data['fonds']['montant'], 
                                    fonds_id=data['fonds']['id'], 
                                    projet_id=data['fonds']['projet'])
                    session.add(newAffecte)
                    session.commit()
                

            return ({'message':'ok'}, 200)
        else:
            return ({'message':'token not valid or expired'}, 400)
    

api.add_resource(AffecteFinancement, '/api/v1/affectefinance')

class AssReglement(MethodResource,Resource):
    def get(self):
        "extrait les financements par reglement"
        token = request.headers.get('HTTP_AUTHORIZATION')
        if isAutorize(token):
            assReglement = session.query(Ass_reglement_projet).all()    

            return ass_reglement_schema.dump(assReglement)
        else:
            return ({'message':'token not valid or expired'}, 400)
    

api.add_resource(AssReglement, '/api/v1/assreglement')

