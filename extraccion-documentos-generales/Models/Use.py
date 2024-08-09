from config import db, relationship, backref, datetime
from index_models import Component, Department, User

class Use(db.Model):
    __tablename__ = 'USO'   
    ID = db.Column(db.Integer, primary_key = True)
    ID_COMPONENTE = db.Column(db.Integer, db.ForeignKey('COMPONENTE.ID'))
    component = relationship(
        Component, backref = backref('uses', uselist = True)
    )
    ID_DEPARTAMENTO = db.Column(db.Integer, db.ForeignKey('DEPARTAMENTO.ID'))
    department = relationship(
        Department, backref = backref('uses', uselist = True)
    )
    ID_USUARIO = db.Column(db.Integer, db.ForeignKey('USUARIO.ID'))
    user = relationship(
        User, backref = backref('uses', uselist = True)
    )
    CODIGO_STATUS = db.Column(db.Integer)
    DESC_VOLUMETRIA = db.Column(db.Text)
    VOLUMETRIA = db.Column(db.Integer)
    TIEMPO_PROCESAMIENTO = db.Column(db.Float())
    TIPO_ERROR = db.Column(db.Text)
    USUARIO_CREACION = db.Column(db.String(1000))
    FECHA_CREACION = db.Column(db.DateTime(), default = datetime.datetime.now())
    USUARIO_ULTIMA_MODIFICACION = db.Column(db.String(1000))
    FECHA_ULTIMA_MODIFICACION = db.Column(db.DateTime(), onupdate = datetime.datetime.now(), default = datetime.datetime.now())
    

