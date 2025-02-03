import requests
from langchain_ollama import ChatOllama
from langchain.prompts import ChatPromptTemplate

class AgenteLangchain:
    def __init__(self):
        self.llm = ChatOllama(model="deepseek-r1:8b", base_url="http://host.docker.internal:11434")
        self.chat_prompt = ChatPromptTemplate.from_messages([
            ("system", """Debes elegir una de las siguientes herramientas según la consulta del usuario. Analiza la consulta y selecciona la herramienta más adecuada en función de su contenido:

- Herramienta: 'query'  
  - Descripción: Para preguntas generales o dudas sobre temas bancarios, financieros o consultas en las que el usuario quiera aprender algo.  
  - Ejemplos de consultas para 'query':  
    - ¿Qué es la Superintendencia de Bancos?  
    - ¿Cuánto capital tengo en mi tarjeta?  
    - ¿Cómo funcionan las cuentas de ahorro?  
    - ¿Qué hacer si me hacen un débito indebido?  
    - ¿Qué es un índice financiero y para qué sirve?  
    - ¿Cómo se calculan los intereses de un préstamo?  
    - ¿Cuál es la diferencia entre una tarjeta de débito y crédito?  
    - Explicación sobre inversiones en bonos.  

- Herramienta: 'consulta_producto'  
  - Descripción: Para consultas en las que el usuario menciona un producto específico o desea buscar información sobre bienes o artículos.  
  - Ejemplos de consultas para 'consulta_producto':  
    - ROLEX, CASIO, SEIKO (Marcas de relojes).  
    - TARJETAS MADRE, PROCESADORES, LAPTOPS (Componentes y dispositivos electrónicos).  
    - QUIERO BUSCAR SOBRE FLORES, ZAPATOS, ROPA (Artículos de consumo).  
    - QUIERO PRECIOS DE ZAPATOS.  
    - BUSCO UN CELULAR NUEVO.  
    - ¿DÓNDE PUEDO COMPRAR UNA CASA?  
    - LISTADO DE VEHÍCULOS DISPONIBLES PARA COMPRA.  
    - QUIERO UNA BICICLETA PARA MONTAÑA.  
    - COMPARACIÓN ENTRE IPHONE Y SAMSUNG.  

Reglas:  
1. La elección no depende del uso de mayúsculas o minúsculas.  
2. Si la consulta es ambigua, elige 'query'.  
3. Devuelve solo el nombre de la herramienta que usarías, sin texto adicional."""),
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
        if  file is not None:
            return self.process_file(consulta,file)
        elif  "query" in tool_choice:
            return self.general_query(consulta)
        elif  "consulta_producto" in tool_choice:
            return self.product_query(consulta)
        else:
            return "No se pudo determinar la herramienta adecuada para la consulta."
