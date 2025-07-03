import sqlite3
import time
import yaml # Import yaml here as nodes use it
from pocketflow import Node
from utils.call_llm import call_llm
from db_adapter import DatabaseAdapter

class GetSchema(Node):
    def prep(self, shared):
        return shared["db_adapter"]

    def exec(self, db_adapter):
        return db_adapter.get_schema()

    def post(self, shared, prep_res, exec_res):
        shared["schema"] = exec_res
        print("\n===== DB SCHEMA =====\n")
        print(exec_res)
        print("\n=====================\n")

class GenerateSQL(Node):
    def prep(self, shared):
        return shared["natural_query"], shared["schema"], shared["db_adapter"].db_type

    def exec(self, prep_res):
        natural_query, schema, db_type = prep_res
        
        # Check if this is a schema description request
        if any(keyword in natural_query.lower() for keyword in ['describe', 'show', 'what is', 'explain']):
            if 'schema' in natural_query.lower():
                # For schema description requests, just return a special command
                return "DESCRIBE_SCHEMA"

        # Determine SQL dialect based on database type
        sql_dialect = "SQLite" if db_type == "sqlite" else "Oracle"

        # For normal SQL queries, proceed with the original logic
        prompt = f"""
Given {sql_dialect} database schema:
{schema}

Question: "{natural_query}"

Generate a {sql_dialect} query to answer this question. 

Respond with ONLY the SQL query in this exact format:
```yaml
sql: |
  SELECT ...
```

Do not include any explanations or other text."""

        llm_response = call_llm(prompt)
        
        # Try to extract SQL from YAML format first
        try:
            yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
            structured_result = yaml.safe_load(yaml_str)
            sql_query = structured_result["sql"].strip().rstrip(';')
            return sql_query
        except (IndexError, KeyError, yaml.YAMLError):
            # Fallback: try to extract SQL from code blocks
            try:
                if "```sql" in llm_response:
                    sql_query = llm_response.split("```sql")[1].split("```")[0].strip()
                elif "```" in llm_response:
                    sql_query = llm_response.split("```")[1].split("```")[0].strip()
                else:
                    # Last resort: look for SELECT statements
                    lines = llm_response.strip().split('\n')
                    sql_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and (line.upper().startswith(('SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE')) or sql_lines):
                            sql_lines.append(line)
                            if line.endswith(';'):
                                break
                    if sql_lines:
                        sql_query = ' '.join(sql_lines).rstrip(';')
                    else:
                        raise ValueError("No valid SQL found in response")
                
                return sql_query.strip()
            except Exception as e:
                # Print the actual response for debugging
                print(f"\n===== DEBUG: LLM Response =====")
                print(repr(llm_response))
                print("===============================\n")
                raise ValueError(f"Failed to parse LLM response. Expected YAML or SQL format. Error: {str(e)}")

    def post(self, shared, prep_res, exec_res):
        if exec_res == "DESCRIBE_SCHEMA":
            print("\nThe schema is shown above. This is a description of your database structure.")
            print("You can use this schema information to formulate SQL queries.\n")
            return
            
        # For normal SQL queries, proceed with original logic
        shared["generated_sql"] = exec_res
        shared["debug_attempts"] = 0
        print(f"\n===== GENERATED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n====================================\n")

