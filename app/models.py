from email.policy import default
from sqlalchemy.ext.declarative import declarative_base
from app.config import session, engine, Config
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import date
from sqlalchemy.dialects.postgresql import JSONB
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt

Base = declarative_base()
annee = date.today().year


class User(Base):
        __tablename__ = 'user'
        id = Column(Integer, primary_key=True)
        username = Column(String(64), index=True, unique=True)
        email = Column(String(120), index=True, unique=True)
        password_hash = Column(String(128))
        statut = Column(String(8), default='attente')#actif, support, attente, archive, admin
        service = Column(String(10))
        projet = relationship('Projet', backref='charge_projet', lazy='dynamic')
        contrat = relationship('Contrat', backref='user', lazy='dynamic')
        jalon = relationship('Jalon', backref='user', lazy='dynamic')
        def __repr__(self):
            return "{} -- {}".format(self.username, self.statut)
        

        def set_password(self, password):
            self.password_hash = generate_password_hash(password)

        def check_password(self, password):
            return check_password_hash(self.password_hash, password)

        def get_reset_password_token(self, expires_in=600):
            return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, Config.SECRET_KEY, algorithm='HS256')

        @staticmethod
        def verify_reset_password_token(token):
            #id = jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')['reset_password']
            try:                
                id = jwt.decode(token, Config.SECRET_KEY, algorithms='HS256')['reset_password']                
            except:
                return
            return session.query(User).filter_by(id = id).first()






class Projet(Base):
        __tablename__ = 'projet'
        id = Column(Integer, primary_key=True)
        no_projet = Column(String(15), index=True, unique=True)#cont : \d{4}-\d{5}
        desc = Column(String(64), index=True)
        cat = Column(String(50), index=True)
        motcle = Column(String(150))
        immo = Column(Boolean, index=True)
        reglA = Column(Integer, index=True)#cont : \d{3}
        reglB = Column(Integer, index=True)#cont : \d{3}
        statut = Column(String(20), index=True, default='En approbation')
        charge = Column(Integer, ForeignKey('user.id'))
        affectation = Column(String(45), index=True)  # 3 choix : D2D3, SD2SD3, D3
        prev_courante = Column(Float)
        nature = Column(JSONB)
        rating = Column(JSONB)
        troncon = relationship('Troncon', backref='projet', lazy='dynamic')
        pti = relationship('Pti', backref='projet', lazy='dynamic')
        depense = relationship('Depense', backref='projet', lazy='dynamic')
        contrat = relationship('Contrat', backref='projet', lazy='dynamic')
        financeSubvention = relationship('Ass_subvention_projet', backref='projet')
        jalon = relationship('Jalon', backref='projet', lazy='dynamic')
        financeReglement = relationship('Ass_reglement_projet', backref='projet')
        financeFonds = relationship('Ass_fonds_projet', backref='projet')

        def __str__(self):
            return "{} - {}".format(self.no_projet, self.desc[:45])
        
        def calcDepense(self):
                anterieur = 0
                courante = 0
                for depense in self.depense:
                        if depense.annee == annee:
                                courante += depense.montant
                                continue
                        anterieur += depense.montant
                                        
                return anterieur, courante
	
        def extractPtiCourant(self):
                ptiCourant = ''
                ptiEnPrep = ''
                for pti in self.pti:
                        if pti.annee == (annee-1):
                                ptiCourant = pti
                        elif pti.annee == annee:
                                ptiEnPrep = pti
                
                return ptiCourant, ptiEnPrep
	
        def extractFinance(self):
                reglements = []
                for reglement in self.financeReglement:
                        reglements.append({'no':reglement.reglement.numero, 'montant' :reglement.montant})

                subventions = []
                for subvention in self.financeSubvention:
                        subventions.append({'nom':subvention.subvention.nomProg, 'montant':subvention.montant})
                
                fonds = []
                for fond in self.financeFonds:
                        fonds.append({'nom':fond.fonds.nom, 'montant':fond.montant})

                return reglements, subventions, fonds


class Troncon(Base):
        __tablename__ = 'troncon'
        id = Column(Integer, primary_key=True)
        no_troncon = Column(String(15), index=True)
        projet_id =  Column(Integer, ForeignKey('projet.id'))

	
class Pti(Base):
        __tablename__ = 'pti'
        id = Column(Integer, primary_key=True)
        annee =  Column(Integer, index=True)# année d'adoption
        projet_id =  Column(Integer, ForeignKey('projet.id'))
        cycleCour = Column(Integer)#premier année du PTI
        cycle2 = Column(Integer)# etc
        cycle3 = Column(Integer)
        cycle4 = Column(Integer)
        cycle5 = Column(Integer)

class Depense(Base):
        __tablename__ = 'depense'
        id = Column(Integer, primary_key=True)
        annee =  Column(Integer, index=True)# cont: \d{4}
        montant = Column(Integer)
        projet_id =  Column(Integer, ForeignKey('projet.id'))

