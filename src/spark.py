from pyspark.sql import SparkSession
from pyspark.sql.functions import expr

spark = SparkSession.builder \
    .appName("KafkaToKafka") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
    .getOrCreate()


def connector(topic):
    try:
        df = spark.readStream.format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:29092") \
            .option("subscribe", topic) \
            .load()

        df = df.selectExpr("CAST(value AS STRING) AS value")
        df = df.withColumn("occupancy", expr("rand()"))

        def foreach_writer(row):
            row_dict = row.asDict()
            print(row_dict)

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

