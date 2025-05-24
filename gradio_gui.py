# gradio_gui.py
# requirements: gradio, requests

# === Imports ===
import os
import subprocess
import gradio as gr
import requests
import server.config as config

# === Constants and Config ===
FLASK_URL = "http://127.0.0.1:5000/llm_call"  # Update if Flask runs elsewhere
RAG_OPTIONS = ["LLM only", "LLM + RAG"]
RAG_URLS = {
    "LLM only": FLASK_URL,
    "LLM + RAG": "http://127.0.0.1:5000/llm_rag_call"
}
MODE_OPTIONS = ["local", "openai", "cloudflare"]
MODE_URL = "http://127.0.0.1:5000/set_mode"
sample_questions = [
    "",
    "What is the typical cost per sqft for structural steel options?  Let's assume a four-story apartment building.  Make assumptions on the loading.",
    "How do steel frame structures compare to concrete frame structures, considering cost and durability?",
    "What are the ROI advantages of using precast concrete in construction projects?",
    "Can you provide a cost estimate for a 10,000 sq ft commercial building?",
    "What are the key factors affecting the cost of a residential building?",
]

# === Global State ===
flask_process = None

# === Utility Functions ===
def query_llm(user_input):
    try:
        response = requests.post(FLASK_URL, json={"input": user_input})
        if response.status_code == 200:
            return response.json().get("response", "No response from server.")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

def query_llm_with_rag(user_input, rag_mode):
    output_header_markdown = f"### Input: {user_input}\n\n"

    url = RAG_URLS.get(rag_mode, FLASK_URL)
    try:
        response = requests.post(url, json={"input": user_input})
        if response.status_code == 200:
            data = response.json()
            if "sources" in data:
                return (
                    output_header_markdown
                    + f"{data.get('response', 'No response from server.')}\n\n**Sources:**\n{data['sources']}"
                )
            else:
                return output_header_markdown + data.get("response", "No response from server.")
        else:
            return output_header_markdown + f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return output_header_markdown + f"Exception: {str(e)}"

def run_flask_server():
    global flask_process
    if flask_process is None or flask_process.poll() is not None:
        # Start Flask server as a subprocess
        flask_process = subprocess.Popen(
            ["python", "gh_server.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        return "Flask server started."
    else:
        return "Flask server is already running."

def stop_flask_server():
    global flask_process
    if flask_process is not None and flask_process.poll() is None:
        flask_process.terminate()
        flask_process = None
        return "Flask server stopped."
    else:
        return "Flask server is not running."

def set_mode_on_server(selected_mode):
    try:
        response = requests.post(MODE_URL, json={"mode": selected_mode})
        if response.status_code == 200:
            return f"Mode set to: {selected_mode}"
        else:
            return f"Error setting mode: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Exception: {str(e)}"

def update_placeholder(selected):
    return gr.update(value=selected)

def poll_flask_status(max_retries=20, delay=0.5):
    """
    Poll the Flask /status endpoint until it returns 200 or timeout.
    Returns a status string for the UI.
    """
    import time
    url = "http://127.0.0.1:5000/status"
    for _ in range(max_retries):
        try:
            resp = requests.get(url, timeout=1)
            if resp.status_code == 200:
                return "Flask server is running."
        except Exception:
            pass
        time.sleep(delay)
    return "Flask server did not respond in time. Check logs."

def start_flask_and_wait():
    status = run_flask_server()
    if "started" in status:
        # Only poll if we just started it
        status = poll_flask_status()
    return status

# === Gradio UI Definition ===
def build_gradio_app():
    with gr.Blocks() as demo:
        gr.Markdown("# Flask Server Control Panel")
        with gr.Row():
            start_flask_btn = gr.Button("Start Flask Server")
            stop_flask_btn = gr.Button("Stop Flask Server")
            flask_status = gr.Textbox(label="Flask Server Status", lines=1)
        with gr.Row():
            gr.Markdown("### Note: The Flask server must be running to get a response.")

        gr.Markdown("## LLM Mode Selection")
        with gr.Row():
            mode_radio = gr.Radio(
                choices=MODE_OPTIONS,
                value="cloudflare",
                label="Select LLM Mode",
                interactive=True
            )
            mode_status = gr.Textbox(label="Current Mode", lines=1)

        mode_radio.change(
            fn=set_mode_on_server,
            inputs=mode_radio,
            outputs=mode_status
        )

        gr.Markdown("## LLM Call Type")
        with gr.Row():
            rag_radio = gr.Radio(
                choices=RAG_OPTIONS,
                value="LLM only",
                label="Choose LLM Call Type",
                interactive=True
            )

        gr.Markdown("# LLM Output Viewer\nEnter your question below:")

        with gr.Row():
            sample_dropdown = gr.Dropdown(
                choices=sample_questions,
                label="Or select a sample question",
                interactive=True,
                value=None,
                allow_custom_value=False,
                info="Pick a sample or type your own below."
            )
        with gr.Row():
            user_input = gr.Textbox(
                label="Your Question",
                lines=2,
                value=sample_dropdown.value
            )

        sample_dropdown.change(
            fn=update_placeholder,
            inputs=sample_dropdown,
            outputs=user_input,
        )

        submit_btn = gr.Button("Submit")
        with gr.Group():
            gr.Markdown("## LLM Output:")
            output = gr.Markdown(label="LLM Output")

        def show_processing(*args):
            return "_Processing..._"

        submit_btn.click(fn=show_processing, inputs=[], outputs=output, queue=False)
        submit_btn.click(fn=query_llm_with_rag, inputs=[user_input, rag_radio], outputs=output, queue=True)
        start_flask_btn.click(fn=start_flask_and_wait, outputs=flask_status)
        stop_flask_btn.click(fn=stop_flask_server, outputs=flask_status)

    return demo

print("\n" * 10)
print("Running gradio GUI...")
demo = build_gradio_app()
demo.launch(inbrowser=True)