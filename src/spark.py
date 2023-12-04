from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
from pyspark.sql import SparkSession
from pyspark.ml import Transformer
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import Point
import joblib

BUCKET = "bda"
ORGANISATION = "IIITA"
TOKEN = "my-super-secret-auth-token"
URL = "http://localhost:8086"


class Ingestor:
    def __init__(self, token: str, org: str, url: str, bucket: str) -> None:
        """Ingestor is used to ingest the data in influxdb

        Args:
            token (str): The token being used for authentication
            org (str): The organisation of the user
            url (str): The url to access the influxdb
            bucket (str): The bucket used for storage of the data
            generator (DataGenerator): A generator whose get function can be called to get a datapoint
        """

        self.bucket = bucket
        self.org = org

        self.client = InfluxDBClient(url=url, token=token, org=org)

    def ingest(self, point) -> None:
        with self.client.write_api(write_options=SYNCHRONOUS) as write_client:
            write_client.write(bucket=self.bucket, org=self.org, record=point)


class ScikitLearnLinearModel(Transformer):
    def __init__(self, model_path, scaler_path):
        super(ScikitLearnLinearModel, self).__init__()
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)

    def _transform(self, row):
        # Assuming the data column is named "value" and contains a JSON string
        columns = row["fields"]

        # Vectorize the features
        data = [
            columns["Temperature"],
            columns["Humidity"],
            columns["Light"],
            columns["CO2"],
            columns["HumidityRatio"],
        ]
        scaled_data = self.scaler.transform([data])
        prediction = self.model.predict(scaled_data)[0]

        row["fields"]["linear_prediction"] = prediction
        return row


class ScikitLearnTreeModel(Transformer):
    def __init__(self, model_path):
        super(ScikitLearnTreeModel, self).__init__()
        self.model = joblib.load(model_path)

    def _transform(self, row):
        # Assuming the data column is named "value" and contains a JSON string
        columns = row["fields"]

        # Vectorize the features
        data = [
            columns["Temperature"],
            columns["Humidity"],
            columns["Light"],
            columns["CO2"],
            columns["HumidityRatio"],
        ]
        prediction = self.model.predict([data])[0]

        row["fields"]["tree_prediction"] = prediction
        return row


spark = (
    SparkSession.builder.appName("KafkaToKafka")
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0")
    .getOrCreate()
)

linear_model = ScikitLearnLinearModel(
    model_path="models/linear_model.joblib",
    scaler_path="models/scaler.joblib",
)


tree_model = ScikitLearnTreeModel(model_path="models/tree_model.joblib")
ingestor = Ingestor(token=TOKEN, org=ORGANISATION, url=URL, bucket=BUCKET)


def connector(topic):
    try:
        # Define the schema based on your provided structure
        json_schema = StructType(
            [
                StructField("measurement", StringType(), True),
                StructField(
                    "tags",
                    StructType([StructField("Occupancy", DoubleType(), True)]),
                    True,
                ),
                StructField(
                    "fields",
                    StructType(
                        [
                            StructField("Humidity", DoubleType(), True),
                            StructField("CO2", DoubleType(), True),
                            StructField("Light", DoubleType(), True),
                            StructField("Temperature", DoubleType(), True),
                            StructField("HumidityRatio", DoubleType(), True),
                        ]
                    ),
                    True,
                ),
                StructField("time", StringType(), True),
            ]
        )

        df = (
            spark.readStream.format("kafka")
            .option("kafka.bootstrap.servers", "localhost:29092")
            .option("subscribe", topic)
            .load()
        )

        df = df.selectExpr("CAST(value AS STRING) AS value")
        df = df.withColumn("value", from_json(df["value"], json_schema))
        df = df.selectExpr(
            "value.measurement", "value.tags", "value.fields", "value.time"
        )

        def foreach_writer(row):
            row_dict = row.asDict()
            row_dict["tags"] = row_dict["tags"].asDict()
            row_dict["fields"] = row_dict["fields"].asDict()
            linear_model._transform(row_dict)
            tree_model._transform(row_dict)
            ingestor.ingest(Point.from_dict(row_dict))

            print(row_dict)

        query = df.writeStream.foreach(foreach_writer).outputMode("append").start()

        query.awaitTermination()

    except Exception as e:
        print("Error occurred:", e)
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    connector("StreamToSpark")
