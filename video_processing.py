from dotenv import load_dotenv
import requests
import json
import time
import os

load_dotenv()

def gpt4_turbo_vision_video_model(model_config, video_config):
    # Ejemplo de la version: 2022-12-01. Todas las versiones tienen la siguiente estructura: YYYY-MM-DD
    api_url = f"{os.getenv("OPENAI_API_ENDPOINT")}/openai/deployments/{os.getenv("GPT_DEPLOYMENT_NAME")}/extensions/chat/completions?api-version={os.getenv("OPENAI_API_VERSION")}"
    
    headers = {
        "Content-Type": "application/json",
        "api-key": os.getenv("OPENAI_API_KEY"),
        "x-ms-useragent": "Azure-GPT-4V-video/1.0.0"
    }
    payload = {
        "model": "gpt-4-vision-preview",
        "dataSources": [
            {
                "type": "AzureComputerVisionVideoIndex",
                "parameters": {
                    "computerVisionBaseUrl": f"{os.getenv("VISION_API_ENDPOINT")}/computervision",
                    "computerVisionApiKey": os.getenv("VISION_API_KEY"),
                    "indexName": video_config["video_index_name"],
                    "videoUrls": [
                        video_config["video_SAS_url"]
                    ]
                }
            }
        ],
        "enhancements": {
            "video": {
                "enabled": True
            }
        },
        "messages": model_config,
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 800
    }

    try:
        response = requests.post(api_url, headers = headers, json = payload, timeout = 30)
        response.raise_for_status() # Lanza una excepción si se obtiene un código de error HTTP
        return response.json()
    except requests.RequestException as e:
        print(f"Error: {e}")

def create_video_index(video_index_name):
    url = f"{os.getenv("VISION_API_ENDPOINT")}/computervision/retrieval/indexes/{video_index_name}?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv("VISION_API_KEY"), 
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
    url = f"{os.getenv("VISION_API_ENDPOINT")}/computervision/retrieval/indexes/{video_index_name}/ingestions/my-ingestion?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv("VISION_API_KEY"), 
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

def wait_for_video_adding_process(video_index_name, max_retries = 30):
    url = f"{os.getenv("VISION_API_ENDPOINT")}/computervision/retrieval/indexes/{video_index_name}/ingestions?api-version=2023-05-01-preview"
    headers = {
        "Ocp-Apim-Subscription-Key": os.getenv("VISION_API_KEY")
    }
    retries = 0
    while retries < max_retries:
        time.sleep(10)
        response = requests.get(url, headers = headers)
        if response.status_code == 200:
            state_data = response.json()
            if state_data["value"][0]["state"] == "Completed":
                print(state_data)
                print("Procesamiento de video desde storage completado.")
                return True
            if state_data["value"][0]["state"] == "Failed":
                print(state_data)
                print("Procesamiento de video desde storage fallido.")
                return False
        retries += 1
    return False

def video_indexing(video_index_name, video_SAS_url, video_id):
    # Creación de index
    response = create_video_index(video_index_name)
    print(response.status_code, response.text)

    # Adición de video al index creado previamente
    response = add_video_to_index(video_index_name, video_SAS_url, video_id)
    print(response.status_code, response.text)

    # Finalización del procesamiento de video
    if not wait_for_video_adding_process(video_index_name):
        print("Procesamiento de video no completado dentro del tiempo esperado.")