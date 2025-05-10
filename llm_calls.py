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
