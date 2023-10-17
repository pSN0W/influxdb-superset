from data_generator import DataGenerator
from ingestor import Ingestor

CSV_FILE_LOC='src/datatraining.txt'
CIRCULAR_GENERATOR = False
TAGS = ["Occupancy","CO2"]
TIME_DELAY = 0.1

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
    ingestor = Ingestor(
        token=TOKEN,
        org=ORGANISATION,
        url=URL,
        bucket=BUCKET,
        generator=generator
    )
    try:
        ingestor.ingest()
    except KeyboardInterrupt:
        print("Stopping Data Ingestion")
        print("Exiting Gracefully")