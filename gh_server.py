from flask import Flask, request, jsonify
# import ghhops_server as hs
import llm_calls
from utils import rag_utils

app = Flask(__name__)

collection, ranker = rag_utils.init_rag()

@app.route('/llm_call', methods=['POST'])
def llm_call():
    data = request.get_json()
    input_string = data.get('input', '')

    router_output = llm_calls.classify_input(input_string)
    if "Refuse to answer" in router_output:
        answer = "Sorry, I can only answer questions about cost estimating and roi."
    else:
        answer = llm_calls.suggest_cost_optimizations(input_string)

    return jsonify({'response': answer})

@app.route('/llm_rag_call', methods=['POST'])
def llm_rag_call():
    data = request.get_json()
    input_string = data.get('input', '')

    # router_output = llm_calls.classify_input(input_string)
    # if "Refuse to answer" in router_output:
    #     answer = "Sorry, I can only answer questions about cost estimating and roi."
    # else:
    answer, sources = rag_utils.rag_call_alt(input_string, collection, ranker)

    return jsonify({'response': answer, 'sources': sources})

if __name__ == '__main__':
    app.run(debug=True)

