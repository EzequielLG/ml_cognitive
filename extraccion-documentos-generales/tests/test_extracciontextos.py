from run import app
import os
import io
from base64 import b64encode
from config import user_basic_auth, password_basic_auth

userPass = user_basic_auth+":"+password_basic_auth
userPassEncoded = b64encode(userPass.encode('ascii'))
headers = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'luis.fortanel@tec.mx'
}


def test_status_code_401():
    tester = app.test_client()
    response = tester.post("/extracciontexto/v1")
    assert response.status_code == 401

def test_status_code_401_2():
    data = {}
    data['file'] = io.open("tests/poema.jpg", "rb", buffering = 0)
    headers_local = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'jose.enrique@tecmilenio.mx'
    }
    tester = app.test_client()
    response = tester.post(
        "/extracciontexto/v1", data=data, follow_redirects=True,
        content_type='multipart/form-data', headers=headers_local
    )
    assert response.status_code == 401
    assert response.data == b'[{"error":{"code":"401","message":"Usuario no autorizado"},"id":1,"jsonrpc":"2.0"}]\n'


def test_no_formato():
    data = {}
    data['file'] = io.open("tests/word.docx", "rb", buffering = 0)
    headers_local = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'luis.fortanel@tec.mx'
    }
    tester = app.test_client()
    response = tester.post("/extracciontexto/v1",data=data, content_type='multipart/form-data', headers=headers_local)
    assert response.status_code == 400
    assert response.data == b'[{"error":{"code":"400","message":"Formato no valido"},"id":1,"jsonrpc":"2.0"}]\n'
    

def test_status_code_200():
    data = {}
    data['file'] = io.open("tests/poema.jpg", "rb", buffering = 0)
    headers_local = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'luis.fortanel@tec.mx'
    }
    tester = app.test_client()
    response = tester.post(
        "/extracciontexto/v1", data=data, follow_redirects=True,
        content_type='multipart/form-data', headers=headers_local
    )
    assert response.status_code == 200

def test_status_code_200_html():
    data = {}
    data['file'] = io.open("tests/explica.htm", "rb", buffering = 0)
    headers_local = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'luis.fortanel@tec.mx'
    }
    tester = app.test_client()
    response = tester.post(
        "/extracciontexto/v1", data=data, follow_redirects=True,
        content_type='multipart/form-data', headers=headers_local
    )
    assert response.status_code == 200

def test_status_code_200_html_2():
    data = {}
    data['file'] = io.open("tests/explica2.htm", "rb", buffering = 0)
    headers_local = {
    'Authorization': 'Basic %s' % userPassEncoded.decode("ascii"),
    'mail': 'luis.fortanel@tec.mx'
    }
    tester = app.test_client()
    response = tester.post(
        "/extracciontexto/v1", data=data, follow_redirects=True,
        content_type='multipart/form-data', headers=headers_local
    )
    assert response.status_code == 200