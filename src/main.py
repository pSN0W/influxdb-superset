from data_generator import DataGenerator
from ingestor import Ingestor

CSV_FILE_LOC='src/datatraining.txt'
CIRCULAR_GENERATOR = True
TAGS = ["Occupancy"]
TIME_DELAY = 1

BUCKET="bda"
MEASURMENT="bda_project"
ORGANISATION="IIITA"
TOKEN="my-super-secret-auth-token"
URL="http://localhost:8086"

if __name__ == '__main__':
    generator = DataGenerator(
        file_loc=CSV_FILE_LOC,
        measurment=MEASURMENT,
        tags=TAGS,
        time_delay=TIME_DELAY,
        circular_generator=CIRCULAR_GENERATOR
    )
    generator.get()