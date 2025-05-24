# This is a utility module for handling RSMeans csv data.
# It includes functions to read, filter, and process the data for use in cost estimation tasks.

import pandas as pd
import server.config as config
from llm_calls import run_llm_query

# For reference, the following are the columns in the RSMeans DataFrame:
# ['Masterformat Section Code', 'Section Name', 'ID', 'Name', 'Crew', 'Daily Output', 'Labor-Hours','Unit', 'Material', 'Labor', 'Equipment', 'Total', 'Total Incl O&P']
# Generally we use Total Incl O&P for cost estimation

# We want the user to be able to find the cost data by searching for a masterformat section code or description of the work
# We can use LLM calls to find the best match for a given description

RSMEANS_CSV_PATH = "cost_data/rsmeans/combined.csv"

def load_rsmeans_data(csv_path=None):
    """
    Load RSMeans CSV data into a pandas DataFrame.
    If csv_path is None, use the default from config.
    """
    if csv_path is None:
        csv_path = RSMEANS_CSV_PATH
    return pd.read_csv(csv_path)


def find_by_section_code(df, section_code):
    """
    Filter the DataFrame by Masterformat Section Code (exact match).
    """
    return df[df['Masterformat Section Code'] == section_code]


def find_by_description(df, description):
    """
    Use LLM to select the most appropriate Masterformat code from the available list for a given description.
    Returns the matching row(s) from the DataFrame.
    """
    # Get unique list of codes and section names
    unique_sections = df[['Masterformat Section Code', 'Section Name']].drop_duplicates().reset_index(drop=True)
    section_list = unique_sections.apply(lambda row: f"{row['Masterformat Section Code']}: {row['Section Name']}", axis=1).tolist()
    # Build prompt for LLM
    system_prompt = (
        "You are an expert at mapping construction task descriptions to Masterformat section codes. "
        "Given a list of Masterformat sections, you will select the most appropriate code for a user's description. "
        "Return only the section code, nothing else."
    )
    user_input = (
        f"Masterformat sections list:\n{chr(10).join(section_list)}\n"
        f"Description: {description}"
    )
    selected_code = run_llm_query(system_prompt, user_input)
    # Filter DataFrame for the selected code
    match = df[df['Masterformat Section Code'] == selected_code.strip()]
    return match


def get_cost_data(df, section_code_or_desc):
    """
    Retrieve cost data for a given section code or description.
    """
    # Try exact code match first
    match = find_by_section_code(df, section_code_or_desc)
    if not match.empty:
        return match
    # Otherwise, try description match
    return find_by_description(df, section_code_or_desc)


def list_sections(df):
    """
    List all available Masterformat section codes and names.
    """
    return df[['Masterformat Section Code', 'Section Name']].drop_duplicates().reset_index(drop=True)

