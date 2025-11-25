#!/usr/bin/env python3
"""
MySQL Migration - BPL and Barcode Fields for Serial Item Transfer Module
November 2025 - SAP B1 Integration Enhancement

This migration adds Business Place (BPL) fields and barcode audit trail support
to the Serial Item Transfer module based on the new specification requirements.

CHANGES:
1. Add bpl_id and bpl_name to serial_item_transfers table (document-level)
2. Add barcode field to serial_item_transfer_items table (for audit trail)
3. Add performance index on (serial_item_transfer_id, item_code)

Run: python mysql_bpl_barcode_migration.py
"""

import os
import sys
import logging
import pymysql
from pymysql.cursors import DictCursor
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BPLBarcodeMigration:
    def __init__(self):
        self.connection = None
        
    def get_mysql_config(self):
        """Get MySQL configuration from environment or defaults"""
        config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': int(os.getenv('MYSQL_PORT', '3306')),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', ''),
            'database': os.getenv('MYSQL_DATABASE', 'wms_db_dev'),
            'charset': 'utf8mb4',
            'autocommit': False
        }
        return config
    
    def connect(self, config):
        """Connect to MySQL database"""
        try:
            self.connection = pymysql.connect(
                host=config['host'],
                port=config['port'],
                user=config['user'],
                password=config['password'],
                database=config['database'],
                charset=config['charset'],
                cursorclass=DictCursor,
                autocommit=config['autocommit']
            )
            logger.info(f"✅ Connected to MySQL: {config['database']} at {config['host']}:{config['port']}")
            return True
        except Exception as e:
            logger.error(f"❌ MySQL connection failed: {e}")
            return False
    
    def execute_query(self, query, params=None):
        """Execute query with error handling"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, params)
                if query.strip().upper().startswith('SELECT'):
                    return cursor.fetchall()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"❌ Query failed: {e}")
            self.connection.rollback()
            raise
    
    def table_exists(self, table_name):
        """Check if table exists"""
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.tables 
        WHERE table_schema = DATABASE() AND table_name = %s
        """
        result = self.execute_query(query, [table_name])
        return result[0]['count'] > 0
    
    def column_exists(self, table_name, column_name):
        """Check if column exists in table"""
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.columns 
        WHERE table_schema = DATABASE() 
        AND table_name = %s 
        AND column_name = %s
        """
        result = self.execute_query(query, [table_name, column_name])
        return result[0]['count'] > 0
    
    def index_exists(self, table_name, index_name):
        """Check if index exists on table"""
        query = """
        SELECT COUNT(*) as count 
        FROM information_schema.statistics 
        WHERE table_schema = DATABASE() 
        AND table_name = %s 
        AND index_name = %s
        """
        result = self.execute_query(query, [table_name, index_name])
        return result[0]['count'] > 0
    
    def add_bpl_fields_to_header(self):
        """Add BPL (Business Place) fields to serial_item_transfers table"""
        logger.info("📝 Adding BPL fields to serial_item_transfers table...")
        
        if not self.table_exists('serial_item_transfers'):
            logger.error("❌ Table 'serial_item_transfers' does not exist. Run main migration first.")
            return False
        
        # Add bpl_id column
        if not self.column_exists('serial_item_transfers', 'bpl_id'):
            query = """
            ALTER TABLE serial_item_transfers 
            ADD COLUMN bpl_id INT NULL 
            COMMENT 'Business Place ID from SAP B1 (set from first validated scan)'
            AFTER to_warehouse
            """
            self.execute_query(query)
            logger.info("✅ Added column: bpl_id to serial_item_transfers")
        else:
            logger.info("⏭️  Column bpl_id already exists in serial_item_transfers")
        
        # Add bpl_name column
        if not self.column_exists('serial_item_transfers', 'bpl_name'):
            query = """
            ALTER TABLE serial_item_transfers 
            ADD COLUMN bpl_name VARCHAR(200) NULL 
            COMMENT 'Business Place Name for UI display'
            AFTER bpl_id
            """
            self.execute_query(query)
            logger.info("✅ Added column: bpl_name to serial_item_transfers")
        else:
            logger.info("⏭️  Column bpl_name already exists in serial_item_transfers")
        
        return True
    
    def add_barcode_field_to_items(self):
        """Add barcode field to serial_item_transfer_items table"""
        logger.info("📝 Adding barcode field to serial_item_transfer_items table...")
        
        if not self.table_exists('serial_item_transfer_items'):
            logger.error("❌ Table 'serial_item_transfer_items' does not exist. Run main migration first.")
            return False
        
        # Add barcode column
        if not self.column_exists('serial_item_transfer_items', 'barcode'):
            query = """
            ALTER TABLE serial_item_transfer_items 
            ADD COLUMN barcode VARCHAR(100) NULL 
            COMMENT 'Scanned barcode in barcode mode (for audit trail)'
            AFTER serial_number
            """
            self.execute_query(query)
            logger.info("✅ Added column: barcode to serial_item_transfer_items")
        else:
            logger.info("⏭️  Column barcode already exists in serial_item_transfer_items")
        
        return True
    
    def add_performance_index(self):
        """Add performance index for item lookup"""
        logger.info("📝 Adding performance index to serial_item_transfer_items table...")
        
        index_name = 'idx_serial_item_transfer_item_lookup'
        
        if not self.index_exists('serial_item_transfer_items', index_name):
            query = f"""
            CREATE INDEX {index_name} 
            ON serial_item_transfer_items (serial_item_transfer_id, item_code)
            """
            self.execute_query(query)
            logger.info(f"✅ Created index: {index_name}")
        else:
            logger.info(f"⏭️  Index {index_name} already exists")
        
        return True
    
    def verify_changes(self):
        """Verify all changes were applied successfully"""
        logger.info("🔍 Verifying migration changes...")
        
        checks = [
            ('serial_item_transfers', 'bpl_id'),
            ('serial_item_transfers', 'bpl_name'),
            ('serial_item_transfer_items', 'barcode')
        ]
        
        all_ok = True
        for table, column in checks:
            if self.column_exists(table, column):
                logger.info(f"✅ Verified: {table}.{column} exists")
            else:
                logger.error(f"❌ Missing: {table}.{column}")
                all_ok = False
        
        # Verify index
        if self.index_exists('serial_item_transfer_items', 'idx_serial_item_transfer_item_lookup'):
            logger.info("✅ Verified: Performance index exists")
        else:
            logger.error("❌ Missing: Performance index")
            all_ok = False
        
        return all_ok
    
    def run_migration(self):
        """Run the BPL and Barcode migration"""
        logger.info("🚀 Starting BPL and Barcode Migration for Serial Item Transfer")
        logger.info("=" * 70)
        
        # Get configuration
        config = self.get_mysql_config()
        
        # Connect to database
        if not self.connect(config):
            logger.error("❌ Migration failed: Could not connect to database")
            return False
        
        try:
            # Add BPL fields to header table
            if not self.add_bpl_fields_to_header():
                return False
            
            # Add barcode field to items table
            if not self.add_barcode_field_to_items():
                return False
            
            # Add performance index
            if not self.add_performance_index():
                return False
            
            # Verify all changes
            if not self.verify_changes():
                logger.error("❌ Migration verification failed")
                return False
            
            logger.info("=" * 70)
            logger.info("🎉 BPL AND BARCODE MIGRATION COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info("✅ Added bpl_id (INT) to serial_item_transfers")
            logger.info("✅ Added bpl_name (VARCHAR) to serial_item_transfers")
            logger.info("✅ Added barcode (VARCHAR) to serial_item_transfer_items")
            logger.info("✅ Added performance index on (serial_item_transfer_id, item_code)")
            logger.info("=" * 70)
            logger.info("📋 NEXT STEPS:")
            logger.info("1. Update application logic to capture BPL from first SAP validation")
            logger.info("2. Validate subsequent scans match the stored BPL ID")
            logger.info("3. Store barcode value in barcode mode for audit purposes")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Migration failed: {e}")
            self.connection.rollback()
            return False
            
        finally:
            if self.connection:
                self.connection.close()
                logger.info("🔐 Database connection closed")


def main():
    """Main entry point"""
    print("🚀 BPL and Barcode Migration for Serial Item Transfer Module")
    print("=" * 70)
    print("This migration adds:")
    print("1. BPL (Business Place) fields to header table")
    print("2. Barcode field to items table for audit trail")
    print("3. Performance index for item lookups")
    print("=" * 70)
    
    # Confirm before running
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        confirm = 'yes'
    else:
        confirm = input("Do you want to run this migration? (y/N): ")
    
    if confirm.lower() in ['y', 'yes']:
        migration = BPLBarcodeMigration()
        success = migration.run_migration()
        
        if success:
            print("\n✅ Migration completed successfully!")
            print("The Serial Item Transfer module now supports BPL and barcode fields.")
        else:
            print("\n❌ Migration failed!")
            sys.exit(1)
    else:
        print("Migration cancelled.")


if __name__ == '__main__':
    main()
