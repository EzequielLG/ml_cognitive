from config import db, datetime
from index_models import Use, User
"""
     La función `save_indicadores` guarda información y métricas del usuario en la base de datos.
    
     :param mail: la dirección de correo electrónico del usuario
     :param headers: el parámetro `headers` suele ser un diccionario que contiene los encabezados HTTP de
     una solicitud. Estos encabezados proporcionan información sobre la solicitud, como el agente de usuario, el contenido.
     tipo y credenciales de autenticación
     :param Processing_time: el parámetro Processing_time es el tiempo que tomó procesar la solicitud.
     medido en segundos
     :param status_code: El código de estado es un código numérico que indica el estado del HTTP
     pedido. Normalmente es un número de tres dígitos, como 200 para una solicitud exitosa o 404 para una no.
     error encontrado
     :param error: El parámetro "error" se utiliza para almacenar cualquier mensaje de error o descripción relacionada con el
     operación que se está realizando. Se puede utilizar para proporcionar información adicional sobre cualquier error que
     ocurrió durante la ejecución del código
"""

def save_indicadores(mail, components_id, status_code, desc_volumetria, volumetria, processing_time, error):
    if processing_time:
        processing_time = round(processing_time, 2)
    user = User.query.filter_by(CORREO_ELECTRONICO=mail).first()
    save_use = Use(
        ID_DEPARTAMENTO = user.ID_DEPARTAMENTO,
        ID_COMPONENTE = components_id,
        ID_USUARIO = user.ID,
        CODIGO_STATUS = status_code,
        DESC_VOLUMETRIA = desc_volumetria,
        VOLUMETRIA = volumetria,
        TIEMPO_PROCESAMIENTO = processing_time,
        TIPO_ERROR = error,
        USUARIO_CREACION = str(user.ID),
        FECHA_CREACION = datetime.datetime.now(),
        USUARIO_ULTIMA_MODIFICACION = str(user.ID),
        FECHA_ULTIMA_MODIFICACION = datetime.datetime.now()
    )
    db.session.add(save_use)
    db.session.commit()