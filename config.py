"""
Configuration settings for Text-to-SQL application.

You can modify these settings or use command line arguments to override them.
"""

# SQLite Configuration
SQLITE_DEFAULT_PATH = "ecommerce.db"

# Oracle Configuration
# You can set these values here or use environment variables
ORACLE_CONFIG = {
    "user": None,  # Set your Oracle username here or use --oracle-user
    "password": None,  # Set your Oracle password here or use --oracle-password  
    "dsn": None,  # Set your Oracle DSN here or use --oracle-dsn
}

# Example Oracle configurations:
# For local Oracle XE:
# ORACLE_CONFIG = {
#     "user": "your_username",
#     "password": "your_password",
#     "dsn": "localhost:1521/XE"
# }

# For Oracle Cloud:
# ORACLE_CONFIG = {
#     "user": "your_username", 
#     "password": "your_password",
#     "dsn": "your_host:1521/your_service_name"
# }

# Environment variable names for Oracle config
ORACLE_ENV_VARS = {
    "user": "ORACLE_USER",
    "password": "ORACLE_PASSWORD", 
    "dsn": "ORACLE_DSN"
}

# Default settings
DEFAULT_MAX_RETRIES = 3 