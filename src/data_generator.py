from datetime import datetime
import time

from influxdb_client import Point
import pandas as pd

class DataGenerator:

    def __init__(self,
                 file_loc: str,
                 measurment: str,
                 tags: list[str],
                 time_delay=1,
                 circular_generator=False) -> None:
        """DataGenerator is used to generate the data from a csv

        Args:
            file_loc (str): Location of the csv file to generate data from
            measurment (str): Name of the table where we want to place the data
            tag (list[str]): Columns used as tag, should not be date
            time_delay (int, optional): Delay for each datapoint. Defaults to 1.
            circular_generator (bool, optional): Whether to generate data from start again. Defaults to False.
        """
        self.measurment = measurment
        self.tags = tags
        self.time_delay = time_delay
        self.circular_generator = circular_generator
        
        df = pd.read_csv(file_loc)
        if "date" in df.columns:
            df.drop(columns=["date"],inplace=True)
        
        self.data = df
        self.columns = list(set(df.columns) - set(self.tags))
        
    def get(self) -> Point:
        idx = 0
        
        while idx < len(self.data):
            values = self.data.iloc[idx].to_dict()
            idx+=1
            if self.circular_generator and idx == len(self.data):
                idx = 0
            
            print(f"{idx}/{len(self.data)}")
            
            tags_values = {tag_name:values[tag_name] for tag_name in self.tags}
            field_values = {field_name: values[field_name] for field_name in self.columns}
            
            point = Point.from_dict({
                "measurement": self.measurment,
                "tags": tags_values,
                "fields": field_values,
                "time": datetime.now()
            })
            
            yield point
            
            time.sleep(self.time_delay)