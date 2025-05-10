import sys
import json
from pyspark.sql.functions import col, udf, lit, when, get_json_object
from pyspark.sql.types import StringType, DoubleType
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# Initialize Spark and Glue
args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Read CSV from S3
df = spark.read.format("csv").option("header", "true").load("s3://airflow-pratical/files/weather_api_data.csv")

# UDF to extract 'main', 'description', and 'icon' from the weather column
def parse_weather(weather_str, field):
    try:
        weather_json = json.loads(weather_str.replace("'", '"'))
        return weather_json[0].get(field, "")
    except:
        return ""

parse_main_udf = udf(lambda x: parse_weather(x, "main"), StringType())
parse_desc_udf = udf(lambda x: parse_weather(x, "description"), StringType())
parse_icon_udf = udf(lambda x: parse_weather(x, "icon"), StringType())

# Add new weather columns
df = df.withColumn("weather_main", parse_main_udf(col("weather")))
df = df.withColumn("weather_description", parse_desc_udf(col("weather")))
df = df.withColumn("weather_icon", parse_icon_udf(col("weather")))

# Safely extract rain.3h (assumes rain column is a JSON string)
df = df.withColumn(
    "rain_volume_3h",
    when(
        col("rain").isNotNull(),
        get_json_object(col("rain"), "$.3h").cast(DoubleType())
    ).otherwise(lit(0.0))
)

# Select and cast necessary fields
df_cleaned = df.select(
    col("dt").cast("long"),
    col("dt_txt").alias("timestamp"),
    col("visibility").cast("int"),
    col("pop").cast("int"),
    col("`main.temp`").cast("double").alias("temp"),
    col("`main.feels_like`").cast("double").alias("feels_like"),
    col("`main.temp_min`").cast("double").alias("temp_min"),
    col("`main.temp_max`").cast("double").alias("temp_max"),
    col("`main.pressure`").cast("int").alias("pressure"),
    col("`main.sea_level`").cast("int").alias("sea_level"),
    col("`main.grnd_level`").cast("int").alias("ground_level"),
    col("`main.humidity`").cast("int").alias("humidity"),
    col("`main.temp_kf`").cast("double").alias("temp_kf"),
    col("`clouds.all`").cast("int").alias("cloud_coverage"),
    col("`wind.speed`").cast("double").alias("wind_speed"),
    col("`wind.deg`").cast("int").alias("wind_deg"),
    col("`wind.gust`").cast("double").alias("wind_gust"),
    col("`sys.pod`").alias("part_of_day"),
    col("rain_volume_3h"),
    col("weather_main"),
    col("weather_description"),
    col("weather_icon")
)

# Save to a single CSV file with exact name in S3
df_cleaned.coalesce(1).write.mode("append").option("header", "true").csv("s3://weather-cleaned-data/files")

# Commit job
job.commit()
