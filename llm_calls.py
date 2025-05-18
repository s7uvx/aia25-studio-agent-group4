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
