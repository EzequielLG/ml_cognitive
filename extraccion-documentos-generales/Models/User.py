from config import db, relationship, backref, pwd_context, datetime
from index_models import Department

class User(db.Model):
    __tablename__ = 'USUARIO'   
    ID = db.Column(db.Integer, primary_key = True)
    ID_DEPARTAMENTO = db.Column(db.Integer, db.ForeignKey('DEPARTAMENTO.ID'))
    department = relationship(
        Department, backref = backref('users', uselist = True)
    )
    CORREO_ELECTRONICO = db.Column(db.String(300))
    CONTRASENA_ENCRIPTADA = db.Column(db.String(128))
    ROL = db.Column(db.Enum('superadmin', 'admin', 'developer'))
    IND_STATUS = db.Column(db.Enum('active', 'deactive', 'frozen'))
    USUARIO_CREACION = db.Column(db.String(1000))
    FECHA_CREACION = db.Column(db.DateTime(), default = datetime.datetime.now())
    USUARIO_ULTIMA_MODIFICACION = db.Column(db.String(1000))
    FECHA_ULTIMA_MODIFICACION = db.Column(db.DateTime(), onupdate = datetime.datetime.now(), default = datetime.datetime.now())

    def hash_password(self, password):
        self.CONTRASENA_ENCRIPTADA = pwd_context.encrypt(password)
    
    def verify_password(self, password):
        return pwd_context.verify(password, self.CONTRASENA_ENCRIPTADA)

