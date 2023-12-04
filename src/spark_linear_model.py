from pyspark.sql import SparkSession
from pyspark.ml import Pipeline, Transformer
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors
from pyspark.sql.functions import col
import json
import joblib


# Define a custom transformer for applying Scikit-learn model and StandardScaler
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
            columns["HumidityRatio"]
        ]
        print(data)

        # Apply the StandardScaler
        # scaled_data = self.scaler.transform(assembled_data)

        # # Apply the Scikit-learn model
        # predict_udf = col("scaled_features").apply(
        #     lambda x: self.model.predict([x.tolist()])[0]
        # )
        # return scaled_data.withColumn("prediction", predict_udf)


# # Initialize a Spark session
# spark = SparkSession.builder.appName("ModelPrediction").getOrCreate()

# # Paths to the saved Scikit-learn model and StandardScaler
# model_path = "model_filename.joblib"
# scaler_path = "scaler_filename.joblib"

# Assuming your Kafka data is structured as JSON
# schema = StructType(
#     [
#         StructField("id", IntegerType()),
#         StructField("sepal_length", DoubleType()),
#         StructField("sepal_width", DoubleType()),
#         StructField("petal_length", DoubleType()),
#         StructField("petal_width", DoubleType()),
#     ]
# )

# # Create a streaming DataFrame from Kafka
# df = (
#     spark.readStream.format("kafka")
#     .option("kafka.bootstrap.servers", "your_bootstrap_servers")
#     .option("subscribe", "your_topic")
#     .load()
# )

# # Create the custom transformer
# scikit_transformer = ScikitLearnModelTransformer(model_path, scaler_path)

# # Apply the transformation
# result_df = scikit_transformer.transform(df)

# # Display the predictions in a streaming manner
# query = result_df.writeStream.outputMode("append").format("console").start()
# query.awaitTermination()

# # Stop the Spark session
# spark.stop()
