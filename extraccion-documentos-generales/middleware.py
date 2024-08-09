from index_models import User, Permission
from config import id_tec_cognitive, get_user_agent

"""
La función `verify_user_request` verifica si la solicitud de un usuario es válida según su correo electrónico y
ID del componente.
:param mail: El parámetro `mail` es la dirección de correo electrónico del usuario que realiza la solicitud
:param componentes_id: El parámetro `components_id` es el ID de un componente que el usuario
solicitando acceso a
:return: un valor booleano. Devuelve True si la solicitud del usuario está verificada y False si no lo está.
verificado o si ocurre una excepción.
"""

def verify_user_request(mail, components_id):

    try :
        user = User.query.filter_by(CORREO_ELECTRONICO = mail).first()
        if not user:
            return False
        
        if user.ID_DEPARTAMENTO != int(id_tec_cognitive) and not Permission.query.filter_by(ID_COMPONENTE = int(components_id), ID_DEPARTAMENTO = user.ID_DEPARTAMENTO).first():
            return False
        
        return True
    except Exception as error:
        return False

"""
La función `get_info_user_agent` toma encabezados como entrada y extrae información como IP
dirección, tipo de dispositivo y si el agente de usuario es un bot.
    
    :param headers: el parámetro `headers` es un diccionario que contiene los encabezados HTTP de una solicitud.
Por lo general, incluye información como el agente de usuario, la dirección IP y otros metadatos asociados.
con la solicitud
    :return: La función `get_info_user_agent` devuelve una tupla que contiene la siguiente información:
     - `ip`: La dirección IP extraída de los encabezados. Si no se encuentra, será "Ninguno".
     - `dispositivo`: el tipo de dispositivo según la cadena del agente de usuario. Si no se encuentra, será "Ninguno".
     - `type_device`: el tipo específico de dispositivo (por ejemplo, "móvil",
"""

def get_info_user_agent(headers):

    try :
        ip = headers.get('X_REAL_IP')
    except:
        ip = None
    ua_string = str(headers.get('User-Agent'))
    print(ua_string)
    try :
        type_device = None
        user_agent = get_user_agent(ua_string)
        device = user_agent.device.family
        is_bot = user_agent.is_bot
        if "postman" in ua_string.lower():
            device = "Postman"
            type_device = "pc"

        
    except:
        device = None 
        type_device = None
        is_bot = None
    
    return ip, device, type_device, is_bot