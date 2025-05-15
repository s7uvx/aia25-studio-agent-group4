# from server.config import * #update to comply with PEP8
# from llm_calls import * #update to comply with PEP8
import server.config as config
import llm_calls
from utils import rag_utils
import json

user_message = "How do architects balance form and function?"

### EXAMPLE 1: Router ###
# Classify the user message to see if we should answer or not
router_output = llm_calls.classify_input(user_message)
if "Refuse to answer" in router_output:
    llm_answer = "Sorry, I can only answer questions about architecture."

else:
    print(router_output)
    ### EXAMPLE 2: Simple call ###
    # simple call to LLM, try different sys prompt flavours
    brainstorm = llm_calls.generate_concept(user_message)
    print(brainstorm)

    ### EXAMPLE 4: Structured Output ###
    # extract the architecture attributes from the user
    # parse a structured output with regex
    attributes = llm_calls.extract_attributes(brainstorm)
    print(attributes)

    attributes = attributes.strip()
    attributes = json.loads(attributes)
    shape, theme, materials = (attributes[k] for k in ("shape", "theme", "materials"))

    ### EXAMPLE 3: Chaining ###
    # brutalist_question = llm_calls.create_question(theme)
    # print(brutalist_question)
    # call llm with the output of a previous call
    # material_answer = llm_calls.assess_material_impact(materials)
    # print(material_answer)

    materials_question = llm_calls.suggest_cost_optimizations(shape)

    ### EXAMPLE 5: RAG ####
    # Get a response based on the knowledge found
    # rag_result= rag_call(brutalist_question, embeddings = "knowledge/brutalism_embeddings.json", n_results = 10)
    # print(rag_result)
    # rag_result = rag_call(
    #     materials_question, 
    #     n_results=15,
    #     max_context_length=3000  # Adjust based on your model's context window
    # )
    collection, ranker = rag_utils.init_rag()
    rag_result = rag_utils.rag_call_alt(
        materials_question,
        collection=collection,
        ranker=ranker,
        n_results=15,
        max_context_length=3000  # Adjust based on your model's context window
    )
    print(rag_result)