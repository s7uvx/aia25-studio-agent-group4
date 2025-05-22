#requirements: gradio, requests

import gradio as gr
import requests

FLASK_URL = "http://127.0.0.1:5000/llm_call"  # Update if Flask runs elsewhere

# Function to call Flask server
def query_llm(user_input):
    try:
        response = requests.post(FLASK_URL, json={"input": user_input})
        if response.status_code == 200:
            return response.json().get("response", "No response from server.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("# LLM Output Viewer\nEnter your question below:")
    with gr.Row():
        user_input = gr.Textbox(label="Your Question", lines=2)
    output = gr.Textbox(label="LLM Output", lines=8)
    submit_btn = gr.Button("Submit")

    submit_btn.click(fn=query_llm, inputs=user_input, outputs=output)

# run = False
if run:
    print("Running in local mode...")
    demo.launch(inbrowser=True)
    
    # Print the URL for the user
    print(f"Open the following URL in your browser: {demo.url}")