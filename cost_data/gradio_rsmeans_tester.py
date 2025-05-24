# Set path to the parent directory
import os
import sys
from pathlib import Path
parent_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(parent_dir))

import gradio as gr
import pandas as pd
from cost_data.rsmeans_utils import load_rsmeans_data, find_by_section_code, find_by_description, get_cost_data, list_sections

# Load data once for the app
rsmeans_df = load_rsmeans_data()

# Gradio functions
def search_by_code(section_code):
    result = find_by_section_code(rsmeans_df, section_code)
    if result.empty:
        return "No results found."
    return result.to_string(index=False)

def search_by_description(description):
    result = find_by_description(rsmeans_df, description)
    if result.empty:
        return "No results found."
    return result.to_string(index=False)

def get_cost(section_code_or_desc):
    result = get_cost_data(rsmeans_df, section_code_or_desc)
    if result.empty:
        return "No results found."
    return result.to_string(index=False)

def show_sections():
    result = list_sections(rsmeans_df)
    # Sort by Masterformat Section Code and Section Name
    result = result.sort_values(['Masterformat Section Code', 'Section Name'])
    # Output as markdown table for Gradio Markdown display
    return result.to_markdown(index=False)

def ask_cost_question(question):
    from llm_calls import route_query_to_function
    tab_name = "Ask Cost Question"
    prompt_display = f"**Tab:** {tab_name}\n\n**Prompt:** {question}\n\n"
    result = route_query_to_function(question)
    return prompt_display + str(result)

with gr.Blocks() as demo:
    gr.Markdown("# RSMeans Utility Tester")
    with gr.Tab("Search by Section Code"):
        code_input = gr.Textbox(label="Masterformat Section Code")
        code_output = gr.Textbox(label="Result")
        code_btn = gr.Button("Search")
        code_btn.click(search_by_code, inputs=code_input, outputs=code_output)
    with gr.Tab("Search by Description"):
        desc_input = gr.Textbox(label="Description")
        desc_output = gr.Textbox(label="Result")
        desc_btn = gr.Button("Search")
        desc_btn.click(search_by_description, inputs=desc_input, outputs=desc_output)
    with gr.Tab("Get Cost Data (Code or Description)"):
        cost_input = gr.Textbox(label="Section Code or Description")
        cost_output = gr.Textbox(label="Result")
        cost_btn = gr.Button("Get Cost Data")
        cost_btn.click(get_cost, inputs=cost_input, outputs=cost_output)
    with gr.Tab("Ask Cost Question"):
        question_input = gr.Textbox(label="Cost Question (natural language)", value="What is the typical cost per sqft for structural steel options?  Let's assume a four-story apartment building.  Make assumptions on the loading.")
        question_output = gr.Markdown(label="Result")
        question_btn = gr.Button("Ask")
        question_btn.click(ask_cost_question, inputs=question_input, outputs=question_output)
    with gr.Tab("List All Sections"):
        gr.Markdown(label="Sections", value=show_sections())

if __name__ == "__main__":
    demo.launch()
