from config import db, relationship, backref, datetime
from index_models import Component, Department

class Permission(db.Model):
    __tablename__ = 'PERMISO'   
    ID = db.Column(db.Integer, primary_key = True)
    ID_COMPONENTE = db.Column(db.Integer, db.ForeignKey('COMPONENTE.ID'))
    component = relationship(
        Component, backref = backref('permissions', uselist = True)
    )
    ID_DEPARTAMENTO = db.Column(db.Integer, db.ForeignKey('DEPARTAMENTO.ID'))
    department = relationship(
        Department, backref = backref('permissions', uselist = True)
    )
    TIPO = db.Column(db.Enum('pay as you go', 'monthly'))
    IND_STATUS = db.Column(db.Enum('active', 'deactive', 'frozen'))
    USUARIO_CREACION = db.Column(db.String(1000))
    FECHA_CREACION = db.Column(db.DateTime(), default = datetime.datetime.now())
    USUARIO_ULTIMA_MODIFICACION = db.Column(db.String(1000))
    FECHA_ULTIMA_MODIFICACION = db.Column(db.DateTime(), onupdate = datetime.datetime.now(), default = datetime.datetime.now())


