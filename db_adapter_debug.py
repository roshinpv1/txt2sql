import sqlite3
import time
from typing import List, Tuple, Optional, Dict, Any

try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

class DatabaseAdapterDebug:
    """Debug version of DatabaseAdapter to identify Oracle connection issues."""
    
    def __init__(self, db_config: Dict[str, Any]):
        """Initialize database adapter with debug output."""
        print(f"🔍 DEBUG: Initializing DatabaseAdapter")
        print(f"   Config received: {db_config}")
        
        self.db_config = db_config
        self.db_type = db_config["type"].lower()
        
        print(f"   Database type: {self.db_type}")
        
        if self.db_type == "oracle":
            print(f"   Oracle config details:")
            print(f"     User: '{self.db_config.get('user', 'NOT_SET')}'")
            print(f"     Password: '{'*' * len(str(self.db_config.get('password', '')))}'")
            print(f"     DSN: '{self.db_config.get('dsn', 'NOT_SET')}'")
            
            if not ORACLE_AVAILABLE:
                raise ImportError("Oracle support not available. Install oracledb: pip install oracledb")
        
        if self.db_type not in ["sqlite", "oracle"]:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_connection(self):
        """Get database connection with debug output."""
        print(f"🔍 DEBUG: get_connection() called for {self.db_type}")
        
        if self.db_type == "sqlite":
            path = self.db_config["path"]
            print(f"   SQLite path: {path}")
            return sqlite3.connect(path)
            
        elif self.db_type == "oracle":
            user = self.db_config["user"]
            password = self.db_config["password"]
            dsn = self.db_config["dsn"]
            
            print(f"   Oracle connection parameters:")
            print(f"     user = '{user}' (type: {type(user)})")
            print(f"     password = '{'*' * len(str(password))}' (type: {type(password)})")
            print(f"     dsn = '{dsn}' (type: {type(dsn)})")
            
            # Check for None values
            if user is None:
                raise ValueError("Oracle user is None")
            if password is None:
                raise ValueError("Oracle password is None")
            if dsn is None:
                raise ValueError("Oracle DSN is None")
            
            print(f"   Calling oracledb.connect()...")
            
            try:
                connection = oracledb.connect(
                    user=user,
                    password=password,
                    dsn=dsn
                )
                print(f"   ✅ Oracle connection successful!")
                return connection
            except Exception as e:
                print(f"   ❌ Oracle connection failed: {e}")
                print(f"   Error type: {type(e).__name__}")
                raise
    
    def test_basic_query(self):
        """Test basic query like the user's working code."""
        print(f"🔍 DEBUG: Testing basic query...")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            query = "SELECT sysdate FROM dual"
            print(f"   Executing: {query}")
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            print(f"   ✅ Query successful: {results}")
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"   ❌ Query failed: {e}")
            return False

def test_working_vs_adapter():
    """Compare working Oracle code vs DatabaseAdapter."""
    
    print("🏛️  Oracle Connection Comparison Test")
    print("=" * 60)
    
    # Test 1: Direct working connection
    print("\n1️⃣  Testing Direct Oracle Connection (User's Working Code)")
    print("-" * 50)
    
    try:
        import oracledb
        
        # Exact same parameters that work for the user
        connection = oracledb.connect(
            user="BM", 
            password="dsd", 
            dsn="danuxl6170si.ds.com:3203/q10bpay_qa"
        )
        
        cursor = connection.cursor()
        cursor.execute("SELECT sysdate FROM dual")
        results = cursor.fetchall()
        
        print(f"✅ Direct connection successful: {results}")
        
        cursor.close()
        connection.close()
        direct_works = True
        
    except Exception as e:
        print(f"❌ Direct connection failed: {e}")
        direct_works = False
    
    # Test 2: DatabaseAdapter
    print("\n2️⃣  Testing DatabaseAdapter")
    print("-" * 50)
    
    try:
        # Same config that should work
        oracle_config = {
            "type": "oracle",
            "user": "BM",
            "password": "dsd", 
            "dsn": "danuxl6170si.ds.com:3203/q10bpay_qa"
        }
        
        adapter = DatabaseAdapterDebug(oracle_config)
        adapter_works = adapter.test_basic_query()
        
    except Exception as e:
        print(f"❌ DatabaseAdapter failed: {e}")
        adapter_works = False
    
    # Results
    print("\n" + "=" * 60)
    print("📋 COMPARISON RESULTS:")
    print(f"   Direct Oracle Connection: {'✅ WORKS' if direct_works else '❌ FAILS'}")
    print(f"   DatabaseAdapter:          {'✅ WORKS' if adapter_works else '❌ FAILS'}")
    
    if direct_works and adapter_works:
        print("\n🎉 SUCCESS: Both methods work!")
    elif direct_works and not adapter_works:
        print("\n🚨 ISSUE: Direct works but DatabaseAdapter fails!")
        print("   Check the debug output above for parameter differences.")
    else:
        print("\n⚠️  NETWORK ISSUE: Direct connection also fails.")
        print("   This suggests network/credential issues, not adapter problems.")

if __name__ == "__main__":
    test_working_vs_adapter() 