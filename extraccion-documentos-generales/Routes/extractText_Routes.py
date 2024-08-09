from config import (request, jsonify, basic_auth, np, cv2, io, cv2, components_id)
from Controllers import  extractText_Controller
from index_models import User
import middleware

@basic_auth.required
def procesar_file():
    headers = request.headers
    mail = str(headers.get('mail'))
    file = request.files.get('file')

    if not middleware.verify_user_request(mail, components_id):
        return jsonify([{"jsonrpc": "2.0", "error": {"code": "401", "message": "Usuario no autorizado"}, "id": 1}]), 401

    filename = file.filename
    filename = filename.lower()
    
    if '.pdf' in filename or '.jpg' in filename or '.png' in filename or '.jpeg' in filename or '.tiff' in filename or '.bmp' in filename:
        filename = file.read()
        filename = io.BytesIO(filename)
        return extractText_Controller.procesar_documento(filename, mail, headers)
    elif '.html' in filename or '.htm' in filename:
        filename = file.read()
        filename.decode('utf-8')
        return extractText_Controller.procesar_html(filename, mail, headers)
    else:
        return jsonify([{"jsonrpc": "2.0", "error": {"code": "400", "message": "Formato no valido"}, "id": 1}]), 400

    

    


