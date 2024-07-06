from pyspark.sql import SparkSession

spark = SparkSession \
    .builder\
    .appName("summa")\
    .getOrCreate()
SNOWFLAKE_SOURCE_NAME = "net.snowflake.spark.snowflake"
snowflake_database = ""
snowflake_schema = ""
snowflake_table_name = ""

snowflake_option = {
    "sfUrl" : " ",
    "sfUser" :" ",
    "sfPassword" : "" ,
    "sfdatabase":snowflake_database,
    "sfschema":snowflake_schema ,
    "sfWarehouse":""

}

df = spark.read.formate(SNOWFLAKE_SOURCE_NAME).option(**snowflake_option).option("dtable",snowflake_table ).option("autopush","on").load()

a = """ 
select * from table """

a.write.format("snowflake")\
.option(**snowflake_option)\
.option("dtable","output").mode("overwrite")\
.save()
