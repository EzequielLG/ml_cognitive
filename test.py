import requests
import base64
import re

# Configuration
GPT4V_KEY = "97f638d139364de48b76b2806d14ae06"
IMAGE_PATH = "test.jpg"
encoded_image = base64.b64encode(open(IMAGE_PATH, 'rb').read()).decode('ascii')
url_image = f"data:image/jpg;base64,{encoded_image}"

headers = {
    "Content-Type": "application/json",
    "api-key": GPT4V_KEY,
}

# Payload for the request
payload = {
  "enhancements": {
    "ocr": {
      "enabled": True
    },
    "grounding": {
      "enabled": True
    }
  },
  "messages": [
    {
      "role": "system",
      "content": [
        {
          "type": "text",
          "text": "You are an AI assistant that helps people find information."
        }
      ]
    },
    {
      "role": "user",
      "content": [
        {
          "type": "image_url",
          "image_url": {
            "url": url_image # encoded_image
          }
        },
        {
          "type": "text",
          "text": "Dime qué colores ves en la imagen"
        }
      ]
    }
  ],
  "temperature": 0.7,
  "top_p": 0.95,
  "max_tokens": 800
}

GPT4V_ENDPOINT = "https://openai-teccognitive-pprd.openai.azure.com/openai/deployments/gpt-4-vision-preview/chat/completions?api-version=2024-02-15-preview"

# Send request
try:
    response = requests.post(GPT4V_ENDPOINT, headers=headers, json=payload)
    response.raise_for_status() # Will raise an HTTPError if the HTTP request returned an unsuccessful status code
    text = response.json()["choices"][0]["message"]["content"]
    sentences = re.split(r"(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s", text)
    for sentence in sentences:
        print(sentence)
except requests.RequestException as e:
    raise SystemExit(f"Failed to make the request. Error: {e}")

# Handle the response as needed (e.g., print or process)
print(response.json())