class ExecuteSQL(Node):
    def prep(self, shared):
        return shared["db_adapter"], shared["generated_sql"]

    def exec(self, prep_res):
        db_adapter, sql_query = prep_res
        return db_adapter.execute_query(sql_query)

    def post(self, shared, prep_res, exec_res):
        success, result_or_error, column_names = exec_res

        if success:
            shared["final_result"] = result_or_error
            shared["result_columns"] = column_names
            print("\n===== SQL EXECUTION SUCCESS =====\n")
            # (Same result printing logic as before)
            if isinstance(result_or_error, list):
                 if column_names: print(" | ".join(column_names)); print("-" * (sum(len(str(c)) for c in column_names) + 3 * (len(column_names) -1)))
                 if not result_or_error: print("(No results found)")
                 else:
                     for row in result_or_error: print(" | ".join(map(str, row)))
            else: print(result_or_error)
            print("\n=================================\n")
            # Don't return anything - let the flow end naturally
        else:
            # Execution failed (SQLite error caught in exec)
            shared["execution_error"] = result_or_error # Store the error message
            shared["debug_attempts"] = shared.get("debug_attempts", 0) + 1
            max_attempts = shared.get("max_debug_attempts", 3) # Get max attempts from shared

            print(f"\n===== SQL EXECUTION FAILED (Attempt {shared['debug_attempts']}) =====\n")
            print(f"Error: {shared['execution_error']}")
            print("=========================================\n")

            if shared["debug_attempts"] >= max_attempts:
                print(f"Max debug attempts ({max_attempts}) reached. Stopping.")
                shared["final_error"] = f"Failed to execute SQL after {max_attempts} attempts. Last error: {shared['execution_error']}"
                # Don't return anything - let the flow end naturally
            else:
                print("Attempting to debug the SQL...")
                return "error_retry" # Signal to go to DebugSQL

class DebugSQL(Node):
    def prep(self, shared):
        return (
            shared.get("natural_query"),
            shared.get("schema"),
            shared.get("generated_sql"),
            shared.get("execution_error"),
            shared["db_adapter"].db_type
        )

    def exec(self, prep_res):
        natural_query, schema, failed_sql, error_message, db_type = prep_res
        
        # Determine SQL dialect based on database type
        sql_dialect = "SQLite" if db_type == "sqlite" else "Oracle"
        
        prompt = f"""
The following {sql_dialect} SQL query failed:
```sql
{failed_sql}
```
It was generated for: "{natural_query}"
Schema:
{schema}
Error: "{error_message}"

Provide a corrected {sql_dialect} query.

Respond with ONLY the corrected SQL query in this exact format:
```yaml
sql: |
  SELECT ... -- corrected query
```

Do not include any explanations or other text."""

        llm_response = call_llm(prompt)

        # Try to extract SQL from YAML format first
        try:
            yaml_str = llm_response.split("```yaml")[1].split("```")[0].strip()
            structured_result = yaml.safe_load(yaml_str)
            corrected_sql = structured_result["sql"].strip().rstrip(';')
            return corrected_sql
        except (IndexError, KeyError, yaml.YAMLError):
            # Fallback: try to extract SQL from code blocks
            try:
                if "```sql" in llm_response:
                    corrected_sql = llm_response.split("```sql")[1].split("```")[0].strip()
                elif "```" in llm_response:
                    corrected_sql = llm_response.split("```")[1].split("```")[0].strip()
                else:
                    # Last resort: look for SELECT statements
                    lines = llm_response.strip().split('\n')
                    sql_lines = []
                    for line in lines:
                        line = line.strip()
                        if line and (line.upper().startswith(('SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE')) or sql_lines):
                            sql_lines.append(line)
                            if line.endswith(';'):
                                break
                    if sql_lines:
                        corrected_sql = ' '.join(sql_lines).rstrip(';')
                    else:
                        raise ValueError("No valid SQL found in response")
                
                return corrected_sql.strip()
            except Exception as e:
                # Print the actual response for debugging
                print(f"\n===== DEBUG: LLM Response =====")
                print(repr(llm_response))
                print("===============================\n")
                raise ValueError(f"Failed to parse LLM response. Expected YAML or SQL format. Error: {str(e)}")

    def post(self, shared, prep_res, exec_res):
        # exec_res is the corrected SQL string
        shared["generated_sql"] = exec_res # Overwrite with the new attempt
        shared.pop("execution_error", None) # Clear the previous error for the next ExecuteSQL attempt

        print(f"\n===== REVISED SQL (Attempt {shared.get('debug_attempts', 0) + 1}) =====\n")
        print(exec_res)
        print("\n====================================\n")