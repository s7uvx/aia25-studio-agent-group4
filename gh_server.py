from flask import Flask, request, jsonify
# from server.config import *
# import server.config as config
# from llm_calls import *
import llm_calls

app = Flask(__name__)


@app.route('/llm_call', methods=['POST'])
def llm_call():
    data = request.get_json()
    input_string = data.get('input', '')

    answer = llm_calls.classify_input(input_string)

    return jsonify({'response': answer})

if __name__ == '__main__':
    app.run(debug=True)

