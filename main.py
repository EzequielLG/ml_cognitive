from video_analysis import gpt4_turbo_vision_video_model
import re

# --------------------------------
# Información del video a analizar
# --------------------------------
"""
- Debe ser un nombre único y sin espacios
- Solo debe contener caracteres alfanuméricos y guiones medios
- No debe contener dos guiones medios juntos
- Debe comenzar con un caracter alfanumérico
- No debe terminar en guion medio
"""
video_index_name = "test-video-index"
"""
- Video SAS (Shared Access Signature) URL, por ejemplo: 
https://<your-storage-account-name>.blob.core.windows.net/<your-container-name>/<your-video-name>?<SAS-token>
"""
video_SAS_url = "https://gpt4vsamples.blob.core.windows.net/videos/Microsoft%20Copilot%20Short.mp4"
"""
- El ID debe ser único
"""
video_id = "video-test"

# --------------------------------
# Configuraciones del modelo de IA
# --------------------------------
system_prompt = "Eres un asistente en el análisis de videos."
user_prompt = "Describe todo lo que ves en este video:"

try:
    response = gpt4_turbo_vision_video_model(system_prompt, user_prompt, video_index_name, video_SAS_url, video_id)
    text = response["choices"][0]["message"]["content"]
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        print(sentence)
except Exception as e:
    print(f"Error: {e}")