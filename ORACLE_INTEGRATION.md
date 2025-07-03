# Oracle Database Integration Guide

This guide explains how to use the Text-to-SQL application with Oracle databases.

## Overview

The Text-to-SQL application now supports both SQLite and Oracle databases. Oracle integration includes:

- **Schema extraction** using Oracle system tables
- **Oracle-specific SQL generation** (NUMBER, VARCHAR2, DATE, TIMESTAMP types)
- **Connection management** with proper error handling
- **Sample data population** for testing

## Prerequisites

1. **Oracle Database Access**
   - Oracle XE, Standard, or Enterprise Edition
   - Oracle Cloud Database
   - Network connectivity to Oracle server

2. **Python Dependencies**
   ```bash
   pip install oracledb>=1.4.0
   ```

3. **Database Credentials**
   - Username with table access permissions
   - Password
   - Connection string (DSN)

## Quick Start

### 1. Basic Oracle Query
```bash
python main.py --db-type oracle \
  --oracle-user hr \
  --oracle-password welcome \
  --oracle-dsn localhost:1521/XE \
  "show me all employees"
```

### 2. Using Environment Variables
```bash
export ORACLE_USER="hr"
export ORACLE_PASSWORD="welcome"
export ORACLE_DSN="localhost:1521/XE"

python main.py --db-type oracle "describe the schema"
```

### 3. Configuration File Setup
Edit `config.py`:
```python
ORACLE_CONFIG = {
    "user": "your_username",
    "password": "your_password",
    "dsn": "localhost:1521/XE"
}
```

Then run:
```bash
python main.py --db-type oracle "your query"
```

## Connection Examples

### Local Oracle XE
```bash
# Default local installation
python main.py --db-type oracle \
  --oracle-user system \
  --oracle-password oracle \
  --oracle-dsn localhost:1521/XE \
  "show all tables"
```

### Oracle Cloud
```bash
# Oracle Cloud Database
python main.py --db-type oracle \
  --oracle-user admin \
  --oracle-password MyCloudPass123 \
  --oracle-dsn mydb.us-west-2.oraclecloud.com:1521/FREEPDB1 \
  "analyze customer data"
```

### Corporate Oracle Server
```bash
# Enterprise Oracle installation
python main.py --db-type oracle \
  --oracle-user app_user \
  --oracle-password SecurePass456 \
  --oracle-dsn oracle-prod.company.com:1521/ORCL \
  "generate sales report"
```

## Sample Data Setup

### Option 1: Using the Population Script
```bash
python populate_oracle_db.py your_username your_host:port/service_name
# Enter password when prompted
```

### Option 2: Manual Schema Creation
The script creates these tables:
- `customers` - Customer information
- `products` - Product catalog
- `orders` - Order records
- `order_items` - Order line items

## Oracle-Specific Features

### Data Types
The Oracle adapter handles these Oracle-specific types:
- `NUMBER` - Numeric data
- `VARCHAR2` - Variable character strings
- `DATE` - Date values
- `TIMESTAMP` - Date and time values
- `CLOB` - Large text objects

### Schema Information
Oracle schema extraction includes:
- Table names from `user_tables`
- Column details from `user_tab_columns`
- Data types, lengths, and NULL constraints
- Primary key and foreign key relationships

### SQL Generation
The LLM receives Oracle-specific context:
- Oracle SQL syntax and functions
- Oracle date/time formatting
- Oracle-specific operators and keywords

## Troubleshooting

### Connection Issues

**Error: "Oracle support not available"**
```bash
pip install oracledb
```

**Error: "ORA-12541: TNS:no listener"**
- Check if Oracle database is running
- Verify host and port in DSN
- Test with `tnsping` if available

**Error: "ORA-01017: invalid username/password"**
- Verify credentials
- Check if account is locked
- Ensure user has required permissions

**Error: "ORA-12514: TNS:listener does not currently know of service"**
- Verify service name in DSN
- Check if database service is started
- Use correct service name (not SID)

### Permission Issues

**Error: "ORA-00942: table or view does not exist"**
- Grant SELECT permissions: `GRANT SELECT ON table_name TO username`
- Check if user has access to system tables
- Verify table names and schema

### Performance Optimization

1. **Limit Result Sets**
   ```bash
   python main.py --db-type oracle "show me top 10 customers by sales"
   ```

2. **Use Specific Queries**
   ```bash
   python main.py --db-type oracle "find customers in California only"
   ```

3. **Index Considerations**
   - Ensure tables have appropriate indexes
   - Monitor query execution plans

## Advanced Usage

### Custom Queries
```bash
# Complex analytical query
python main.py --db-type oracle \
  "show me monthly sales trends for the last 6 months with product categories"

# Data quality checks
python main.py --db-type oracle \
  "find duplicate customer records based on email addresses"
```

### Debugging Mode
```bash
# Increase retry attempts for complex queries
python main.py --db-type oracle --max-retries 5 \
  "complex analytical query that might need multiple attempts"
```

### Example Script
Run the included Oracle example:
```bash
python oracle_example.py
```

## Integration Tips

1. **Test Connection First**
   ```bash
   python main.py --db-type oracle "describe the schema"
   ```

2. **Start Simple**
   Begin with basic queries before attempting complex analytics

3. **Use Oracle SQL Reference**
   The LLM understands Oracle-specific syntax and functions

4. **Monitor Performance**
   Complex queries may take longer on large Oracle databases

5. **Security Best Practices**
   - Use environment variables for passwords
   - Create dedicated database users for the application
   - Grant minimum required permissions

## File Structure

```
txt2sql/
├── main.py                 # Main application with Oracle support
├── db_adapter.py          # Database abstraction layer
├── nodes.py               # Updated nodes with Oracle support
├── config.py              # Configuration settings
├── populate_oracle_db.py  # Oracle sample data script
├── oracle_example.py      # Example Oracle usage
└── requirements.txt       # Updated with Oracle dependencies
```

## Support

For Oracle-specific issues:
1. Check Oracle database logs
2. Verify network connectivity
3. Test with standard Oracle tools (SQL*Plus, SQL Developer)
4. Review Oracle documentation for error codes

For application issues:
1. Enable debug mode with `--max-retries 5`
2. Check the LLM response format
3. Verify query syntax with Oracle SQL standards 