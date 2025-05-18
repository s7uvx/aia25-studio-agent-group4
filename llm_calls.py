import server.config as config  

# Joao Prompts:

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
        ],
        temperature=0.0,  # Lower temperature for deterministic output
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
        ],
        temperature=0.8,  # Higher temperature for more creative output
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
        ],
        temperature=0.0,  # Lower temperature for more deterministic output
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
        ],
        temperature=0.3,  # Adjust temperature for more or less creative responses
    )
    return response.choices[0].message.content.strip()

# Group 4 Prompts:

# Cost Estimation & ROI Analysis Functions
def analyze_cost_tradeoffs(query: str) -> str:
    """
    Analyze cost trade-offs based on the user's query.
    E.g., comparing two design options or the impact of a design change on cost/ROI.
    """
    system_prompt = (
        "You are an expert architectural cost consultant.\n"
        "# Task:\n"
        "Given a scenario or query, analyze and compare the cost trade-offs between the design options or changes described. Consider both initial construction costs and long-term financial impacts (such as ROI, maintenance, or operational costs) if relevant.\n"
        "# Instructions:\n"
        "- Break down each option or change, explaining how it affects construction cost (e.g., cost per area, material and/or labor differences) and potential changes to the project's value.\n"
        "- Highlight the pros and cons of each option: which is more expensive upfront, which may save money over time, and any relevant risks or benefits.\n"
        "- Use any specific numbers given in the query; if none are given, provide reasoned estimates or qualitative comparisons.\n"
        "- Clearly state any assumptions for your estimates (e.g., unit costs, rates, location, or market conditions).\n"
        "- Structure your answer logically (e.g., Option A vs Option B, or Before vs After change), and quantify differences where possible.\n"
        "- Conclude with a recommendation or summary of which option is cost-favorable and why, if asked for advice.\n"
        "- Always mention that actual costs can vary by project and location, and the comparison is based on typical scenarios.\n"
        "# Example:\n"
        "Query: Should we use steel or timber for the main structure?\n"
        "Output: Steel framing typically costs 10-20% more than timber for similar spans, but offers greater durability and fire resistance. Timber is less expensive upfront and can be installed faster, reducing labor costs. However, steel may have lower maintenance costs over the building's life. In most urban markets, timber is more cost-effective for low-rise buildings, while steel is preferred for high-rise or long-span structures. Actual costs depend on local material prices and labor rates." # TODO fact-check this example
    )
    # (Optionally, I think we might be able to retrieve relevant data here via rag_utils if needed to inform the comparison.)
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.5,  # Adjust temperature for more or less creative responses
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
        "Given a scenario or query, explain how the project's return on investment (ROI) or other financial metrics would change if key variables (such as construction cost, rent, interest rate, or occupancy) increase or decrease.\n"
        "# Instructions:\n"
        "- Identify the main variables mentioned in the query that could impact ROI.\n"
        "- For each variable, describe how changes (e.g., +10% cost, -10% revenue) would affect ROI or payback period.\n"
        "- Use approximate calculations if possible (e.g., \"ROI drops from 15% to ~12% if cost rises 10%\"), or provide qualitative analysis if no numbers are given.\n"
        "- Clearly state any assumptions you make (such as base ROI, cost, or revenue figures).\n"
        "- Highlight which variables have the greatest impact on ROI, if relevant.\n"
        "- End with a note that these are scenario estimates for planning, not exact predictions, and that actual results may vary by project and market.\n"
        "# Example:\n"
        "Query: What happens to ROI if construction costs rise by 10% and rents fall by 5%?\n"
        "Output: Assuming a base ROI of 15%, a 10% increase in construction costs would reduce ROI to approximately 13%. If rents also fall by 5%, ROI could drop further to around 11%. ROI is generally more sensitive to changes in revenue than to moderate cost overruns. Actual impacts depend on the project's financial structure and local market conditions." # TODO fact-check this example
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.5,  # Adjust temperature for more or less creative responses
    )
    return response.choices[0].message.content.strip()

