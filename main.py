from video_analysis import gpt4_turbo_vision_video_model
import re

# ----------
# Datos demo
# ----------

videos_demo = [
    {
        "index_name": "demo-1",
        "url": "https://stg0lang0cognitive0pprd.blob.core.windows.net/demo-elg-container/Microsoft%20Copilot%20Short.mp4?sp=r&st=2024-08-01T01:32:53Z&se=2025-08-07T09:32:53Z&spr=https&sv=2022-11-02&sr=b&sig=cN8gsri%2F1o7pYVhRKRz3y1%2B9P87CCEb6ZiVs1GThpVE%3D",
        "id": "video-demo-1"
    },
    {
        "index_name": "demo-2",
        "url": "https://stg0lang0cognitive0pprd.blob.core.windows.net/demo-elg-container/Video%20de%20prueba%20-%201.mp4?sp=r&st=2024-08-01T02:08:31Z&se=2025-08-08T10:08:31Z&spr=https&sv=2022-11-02&sr=b&sig=ckRczrhaPceHZh5iz%2BDMOQ8L6xYq6wqJAQKH9HmgL5U%3D",
        "id": "video-demo-2"
    },
    {
        "index_name": "demo-3",
        "url": "https://stg0lang0cognitive0pprd.blob.core.windows.net/demo-elg-container/Video%20de%20prueba%20-%202.mp4?sp=r&st=2024-08-01T03:11:33Z&se=2025-08-08T11:11:33Z&spr=https&sv=2022-11-02&sr=b&sig=ANFHCpAkDt7zRg6h8paOJjAknoGkA6i7dLzWpzPCWjA%3D",
        "id": "video-demo-3"
    },
    {
        "index_name": "demo-4",
        "url": "https://stg0lang0cognitive0pprd.blob.core.windows.net/demo-elg-container/Video%20de%20prueba%20-%203.mp4?sp=r&st=2024-08-01T03:17:37Z&se=2025-08-08T11:17:37Z&spr=https&sv=2022-11-02&sr=b&sig=eulFSeyqHndj2UxVbvmrlsu1AquRuIbxrLSXPMf1sP0%3D",
        "id": "video-demo-4"
    }
]

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
video_index_name = videos_demo[1]["index_name"]
"""
- Video SAS (Shared Access Signature) URL: 
https://<storage-account-name>.blob.core.windows.net/<container-name>/<video-name>?<SAS-token>
"""
video_SAS_url = videos_demo[1]["url"]
"""
- El ID debe ser único
"""
video_id = videos_demo[1]["id"]

# --------------------------------
# Configuraciones del modelo de IA
# --------------------------------
system_prompt = "Eres un asistente en el análisis de videos."
user_prompt = "Describe las emociones las personas que están en el video, posteriormente haz un resumen de su comportamiento cognitivo."

try:
    response = gpt4_turbo_vision_video_model(system_prompt, user_prompt, video_index_name, video_SAS_url, video_id)
    text = response["choices"][0]["message"]["content"]
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        print(sentence)
except Exception as e:
    print(f"Error: {e}")