# MySQL Migration Guide - FINAL VERSION

## Overview
This guide consolidates ALL MySQL migration needs into a single comprehensive script. All duplicate migration files have been removed and replaced with one master migration file.

## Single Migration File
**`mysql_complete_migration_final.py`** - This is the ONLY MySQL migration file you need.

## What It Includes
- ✅ User Management (admin, manager, user, qc roles)
- ✅ Branch Management
- ✅ GRPO (Goods Receipt Purchase Order) with line items
- ✅ Inventory Transfer with line items and warehouse support
- ✅ Serial Number Transfer with warehouse-specific validation (Updated 2025-08-22)
- ✅ Pick List Management with SAP B1 integration (ps_released focus)
- ✅ Pick List Lines and Bin Allocations (SAP B1 compatible)
- ✅ Sales Orders and Sales Order Lines (for enhanced picklist integration)
- ✅ Inventory Counting with line items
- ✅ Bin Scanning with logging
- ✅ QR Code Label printing and tracking
- ✅ Complete indexing for performance
- ✅ Foreign key relationships
- ✅ Default user accounts
- ✅ Comprehensive .env file generation

## Recent Changes (2025-08-22)
### Serial Number Transfer Validation Enhancement
- ✅ Fixed validation logic to properly reject serial numbers not available in FromWarehouse
- ✅ Serial numbers not available in FromWarehouse now display as red with delete option
- ✅ Only serial numbers available in FromWarehouse are marked as valid for stock transfer
- ✅ Fixed import errors in serial number edit functionality

### Serial Transfer Index Page Enhancement
- ✅ Added pagination with configurable rows per page (10, 25, 50, 100)
- ✅ Added search functionality across transfer number, warehouse, and status
- ✅ Added user-based filtering option for admin/manager users
- ✅ Enhanced UI with search controls and pagination navigation
- ✅ Auto-submit filters for better user experience

### Rejected Transfer Reopen Functionality
- ✅ Added "Reopen Transfer" button for rejected transfers
- ✅ Only admin, manager, or transfer owner can reopen rejected transfers
- ✅ Reopening resets status to 'draft' and clears QC rejection data
- ✅ Allows users to modify and resubmit previously rejected transfers
- ✅ Proper permission checking and status validation

## Recent Changes (2025-08-26)
### Performance Optimization for Large Serial Number Batches
- ✅ Implemented batch serial number validation for processing 1000+ serials efficiently
- ✅ Added optimized batch validation functions that process serial numbers in chunks of 100
- ✅ Enhanced SAP B1 integration to support bulk queries reducing processing time from minutes to seconds
- ✅ Added intelligent batch processing with progress tracking and memory management
- ✅ Updated serial transfer functionality to use batch validation for improved performance
- ✅ Migration completed to Replit environment with PostgreSQL support and performance optimizations

## Recent Changes (2025-10-27)
### SAP B1 SQL Query Auto-Initialization
- ✅ Implemented automatic SAP B1 SQL query validation on application startup
- ✅ Application now checks for 10 required SAP queries and creates missing ones automatically
- ✅ Eliminates manual SQL query setup in SAP B1 Service Layer
- ✅ Queries are validated and created before application starts serving requests
- ✅ See **SAP SQL Query Management** section below for details

## How to Run

### Step 1: Prepare MySQL Database
```bash
# Create database in MySQL
mysql -u root -p
CREATE DATABASE wms_db_dev;
exit
```

### Step 2: Run Migration
```bash
python mysql_complete_migration_final.py
```

The script will:
1. Ask for MySQL connection details (host, port, user, password, database)
2. Create comprehensive .env file with all settings
3. Create all 13 WMS tables with proper relationships
4. Insert default users and sample data
5. Remove all duplicate migration files
6. Provide login credentials

### Step 3: Default User Accounts
After migration, you can login with:
- **Admin**: username=`admin`, password=`admin123`
- **Manager**: username=`manager`, password=`manager123`
- **User**: username=`user`, password=`user123`
- **QC**: username=`qc`, password=`qc123`

