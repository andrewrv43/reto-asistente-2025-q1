import requests
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class AgenteLangchain:
    def __init__(self):
        self.llm = ChatOllama(model="deepseek-r1:8b", base_url="http://host.docker.internal:11434")
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """Debes elegir una de las siguientes herramientas según la consulta del usuario: "
                       Herramienta: 'query' Descripcion: para preguntas generales, dudas sobre temas bancarios o cualquier duda en general, donde el usuario quiera aprender o saber algo y 
                       Herramienta: 'consulta_producto' Descripcion: El usuario describe o menciona el nombre de uno o varios productos. 
                       Devuelve solo el nombre de la herramientaque usarías sin texto adicional."""),
            ("user", "{consulta}")
        ])
    def general_query(self, query: str):
        response = requests.get("http://flask-assistant:5000/assistant/rag", params={"query": query})
        return response.json() if response.status_code == 200 else "Error en la consulta."
    def process_file(self,consulta, file):
            files = {'file': (file.filename, file.stream, file.content_type)}
            body = {'query': consulta}
            response = requests.post('http://flask-assistant:5000/assistant/analyze-pdf', files=files,data=body)
            
            return response.json() if response.status_code == 200 else "Error al procesar el archivo."
    def product_query(self, product_name: str):
        response = requests.get("http://flask-assistant:5000/assistant/shopping-advisor", params={"product_name": product_name})
        return response.json() if response.status_code == 200 else "Producto no encontrado."
    def ejecutar_agente(self, consulta,file=None,i=0):
        messages = self.chat_prompt.format_messages(consulta=consulta)
        tool_choice = self.llm.invoke(messages).content.strip().lower()
        if  file is not None:
            return self.process_file(consulta,file)
        elif  "query" in tool_choice:
            return self.general_query(consulta)
        elif  "consulta_producto" in tool_choice:
            return self.product_query(consulta)
        else:
            if i==3:
                return "No se pudo determinar la herramienta adecuada para la consulta."
            return self.ejecutar_agente(consulta, file,i+1)
