from routes import app
from config import db
import time

with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(host = "localhost", debug = False, port = "9876")