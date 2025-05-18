def analyze_cost_tradeoffs(query: str) -> str:
    prompt = """
    You are a cost consultant.
    Analyze trade-offs between different materials or design choices mentioned.
    Compare based on construction cost, longevity, and typical ROI impacts.

    Example:
    Query: Should we use cross-laminated timber or reinforced concrete for the structure?
    Output: CLT costs $320/sqft vs concrete at $280/sqft. CLT may reduce construction time by 15%, but has higher insurance costs. Concrete offers better durability.
    """
    return run_llm_query(prompt, query)

def analyze_roi_sensitivity(query: str) -> str:
    prompt = """
    You are a financial analyst.
    Evaluate how changes in construction cost, rent, or occupancy affect ROI.
    Provide scenario-based sensitivity analysis.

    Example:
    Query: What happens if construction costs go up by 10%?
    Output: ROI decreases from 12% to ~10.5%, assuming stable rents and no other changes.
    """
    return run_llm_query(prompt, query)

def get_cost_benchmarks(query: str) -> str:
    prompt = """
    You are a cost benchmark assistant.
    Provide standard cost per sqft values or material unit prices from industry data.
    Tailor output to context (location, building type) if given.

    Example:
    Query: What is the average cost per sqft for office buildings in London?
    Output: £400–£550/sqft, depending on spec and location (2023 estimate).
    """
    return run_llm_query(prompt, query)

def suggest_cost_optimizations(query: str) -> str:
    prompt = """
    You are a value engineering assistant.
    Suggest practical ways to reduce project costs while maintaining design intent.
    Focus on materials, layout, structural systems.

    Example:
    Query: How can we reduce cost by 10% without changing the layout?
    Output:
    1. Replace curtain wall with punched window system (~8% savings).
    2. Use modular bathrooms (~2–3% savings).
    """
    return run_llm_query(prompt, query)

def analyze_project_data_inputs(query: str) -> str:
    prompt = """
    You are a project insight analyst.
    Use IFC/CSV and data encoding outputs to extract cost-related insights based on available quantities.
    Return findings like concrete volume cost, or unit type ratios.

    Example:
    Query: What is the total concrete cost for this project?
    Output: Based on 500 m³ at $120/m³, total cost = $60,000.
    """
    return run_llm_query(prompt, query)

def run_llm_query(system_prompt: str, user_input: str) -> str:
    import server.config as config
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ],
        temperature=0.3
    )
    return response.choices[0].message.content.strip()
