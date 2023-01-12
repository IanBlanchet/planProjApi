from app import app
from flask_restful import Resource, Api, abort
from flask_apispec.views import MethodResource
from app.API.email import sendmail

api = Api(app)


class SendMail(MethodResource,Resource):
    def get(self):
        "envoi un email"
        sendmail("ian.blanchet@ville.valleyfield.qc.ca", "tag.ianblanchet@gmail.com")
        return ({'success':'success'}, 200)

api.add_resource(SendMail, '/api/v1/sendmail')