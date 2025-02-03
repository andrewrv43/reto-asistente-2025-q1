from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename

from datetime import datetime
from Agent import AgenteLangchain
from Graph import GraphWorkflow

app = Flask(__name__)

@app.route('/orchestrator', methods=['POST'])
def orchestrate():

    if 'file' in request.files:
        file = request.files['file']
    else:
        file = None
        
    query = request.form.get('query','NO EXISTE PREGUNTA NI NADA') 
    res1=GraphWorkflow(file=file).invoke({'input':query})
           
    if  res1:
        response = {
            "query": query,
            "response": res1,
            "timestamp":datetime.now().isoformat() 
        }
        return jsonify(response), 200
    return jsonify({"Error": "Envie un query formato correcto"}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
