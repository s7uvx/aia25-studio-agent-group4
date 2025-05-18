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

