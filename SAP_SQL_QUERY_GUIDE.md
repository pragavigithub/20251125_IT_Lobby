# SAP B1 SQL Query Auto-Management Guide

## Overview
The WMS application automatically validates and creates required SAP Business One SQL queries on startup. This eliminates the need for manual query setup in SAP B1 Service Layer.

## How It Works

### Startup Process
When the application starts (`app.py`), it automatically:
1. Connects to SAP B1 Service Layer
2. Checks for 10 required SQL queries
3. Creates any missing queries automatically
4. Logs the validation results
5. Continues application startup

### Implementation Files
- **`sap_sql_queries.py`**: Core module containing `SAPSQLQueryManager` class
- **`app.py`**: Integration point where queries are validated on startup
- **Integration code in app.py**:
  ```python
  # Initialize SAP B1 SQL Queries (validates and creates required queries)
  try:
      from sap_sql_queries import initialize_sap_queries
      initialize_sap_queries()
  except Exception as e:
      logging.warning(f"⚠️ SAP SQL query initialization skipped: {str(e)}")
  ```

## Required SQL Queries

The system automatically manages these 10 SAP B1 queries:

### 1. Series_Validation
- **SqlCode**: `Series_Validation`
- **SqlName**: `Seriel_Validation`
- **Purpose**: Validates serial numbers in warehouse
- **Parameters**: `itemCode`, `series`, `whsCode`

### 2. Quantity_Check
- **SqlCode**: `Quantity_Check`
- **SqlName**: `Quantity_Check`
- **Purpose**: Checks item quantity in warehouse
- **Parameters**: `whCode`, `itemCode`

### 3. ItemCode_Validation
- **SqlCode**: `ItemCode_Validation`
- **SqlName**: `ItemCode_Validation`
- **Purpose**: Validates item codes in warehouse
- **Parameters**: `item_code`, `whcode`

### 4. Item_Validation
- **SqlCode**: `Item_Validation`
- **SqlName**: `Item_Validation`
- **Purpose**: Validates items by serial number
- **Parameters**: `seriel_number`, `whcode`

### 5. Get_SO_Details
- **SqlCode**: `Get_SO_Details`
- **SqlName**: `Get_SO_Details`
- **Purpose**: Retrieves Sales Order details
- **Parameters**: `SONumber`, `Series`

### 6. Invoise_creation
- **SqlCode**: `Invoise_creation`
- **SqlName**: `Invoise_creation`
- **Purpose**: Invoice creation query
- **Parameters**: `serial_number`

### 7. Get_SO_Series
- **SqlCode**: `Get_SO_Series`
- **SqlName**: `Get_SO_Series`
- **Purpose**: Gets Sales Order series
- **Parameters**: None (ObjectCode = '17')

### 8. Get_Item
- **SqlCode**: `Get_Item`
- **SqlName**: `Get_Item`
- **Purpose**: Retrieves items from warehouse
- **Parameters**: `whcode`

### 9. Checkseries
- **SqlCode**: `Checkseries`
- **SqlName**: `Checkseries`
- **Purpose**: Checks serial availability
- **Parameters**: `Itemcode`, `Serials`, `Whscode`

### 10. GetItemWarehouseSerialStatus
- **SqlCode**: `GetItemWarehouseSerialStatus`
- **SqlName**: `Get Item Warehouse Serial Status`
- **Purpose**: Gets item/serial/warehouse status
- **Parameters**: `ItemCode`, `SerialNumber`, `WarehouseCode`

## API Endpoints Used

### Check Query Existence
```
GET https://{SAP_B1_SERVER}/b1s/v1/SQLQueries('{SqlCode}')
```
**Response (Exists)**:
```json
{
    "odata.metadata": "...",
    "SqlCode": "Series_Validation",
    "SqlName": "Seriel_Validation",
    "SqlText": "SELECT ...",
    "ParamList": "itemCode,series,whsCode",
    "CreateDate": "2025-09-12T00:00:00Z",
    "UpdateDate": "2025-09-12T00:00:00Z"
}
```

**Response (Not Exists)**:
```json
{
    "error": {
        "code": -2028,
        "message": {
            "lang": "en-us",
            "value": "No matching records found (ODBC -2028)"
        }
    }
}
```

### Create Query
```
POST https://{SAP_B1_SERVER}/b1s/v1/SQLQueries
Content-Type: application/json

{
   "SqlCode": "Series_Validation",
   "SqlName": "Seriel_Validation",
   "SqlText": "SELECT T0.\"ItemCode\", T0.\"DistNumber\", T1.\"WhsCode\" FROM \"OSRN\" T0  INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" WHERE  T1.\"Quantity\" >'0'AND T1.\"ItemCode\" =:itemCode AND T0.\"DistNumber\"=:series AND T1.\"WhsCode\"=:whsCode"
}
```

## Monitoring and Logs

### Successful Startup (All Queries Exist)
```
INFO:root:✅ SAP B1 login successful for SQL query validation
INFO:root:🔍 Starting SAP B1 SQL query validation...
DEBUG:root:✓ Query 'Series_Validation' already exists
DEBUG:root:✓ Query 'Quantity_Check' already exists
DEBUG:root:✓ Query 'ItemCode_Validation' already exists
DEBUG:root:✓ Query 'Item_Validation' already exists
DEBUG:root:✓ Query 'Get_SO_Details' already exists
DEBUG:root:✓ Query 'Invoise_creation' already exists
DEBUG:root:✓ Query 'Get_SO_Series' already exists
DEBUG:root:✓ Query 'Get_Item' already exists
DEBUG:root:✓ Query 'Checkseries' already exists
DEBUG:root:✓ Query 'GetItemWarehouseSerialStatus' already exists
INFO:root:📊 SQL Query Validation Summary:
INFO:root:   - Total queries checked: 10
INFO:root:   - Existing queries: 10
INFO:root:   - Newly created queries: 0
INFO:root:   - Failed/Skipped: 0
```

