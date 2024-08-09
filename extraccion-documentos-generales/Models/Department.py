from config import db, relationship, backref, datetime, pwd_context

class Department(db.Model):
    __tablename__ = 'DEPARTAMENTO'   
    ID = db.Column(db.Integer, primary_key = True)
    NOMBRE_DEPARTAMENTO = db.Column(db.String(3000))
    AREA = db.Column(db.String(3000))
    ROL_DEL_DEPARTAMENTO = db.Column(db.String(3000))
    EMAIL_ENCARGADO_DEPARTAMENTO = db.Column(db.String(3000))
    APIM_CLAVE_SUSCRIPCION = db.Column(db.String(128))
    USUARIO_CREACION = db.Column(db.String(1000))
    FECHA_CREACION = db.Column(db.DateTime(), default = datetime.datetime.now())
    USUARIO_ULTIMA_MODIFICACION = db.Column(db.String(1000))
    FECHA_ULTIMA_MODIFICACION = db.Column(db.DateTime(), onupdate = datetime.datetime.now(), default = datetime.datetime.now())

    def hash_apim(self, apim):
        self.APIM_CLAVE_SUSCRIPCION = pwd_context.encrypt(apim)
    
    def verify_apim(self, apim):
        return pwd_context.verify(apim, self.APIM_CLAVE_SUSCRIPCION)
