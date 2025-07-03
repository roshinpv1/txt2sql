import sys
import os
import warnings
import argparse
from flow import create_text_to_sql_flow
from populate_db import populate_database, DB_FILE
from db_adapter import DatabaseAdapter
from config import ORACLE_CONFIG, ORACLE_ENV_VARS, DEFAULT_MAX_RETRIES

# Suppress the specific PocketFlow warning about flow endings
warnings.filterwarnings("ignore", message="Flow ends:*", category=UserWarning)

def get_oracle_config_from_env():
    """Get Oracle configuration from environment variables."""
    config = {}
    for key, env_var in ORACLE_ENV_VARS.items():
        config[key] = os.environ.get(env_var, ORACLE_CONFIG.get(key))
    return config

def parse_arguments():
    """Parse command line arguments for database configuration and query."""
    parser = argparse.ArgumentParser(description='Text-to-SQL converter supporting SQLite and Oracle')
    
    # Database type selection
    parser.add_argument('--db-type', choices=['sqlite', 'oracle'], default='sqlite',
                        help='Database type (default: sqlite)')
    
    # SQLite options
    parser.add_argument('--sqlite-path', default=DB_FILE,
                        help='Path to SQLite database file (default: ecommerce.db)')
    
    # Oracle options - get defaults from config/env
    oracle_env_config = get_oracle_config_from_env()
    parser.add_argument('--oracle-user', default=oracle_env_config.get('user'),
                        help='Oracle username (or set ORACLE_USER env var)')
    parser.add_argument('--oracle-password', default=oracle_env_config.get('password'),
                        help='Oracle password (or set ORACLE_PASSWORD env var)')
    parser.add_argument('--oracle-dsn', default=oracle_env_config.get('dsn'),
                        help='Oracle DSN like host:port/service_name (or set ORACLE_DSN env var)')
    
    # Other options
    parser.add_argument('--max-retries', type=int, default=DEFAULT_MAX_RETRIES,
                        help=f'Maximum debug retry attempts (default: {DEFAULT_MAX_RETRIES})')
    
    # Query (can be multiple words)
    parser.add_argument('query', nargs='*', 
                        help='Natural language query (if not provided, uses default query)')
    
    return parser.parse_args()

def create_db_config(args):
    """Create database configuration from arguments."""
    if args.db_type == 'sqlite':
        return {"type": "sqlite", "path": args.sqlite_path}
    elif args.db_type == 'oracle':
        if not all([args.oracle_user, args.oracle_password, args.oracle_dsn]):
            print("\nError: Oracle database requires connection details.")
            print("Provide them via:")
            print("  1. Command line: --oracle-user USERNAME --oracle-password PASSWORD --oracle-dsn HOST:PORT/SERVICE")
            print("  2. Environment variables: ORACLE_USER, ORACLE_PASSWORD, ORACLE_DSN")
            print("  3. config.py file")
            print("\nExample:")
            print("  python main.py --db-type oracle --oracle-user myuser --oracle-password mypass --oracle-dsn localhost:1521/XE \"show me all tables\"")
            sys.exit(1)
        return {
            "type": "oracle",
            "user": args.oracle_user,
            "password": args.oracle_password,
            "dsn": args.oracle_dsn
        }

def run_text_to_sql(natural_query, db_config, max_debug_retries=3):
    # Create database adapter
    try:
        db_adapter = DatabaseAdapter(db_config)
    except Exception as e:
        print(f"Error creating database adapter: {e}")
        sys.exit(1)

    # For SQLite, check if database exists and populate if needed
    if db_config["type"] == "sqlite":
        db_path = db_config["path"]
        if not os.path.exists(db_path) or os.path.getsize(db_path) == 0:
            print(f"Database at {db_path} missing or empty. Populating...")
            populate_database(db_path)

    shared = {
        "db_adapter": db_adapter,
        "natural_query": natural_query,
        "max_debug_attempts": max_debug_retries,
        "debug_attempts": 0,
        "final_result": None,
        "final_error": None
    }

    print(f"\n=== Starting Text-to-SQL Workflow ===")
    print(f"Query: '{natural_query}'")
    print(f"Database: {db_adapter.get_db_info()}")
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
    return shared

if __name__ == "__main__":
    args = parse_arguments()
    
    # Determine query
    if args.query:
        query = " ".join(args.query)
    else:
        # Default query
        query = "Show me the names and email addresses of customers from New York"
    
    # Create database configuration
    db_config = create_db_config(args)
    
    # Run the workflow
    run_text_to_sql(query, db_config, args.max_retries) 