from config import (os, time, request, db, datetime, np, ComputerVisionClient, url_computer, computer_key, OperationStatusCodes, Flask, jsonify, components_id)
from index_models import Use, User
import middleware
from bs4 import BeautifulSoup
import re
import requests
import io
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from utils import save_indicadores

def preprocesing_text(oracion):
      oracion = oracion.replace("(","( ")
      oracion = oracion.replace(")"," )")
      oracion = re.sub(r'(\d{1,5}.\d{1,5})', r'\1. ', oracion)
      oracion = oracion.replace("&","y")
      oracion = oracion.replace("<",",menor que")
      oracion = oracion.replace(">",",mayor que")
      return oracion


def procesar_html(text_html, mail, headers):
    start_processing_time = time.time()
    error=""
    romper = False # Variable booleana que se utiliza para indicar si el programa debe detenerse o no.
    soup = BeautifulSoup(text_html, 'html.parser')
    text = ""

    for link in soup.find_all(['p','li','iframe','table', 'a', 'h4', 'h1', 'h2', 'h3', 'h5', 'h6']):
    # El bloque de código que proporcionó es responsable de extraer y procesar datos de tablas HTML.
        #print(str(link))
        if '<table' in str(link):
            text += "\n"+"El siguiente audio, es la descripción de una tabla"+"\n"
            print(headers)
            headers = link.find('tr')
            headers_cells = headers.find_all('td')
            colums = [cell.get_text() for cell in headers_cells]
            concatenated_headers = ', '.join(colums)
            text += preprocesing_text("Las columnas se llaman:" + concatenated_headers + "\n")
            data_rows = link.find_all('tr')[1:]
            if ">l<" in str(link):
                for idx,row in enumerate(data_rows, start=1):
                    cells = row.find_all('td') 
                    cell1 = cells[0].getText()
                    cell_selected = ','.join([colums[index + 1] for index, cell in enumerate(cells[1:]) if ">l<" in str(cell)])
                    text += preprocesing_text(f"Fila {idx}: {cell1}. Las columnas seleccionadas son: {cell_selected} " + "\n")
            else:               
                for idx,row in enumerate(data_rows, start=1):
                    cells = row.find_all('td')
                    row_content = ', '.join(cell.get_text() for cell in cells)
                    text += preprocesing_text(f"La fila {idx} es: {row_content}" + "\n")
                
            continue
        
        if 'iframe' in str(link):
            text += preprocesing_text("\n"+"El siguiente contenido es un video que es ajeno a la Universidad Tec Milenio, para acceder a el deberas darle clic en otro apartado."+"\n")
            continue

        if '<p' in str(link) or '<li' in str(link) or '<a' in str(link) or '<h4' in str(link) or '<h1' in str(link) or '<h2' in str(link) or '<h3' in str(link) or '<h5' in str(link) or '<h6' in str(link):
            if preprocesing_text(link.text) not in text:
                text += preprocesing_text(link.text+"\n")
            for image in link.findAll('img'):
                cimage = image.get("src")
                try:
                    descimage = image.get("alt")
                    text += preprocesing_text("\n"+descimage+"\n")
                except:
                    error = "Falta atributo alt de la imagen del src: " + cimage
                    processing_time = time.time() - start_processing_time
                    save_indicadores(mail, components_id, 400, "palabras", len(error.split(' ')), processing_time, error)
                    romper = True
                    return jsonify([{"jsonrpc": "2.0", "error": {"code": 400, "message": error}, "id": 1}]), 400
                
                if descimage == "":
                    error = "Falta descripción de la imagen en el atributo alt del src: " + cimage
                    processing_time = time.time() - start_processing_time
                    save_indicadores(mail, components_id, 400, "palabras", len(error.split(' ')), processing_time, error)
                    romper = True
                    return jsonify([{"jsonrpc": "2.0", "error": {"code": 400, "message": error}, "id": 1}]), 400

            if romper:
                break   
    print(text)
    processing_time = time.time() - start_processing_time
    num_palabras = len(text.split(' '))
    save_indicadores(mail, components_id, 200, "palabras", num_palabras, processing_time, "None")
    return jsonify([{"jsonrpc": "2.0", "result": {"code": 200, "message": text}, "id": 1}]), 200



def procesar_documento(document_path, mail, headers):
    start_processing_time = time.time()
    error=""
    computervision_client = ComputerVisionClient(url_computer, CognitiveServicesCredentials(computer_key))
    texto = ""
    try:

        #print("===== Read File - remote =====")
        # Llamada API con URL y respuesta en bruto (permite obtener la ubicación de la operación)
        read_response = computervision_client.read_in_stream(document_path, raw=True)
        
        # Obtén la ubicación de la operación (URL con un ID al final) desde la respuesta
        read_operation_location = read_response.headers["Operation-Location"]
        # Extrae el ID de la URL
        operation_id = read_operation_location.split("/")[-1]
        
        # Llamada a la API "GET" y espera a que recupere los resultados
        while True:
            read_result = computervision_client.get_read_result(operation_id)
            if read_result.status not in ['notStarted', 'running']:
                break
            time.sleep(1)
        
        # Imprime el texto detectado, línea por línea
        if read_result.status == OperationStatusCodes.succeeded:
            for text_result in read_result.analyze_result.read_results:
                for line in text_result.lines:
                    #print(line.text)
                    #print(line.bounding_box)
                    texto += line.text + "\n"
                    #print(texto)
        print(texto)
        '''
        END - Read File - remote
        '''
        
        #print("End of Computer Vision quickstart.")

    except:
        error = "Formato de documento no compatible."
        processing_time = time.time() - start_processing_time
        save_indicadores(mail, components_id, 400, "palabras", len(error.split(' ')), processing_time, error)
        return jsonify([{"jsonrpc": "2.0", "error": {"code": 400, "message": error}, "id": 1}]), 400
    
    processing_time = time.time() - start_processing_time
    num_palabras = len(texto.split(' '))
    save_indicadores(mail, components_id, 200, "palabras", num_palabras, processing_time, "None")
    return jsonify([{"jsonrpc": "2.0", "result": {"code": "Success", "message": texto}, "id": 1}]), 200