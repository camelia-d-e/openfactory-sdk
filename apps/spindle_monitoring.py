import time
import csv
from openfactory.apps import OpenFactoryApp
from openfactory.kafka import KSQLDBClient
from openfactory.assets import Asset



class SpindleMonitoring(OpenFactoryApp):

    def __init__(self, app_uuid, ksqlClient, bootstrap_servers, loglevel):
        super().__init__(app_uuid, ksqlClient, bootstrap_servers, loglevel)
        self.ksqlClient = ksqlClient

    def main_loop(self):
        try:
            ivac = Asset('IVAC', ksqlClient=self.ksqlClient)
            
            ivac.subscribe_to_events(on_event, 'ivac_events_group')
            
            self.logger.info("Successfully connected to services and subscribed to events")
            
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("Stopping consumer threads...")
            try:
                ivac.stop_samples_subscription()
                self.logger.info("Consumers stopped")
            except:
                pass
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise

    
        def on_event(self, msg_key, msg_value):
            with open('ivac_events.csv', 'a', newline='') as csvfile:
                fieldnames = []
                for key in msg_value.keys():
                    fieldnames.append(key)

                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                csvfile.seek(0, 2)
                if csvfile.tell() == 0:
                        writer.writeheader()

                writer.writerow(msg_value)
            print(f"[Event] [{msg_key}] {msg_value}")

app = SpindleMonitoring(
    app_uuid='SPINDLE-MONITORING',
    ksqlClient=KSQLDBClient("http://ksqldb-server:8088"),
    bootstrap_servers="broker:29092"
)
app.run()

