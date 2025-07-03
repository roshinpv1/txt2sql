#!/usr/bin/env python3
"""
Quick Oracle connectivity test script.
This script tests Oracle database connectivity with proper timeout handling.
"""

import sys
import time
import signal

def timeout_handler(signum, frame):
    raise TimeoutError("Connection attempt timed out")

def test_oracle_connection(user, password, dsn, timeout=10):
    """
    Test Oracle connection with timeout.
    
    Args:
        user: Oracle username
        password: Oracle password  
        dsn: Oracle DSN (hostname:port/service_name)
        timeout: Connection timeout in seconds
    """
    
    print(f"🔍 Testing Oracle connection...")
    print(f"   User: {user}")
    print(f"   DSN: {dsn}")
    print(f"   Timeout: {timeout} seconds")
    print("-" * 50)
    
    # Check if oracledb is installed
    try:
        import oracledb
        print("✅ oracledb module is available")
    except ImportError:
        print("❌ oracledb module not found")
        print("   Install with: pip install oracledb")
        return False
    
    # Set connection timeout
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(timeout)
    
    try:
        start_time = time.time()
        print("🔗 Attempting connection...")
        
        # Try to connect
        connection = oracledb.connect(
            user=user,
            password=password,
            dsn=dsn
        )
        
        connection_time = time.time() - start_time
        print(f"✅ Connection successful! ({connection_time:.2f}s)")
        
        # Test a simple query
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result = cursor.fetchone()
        
        if result:
            print("✅ Query test successful!")
            
        # Test schema access
        cursor.execute("SELECT COUNT(*) FROM user_tables")
        table_count = cursor.fetchone()[0]
        print(f"✅ Found {table_count} tables in your schema")
        
        connection.close()
        signal.alarm(0)  # Cancel timeout
        
        print("\n🎉 Oracle connection test PASSED!")
        return True
        
    except TimeoutError:
        print(f"❌ Connection timed out after {timeout} seconds")
        print("   This could indicate:")
        print("   - Network connectivity issues")
        print("   - Firewall blocking the connection")
        print("   - Oracle server not responding")
        print("   - Wrong hostname/port")
        return False
        
    except Exception as e:
        signal.alarm(0)  # Cancel timeout
        error_msg = str(e)
        
        print(f"❌ Connection failed: {error_msg}")
        
        # Provide specific troubleshooting based on error
        if "ORA-12541" in error_msg:
            print("   → TNS:no listener - Check if Oracle is running and port is correct")
        elif "ORA-01017" in error_msg:
            print("   → Invalid username/password")
        elif "ORA-12514" in error_msg:
            print("   → TNS:listener does not know service - Check service name")
        elif "ORA-12154" in error_msg:
            print("   → TNS:could not resolve service name - Check DSN format")
        elif "Network" in error_msg or "timeout" in error_msg.lower():
            print("   → Network issue - Check connectivity to Oracle server")
        
        return False

def main():
    """Main function for interactive testing."""
    
    print("🏛️  Oracle Quick Connection Test")
    print("=" * 40)
    
    if len(sys.argv) == 4:
        # Command line arguments provided
        user, password, dsn = sys.argv[1], sys.argv[2], sys.argv[3]
    else:
        # Interactive input
        print("Enter Oracle connection details:")
        user = input("Username: ").strip()
        password = input("Password: ").strip()
        dsn = input("DSN (hostname:port/service): ").strip()
    
    if not all([user, password, dsn]):
        print("❌ All connection details are required!")
        sys.exit(1)
    
    # Test with 10 second timeout
    success = test_oracle_connection(user, password, dsn, timeout=10)
    
    if success:
        print("\n✅ Your Oracle connection is working!")
        print("   You can now use it with the main application:")
        print(f"   python main.py --db-type oracle --oracle-user {user} --oracle-password {password} --oracle-dsn {dsn} \"describe the schema\"")
    else:
        print("\n❌ Oracle connection failed!")
        print("   Please check your connection details and try again.")
    
    return 0 if success else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(1) 