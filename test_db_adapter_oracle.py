#!/usr/bin/env python3
"""
Test script to validate DatabaseAdapter Oracle functionality
against a known working Oracle connection.
"""

import sys
import traceback

def test_working_oracle_connection():
    """Test the working Oracle connection code from the user."""
    print("🔍 Testing Working Oracle Connection Code...")
    print("-" * 50)
    
    try:
        import oracledb
        print("✅ oracledb module imported successfully")
        
        # Define connection parameters (using user's working details)
        connection = oracledb.connect(
            user="BM", 
            password="dsd", 
            dsn="danuxl6170si.ds.com:3203/q10bpay_qa"
        )
        print("✅ Direct oracledb.connect() successful")
        
        # Create a cursor
        cursor = connection.cursor()
        print("✅ Cursor created successfully")
        
        # Execute the query
        query = "SELECT sysdate from dual"
        cursor.execute(query)
        print("✅ Query executed successfully")
        
        # Fetch all results
        results = cursor.fetchall()
        print(f"✅ Results fetched: {results}")
        
        # Close connections
        cursor.close()
        connection.close()
        print("✅ Connection closed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def test_database_adapter():
    """Test our DatabaseAdapter with the same Oracle credentials."""
    print("\n🔍 Testing DatabaseAdapter Implementation...")
    print("-" * 50)
    
    try:
        from db_adapter import DatabaseAdapter
        print("✅ DatabaseAdapter imported successfully")
        
        # Create config using same credentials that work
        oracle_config = {
            "type": "oracle",
            "user": "BM",
            "password": "dsd", 
            "dsn": "danuxl6170si.ds.com:3203/q10bpay_qa"
        }
        print("✅ Oracle config created")
        
        # Test DatabaseAdapter initialization
        adapter = DatabaseAdapter(oracle_config)
        print("✅ DatabaseAdapter initialized")
        
        # Test get_connection method
        print("🔗 Testing get_connection()...")
        connection = adapter.get_connection()
        print("✅ get_connection() successful")
        
        # Test execute_query method
        print("🔗 Testing execute_query()...")
        success, results, columns = adapter.execute_query("SELECT sysdate FROM dual")
        
        if success:
            print(f"✅ execute_query() successful: {results}")
            print(f"   Columns: {columns}")
        else:
            print(f"❌ execute_query() failed: {results}")
            return False
        
        # Test get_schema method
        print("🔗 Testing get_schema()...")
        try:
            schema = adapter.get_schema()
            print(f"✅ get_schema() successful")
            print(f"   Schema preview: {schema[:200]}...")
        except Exception as e:
            print(f"❌ get_schema() failed: {e}")
            # This might fail if user doesn't have tables, but connection works
        
        # Test get_db_info method
        print("🔗 Testing get_db_info()...")
        db_info = adapter.get_db_info()
        print(f"✅ get_db_info() successful: {db_info}")
        
        return True
        
    except Exception as e:
        print(f"❌ DatabaseAdapter test failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        traceback.print_exc()
        return False

def compare_implementations():
    """Compare the working code with our implementation."""
    print("\n🔍 Comparing Implementations...")
    print("-" * 50)
    
    print("Your working code:")
    print("  oracledb.connect(user='BM', password='dsd', dsn='danuxl6170si.ds.com:3203/q10bpay_qa')")
    
    print("\nOur DatabaseAdapter code:")
    print("  oracledb.connect(user=config['user'], password=config['password'], dsn=config['dsn'])")
    
    print("\nKey differences to check:")
    print("1. ✅ Both use same oracledb.connect() method")
    print("2. ✅ Both use same parameter names (user, password, dsn)")
    print("3. ✅ DSN format looks identical")
    print("4. 🔍 Need to verify parameter passing in DatabaseAdapter")

def identify_potential_issues():
    """Identify potential issues in DatabaseAdapter."""
    print("\n🔍 Potential Issues in DatabaseAdapter...")
    print("-" * 50)
    
    issues = [
        "1. Parameter passing - config values might be None/empty",
        "2. String encoding - special characters in password/dsn",
        "3. Connection pooling - adapter might use different connection settings",
        "4. Error handling - adapter might catch/mask connection errors",
        "5. Import issues - oracledb might not be available in adapter context",
        "6. Timeout settings - adapter might have different timeout configuration"
    ]
    
    for issue in issues:
        print(f"   {issue}")
    
    print("\nRecommended fixes:")
    print("1. Add debug prints to see exact values passed to oracledb.connect()")
    print("2. Test adapter with same exact credentials that work")
    print("3. Check if adapter modifies DSN format")
    print("4. Verify oracledb import in adapter")

def main():
    """Main test function."""
    print("🏛️  DatabaseAdapter Oracle Validation")
    print("=" * 60)
    
    # Test 1: Direct Oracle connection (should work)
    direct_works = test_working_oracle_connection()
    
    # Test 2: DatabaseAdapter (might fail)
    adapter_works = test_database_adapter()
    
    # Analysis
    compare_implementations()
    
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS:")
    print(f"   Direct Oracle Connection: {'✅ PASS' if direct_works else '❌ FAIL'}")
    print(f"   DatabaseAdapter:          {'✅ PASS' if adapter_works else '❌ FAIL'}")
    
    if direct_works and not adapter_works:
        print("\n🚨 ISSUE IDENTIFIED:")
        print("   Your Oracle connection works directly but fails through DatabaseAdapter!")
        identify_potential_issues()
    elif direct_works and adapter_works:
        print("\n🎉 SUCCESS:")
        print("   Both direct connection and DatabaseAdapter work!")
    else:
        print("\n⚠️  NETWORK/CREDENTIALS ISSUE:")
        print("   Direct connection also fails - check network/credentials")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        traceback.print_exc() 