### Startup with Missing Queries
```
INFO:root:✅ SAP B1 login successful for SQL query validation
INFO:root:🔍 Starting SAP B1 SQL query validation...
DEBUG:root:✓ Query 'Series_Validation' already exists
INFO:root:⚠️ Query 'Quantity_Check' not found. Creating...
INFO:root:✅ Created SQL query: Quantity_Check (Quantity_Check)
DEBUG:root:✓ Query 'ItemCode_Validation' already exists
INFO:root:📊 SQL Query Validation Summary:
INFO:root:   - Total queries checked: 10
INFO:root:   - Existing queries: 9
INFO:root:   - Newly created queries: 1
INFO:root:   - Failed/Skipped: 0
```

### Offline Mode (SAP B1 Not Available)
```
WARNING:root:⚠️ Credential 'SAP_B1_SERVER' not found in JSON file or environment
WARNING:root:⚠️ SAP B1 configuration incomplete. Skipping SQL query validation.
WARNING:root:⚠️ Skipping SAP SQL query validation - SAP B1 not available
```

## Adding New SQL Queries

To add additional SAP SQL queries to the auto-management system:

### Step 1: Edit sap_sql_queries.py
Add your query definition to the `REQUIRED_QUERIES` list:

```python
class SAPSQLQueryManager:
    REQUIRED_QUERIES = [
        # ... existing queries ...
        {
            "SqlCode": "Your_Query_Code",
            "SqlName": "Your Query Name",
            "SqlText": "SELECT T0.\"Column\" FROM \"Table\" T0 WHERE T0.\"Field\" = :parameter",
            "ParamList": "parameter"  # Optional, comma-separated if multiple
        }
    ]
```

### Step 2: Restart Application
The new query will be automatically checked and created on next startup.

### Step 3: Verify
Check application logs for confirmation:
```
INFO:root:⚠️ Query 'Your_Query_Code' not found. Creating...
INFO:root:✅ Created SQL query: Your_Query_Code (Your Query Name)
```

## Best Practices

### Query Design
1. **Use Named Parameters**: Always use `:parameterName` syntax for parameters
2. **Specify ParamList**: Include comma-separated parameter names for clarity
3. **Test SQL First**: Test your SQL in SAP B1 before adding to the system
4. **Use Table Aliases**: Use T0, T1, etc. for readability

### Error Handling
- The system gracefully handles SAP B1 unavailability
- Application continues running even if queries cannot be created
- All errors are logged but don't stop application startup

### Security
- SAP B1 credentials are loaded from credential JSON file or environment variables
- Session management handled automatically
- SSL verification disabled for development (configure for production)

## Troubleshooting

### Queries Not Being Created
**Problem**: Queries show as "Failed/Skipped" in summary

**Solutions**:
1. Check SAP B1 credentials in credential.json or environment variables
2. Verify SAP B1 Service Layer is accessible
3. Check user permissions in SAP B1 (user must have rights to create queries)
4. Review application logs for specific error messages

### Query Creation Fails
**Problem**: Specific query fails to create

**Solutions**:
1. Verify SQL syntax is correct for SAP HANA
2. Check parameter names match between SqlText and ParamList
3. Test the query manually in SAP B1 Query Generator
4. Review response error message in logs

### SAP B1 Connection Issues
**Problem**: "SAP B1 login failed" message

**Solutions**:
1. Verify SAP_B1_SERVER URL is correct
2. Check username and password are valid
3. Confirm company database name is correct
4. Ensure SAP B1 Service Layer is running

## Configuration

### Credential File Location
Primary: `C:/tmp/sap_login/credential.json` (Windows) or `/tmp/sap_login/credential.json` (Linux)

### Required Credentials
```json
{
  "SAP_B1_SERVER": "https://your-sap-server:50000",
  "SAP_B1_USERNAME": "manager",
  "SAP_B1_PASSWORD": "your-password",
  "SAP_B1_COMPANY_DB": "YourCompanyDB"
}
```

### Environment Variables (Fallback)
- `SAP_B1_SERVER`
- `SAP_B1_USERNAME`
- `SAP_B1_PASSWORD`
- `SAP_B1_COMPANY_DB`

## Benefits

✅ **Zero Manual Configuration**: No need to manually create queries in SAP B1  
✅ **Consistent Across Environments**: Version-controlled query definitions  
✅ **Automatic Recovery**: Missing queries are recreated automatically  
✅ **Graceful Degradation**: App continues if SAP B1 unavailable  
✅ **Easy Maintenance**: Add new queries by editing one file  
✅ **Error Prevention**: Eliminates "query not found" runtime errors  
✅ **Audit Trail**: Complete logging of query validation and creation  

## Related Documentation
- **MYSQL_MIGRATION_GUIDE_FINAL.md**: Database migration and setup
- **sap_sql_queries.py**: Implementation source code
- **app.py**: Application startup integration
- **sap_integration.py**: SAP B1 API integration

## Summary
The SAP SQL query auto-management system ensures all required queries exist in SAP B1 before the application serves requests, eliminating manual setup and preventing runtime errors due to missing queries.
