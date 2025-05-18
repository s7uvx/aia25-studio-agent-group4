import server.config as config

# Master Routing Function

def route_query_to_function(message: str) -> str:
    """
    Classify the user message into one of the five core categories and route it to the appropriate response function.
    """
    classification = classify_question_type(message)

    if classification == "Cost Benchmark":
        return get_cost_benchmarks(message)
    elif classification == "ROI Analysis":
        return analyze_roi_sensitivity(message)
    elif classification == "Design-Cost Comparison":
        return analyze_cost_tradeoffs(message)
    elif classification == "Value Engineering":
        return suggest_cost_optimizations(message)
    elif classification == "Project Data Lookup":
        return analyze_project_data_inputs(message)
    else:
        return "I'm sorry, I cannot process this request. Please ask a question related to cost, ROI, or project data."

# Classification Function

def classify_question_type(message: str) -> str:
    """
    Returns the category of the query: Cost Benchmark, ROI Analysis, Design-Cost Comparison, Value Engineering, or Project Data Lookup.
    """
    system_prompt = (
        "You are a query classification agent for a building project assistant.\n"
        "Classify the user's query into one of the following categories:\n"
        "1. Cost Benchmark\n"
        "2. ROI Analysis\n"
        "3. Design-Cost Comparison\n"
        "4. Value Engineering\n"
        "5. Project Data Lookup\n"
        "Return only the category name.\n\n"
        "Examples:\n"
        "Query: What is the typical cost per sqft for concrete in NYC?\nOutput: Cost Benchmark\n"
        "Query: How much would I save by replacing glass with stone on the facade?\nOutput: Design-Cost Comparison\n"
        "Query: If rents fall by 10%, what happens to ROI?\nOutput: ROI Analysis\n"
        "Query: How can I lower construction costs without reducing quality?\nOutput: Value Engineering\n"
        "Query: How many units does my current project support and what’s the total cost of concrete?\nOutput: Project Data Lookup"
    )

   