from config import (openai_api_endpoint, openai_api_key, gpt_deployment_name, vision_api_endpoint, vision_api_key, openai_api_version)
import requests
import json
import time

def gpt4_turbo_vision_video_model(system_prompt, user_prompt, video_index_name, video_SAS_url, video_id):

    # Creación de index y adición de video al index
    video_indexing(video_index_name, video_SAS_url, video_id)

    # Análisis de video
    api_url = f"{openai_api_endpoint}/openai/deployments/{gpt_deployment_name}/extensions/chat/completions?api-version={openai_api_version}"
    headers = {
        "Content-Type": "application/json",
        "api-key": openai_api_key,
        "x-ms-useragent": "Azure-GPT-4V-video/1.0.0"
    }

    # El contenido del tipo "acv_document_id" debe declararse en primer lugar en la lista del contenido del usuario, 
    # ya que, de lo contrario puede esperarse un comportamiento inesperado
    payload = {
        "model": "gpt-4-vision-preview",
        "dataSources": [
            {
                "type": "AzureComputerVisionVideoIndex",
                "parameters": {
                    "computerVisionBaseUrl": f"{vision_api_endpoint}/computervision",
                    "computerVisionApiKey": vision_api_key,
                    "indexName": video_index_name,
                    "videoUrls": [
                        video_SAS_url
                    ]
                }
            }
        ],
        "enhancements": {
            "video": {
                "enabled": True
            }
        },
        "messages": [
            {
                "role": "system", 
                "content": [
                    {
                        "type": "text", 
                        "text": system_prompt
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "acv_document_id", 
                        "acv_document_id": video_id
                    }, 
                    {
                        "type": "text", 
                        "text": user_prompt
                    }
                ]
            }
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(api_url, headers = headers, json = payload, timeout = 100)
        response.raise_for_status() # Lanza una excepción si se obtiene un código de error HTTP
        return response.json()
    except requests.RequestException as e:
        print(f"Error: {e}")

def create_video_index(video_index_name):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{video_index_name}?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": vision_api_key, 
        "Content-Type": "application/json"
    }
    data = {
        "features": [
            {
                "name": "vision", 
                "domain": "surveillance"
            }, 
            {
                "name": "speech"
            }
        ]
    }
    return requests.put(url, headers = headers, data = json.dumps(data))

def add_video_to_index(video_index_name, video_SAS_url, video_id):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{video_index_name}/ingestions/my-ingestion?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": vision_api_key, 
        "Content-Type": "application/json"
    }
    data = {
        "videos": [
            {
                "mode": "add", 
                "documentId": video_id, 
                "documentUrl": video_SAS_url
            }
        ],
        "generateInsightIntervals": False,
        "moderation": False,
        "filterDefectedFrames": False,
        "includeSpeechTranscrpt": True
    }
    return requests.put(url, headers = headers, data = json.dumps(data))

def wait_for_video_adding_process(video_index_name, max_retries = 100):
    url = f"{vision_api_endpoint}/computervision/retrieval/indexes/{video_index_name}/ingestions?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": vision_api_key
    }
    retries = 0
    while retries < max_retries:
        time.sleep(10)
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            state_data = response.json()
            if state_data["value"][0]["state"] == "Completed":
                return True
            if state_data["value"][0]["state"] == "Failed":
                return False
        retries += 1
    return False

def video_indexing(video_index_name, video_SAS_url, video_id):
    # Creación de index
    response = create_video_index(video_index_name)
    
    # Si el index del video ya existe entonces ya no se procesa
    if(response.status_code == 409):
        return

    # Adición de video al index creado previamente
    response = add_video_to_index(video_index_name, video_SAS_url, video_id)
    
    # Finalización del procesamiento de video
    if not wait_for_video_adding_process(video_index_name):
        print("Procesamiento de video no completado dentro del tiempo esperado.")