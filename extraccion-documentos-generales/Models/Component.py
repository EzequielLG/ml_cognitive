from config import db, relationship, backref, datetime

class Component(db.Model):
    __tablename__ = 'COMPONENTE'   
    ID = db.Column(db.Integer, primary_key = True)
    NOMBRE_COMPONENTE = db.Column(db.String(3000))
    DESC_COMPONENTE = db.Column(db.Text)
    CATEGORIA = db.Column(db.String(1000))
    VERSION_ACTUAL = db.Column(db.String(60))
    FECHA_LIBERACION = db.Column(db.DateTime())
    USUARIO_CREACION = db.Column(db.String(1000))
    FECHA_CREACION = db.Column(db.DateTime(), default = datetime.datetime.now())
    USUARIO_ULTIMA_MODIFICACION = db.Column(db.String(1000))
    FECHA_ULTIMA_MODIFICACION = db.Column(db.DateTime(), onupdate = datetime.datetime.now(), default = datetime.datetime.now())