## Environment Variables
The migration creates a comprehensive .env file with:

### Database Configuration
- `DATABASE_URL` - SQLAlchemy connection string
- `MYSQL_HOST`, `MYSQL_PORT`, `MYSQL_USER`, `MYSQL_PASSWORD`, `MYSQL_DATABASE`

### SAP B1 Integration
- `SAP_B1_SERVER`, `SAP_B1_USERNAME`, `SAP_B1_PASSWORD`, `SAP_B1_COMPANY_DB`
- `SAP_B1_TIMEOUT`, `SAP_B1_VERIFY_SSL`

### Application Settings
- `SESSION_SECRET` - Flask session security
- `FLASK_ENV`, `FLASK_DEBUG`

### Warehouse Settings
- `DEFAULT_WAREHOUSE`, `DEFAULT_BIN_LOCATION`
- `BARCODE_FORMAT`, `QR_CODE_SIZE`, `LABEL_PRINTER_IP`

### Optional Features
- Email configuration for notifications
- Logging configuration
- Backup settings

## Database Schema Overview

### Core Tables
1. **users** - User accounts with roles and permissions
2. **branches** - Multi-branch warehouse support
3. **grpo_documents** + **grpo_line_items** - Purchase receipt processing
4. **inventory_transfer_documents** + **inventory_transfer_line_items** - Stock movements
5. **pick_lists** + **pick_list_lines** + **pick_list_bin_allocations** - SAP B1 compatible picking
6. **sales_orders** + **sales_order_lines** - Sales Order integration for enhanced picklist functionality
7. **inventory_counting_documents** + **inventory_counting_line_items** - Stock counting
8. **bin_scanning_logs** - Barcode scanning history
9. **qr_code_labels** - Label generation and tracking

### Key Features
- **SAP B1 Integration**: Pick lists fully compatible with SAP Business One API
- **ps_released Focus**: Pick list module configured to focus on released items, avoiding closed items
- **Performance Optimized**: Comprehensive indexing on all lookup columns
- **Data Integrity**: Foreign key constraints and proper relationships
- **Audit Trail**: Created/updated timestamps on all tables
- **Multi-warehouse**: Full support for multiple warehouses and bin locations

## Post-Migration Steps

1. **Start Application**:
   ```bash
   python main.py
   ```

2. **Login**: Use admin/admin123 to access the system

3. **Configure SAP B1**: Update .env file with your SAP B1 server details

4. **Test Pick Lists**: The system now focuses on ps_released items from SAP B1

5. **Add Real Users**: Create additional users through the User Management screen

## Troubleshooting

### Connection Issues
- Verify MySQL credentials
- Ensure database exists
- Check MySQL server is running

### Permission Issues
- Ensure MySQL user has CREATE, INSERT, ALTER privileges
- Database user should have full access to the specified database

### SAP B1 Integration
- Verify SAP B1 server URL and credentials in .env
- Test connection from SAP B1 > Pick Lists screen
- Check that pick lists have ps_released status items

## Schema Compatibility
The migration now handles both fresh installations and existing database updates:
- **Fresh Install**: Creates all tables with proper column names
- **Existing Database**: Detects missing columns and adds them safely
- **Mixed Schema**: Handles both `name` and `branch_name` columns in branches table
- **Error Handling**: Graceful fallback if branches table has column mismatches

## Files Removed
The following duplicate migration files have been removed:
- `mysql_migration.py`
- `mysql_complete_migration.py` 
- `mysql_picklist_migration.py`
- `mysql_qr_code_migration.py`
- `mysql_complete_picklist_migration_august_2025.py`
- `run_mysql_picklist_migration.py`
- `complete_mysql_fix.py`
- `fix_mysql_schema.py`
- `setup_mysql_env.py`
- `sync_mysql_changes.py`
- `qr_code_migration.py`
- `fix_picklist_schema.py`

