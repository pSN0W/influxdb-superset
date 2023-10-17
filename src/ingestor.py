from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from data_generator import DataGenerator

class Ingestor:
    
    def __init__(self, 
                 token: str,
                 org: str,
                 url: str, 
                 bucket: str, 
                 generator: DataGenerator) -> None:
        """Ingestor is used to ingest the data in influxdb

        Args:
            token (str): The token being used for authentication
            org (str): The organisation of the user
            url (str): The url to access the influxdb
            bucket (str): The bucket used for storage of the data
            generator (DataGenerator): A generator whose get function can be called to get a datapoint
        """ 
        
        self.generator = generator
        self.bucket = bucket
        self.org = org
        
        self.client = InfluxDBClient(url=url, token=token, org=org)
        
    def ingest(self) -> None:
        with self.client.write_api(write_options=SYNCHRONOUS) as write_client:
            for point in self.generator.get():
                write_client.write(
                    bucket=self.bucket,
                    org=self.org,
                    record=point
                )