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
video_index_name = "test-video-index-1"
"""
- Video SAS (Shared Access Signature) URL: 
https://<storage-account-name>.blob.core.windows.net/<container-name>/<video-name>?<SAS-token>
"""
video_SAS_url = "https://stg0lang0cognitive0pprd.blob.core.windows.net/demo-elg-container/Microsoft%20Copilot%20Short.mp4?sp=r&st=2024-08-01T01:32:53Z&se=2025-08-07T09:32:53Z&spr=https&sv=2022-11-02&sr=b&sig=cN8gsri%2F1o7pYVhRKRz3y1%2B9P87CCEb6ZiVs1GThpVE%3D"
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