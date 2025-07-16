"""
Configuration settings for Text-to-SQL application.

You can modify these settings or use command line arguments to override them.
"""

# SQLite Configuration
SQLITE_DEFAULT_PATH = "ecommerce.db"

# Oracle Configuration
# You can set these values here or use environment variables
ORACLE_CONFIG = {
    "user": "your_username",        # Your Oracle username
    "password": "your_password",    # Your Oracle password  
    "dsn": "hostname:port/service_name",  # Format: hostname:port/service_name
}

# Example Oracle configurations:
# For local Oracle XE:
# ORACLE_CONFIG = {
#     "user": "hr",
#     "password": "welcome",
#     "dsn": "localhost:1521/XE"
# }

# For Oracle Cloud or Remote Server:
# ORACLE_CONFIG = {
#     "user": "admin", 
#     "password": "MyPassword123",
#     "dsn": "myhost.oraclecloud.com:1521/FREEPDB1"
# }

# For Corporate Oracle Server:
# ORACLE_CONFIG = {
#     "user": "app_user",
#     "password": "SecurePass456", 
#     "dsn": "oracle-prod.company.com:1521/ORCL"
# }

# Environment variable names for Oracle config
ORACLE_ENV_VARS = {
    "user": "ORACLE_USER",
    "password": "ORACLE_PASSWORD", 
    "dsn": "ORACLE_DSN"
}

# Default settings
DEFAULT_MAX_RETRIES = 3 