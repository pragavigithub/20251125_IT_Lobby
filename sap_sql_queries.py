import requests
import logging
import urllib3
from credential_loader import load_credentials_from_json, get_credential

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class SAPSQLQueryManager:
    """Manages SAP B1 SQL Queries - ensures required queries exist on application startup"""
    
    REQUIRED_QUERIES = [
        {
            "SqlCode": "Series_Validation",
            "SqlName": "Seriel_Validation",
            "SqlText": "SELECT T0.\"ItemCode\", T0.\"DistNumber\", T1.\"WhsCode\" FROM \"OSRN\" T0  INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" WHERE  T1.\"Quantity\" >'0'AND T1.\"ItemCode\" =:itemCode AND T0.\"DistNumber\"=:series AND T1.\"WhsCode\"=:whsCode"
        },
        {
            "SqlCode": "Quantity_Check",
            "SqlName": "Quantity_Check",
            "SqlText": "SELECT Distinct T1.\"OnHand\", T0.\"ItemCode\", T0.\"ManSerNum\" FROM \"OITM\" T0  INNER JOIN \"OITW\" T1 ON T0.\"ItemCode\" = T1.\"ItemCode\" WHERE T1.\"OnHand\" >'0' AND  T1.\"WhsCode\" =:whCode AND  T0.\"ItemCode\" =:itemCode",
            "ParamList": "whCode,itemCode"
        },
        {
            "SqlCode": "ItemCode_Validation",
            "SqlName": "ItemCode_Validation",
            "SqlText": "SELECT Distinct T0.\"ItemCode\",T0.\"itemName\", T0.\"DistNumber\", T1.\"WhsCode\" FROM \"OSRN\" T0  INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" WHERE  T1.\"Quantity\" >'0' AND T0.\"ItemCode\"=:item_code AND T1.\"WhsCode\"=:whcode"
        },
        {
            "SqlCode": "Item_Validation",
            "SqlName": "Item_Validation",
            "SqlText": "SELECT Distinct T0.\"ItemCode\",T0.\"itemName\", T0.\"DistNumber\", T1.\"WhsCode\" FROM \"OSRN\" T0  INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" WHERE  T1.\"Quantity\" >'0' AND T0.\"DistNumber\"=:seriel_number AND T1.\"WhsCode\"=:whcode"
        },
        {
            "SqlCode": "Get_SO_Details",
            "SqlName": "Get_SO_Details",
            "SqlText": "SELECT T0.\"DocEntry\" FROM \"ORDR\" T0 INNER JOIN \"NNM1\" T1 ON T0.\"Series\" = T1.\"Series\" WHERE T0.\"DocNum\" =:SONumber AND  T1.\"Series\"=:Series"
        },
        {
            "SqlCode": "Invoise_creation",
            "SqlName": "Invoise_creation",
            "SqlText": "SELECT DISTINCT T0.\"ItemCode\",T0.\"itemName\", T0.\"DistNumber\", T2.\"WhsCode\",T2.\"WhsName\",T3.\"BPLName\",T2.\"BPLid\" FROM \"OSRN\" T0 INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" INNER JOIN \"OWHS\" T2 ON T2.\"WhsCode\"=T1.\"WhsCode\" INNER JOIN \"OBPL\" T3 ON T3.\"BPLId\"=T2.\"BPLid\"WHERE  T1.\"Quantity\" >'0'AND T0.\"DistNumber\"=:serial_number"
        },
        {
            "SqlCode": "Get_SO_Series",
            "SqlName": "Get_SO_Series",
            "SqlText": "SELECT T0.\"SeriesName\", T0.\"Series\" FROM \"NNM1\" T0 WHERE T0.\"ObjectCode\" = '17'"
        },
        {
            "SqlCode": "Get_Item",
            "SqlName": "Get_Item",
            "SqlText": "SELECT DISTINCT T0.\"ItemCode\", T0.\"ItemName\" FROM \"OITM\" T0  INNER JOIN \"OITW\" T1 ON T0.\"ItemCode\" = T1.\"ItemCode\" WHERE T1.\"OnHand\" >'0' AND  T0.\"ManBtchNum\" ='N'AND T1.\"WhsCode\" =:whcode"
        },
        {
            "SqlCode": "Checkseries",
            "SqlName": "Checkseries",
            "SqlText": "SELECT T0.\"ItemCode\", T0.\"DistNumber\", T1.\"WhsCode\" FROM \"OSRN\" T0  INNER JOIN \"OSRQ\" T1 ON T0.\"AbsEntry\" =T1.\"MdAbsEntry\" WHERE T1.\"ItemCode\" =:Itemcode AND T0.\"DistNumber\"=:Serials AND T1.\"WhsCode\"=:Whscode"
        },
        {
            "SqlCode": "GetItemWarehouseSerialStatus_i",
            "SqlName": "Get Item Warehouse Serial Status_i",
            "SqlText": "SELECT \"OSRN\".\"ItemCode\", \"OSRN\".\"DistNumber\" AS \"SerialNumber\", \"OSRQ\".\"WhsCode\" AS \"WarehouseCode\", \"OSRQ\".\"Quantity\" AS \"QtyInWhs\" FROM \"OSRN\" INNER JOIN \"OSRQ\" ON \"OSRN\".\"SysNumber\" = \"OSRQ\".\"SysNumber\" AND \"OSRN\".\"ItemCode\" = \"OSRQ\".\"ItemCode\" WHERE \"OSRN\".\"ItemCode\" = :ItemCode AND \"OSRN\".\"DistNumber\" = :SerialNumber AND \"OSRQ\".\"WhsCode\" = :WarehouseCode AND \"OSRQ\".\"Quantity\" > 0"
        }
    ]
    
    def __init__(self):
        credentials = load_credentials_from_json()
        self.base_url = get_credential(credentials, 'SAP_B1_SERVER', '')
        self.username = get_credential(credentials, 'SAP_B1_USERNAME', '')
        self.password = get_credential(credentials, 'SAP_B1_PASSWORD', '')
        self.company_db = get_credential(credentials, 'SAP_B1_COMPANY_DB', '')
        self.session = requests.Session()
        self.session.verify = False
        self.session_id = None
        
    def login(self):
        """Login to SAP B1 Service Layer"""
        if not self.base_url or not self.username or not self.password or not self.company_db:
            logging.warning("⚠️ SAP B1 configuration incomplete. Skipping SQL query validation.")
            return False
            
        login_url = f"{self.base_url}/b1s/v1/Login"
        login_data = {
            "UserName": self.username,
            "Password": self.password,
            "CompanyDB": self.company_db
        }
        
        try:
            response = self.session.post(login_url, json=login_data, timeout=30)
            if response.status_code == 200:
                self.session_id = response.json().get('SessionId')
                logging.info("✅ SAP B1 login successful for SQL query validation")
                return True
            else:
                logging.warning(f"⚠️ SAP B1 login failed: {response.status_code}")
                return False
        except Exception as e:
            logging.warning(f"⚠️ SAP B1 login error: {str(e)}")
            return False
    
    def check_query_exists(self, sql_code):
        """Check if a SQL query exists in SAP B1"""
        try:
            url = f"{self.base_url}/b1s/v1/SQLQueries('{sql_code}')"
            headers = {
                'Cookie': f'B1SESSION={self.session_id}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                return True
            elif response.status_code == 404 or (response.status_code >= 400 and "No matching records found" in response.text):
                return False
            else:
                logging.warning(f"⚠️ Unexpected response checking query '{sql_code}': {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Error checking query '{sql_code}': {str(e)}")
            return None
    
    def create_query(self, query_definition):
        """Create a SQL query in SAP B1"""
        try:
            url = f"{self.base_url}/b1s/v1/SQLQueries"
            headers = {
                'Cookie': f'B1SESSION={self.session_id}',
                'Content-Type': 'application/json'
            }
            
            response = self.session.post(url, headers=headers, json=query_definition, timeout=10)
            
            if response.status_code in [200, 201, 204]:
                logging.info(f"✅ Created SQL query: {query_definition['SqlCode']} ({query_definition['SqlName']})")
                return True
            else:
                logging.error(f"❌ Failed to create query '{query_definition['SqlCode']}': {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logging.error(f"❌ Error creating query '{query_definition['SqlCode']}': {str(e)}")
            return False
    
    def validate_and_create_queries(self):
        """Main method: Check all required queries and create missing ones"""
        if not self.login():
            logging.warning("⚠️ Skipping SAP SQL query validation - SAP B1 not available")
            return False
        
        logging.info("🔍 Starting SAP B1 SQL query validation...")
        
        queries_checked = 0
        queries_created = 0
        queries_existing = 0
        queries_failed = 0
        
        for query_def in self.REQUIRED_QUERIES:
            sql_code = query_def['SqlCode']
            queries_checked += 1
            
            exists = self.check_query_exists(sql_code)
            
            if exists is True:
                queries_existing += 1
                logging.debug(f"✓ Query '{sql_code}' already exists")
            elif exists is False:
                logging.info(f"⚠️ Query '{sql_code}' not found. Creating...")
                if self.create_query(query_def):
                    queries_created += 1
                else:
                    queries_failed += 1
            else:
                queries_failed += 1
                logging.warning(f"⚠️ Could not verify query '{sql_code}'")
        
        logging.info(f"📊 SQL Query Validation Summary:")
        logging.info(f"   - Total queries checked: {queries_checked}")
        logging.info(f"   - Existing queries: {queries_existing}")
        logging.info(f"   - Newly created queries: {queries_created}")
        logging.info(f"   - Failed/Skipped: {queries_failed}")
        
        return queries_failed == 0


def initialize_sap_queries():
    """Initialize SAP B1 SQL queries on application startup"""
    try:
        manager = SAPSQLQueryManager()
        manager.validate_and_create_queries()
    except Exception as e:
        logging.error(f"❌ Error initializing SAP SQL queries: {str(e)}")
        logging.warning("⚠️ Application will continue without SAP query validation")