class Contrat(Base):
        __tablename__ = 'contrat'
        id = Column(Integer, primary_key=True)
        no =  Column(String(15), index=True, unique=True)
        princ = Column(Boolean, index=True)#indique si il s'agit du contrat principal de construction
        desc = Column(String(100), index=True)
        estimation = Column(Float)
        montant = Column(Float)
        reso = Column(String(15), index=True)
        no_commande = Column(String(12))
        dessin = Column(String(45), index=True)
        releve = Column(String(45), index=True)
        surveillance = Column(String(45), index=True)
        livrable = Column(String(45), index=True)
        statut = Column(String(20), index=True, default='actif')
        charge_contrat = Column(Integer, ForeignKey('user.id'))
        projet_id =  Column(Integer, ForeignKey('projet.id'))
        jalon = relationship('Jalon', backref='contrat', lazy='dynamic')
        bordereau = relationship('Bordereau', backref='contrat', lazy='dynamic')
        modification = relationship('Modification', backref='contrat', lazy='dynamic')
        def __str__(self):
            return "{} - {}".format(self.no, self.desc[:40])

class Subvention(Base):
        __tablename__ = 'subvention'
        id = Column(Integer, primary_key=True)
        nomProg = Column(String(100), index=True)
        no_id = Column(String(20), index=True, unique=True)#identification de la subvention
        montantAcc = Column(Float)
        montantFin = Column(Float)
        financeProjet = relationship('Ass_subvention_projet', backref='subvention')
        def __str__(self):
            return "{} - {} - {}".format(self.nomProg, self.no_id, self.montantAcc)


class Reglement(Base):
        __tablename__ = 'reglement'
        id = Column(Integer, primary_key=True)
        numero = Column(String(10), index=True, unique=True)
        montant = Column(Integer)
        ratioSecteur = Column(Float)
        financeProjet = relationship('Ass_reglement_projet', backref='reglement')
        def __str__(self):
            return "{} - {}".format(self.numero, self.montant)

class Fonds(Base):
        __tablename__ = 'fonds'
        id = Column(Integer, primary_key=True)
        nom = Column(String(100), index=True, unique=True)
        montantDisp = Column(Float)
        financeProjet = relationship('Ass_fonds_projet', backref='fonds')
        def __str__(self):
            return "{} - {}".format(self.nom, self.montantDisp)

#table d'association du financement provenant des règlement
class Ass_reglement_projet(Base):
        __tablename__ = 'ass_reglement_projet'
        montant = Column(Integer)#la portion du reglement qui va sur le projet
        reglement_id = Column(Integer, ForeignKey('reglement.id'), primary_key=True)
        projet_id = Column(Integer, ForeignKey('projet.id'), primary_key=True)

#table d'association du financement provenant des subventions
class Ass_subvention_projet(Base):
        __tablename__ = 'ass_subvention_projet'
        montant = Column(Integer)#la portion de la subvention qui va sur le projet
        subvention_id = Column(Integer, ForeignKey('subvention.id'), primary_key=True)
        projet_id = Column(Integer, ForeignKey('projet.id'), primary_key=True)

class Ass_fonds_projet(Base):
        __tablename__ = 'ass_fonds_projet'
        montant = Column(Integer)#la portion du reglement qui va sur le projet
        fonds_id = Column(Integer, ForeignKey('fonds.id'), primary_key=True)
        projet_id = Column(Integer, ForeignKey('projet.id'), primary_key=True)


class Jalon(Base):
        __tablename__ = 'jalon'
        id = Column(Integer, primary_key=True)
        date = Column(Date)
        jalon = Column(String(20), index=True)
        commentaire = Column(String(50))
        etat = Column(String(10), index=True, default='travail')
        charge_jalon = Column(Integer, ForeignKey('user.id'))
        projet_id =  Column(Integer, ForeignKey('projet.id'))
        contrat_id =  Column(Integer, ForeignKey('contrat.id'))
        duree = Column(Integer)
	


class Bordereau(Base):
        __tablename__ = 'bordereau'
        id = Column(Integer, primary_key=True)
        quantite = Column(Float)
        prix_un = Column(Float)
        item_id =  Column(Integer, ForeignKey('item.id'))
        contrat_id =  Column(Integer, ForeignKey('contrat.id'))
        decompte = relationship('Decompte', backref='bordereau', lazy='dynamic')


class Item(Base):
        __tablename__ = 'item'
        id = Column(Integer, primary_key=True)
        description = Column(String(75))
        unite = Column(String(20), index=True)
        bordereau = relationship('Bordereau', backref='item', lazy='dynamic')


class Modification(Base):
        __tablename__ = 'modification'
        id = Column(Integer, primary_key=True)
        no = Column(Integer)
        description = Column(String(125))
        montant = Column(Float)
        date = Column(Date)
        contrat_id =  Column(Integer, ForeignKey('contrat.id'))

class Decompte(Base):
        __tablename__ = 'decompte'
        id = Column(Integer, primary_key=True)
        quantite = Column(Float)
        no_decompte = Column(Integer)
        bordereau_id =  Column(Integer, ForeignKey('bordereau.id'))

class Events(Base):
        __tablename__ = 'events'
        id = Column(Integer, primary_key=True)
        title = Column(String(25))
        date = Column(Date)


Base.metadata.create_all(engine)