## Quick Fix Tool
If you have an existing database with column issues, run:
```bash
python fix_mysql_branches_schema.py
```
This will add any missing columns to the branches table without data loss.

## SAP SQL Query Management

### Overview
The application automatically validates and creates required SAP B1 SQL queries on startup. This eliminates the need for manual query setup in SAP Business One Service Layer.

### How It Works
1. **Startup Check**: When the application starts, it automatically:
   - Connects to SAP B1 Service Layer
   - Checks for 10 required SQL queries
   - Creates any missing queries automatically
   - Logs the validation results

2. **Required Queries**: The following SQL queries are automatically managed:
   - `Series_Validation` - Validates serial numbers in warehouse
   - `Quantity_Check` - Checks item quantity in warehouse
   - `ItemCode_Validation` - Validates item codes
   - `Item_Validation` - Validates items by serial number
   - `Get_SO_Details` - Retrieves Sales Order details
   - `Invoise_creation` - Invoice creation query
   - `Get_SO_Series` - Gets Sales Order series
   - `Get_Item` - Retrieves items from warehouse
   - `Checkseries` - Checks serial availability
   - `GetItemWarehouseSerialStatus` - Gets item/serial/warehouse status

### Implementation Details

**File**: `sap_sql_queries.py`
- Contains `SAPSQLQueryManager` class
- Automatically invoked on application startup in `app.py`
- Handles login, validation, and query creation

**Startup Integration**: In `app.py`:
```python
# Initialize SAP B1 SQL Queries (validates and creates required queries)
try:
    from sap_sql_queries import initialize_sap_queries
    initialize_sap_queries()
except Exception as e:
    logging.warning(f"⚠️ SAP SQL query initialization skipped: {str(e)}")
```

### Query Validation Process

For each required query:
1. **Check Existence**: GET request to `/b1s/v1/SQLQueries('SqlCode')`
2. **If Exists**: Log as verified ✓
3. **If Missing**: POST query definition to `/b1s/v1/SQLQueries`
4. **Log Results**: Summary shows queries checked, existing, created, and failed

### Adding New Queries

To add additional SAP SQL queries:

1. Edit `sap_sql_queries.py`
2. Add to `REQUIRED_QUERIES` list:
```python
{
    "SqlCode": "Your_Query_Code",
    "SqlName": "Your Query Name",
    "SqlText": "SELECT ... WHERE ... =:param",
    "ParamList": "param1,param2"  # Optional
}
```
3. Restart application - new query will be created automatically

### Monitoring

Check application logs on startup for SQL query validation:
```
🔍 Starting SAP B1 SQL query validation...
✓ Query 'Series_Validation' already exists
⚠️ Query 'NewQuery' not found. Creating...
✅ Created SQL query: NewQuery (New Query Name)
📊 SQL Query Validation Summary:
   - Total queries checked: 10
   - Existing queries: 9
   - Newly created queries: 1
   - Failed/Skipped: 0
```

### Offline Mode

If SAP B1 is not available:
- Application logs a warning and continues
- SQL query validation is skipped
- Application runs normally without SAP integration

### Benefits
- ✅ Zero manual configuration in SAP B1
- ✅ Consistent query definitions across environments
- ✅ Automatic recovery from missing queries
- ✅ Version-controlled query definitions
- ✅ Eliminates "query not found" errors

## Support
If you need to re-run the migration:
```bash
# Drop all tables first (CAREFUL - THIS DELETES DATA!)
mysql -u root -p wms_db_dev -e "SET FOREIGN_KEY_CHECKS = 0; DROP TABLE IF EXISTS users, branches, grpo_documents, grpo_line_items, inventory_transfer_documents, inventory_transfer_line_items, pick_lists, pick_list_lines, pick_list_bin_allocations, inventory_counting_documents, inventory_counting_line_items, bin_scanning_logs, qr_code_labels; SET FOREIGN_KEY_CHECKS = 1;"

# Then re-run migration
python mysql_complete_migration_final.py
```

**This is now your single source of truth for MySQL database setup.**