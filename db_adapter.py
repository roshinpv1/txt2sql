import sqlite3
import time
from typing import List, Tuple, Optional, Dict, Any

try:
    import oracledb
    ORACLE_AVAILABLE = True
except ImportError:
    ORACLE_AVAILABLE = False

class DatabaseAdapter:
    """Database adapter that supports both SQLite and Oracle databases."""
    
    def __init__(self, db_config: Dict[str, Any]):
        """
        Initialize database adapter.
        
        For SQLite:
        db_config = {"type": "sqlite", "path": "database.db"}
        
        For Oracle:
        db_config = {
            "type": "oracle", 
            "user": "username", 
            "password": "password", 
            "dsn": "host:port/service_name"
        }
        """
        self.db_config = db_config
        self.db_type = db_config["type"].lower()
        
        if self.db_type == "oracle" and not ORACLE_AVAILABLE:
            raise ImportError("Oracle support not available. Install oracledb: pip install oracledb")
        
        if self.db_type not in ["sqlite", "oracle"]:
            raise ValueError(f"Unsupported database type: {self.db_type}")
    
    def get_connection(self):
        """Get database connection based on database type."""
        if self.db_type == "sqlite":
            return sqlite3.connect(self.db_config["path"])
        elif self.db_type == "oracle":
            return oracledb.connect(
                user=self.db_config["user"],
                password=self.db_config["password"],
                dsn=self.db_config["dsn"]
            )
    
    def get_schema(self) -> str:
        """Extract database schema."""
        if self.db_type == "sqlite":
            return self._get_sqlite_schema()
        elif self.db_type == "oracle":
            return self._get_oracle_schema()
    
    def _get_sqlite_schema(self) -> str:
        """Extract SQLite schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        schema = []
        
        for table_name_tuple in tables:
            table_name = table_name_tuple[0]
            schema.append(f"Table: {table_name}")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                schema.append(f"  - {col[1]} ({col[2]})")
            schema.append("")
        
        conn.close()
        return "\n".join(schema).strip()
    
    def _get_oracle_schema(self) -> str:
        """Extract Oracle schema."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get tables for current user
        cursor.execute("""
            SELECT table_name 
            FROM user_tables 
            ORDER BY table_name
        """)
        tables = cursor.fetchall()
        schema = []
        
        for table_tuple in tables:
            table_name = table_tuple[0]
            schema.append(f"Table: {table_name}")
            
            # Get columns for this table
            cursor.execute("""
                SELECT column_name, data_type, data_length, nullable
                FROM user_tab_columns 
                WHERE table_name = :table_name
                ORDER BY column_id
            """, {"table_name": table_name})
            
            columns = cursor.fetchall()
            for col in columns:
                col_name, data_type, data_length, nullable = col
                nullable_str = "NULL" if nullable == "Y" else "NOT NULL"
                if data_length and data_type in ['VARCHAR2', 'CHAR', 'NVARCHAR2', 'NCHAR']:
                    type_str = f"{data_type}({data_length})"
                else:
                    type_str = data_type
                schema.append(f"  - {col_name} ({type_str}) {nullable_str}")
            schema.append("")
        
        conn.close()
        return "\n".join(schema).strip()
    
    def execute_query(self, sql_query: str) -> Tuple[bool, Any, List[str]]:
        """
        Execute SQL query and return results.
        
        Returns:
            Tuple of (success, results, column_names)
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            start_time = time.time()
            
            cursor.execute(sql_query)
            
            # Determine if this is a SELECT query
            is_select = sql_query.strip().upper().startswith(("SELECT", "WITH"))
            
            if is_select:
                results = cursor.fetchall()
                # Get column names
                if self.db_type == "sqlite":
                    column_names = [desc[0] for desc in cursor.description] if cursor.description else []
                elif self.db_type == "oracle":
                    column_names = [desc[0] for desc in cursor.description] if cursor.description else []
            else:
                conn.commit()
                if self.db_type == "sqlite":
                    results = f"Query OK. Rows affected: {cursor.rowcount}"
                elif self.db_type == "oracle":
                    results = f"Query OK. Rows affected: {cursor.rowcount}"
                column_names = []
            
            conn.close()
            duration = time.time() - start_time
            print(f"SQL executed in {duration:.3f} seconds.")
            return (True, results, column_names)
            
        except Exception as e:
            print(f"Database Error during execution: {e}")
            if 'conn' in locals() and conn:
                try:
                    conn.close()
                except Exception:
                    pass
            return (False, str(e), [])
    
    def get_db_info(self) -> str:
        """Get database type and connection info for display."""
        if self.db_type == "sqlite":
            return f"SQLite: {self.db_config['path']}"
        elif self.db_type == "oracle":
            return f"Oracle: {self.db_config['user']}@{self.db_config['dsn']}" 