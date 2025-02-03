import requests
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class AgenteLangchain:
    def __init__(self):
        self.llm = ChatOllama(model="deepseek-r1:8b", base_url="http://host.docker.internal:11434")
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """

Instrucción:

Analiza la consulta del usuario y selecciona la herramienta más adecuada según su contenido:

'query': Para preguntas generales o dudas sobre temas bancarios y financieros.

Ejemplos:
¿Qué es la Superintendencia de Bancos?
¿Cómo funcionan las cuentas de ahorro?
¿Qué es un índice financiero y para qué sirve?


'consulta_producto': Para consultas que mencionan un producto específico o buscan información sobre bienes o artículos, incluyendo precios o referencias a productos económicos o costosos.

Ejemplos:
Marcas de relojes: ROLEX, CASIO, SEIKO.
Componentes electrónicos: TARJETAS MADRE, PROCESADORES, LAPTOPS.
Artículos de consumo: flores, zapatos, ropa.
Consultas de precios: "Quiero precios de zapatos".
Búsqueda de productos: "Busco un celular nuevo".
Reglas:

La elección no depende del uso de mayúsculas o minúsculas.
Devuelve solo el nombre de la herramienta seleccionada, sin texto adicional.

"""),
            ("user", "{consulta}")
        ])
    def general_query(self, query: str):
        response = requests.post("http://flask-assistant:5000/assistant/rag", json={"query": query})
        return response.json() if response.status_code == 200 else "Error en la consulta."
    def process_file(self,consulta, file):
            files = {'file': (file.filename, file.stream, file.content_type)}
            body = {'query': consulta}
            response = requests.post('http://flask-assistant:5000/assistant/analyze-pdf', files=files,data=body)
            
            return response.json() if response.status_code == 200 else "Error al procesar el archivo."
    def product_query(self, product_name: str):
        response = requests.post("http://flask-assistant:5000/assistant/shopping-advisor", json={"query": product_name})
        return response.json() if response.status_code == 200 else "Producto no encontrado."
    def ejecutar_agente(self, consulta,file=None,i=0):
        messages = self.chat_prompt.format_messages(consulta=consulta)
        tool_choice = self.llm.invoke(messages).content.strip().lower()
        print("#############",tool_choice)
        if  file is not None:
            return self.process_file(consulta,file)
        elif  "query" in tool_choice:
            return self.general_query(consulta)
        elif  "consulta_producto" in tool_choice:
            return self.product_query(consulta)
        else:
            return "No se pudo determinar la herramienta adecuada para la consulta."
