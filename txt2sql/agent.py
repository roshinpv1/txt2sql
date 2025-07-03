
import sys
import os
from flow import create_text_to_sql_flow
from populate_db import populate_database, DB_FILE
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
import subprocess
from google.adk.tools import FunctionTool
import sys
import os


def text_to_sql(query):
    db_path=DB_FILE
    max_debug_retries=3
    if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
        print(f"Database at {db_path} missing or empty. Populating...")
        populate_database(db_path)

    shared = {
        "db_path": db_path,
        "natural_query": query,
        "max_debug_attempts": max_debug_retries,
        "debug_attempts": 0,
        "final_result": None,
        "final_error": None
    }

    print(f"\n=== Starting Text-to-SQL Workflow ===")
    print(f"Query: '{natural_query}'")
    print(f"Database: {db_path}")
    print(f"Max Debug Retries on SQL Error: {max_debug_retries}")
    print("=" * 45)

    flow = create_text_to_sql_flow()
    flow.run(shared) # Let errors inside the loop be handled by the flow logic

    # Check final state based on shared data
    if shared.get("final_error"):
            print("\n=== Workflow Completed with Error ===")
            print(f"Error: {shared['final_error']}")
    elif shared.get("final_result") is not None:
            print("\n=== Workflow Completed Successfully ===")
            # Result already printed by ExecuteSQL node
    else:
            # Should not happen if flow logic is correct and covers all end states
            print("\n=== Workflow Completed (Unknown State) ===")

    print("=" * 36)
    return shared.get("final_result")

sqlagent = Agent(
    model=LiteLlm(model="gpt-3.5-turbo", base_url="http://localhost:1234/v1", api_key="sdsd", provider="openai"),
    name='txt2sql',
    instruction = """all the basic queries need to be handled separately and SQL related queries need to be processed by tool `text_to_sql`cas a natural language to SQl convertor you are responsible to identify the natural language query and convert it to a valid SQL query""",
    description = """all the basic queries need to be handled separately and SQL related queries need to be processed by tool `text_to_sql`cas a natural language to SQl convertor you are responsible to identify the natural language query and convert it to a valid SQL query""",
    tools=[text_to_sql]
)

root_agent = Agent(
    model=LiteLlm(model="gpt-3.5-turbo", base_url="http://localhost:1234/v1", api_key="sdsd", provider="openai"),
    name='txt2sql',
    instruction = """As a natural language to SQL agent I want to processing incoming valid natuaral language text which is eligible to be converted  shouldb e passed by tool sqlagent""",
    description = """As a natural language to SQL agent I want to processing incoming valid natuaral language text which is eligible to be converted  shouldb e passed by tool sqlagent""",
    sub_agents=[sqlagent]
)