def assess_material_impact(query: str) -> str:
    """
    Evaluate how different material or structural choices impact cost (and possibly ROI or schedule).
    """
    system_prompt = (
        "You are a building materials cost expert, specializing in evaluating the impact of material and structural choices on project cost, ROI, and schedule.\n"
        "# Task:\n"
        "Given a query comparing materials or systems, analyze and compare their effects on initial construction cost, long-term costs (maintenance, durability), schedule, and ROI if relevant.\n"
        "# Instructions:\n"
        "- For each material or system mentioned, discuss:\n"
        "    - Initial cost differences (e.g., per area, percentage difference, or qualitative comparison if no data).\n"
        "    - Long-term implications: for example, durability, maintenance, insurance, resale value, and sustainability if relevant.\n"
        "    - Effects on construction schedule (e.g., faster/slower installation).\n"
        "    - Any impact on ROI or lifecycle cost, if applicable.\n"
        "- Clearly state any assumptions or typical benchmarks you use.\n"
        "- Note context factors: local availability, labor skill, incentives, or code requirements that might influence the choice.\n"
        "- Structure your answer by material/system, then provide a concluding comparison or recommendation.\n"
        "- Always add a caveat that market prices and impacts vary by region and project, so the comparison is general.\n"
        "# Example:\n"
        "Query: Compare cross-laminated timber (CLT) and reinforced concrete for a mid-rise building.\n"
        "Output: CLT typically costs 5-15% more per square foot than reinforced concrete in most markets, but can reduce construction time by up to 30% due to prefabrication. CLT offers sustainability benefits and lower embodied carbon, but may require additional fireproofing and has higher insurance costs in some regions. Concrete is more durable and widely available, with lower long-term maintenance. The best choice depends on project priorities, local expertise, and regulatory context. Actual costs and benefits will vary by location." # TODO fact-check this example
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.3,  # Adjust temperature for more or less creative responses
    )
    return response.choices[0].message.content.strip()

def compare_typologies(query: str) -> str:
    """
    Compare costs and ROI between different project typologies or design approaches given in the query.
    """
    system_prompt = (
        "You are an expert architectural cost estimator, skilled in comparing different project typologies and design approaches.\n"
        "# Task:\n"
        "Given a query comparing project types or design options, analyze and contrast their typical costs and ROI potential.\n"
        "# Instructions:\n"
        "- For each typology or scenario mentioned:\n"
        "    - Provide known cost benchmarks (e.g., cost per square foot, total cost range) if available.\n"
        "    - Discuss ROI or financial viability (e.g., rental rates, demand, payback period) if relevant.\n"
        "    - Identify key drivers for cost and ROI differences: structural needs (high-rise vs low-rise), code requirements, level of finish, location, etc.\n"
        "- Use a clear, side-by-side format (bullet points or separate paragraphs) to contrast the options.\n"
        "- Clearly state any assumptions or typical market conditions you are using.\n"
        "- End with a summary of which typology might be more cost-effective or profitable, or note that the answer depends on specific project context.\n"
        "- Always add a disclaimer that actual costs and ROI can vary significantly by region, market, and project specifics.\n"
        "# Example:\n"
        "Query: Compare the cost and ROI of a mid-rise apartment building vs. a low-rise townhouse development.\n"
        "Output:\n"
        "- Mid-rise Apartment:\n"
        "  - Typical construction cost: $250–$350/sqft (urban US markets)\n" # TODO fact-check this example
        "  - Higher density, often higher ROI due to more units per land area\n"
        "  - Requires elevators, more complex structure, higher code requirements\n"
        "- Low-rise Townhouse:\n"
        "  - Typical construction cost: $180–$250/sqft\n" # TODO fact-check this example
        "  - Lower density, but may have faster sales and lower construction complexity\n"
        "  - Simpler code requirements, easier phasing\n"
        "Summary: Mid-rise apartments can offer higher ROI in dense markets, but townhouses may be more cost-effective and less risky in suburban contexts. Actual costs and returns depend on location, design, and market demand."
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.5,  # Adjust temperature for more or less creative responses
    )
    return response.choices[0].message.content.strip()

