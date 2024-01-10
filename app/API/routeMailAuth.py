from app import app
from flask import Response, redirect, request, url_for
from flask_restful import Resource, Api, abort
from flask_apispec.views import MethodResource
from app.config import session
from app.models import User
from app.API.email import sendmail, sendPasswordResetEmail
from app.API.schemas import UserSchema

api = Api(app)

user_schema = UserSchema()

class SendMail(MethodResource,Resource):
    def get(self):
        "envoi un email"
        sendmail("ian.blanchet@ville.valleyfield.qc.ca", "tag.ianblanchet@gmail.com")
        return ({'success':'success'}, 200)

api.add_resource(SendMail, '/api/v1/sendmail')

class ResetPasswordRequest(MethodResource,Resource):
    def post(self):
        "envoi un lien pour réinitialiser le password"
        data = request.get_json(force=True)
        user = session.query(User).filter_by(email = data['email']).first()
        
        if user :
            token = user.get_reset_password_token()
            domain = data['url']            
            sendPasswordResetEmail('ian.blanchet@ville.valleyfield.qc.ca', user, token, domain)
            return ({'user':user_schema.dump(user)}, 200)
        
        return ({'user':None}, 400)

api.add_resource(ResetPasswordRequest, '/api/v1/resetPasswordRequest')

class ResetPassword(MethodResource,Resource):
    def post(self):
        "réinitialiser le password"
        data = request.get_json(force=True)        
        #user = session.query(User).filter_by(email = data['email']).first()
        
        user = User.verify_reset_password_token(data['token'])
        if user :           
            user.set_password(data['newPass'])
            return ({'user':user_schema.dump(user)}, 200)
        
        else :
            return ({'user':None}, 400)

api.add_resource(ResetPassword, '/api/v1/resetPassword')
