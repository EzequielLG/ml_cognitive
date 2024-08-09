from config import (app, db)
from Routes import (extractText_Routes)

# Esta línea de código agrega una regla de URL a la aplicación Flask.
app.add_url_rule("/extracciontexto/v1", view_func = extractText_Routes.procesar_file, methods = ["POST"])

@app.after_request
def after_request(response):
    db.session.close()
    response.headers['Access-Control-Allow-Origin'] = 'domain'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    return response