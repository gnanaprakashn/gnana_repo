

### Project Overview

#### Description
This project demonstrates the integration of Snowflake with AWS S3 . It includes setting up Snowflake storage integration, creating a database schema, defining a table structure for marketing data, and implementing a data pipeline for continuous data loading from S3 to Snowflake.

#### Architecture Diagram
![Architecture Diagram](link_to_your_architecture_diagram_image)

#### SQL Setup and Data Pipeline

1. **Setting up Storage Integration**
   ```sql
   use role accountadmin;

   CREATE or replace STORAGE INTEGRATION aws_sf_data
     TYPE = EXTERNAL_STAGE
     STORAGE_PROVIDER = S3
     ENABLED = TRUE
     STORAGE_AWS_ROLE_ARN = 'your_arn'
     STORAGE_ALLOWED_LOCATIONS = ('s3_url');

   desc INTEGRATION aws_sf_data;
   ```

   - **Description**: Creates a storage integration `aws_sf_data` for accessing data stored in AWS S3 using Snowflake.

2. **Creating Database and Schema**
   ```sql
   use role sysadmin;

   create database store;
   use database store;

   create schema superstore;
   use schema superstore;
   ```

   - **Description**: Sets up a new database `store` and schema `superstore` within Snowflake.

3. **Defining Marketing Data Table**
   ```sql
   CREATE TABLE marketingdata (
     ad_id INT NOT NULL,
     xyz_campaign_id INT,
     fb_campaign_id INT,
     age VARCHAR(5),
     gender CHAR(1),
     interest INT,
     Impressions BIGINT,
     Clicks INT,
     Spent DECIMAL(10, 2),
     Total_Conversion INT,
     Approved_Conversion INT,
     PRIMARY KEY (ad_id)
   );

   select * from marketingdata;
   ```

   - **Description**: Creates a table `marketingdata` to store marketing campaign data with specified columns and primary key.

4. **Setting up File Format for CSV Data**
   ```sql
   use role accountadmin;

   CREATE FILE FORMAT csv_load_format
       TYPE = 'CSV' 
       COMPRESSION = 'AUTO' 
       FIELD_DELIMITER = ',' 
       RECORD_DELIMITER = '\n' 
       SKIP_HEADER =1 
       FIELD_OPTIONALLY_ENCLOSED_BY = '\042' 
       TRIM_SPACE = FALSE 
       ERROR_ON_COLUMN_COUNT_MISMATCH = TRUE 
       ESCAPE = 'NONE' 
       ESCAPE_UNENCLOSED_FIELD = '\134' 
       DATE_FORMAT = 'AUTO' 
       TIMESTAMP_FORMAT = 'AUTO';
   ```

   - **Description**: Defines a file format `csv_load_format` for loading CSV data into Snowflake with specific formatting options.

5. **Creating Stage for Loading Data**
   ```sql
   use role accountadmin;

   create or replace stage stg_marketing_csv_dev
     storage_integration = aws_sf_data
     url = 's3_url'
     file_format = csv_load_format;

   list @stg_marketing_csv_dev;
   ```

   - **Description**: Creates a stage `stg_marketing_csv_dev` that references the `aws_sf_data` integration for loading CSV data from AWS S3 into Snowflake.

6. **Creating Data Pipe for Continuous Data Loading**
   ```sql
   create or replace pipe marketing_pipe auto_ingest=true as
     copy into marketingdata from @stg_marketing_csv_dev ON_ERROR = continue;

   select * from marketingdata limit 10;
   ```

   - **Description**: Sets up a pipe `marketing_pipe` for continuous ingestion of data from the `stg_marketing_csv_dev` stage into the `marketingdata` table. Errors are handled with `ON_ERROR = continue`.

#### Usage Instructions

1. **Configure Snowflake Connection**: Modify Snowflake connection parameters (`STORAGE_AWS_ROLE_ARN`, `STORAGE_ALLOWED_LOCATIONS`, etc.) in the SQL scripts according to your AWS and Snowflake configurations.

2. **Execute SQL Scripts**: Run the SQL scripts provided in your Snowflake environment to set up the database, schema, table, file format, stage, and data pipe.

3. **Monitor Data Pipeline**: Monitor the `marketing_pipe` for continuous ingestion of CSV data from S3 into Snowflake's `marketingdata` table.

#### Conclusion
This GitHub repository showcases a robust data pipeline setup using Snowflake, AWS S3,  It enables efficient management, transformation, and analysis of marketing data from CSV files stored in AWS S3, providing insights for business decision-making.

---

Ensure to replace placeholders (`your_arn`, `s3_url`, etc.) with actual values relevant to your setup. This structured explanation will help users understand and effectively utilize your project repository on GitHub.