def get_cost_benchmarks(query: str) -> str:
    """
    Provide cost benchmarks or typical values relevant to the user’s query.
    This might involve retrieving data from a knowledge base (RAG) or using known industry standards.
    """
    # Potential integration point: Use rag_utils to fetch relevant data before constructing the prompt.
    # e.g., context_data = rag_call(query, n_results=5) and then include context_data in the system_prompt or user_prompt.
    system_prompt = (
        "You are a knowledgeable assistant for architecture and real estate costs, tasked with providing reliable cost and ROI benchmarks.\n"
        "# Task:\n"
        "Given the user's query, retrieve or recall typical cost figures or ROI benchmarks (e.g., cost per sqft, average unit prices, typical yields) that apply.\n"
        "# Instructions:\n"
        "- Present all figures with proper units and clear context (e.g., location, building type, year, or source if relevant).\n"
        "- If multiple benchmarks are relevant, list them clearly using bullet points or concise sentences.\n"
        "- If the query specifies a location, building type, or time period, tailor your answer to that context.\n"
        "- Use knowledge base data if available; otherwise, provide educated estimates and clearly note when values are general or approximate.\n"
        "- If you are unsure or data is unavailable, give a reasonable range or state that costs can vary widely.\n"
        "- Keep the answer concise, factual, and easy to scan.\n"
        "- Optionally, add a brief note on factors that affect these benchmarks (such as market conditions, inflation, or project complexity).\n"
        "- Always include a disclaimer that these are standard values and actual project costs can differ significantly based on specific circumstances.\n"
        "# Example:\n"
        "Query: What is the typical construction cost per square foot for office buildings in London?\n"
        "Output:\n"
        "- Typical construction cost for office buildings in central London: £350–£600/sqft (2023, source: industry reports)\n" # TODO fact-check this example
        "- Costs vary based on specification, location, and market conditions.\n"
        "Note: These are standard benchmarks; actual project costs may differ."
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.0,  # Lower temperature for more deterministic output
    )
    return response.choices[0].message.content.strip()

def suggest_cost_optimizations(query: str) -> str:
    """
    Suggest ways to optimize or reduce costs (value engineering) based on the user’s situation.
    """
    system_prompt = (
        "You are an architectural value-engineering assistant, expert in cost optimization.\n"
        "# Task:\n"
        "The user wants to reduce costs or improve ROI through design adjustments. Provide practical suggestions.\n"
        "- Identify costly aspects implied or stated in the query (e.g., expensive materials, complex geometry, high parking ratio).\n"
        "- Suggest alternative solutions or optimizations for each (cheaper material alternatives, simplifying design, adjusting scope, etc.).\n"
        "# Guidelines:\n"
        "1. Format the response as a set of suggestions (bullet points or numbered) so it's easy to scan.\n"
        "2. For each suggestion, include a brief rationale and potential cost impact (e.g., \"Using XYZ could save ~5% of total cost\").\n"
        "3. Maintain a constructive tone – focus on keeping essential design intent while cutting cost.\n"
        "4. If the user provided a target (like cut 15% cost), address whether each suggestion gets part of the way to that goal.\n"
        "5. End with a reminder that these are general suggestions and actual savings should be validated (since exact savings may vary)."
    )
    system_prompt = (
        "You are an architectural value-engineering assistant, expert in cost optimization for building projects.\n"
        "# Task:\n"
        "Given the user's query, suggest practical ways to reduce costs or improve ROI through design, material, or process adjustments, while maintaining essential project goals.\n"
        "# Instructions:\n"
        "- Identify costly aspects or inefficiencies mentioned or implied in the query (e.g., premium materials, complex geometry, high parking ratio, over-specified systems).\n"
        "- For each identified aspect or inefficiency, suggest solutions or optimizations (e.g., substitute materials, simplify design, adjust scope, modularize construction, optimize building systems).\n"
        "- For each suggestion, briefly explain the rationale and estimate potential cost impact (e.g., \"Switching to X could save ~10% on facade costs\").\n"
        "- If the user provides a savings target (e.g., \"reduce cost by 15%\"), address whether each suggestion contributes toward that goal.\n"
        "- Use a clear, easy-to-scan format (bullet points or numbered list).\n"
        "- Maintain a constructive, solution-oriented tone, focusing on preserving design intent where possible.\n"
        "- End with a reminder that these are general suggestions and actual savings should be validated for the specific project.\n"
        "# Example:\n"
        "Query: How can we reduce costs for a mid-rise apartment building with a glass curtain wall and underground parking?\n"
        "Output:\n"
        "1. Replace the glass curtain wall with a mix of glass and insulated panels—can reduce facade costs by 10–20% while maintaining aesthetics.\n" # TODO fact-check this example
        "2. Reduce the amount of underground parking or switch to surface parking if feasible—underground parking is often 3–4 times more expensive per space.\n" # TODO fact-check this example
        "3. Simplify building geometry—fewer facade corners and unique shapes lower construction complexity and cost.\n"
        "4. Standardize unit layouts and finishes—bulk purchasing and repetitive construction can yield 5–10% savings.\n"
        "Note: These are general strategies; actual savings depend on project specifics and should be confirmed with your design and construction team." # TODO fact-check this example
    )
    response = config.client.chat.completions.create(
        model=config.completion_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ],
        temperature=0.5,  # Adjust temperature for more or less creative responses
    )
    return response.choices[0].message.content.strip()
