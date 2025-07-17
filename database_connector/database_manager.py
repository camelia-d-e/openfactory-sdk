from typing import List
import pyodbc
import os
import time
from init_db.build_bd import main as init_db

class DatabaseManager:
    def __init__(self, database_name, user, password, server=None, max_retries=5, retry_delay=5):
        self.database_name = database_name
        self.user = user
        self.password = password
        self.server = server or os.getenv("SQL_SERVER", "localhost")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.connection = None
        self.create_database_if_not_exists() ##Temporary fix to ensure database exists before connecting
        if not self.connect():
            raise ConnectionError("Failed to connect to the database after retries.")
        try:
            init_db(self.connection, database_name, user, password, server)
            print("Database schema initialized successfully")
        except Exception as e:
            print(f"Database schema initialization failed: {e}")
       
    
    def connect(self):
        """Connect to SQL Server with retry logic"""
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={self.server};"
            f"DATABASE={self.database_name};"
            f"UID={self.user};"
            f"PWD={self.password};"
            f"TrustServerCertificate=yes;"
            f"Connection Timeout=30;"
        )
        
        for attempt in range(self.max_retries):
            try:
                print(f"Attempting to connect to SQL Server (attempt {attempt + 1}/{self.max_retries})")
                print(f"Server: {self.server}")
                print(f"Database: {self.database_name}")
                print(f"User: {self.user}")
                
                self.connection = pyodbc.connect(connection_string)
                print("Database connection established successfully.")
                return True
                
            except pyodbc.Error as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("All connection attempts failed.")
                    return False
        
        return False
    
    def disconnect(self):
        """Disconnect from database"""
        if self.connection:
            self.connection.close()
            print("Database connection closed.")
    
    def create_database_if_not_exists(self):
        """Create database if it doesn't exist"""
        try:
            master_connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE=master;"
                f"UID={self.user};"
                f"PWD={self.password};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            
            master_conn = pyodbc.connect(master_connection_string, autocommit=True)
            cursor = master_conn.cursor()
            
            cursor.execute(f"SELECT name FROM sys.databases WHERE name = '{self.database_name}'")
            if not cursor.fetchone():
                print(f"Creating database: {self.database_name}")
                cursor.execute(f"CREATE DATABASE [{self.database_name}]")
                cursor.commit()
                print(f"Database {self.database_name} created successfully.")
            else:
                print(f"Database {self.database_name} already exists.")
                
            cursor.close()
            master_conn.close()
            
        except Exception as e:
            print(f"Error creating database: {e}")
            return False
        
        return True
    
    def insert_strvalue(self, variable_id, update_value, update_timestamp):
        """Insert new value into StrValue table"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO StrValue (VariableId, Value, Timestamp) VALUES (?, ?, ?)",
                           (variable_id, update_value, update_timestamp))
            cursor.commit()
            cursor.close()
        except Exception as e:
            print(f"Error updating variable {variable_id}: {e}")

    def fetch_all_assets(self) -> List[str]:
        """Fetch all assets from the database"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT AssetUuid FROM OpenFactoryLink ")
            assets = []
            for row in cursor:
                assets = [elem for elem in row]
            cursor.close()
            return assets
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return []
    
    def fetch_variable_id(self, asset_uuid: str, dataitem_id: str) -> str:
        """Fetch VariableId from DataitemId"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT VariableId FROM OpenFactoryLink WHERE DataitemId = ? AND AssetUuid = ?", (dataitem_id, asset_uuid))
            variable_id = []
            for row in cursor:
                variable_id = [elem for elem in row]
            cursor.close()
            return variable_id[0]
        except Exception as e:
            print(f"Error fetching variable_id: {e}")
            return ''
        
    def fetch_type(self, variable_id: str) -> str:
        """Fetch data Type from VariableId"""
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT Nom FROM Type WHERE Id = (SELECT TypeId FROM Variable WHERE Id = ?)", (variable_id))
            datatype = []
            for row in cursor:
                datatype = [elem for elem in row]
            cursor.close()
            return datatype[0]
        except Exception as e:
            print(f"Error fetching variable_id: {e}")
            return ''