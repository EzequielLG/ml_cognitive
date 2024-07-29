from video_processing import gpt4_turbo_vision_video_model, video_indexing
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
import os
import re

load_dotenv()
# keyVaultName = os.getenv("KEY_VAULT_NAME")
# KVUri = f"https://{keyVaultName}.vault.azure.net"
# credential_kv = DefaultAzureCredential(additionally_allowed_tenants=['*'])
# client_kv = SecretClient(vault_url=KVUri, credential=credential_kv)

"""
- Debe ser un nombre único y sin espacios
- Solo debe contener caracteres alfanuméricos y guiones medios
- No debe contener dos guiones medios juntos
- Debe comenzar con un caracter alfanumérico
- No debe terminar en guion medio
"""
video_index_name = "test-videos-2"
"""
Video SAS (Shared Access Signature) URL (por ejemplo): 
https://<your-storage-account-name>.blob.core.windows.net/<your-container-name>/<your-video-name>?<SAS-token>
"""
video_SAS_url = "https://gpt4vsamples.blob.core.windows.net/videos/Microsoft%20Copilot%20Short.mp4"
"""
Debe ser único
"""
video_id = "test-video-1"

video_config = {
    "video_index_name": video_index_name,
    "video_SAS_url": video_SAS_url,
    "video_id": video_id
}

# Creación de index (ejecutar una única vez por video)
# video_indexing(video_config["video_index_name"], video_config["video_SAS_url"], video_config["video_id"])

# Rol del modelo
sys_message = "You are a helpful assistant."
# Prompt para el modelo
user_prompt = "Describe this video:"

# El contenido del tipo "acv_document_id" debe declararse en primer lugar en la lista del contenido del usuario, 
# ya que, de lo contrario puede esperarse un comportamiento inesperado
model_config = [
    {
        "role": "system", 
        "content": [
            {
                "type": "text", 
                "text": sys_message
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
                "type": "acv_document_id", 
                "acv_document_id": video_config["video_id"]
            }, 
            {
                "type": "text", 
                "text": user_prompt
            }
        ]
    }
]

try:
    response = gpt4_turbo_vision_video_model(model_config, video_config)
    text = response["choices"][0]["message"]["content"]
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        print(sentence)
except Exception as e:
    print(f"Error: {e}")