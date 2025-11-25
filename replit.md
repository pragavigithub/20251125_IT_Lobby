# WMS (Warehouse Management System) Application

## Overview
This Flask-based Warehouse Management System integrates with SAP B1 to provide comprehensive inventory management, transfer operations, barcode generation, and invoice creation functionalities. It aims to streamline warehouse processes and enhance operational efficiency with features like serial number tracking, pick list management, and GRPO (Goods Receipt PO) functionality.

## User Preferences
I prefer iterative development with clear, modular code. Please ask before making major architectural changes or introducing new external dependencies. I appreciate detailed explanations for complex solutions. Do not make changes to files related to MySQL if PostgreSQL is the active database.

## System Architecture
The application is built with Flask, utilizing HTML templates with Bootstrap for the frontend. PostgreSQL is used as the primary database, managed by Replit. Authentication is handled via Flask-Login. The system integrates with SAP Business One through a dedicated API. Credentials for SAP B1 and database connections are managed via a JSON file (`C:/tmp/sap_login/credential.json` or `/tmp/sap_login/credential.json`), with environment variables as a fallback. The application is production-ready, configured to run on Gunicorn, and includes file-based logging. Key modules include Inventory Transfer, Serial Item Transfer, Invoice Creation, GRPO, and SO Against Invoice. The UI/UX prioritizes clear, functional design with Bootstrap components.

## Recent Changes

**November 25, 2025**: Implemented Edit and Delete Functionality for Serial Item Transfer Line Items
- ✅ Added edit route (`/items/<int:item_id>/edit`) with comprehensive validation
- ✅ Edit functionality restricted to non-serial items only (serial items must be deleted and re-added)
- ✅ Implemented balanced SAP validation approach:
  - When SAP is online: Enforces stock level validation and blocks exceeding quantities
  - When SAP is offline/unavailable: Allows edits with warning messages to user
  - All validation attempts logged for audit trail
- ✅ Added edit and delete buttons to line items in transfer detail view
- ✅ Created edit modal with read-only item description and editable quantity field
- ✅ Frontend validation prevents editing of serial items with clear user messaging
- ✅ Comprehensive error handling for all scenarios (400/403/503 HTTP status codes)
- ✅ User-friendly error messages with retry guidance for SAP unavailability
- ✅ Security checks enforce draft status and user permissions (owner or admin/manager)
- ✅ Production-ready with proper logging, validation, and offline resilience

**November 22, 2025**: Enhanced Warehouse Assignment Configuration Screen with Pagination and Filtering
- ✅ Added real-time search/filter input for users (searches by username or email)
- ✅ Implemented rows-per-page selector with options: 10, 25, 50, 100 (default: 25)
- ✅ Added pagination controls with Previous/Next buttons and page numbers
- ✅ Shows up to 5 page numbers at a time with ellipsis for large datasets
- ✅ Displays "Showing X to Y of Z users" count that updates based on pagination and filtering
- ✅ Smooth scroll to top when changing pages
- ✅ Zero regressions to existing warehouse assignment modal workflows
- ✅ Production-ready with clean JavaScript implementation

**October 27, 2025 (Evening)**: Fixed User Model is_active Recursion Error
- ✅ Fixed infinite recursion in User model's `is_active` property
- ✅ Removed redundant property decorator that was causing RecursionError
- ✅ Fixed 3 SQL queries using incorrect column name `is_active` instead of `active` for branches table
- ✅ Fixed user edit form to correctly update `user.is_active` instead of non-existent `user.active`
- ✅ Application now starts without errors and user authentication works properly

**October 27, 2025 (Morning)**: SAP B1 SQL Query Auto-Initialization Implemented
- ✅ Implemented automatic SAP B1 SQL query validation and creation on application startup
- ✅ Created `sap_sql_queries.py` module to manage 10 required SAP queries
- ✅ Integrated query validation into `app.py` startup sequence
- ✅ Application automatically checks for required queries and creates missing ones
- ✅ Graceful handling when SAP B1 is not available (offline mode)
- ✅ Updated MySQL migration guide with comprehensive SAP query documentation
- ✅ Zero manual configuration required for SAP SQL queries
- ✅ Queries validated: Series_Validation, Quantity_Check, ItemCode_Validation, Item_Validation, Get_SO_Details, Invoise_creation, Get_SO_Series, Get_Item, Checkseries, GetItemWarehouseSerialStatus

**September 27, 2025**: Successfully imported and configured for Replit environment
- ✅ Created and configured PostgreSQL database connection with Replit's managed database
- ✅ Verified all environment variables (SESSION_SECRET, DATABASE_URL) are properly set
- ✅ Configured Flask app with ProxyFix middleware for Replit proxy environment
- ✅ Set up workflow for frontend on port 5000 with webview output type and proper host binding (0.0.0.0:5000)
- ✅ Configured deployment settings for autoscale deployment target with Gunicorn
- ✅ Verified application startup: PostgreSQL connection successful, all modules registered
- ✅ All database tables created successfully, default admin user and branch configured
- ✅ All modules properly loaded: GRPO, Inventory Transfer, Invoice Creation, Serial Item Transfer, SO Against Invoice
- ✅ Application serving correctly on port 5000 with professional login interface
- ✅ Application is fully functional and production-ready in Replit environment
- ✅ Project import completed successfully

## External Dependencies
- **SAP Business One API**: For integration with SAP B1 for warehouse operations.
- **PostgreSQL**: Replit-managed database for all application data.
- **Flask**: Python web framework.
- **Gunicorn**: WSGI HTTP Server for Python web applications.
- **Flask-Login**: For user authentication and session management.
- **uv package manager**: For managing Python dependencies.
- **Bootstrap**: Frontend styling and components.