#Librerias audio
import json
import logging
import os
import sys
import time
from pathlib import Path
import requests
import pprint
import datetime
from flask import jsonify

import io
import time
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
from bs4 import BeautifulSoup
import re
import numpy as np
import cv2


#Librerias para crear la API
from passlib.apps import custom_app_context as pwd_context
from flask import Flask, request, jsonify, make_response, send_file
from flask_basicauth import BasicAuth
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from sqlalchemy.orm import relationship, backref
import urllib
from user_agents import parse as get_user_agent

#Librerias de Azure
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential

#Cargar .env
from dotenv import load_dotenv
load_dotenv()
wtf_csrf_check_default = os.getenv("WTF_CSRF_CHECK_DEFAULT")
keyVaultName = os.getenv("KEY_VAULT_NAME")
KVUri = f"https://{keyVaultName}.vault.azure.net"
credential_kv = DefaultAzureCredential(additionally_allowed_tenants=['*'])
client_kv = SecretClient(vault_url=KVUri, credential=credential_kv)
components_id = os.getenv("COMPONENTS_ID")

user_basic_auth = client_kv.get_secret("user-basicauth-api").value
password_basic_auth = client_kv.get_secret("password-basicauth-api").value
secret_key = client_kv.get_secret("secret-key-api").value
urls_cors = client_kv.get_secret("url-cors").value
user_db = client_kv.get_secret("db-user").value
password_db = client_kv.get_secret("db-password").value
url_db = client_kv.get_secret("db-url").value
name_db = client_kv.get_secret("db-name").value
id_tec_cognitive = client_kv.get_secret("id-teccognitive").value


computer_key = client_kv.get_secret("key-computer-vision").value
url_computer = client_kv.get_secret("url-computer-vision").value

#Create url conection to database
params = urllib.parse.quote_plus('Driver={ODBC Driver 17 for SQL Server};Server=tcp:'+url_db+',1433;Database='+name_db+';Uid='+user_db+';Pwd='+password_db+';Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;')

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config['WTF_CSRF_CHECK_DEFAULT'] = wtf_csrf_check_default
app.config['BASIC_AUTH_USERNAME'] = user_basic_auth
app.secret_key = secret_key
app.config['BASIC_AUTH_PASSWORD'] = password_basic_auth
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=%s" % params
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


basic_auth = BasicAuth(app)
db = SQLAlchemy(app)

CORS(app, supports_credentials = True, origins = urls_cors, methods = ["POST"])

