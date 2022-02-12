from app.models import Contrat, Projet
from flask_marshmallow import Marshmallow
from marshmallow import post_load, INCLUDE, EXCLUDE, fields

from app import app
from app.config import session


ma = Marshmallow(app)


class ContratSchema(ma.Schema):
    class Meta:
        model = Contrat
        include_fk = True
        unknown = EXCLUDE
        sqla_session = session
        fields = ('id', 'no', 'desc')
        
    @post_load
    def make_position(self, data, **kwargs):
        return Contrat(**data)









