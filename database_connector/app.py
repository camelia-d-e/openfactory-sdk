import os
import asyncio
from message_handler import MessageHandler
from websocket_client import OpenFactoryWebSocketClient
from database_manager import DatabaseManager

class DatabaseConnectorApp:
    def __init__(self, database_name, user, password, server, websocket_base_url: str = "ws://ofa-api:8000"):
        self.assets = []
        self.websocket_client = OpenFactoryWebSocketClient(websocket_base_url)
        self.db_manager = DatabaseManager(database_name, user, password, server)
    
    async def run(self):
        """Run the application"""
        print("Application is running. Press Ctrl+C to stop.")
        try:
            message_handler = MessageHandler(self.db_manager)

            self.websocket_client.set_message_handler(message_handler.handle_message)

            self.assets = self.db_manager.fetch_all_assets()
            
            await self.websocket_client.start(self.assets)
        except KeyboardInterrupt:
            print("\nShutting down app...")
            self.websocket_client.stop()
            self.db_manager.disconnect()

if __name__ == "__main__":
    DATABASE_NAME = os.getenv("DATABASE_NAME", "mytest")
    WEBSOCKETS_URL = os.getenv("WEBSOCKETS_URL", "ws://ofa-api:8000")
    USER = os.getenv("SQL_USER", "sa")
    PASSWORD = os.getenv("SQL_PASSWORD", "YourStrong@Passw0rd")
    SERVER = os.getenv("SQL_SERVER", "localhost")
    
    print(f"Connecting to database: {DATABASE_NAME}")
    print(f"SQL Server: {SERVER}")
    print(f"WebSocket URL: {WEBSOCKETS_URL}")
    
    try:
        app = DatabaseConnectorApp(DATABASE_NAME, USER, PASSWORD, SERVER, WEBSOCKETS_URL)
        asyncio.run(app.run())
    except Exception as e:
        print(f"Failed to start application: {e}")