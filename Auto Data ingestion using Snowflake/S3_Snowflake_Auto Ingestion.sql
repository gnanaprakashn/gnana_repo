use role accountadmin;

CREATE or replace STORAGE INTEGRATION aws_sf_data
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = S3
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'yours arn'
  STORAGE_ALLOWED_LOCATIONS = ('s3 url');

desc INTEGRATION aws_sf_data;

use role sysadmin;

create database store;
use database store;
create schema superstore;

use schema superstore;

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

use role accountadmin;








create or replace stage stg_marketing_csv_dev
storage_integration = aws_sf_data
url = 's3 url'
file_format = csv_load_format;



list @stg_marketing_csv_dev;

create or replace pipe marketing_pipe auto_ingest=true as
copy into marketingdata from @stg_marketing_csv_dev ON_ERROR = continue;

select * from marketingdata limit 10;