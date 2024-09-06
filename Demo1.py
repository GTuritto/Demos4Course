from IPython.display import Image, display
from google.colab import userdata

import os
import autogen
from autogen.coding import LocalCommandLineCodeExecutor

# API Configuracion para OpenAI
# apiConfig = [{
#        "model": "gpt-4o-mini",
#        "max_tokens": 500,
#        "api_key": userdata.get('OPENAI_API_KEY')
#    }]


# API Configuracion para Mistral -- Preferimos usar esta ya que no hay que pagar y es tan buena como la de OpenAI
api_config = [{
        "model": "mistral-large-latest",
        "max_tokens": 1000,
        "api_key": userdata.get('MISTRAL_API_KEY'),
        "api_type": "mistral"
    }]

# crea el AssistantAgent named "Asistente"
asistente = autogen.AssistantAgent(
    name="Asistente",
    llm_config={
        "cache_seed": 41,  # semilla del caching
        "config_list": api_config,  # configuracion para la API a ser usada
        "temperature": 0,  # temperature para sampling
    },
)

# crea el agente que actuara como Proxy del Usuario
proxy_usuario = autogen.UserProxyAgent(
    name="Usuario - Proxy",
    human_input_mode="NEVER",  # no solicita feedback al usuario hay tres alternativas "ALWAYS", "TERMINATE", "NEVER"
    max_consecutive_auto_reply=10,
    is_termination_msg=lambda x: x.get("contenido", "").rstrip().endswith("TERMINATE"),
    code_execution_config={
        "executor": LocalCommandLineCodeExecutor(work_dir="contenido"),   # como y donde ejecutamos el codigo generado
    },
)

proxy_usuario.initiate_chat(
    recipient=asistente,
    message="""Plot the YTD Bitcoin prices in Euros and volume of transactions Bitcoin_YTD.png.""",
)

try:
    image = Image(filename="contenido/Bitcoin_YTD.png")
    display(image)
except FileNotFoundError:
    print("Image no encontrada.")


