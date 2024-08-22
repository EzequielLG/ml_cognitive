from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from dotenv import load_dotenv
import os

load_dotenv()
keyVaultName = os.getenv("KEY_VAULT_NAME")
KVUri = f"https://{keyVaultName}.vault.azure.net"
credential_kv = DefaultAzureCredential(additionally_allowed_tenants=['*'])
client_kv = SecretClient(vault_url=KVUri, credential=credential_kv)

openai_api_endpoint = client_kv.get_secret(os.getenv("OPENAI_API_ENDPOINT")).value
openai_api_key = client_kv.get_secret(os.getenv("OPENAI_API_KEY")).value
gpt_deployment_name = client_kv.get_secret(os.getenv("GPT_DEPLOYMENT_NAME")).value
vision_api_endpoint = client_kv.get_secret(os.getenv("VISION_API_ENDPOINT")).value
vision_api_key = client_kv.get_secret(os.getenv("VISION_API_KEY")).value
openai_api_version = client_kv.get_secret(os.getenv("OPENAI_API_VERSION")).value