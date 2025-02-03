import requests
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph
from typing import Dict, TypedDict
from langchain_core.output_parsers import StrOutputParser
from Agent import AgenteLangchain

class GraphState(TypedDict):
    input: str
    is_toxic: bool
    final_output: str

class GraphWorkflow():
    def __init__(self,file=None):
        self.llm = ChatOllama(model="deepseek-r1:8b", base_url="http://host.docker.internal:11434")
        self.workflow = StateGraph(GraphState)
        self._setup_workflow()
        self.file=file

    def call_model(self, system: str, user_input: str) -> str:
        output_parser = StrOutputParser()
        prompt = ChatPromptTemplate.from_messages([
            ("system", system),
            ("user", "{user_input}")
        ])
        chain = prompt | self.llm | output_parser
        return chain.invoke({"user_input": user_input}).strip()

    def toxicity_check(self, state: GraphState) -> Dict:
        query = state["input"]
        system_prompt = (
            "Eres un modelo que verifica si existe toxicidad en un mensaje, es decir, malas palabras, "
            "malas intenciones o desagrado y desprestigio. Si el mensaje contiene alguno de estos elementos, "
            "ten especial atencion con busquedas inapropiadas o que pueden resultar peligrosas como armas drogas y más"
            "responde con 'SI'; de lo contrario, responde 'NO'. No entregues ningún contexto extra, únicamente 'SI' o 'NO'."
        )
        response = self.call_model(system_prompt, query).split('</think>')[1]
        print(response)
        print("response", response)
        if "si" in  response.lower():
            return {"is_toxic": True, "final_output": "Consulta rechazada: Contiene lenguaje inapropiado."}
        else:
            return {"is_toxic": False}
    
    def functionsAgentsNode(self, state: GraphState) -> Dict:
        query = state["input"]
        res=AgenteLangchain().ejecutar_agente(query,self.file)
        print(res)
        return {"final_output": res}
        
    def toxicity_condition(self, state):
        if state.get("is_toxic"):
            return "end"
        else:
            return "callFunctions"
    
    def end_node(self, state: GraphState) -> Dict:
        if state.get("is_toxic") is False:
            return {"final_output": state["final_output"]}
        else:
            return {"final_output": f"Error en la consulta verifica tu prompt\n Recuerda ser cordial y no buscar temas indevidos: {state['input']}"}

    def _setup_workflow(self):
        self.workflow.add_node("toxicity_check", self.toxicity_check)
        self.workflow.add_node("callFunctions", self.functionsAgentsNode)
        self.workflow.add_node("end", self.end_node)
        
        self.workflow.add_conditional_edges("toxicity_check", self.toxicity_condition)
        self.workflow.add_edge("callFunctions", "end")
        self.workflow.set_entry_point("toxicity_check")
        self.app = self.workflow.compile()

    def invoke(self, query: Dict) -> str:
        response = self.app.invoke(query)
        return response.get("final_output", "Error: No se generó respuesta.")
