from pyspark.sql import SparkSession
from pyspark.sql.functions import expr, from_json
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

spark = SparkSession.builder \
    .appName("KafkaToKafka") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()

def connector(topic):
    try:
        # Define the schema based on your provided structure
        json_schema = StructType([
            StructField("measurement", StringType(), True),
            StructField("tags", StructType([
                StructField("Occupancy", DoubleType(), True)
            ]), True),
            StructField("fields", StructType([
                StructField("Humidity", DoubleType(), True),
                StructField("CO2", DoubleType(), True),
                StructField("Light", DoubleType(), True),
                StructField("Temperature", DoubleType(), True),
                StructField("HumidityRatio", DoubleType(), True)
            ]), True),
            StructField("time", StringType(), True)
        ])

        df = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:29092") \
            .option("subscribe", topic) \
            .load()

        df = df.selectExpr("CAST(value AS STRING) AS value")
        df = df.withColumn("value", from_json(df["value"], json_schema))
        df = df.selectExpr("value.measurement", "value.tags", "value.fields", "value.time")

        def foreach_writer(row):
            row_dict = row.asDict()
            row_dict["tags"] = row_dict["tags"].asDict()
            row_dict["fields"] = row_dict["fields"].asDict()


        query = df.writeStream \
            .foreach(foreach_writer) \
            .outputMode("append") \
            .start()

        query.awaitTermination()

    except Exception as e:
        print("Error occurred:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    connector("StreamToSpark")

