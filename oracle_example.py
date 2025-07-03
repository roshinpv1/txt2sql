#!/usr/bin/env python3
"""
Example script demonstrating Oracle database integration with the Text-to-SQL workflow.

This script shows how to:
1. Set up Oracle connection using environment variables
2. Test the connection
3. Run sample queries

Before running this script:
1. Install Oracle dependencies: pip install oracledb
2. Set environment variables or modify the config below
3. Ensure your Oracle database is accessible
"""

import os
import sys
from main import run_text_to_sql

# Example Oracle configuration
# Modify these values or set environment variables
ORACLE_CONFIG = {
    "type": "oracle",
    "user": os.environ.get("ORACLE_USER", "hr"),  # Default to 'hr' user
    "password": os.environ.get("ORACLE_PASSWORD", "welcome"),  # Default password
    "dsn": os.environ.get("ORACLE_DSN", "localhost:1521/XE")  # Default to local XE
}

def test_oracle_connection():
    """Test Oracle database connection."""
    try:
        from db_adapter import DatabaseAdapter
        
        print("Testing Oracle connection...")
        adapter = DatabaseAdapter(ORACLE_CONFIG)
        
        # Try to get schema
        schema = adapter.get_schema()
        print(f"✅ Connection successful!")
        print(f"📊 Found {len(schema.split('Table:')) - 1} tables")
        return True
        
    except ImportError:
        print("❌ Oracle support not available. Install oracledb: pip install oracledb")
        return False
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your Oracle connection details")
        print("2. Ensure Oracle database is running")
        print("3. Verify network connectivity")
        print("4. Check username/password and permissions")
        return False

def run_oracle_examples():
    """Run example queries against Oracle database."""
    
    print(f"\n🔗 Connecting to Oracle: {ORACLE_CONFIG['user']}@{ORACLE_CONFIG['dsn']}")
    
    if not test_oracle_connection():
        return
    
    # Example queries to demonstrate Oracle-specific features
    example_queries = [
        "describe the schema for me",
        "show me all table names",
        "what tables contain customer information?",
        "give me a count of records in each table",
        # Add more queries based on your Oracle schema
    ]
    
    print(f"\n🚀 Running {len(example_queries)} example queries...\n")
    
    for i, query in enumerate(example_queries, 1):
        print(f"{'='*60}")
        print(f"Example {i}/{len(example_queries)}: {query}")
        print(f"{'='*60}")
        
        try:
            result = run_text_to_sql(query, ORACLE_CONFIG)
            print(f"✅ Query {i} completed successfully")
        except Exception as e:
            print(f"❌ Query {i} failed: {e}")
        
        print()  # Add spacing between queries

def main():
    """Main function."""
    print("🏛️  Oracle Database Text-to-SQL Example")
    print("="*50)
    
    # Check if Oracle credentials are provided
    if not all([ORACLE_CONFIG["user"], ORACLE_CONFIG["password"], ORACLE_CONFIG["dsn"]]):
        print("⚠️  Oracle credentials not fully configured!")
        print("\nPlease set environment variables:")
        print("export ORACLE_USER='your_username'")
        print("export ORACLE_PASSWORD='your_password'")
        print("export ORACLE_DSN='host:port/service_name'")
        print("\nOr modify the ORACLE_CONFIG in this script.")
        return
    
    print(f"🎯 Target Database: {ORACLE_CONFIG['user']}@{ORACLE_CONFIG['dsn']}")
    
    # Ask user if they want to proceed
    response = input("\n▶️  Proceed with Oracle examples? (y/N): ").strip().lower()
    if response not in ['y', 'yes']:
        print("👋 Exiting...")
        return
    
    # Run the examples
    run_oracle_examples()
    
    print("🎉 Oracle examples completed!")
    print("\n💡 Next steps:")
    print("1. Try your own queries using: python main.py --db-type oracle 'your query'")
    print("2. Populate sample data using: python populate_oracle_db.py")
    print("3. Explore advanced Oracle features like views, stored procedures, etc.")

if __name__ == "__main__":
    main() 