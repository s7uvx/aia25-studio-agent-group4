import server.config as config  

# Routing & Filtering Functions
def classify_input(message: str) -> str:
    """
    Classify if the user message is related to architecture/buildings or not.
    Returns "Related" for architecture-related queries, otherwise "Refuse to answer".
    """
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": 
                "Your task is to classify if the user message is related to buildings and architecture or not. "
                "Output only a single word: If related, output 'Related'; if not, output 'Refuse to answer'."},
            {"role": "user", "content": message}
        ]
    )
    return response.choices[0].message.content.strip()

# Design Ideation & Concept Functions
def generate_concept(initial_info: str) -> str:
    """
    Generate a short, imaginative concept statement for a building design based on initial info.
    Useful for early-stage creative brainstorming.
    """
    system_prompt = (
        "You are a visionary designer at a leading architecture firm.\n"
        "Your task is to craft a short, poetic and imaginative concept for a building design, based on the given information.\n"
        "- Weave the provided details into a bold and evocative idea, like the opening lines of a story.\n"
        "- Keep it one paragraph, focusing on mood and atmosphere rather than technical details.\n"
        "- Avoid generic descriptions; use vivid imagery and emotional resonance."
    )
    user_prompt = f"What is the concept for this building?\nInitial information: {initial_info}"
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def extract_attributes(description: str) -> str:
    """
    Extract key design attributes (shape, theme, materials) from a text description.
    Returns a JSON string with fields "shape", "theme", "materials".
    """
    system_prompt = (
        "You are a keyword extraction assistant.\n"
        "# Instructions:\n"
        "Extract relevant keywords from the given building description, categorized into three fields: shape, theme, materials.\n"
        "Provide the output as a JSON object with exactly those keys.\n"
        "# Rules:\n"
        "- If a category has no relevant info, use \"None\" as the value.\n"
        "- Separate multiple keywords with commas in a single string.\n"
        "- Output JSON only, no explanation or extra text."
    )
    user_prompt = f"GIVEN DESCRIPTION:\n{description}"
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def create_question(theme: str) -> str:
    """
    Create an open-ended question for further exploration, based on a given theme (e.g., a design theme).
    This can be used to prompt the knowledge base or user for more input.
    """
    system_prompt = (
        "You are a thoughtful research assistant specializing in architecture.\n"
        "Your task is to formulate an open-ended question related to the theme provided, inviting deeper exploration.\n"
        "- The question should connect to architectural examples or theory (e.g., notable projects, historical context) related to the theme.\n"
        "- Keep it open-ended and intellectually curious, so it could be answered with detailed insights.\n"
        "- Do not include any extra text, just the question itself."
    )
    user_prompt = theme  # The theme or topic from which to derive a question
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Cost Estimation & ROI Analysis Functions
def analyze_cost_tradeoffs(query: str) -> str:
    """
    Analyze cost trade-offs based on the user's query.
    E.g., comparing two design options or the impact of a design change on cost/ROI.
    """
    system_prompt = (
        "You are an experienced architectural cost consultant tasked with analyzing cost trade-offs in design options.\n"
        "# Task:\n"
        "Consider the user's scenario and compare the options or changes mentioned in terms of cost (and ROI if relevant).\n"
        "- Break down how each option would affect construction cost (e.g., cost per sqft, material/labor differences) and potential returns.\n"
        "- Highlight the pros and cons: which option is more expensive upfront, which might save money long-term, etc.\n"
        "# Guidelines:\n"
        "1. Use any specific numbers given in the query; if none are given, provide reasoned estimates or qualitative comparisons.\n"
        "2. Clearly state assumptions for any estimates (e.g., unit costs, rates) so the reasoning is transparent.\n"
        "3. Structure the answer logically (option A vs option B, or Before vs After change) and possibly quantify the difference.\n"
        "4. Conclude with a recommendation or summary of which option is cost-favorable and why, if asked for advice.\n"
        "5. Important: mention that actual costs can vary, and the comparison is based on typical scenarios."
    )
    # (Optionally, I think we might be able to retrieve relevant data here via rag_utils if needed to inform the comparison.)
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content.strip()

def analyze_roi_sensitivity(query: str) -> str:
    """
    Analyze ROI sensitivity given a scenario in the user's query.
    Describes how changes in inputs (cost, revenue, etc.) affect the return on investment.
    """
    system_prompt = (
        "You are a financial analyst for architecture projects, focusing on ROI sensitivity.\n"
        "# Task:\n"
        "Explain how the project's ROI or other financial metrics change when certain variables change, based on the query.\n"
        "- Identify the key variables mentioned (e.g., construction cost, rent income, interest rate) and describe their impact on ROI.\n"
        "- If multiple scenarios (e.g., +10% cost, -10% revenue) are implied, discuss each scenario's outcome on ROI.\n"
        "# Guidelines:\n"
        "1. Begin by stating the base assumption (if any) for ROI, then show how it shifts under the new conditions.\n"
        "2. Use approximate calculations if possible (e.g., \"ROI drops from 15% to ~12% if cost rises 10%\") to give a concrete sense.\n"
        "3. If no numbers are given, speak qualitatively about high-level impact (e.g., \"higher interest rates reduce ROI by increasing financing costs\").\n"
        "4. Highlight which factor the ROI is most sensitive to, if applicable (e.g., \"ROI is more sensitive to rent changes than to minor cost overruns\").\n"
        "5. End with a note that these are estimates for scenario planning, not exact predictions."
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content.strip()

def assess_material_impact(query: str) -> str:
    """
    Evaluate how different material or structural choices impact cost (and possibly ROI or schedule).
    """
    system_prompt = (
        "You are a building materials cost expert, helping assess the cost impact of material choices.\n"
        "# Task:\n"
        "Compare the materials or systems mentioned in the query in terms of cost and any other effects (maintenance, speed, ROI).\n"
        "- Discuss initial cost differences (e.g., material A vs B per sqft or overall percentage difference).\n"
        "- Mention any relevant long-term implications: durability, maintenance costs, insurance, resale value, etc., if they affect ROI.\n"
        "# Guidelines:\n"
        "1. Use known benchmarks if available (e.g., \"steel framing is ~15% more expensive than wood for the structure\") or qualitative terms if exact data isn't provided.\n"
        "2. Structure the answer by material/system: address each option in turn, then a concluding comparison.\n"
        "3. Note any context factors: availability of material locally, skill/labor differences, sustainability incentives, etc., that might sway the choice.\n"
        "4. Conclude with which material is more cost-effective or how the choice should be made (\"depends on priorities\", etc.).\n"
        "5. Add a caveat that market prices fluctuate and region affects cost – so the comparison is general."
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
    )
    return response.choices[0].message.content.strip()
