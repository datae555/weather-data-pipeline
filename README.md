# weather-data-pipeline
Overview:
This project is an end-to-end automated weather data pipeline built entirely using AWS Serverless services — all within the AWS Free Tier.
It periodically fetches live weather data for selected cities, processes it automatically, and makes it available for querying using Amazon Athena.

| Service               | Purpose                                                            |
| --------------------- | ------------------------------------------------------------------ |
| **Lambda1_FetchRaw**  | Fetches weather data from OpenWeatherMap API and stores JSON in S3 |
| **Lambda2_Transform** | Triggered by S3 upload, transforms JSON → CSV                      |
| **S3**                | Stores raw and clean data                                          |
| **CloudWatch**        | Schedules daily execution                                          |
| **Glue + Athena**     | Schema discovery and SQL querying                                  |



Here is step wise guide to get an idea so that you can also create similar POC :)  
Setup Guide (via AWS Console)
Step 1 — Prerequisites
  Create a free AWS account: https://aws.amazon.com/free
  Get a free OpenWeatherMap API key:
  → https://openweathermap.org/api
  Ensure you have IAM permissions for:
    Lambda
    S3
    CloudWatch
    Glue
    Athena

Step 2 — Create S3 Bucket
Go to S3 Console → Create bucket
Name it: omkar-weather-poc-2025(You can name anything)
Keep defaults and click Create
Inside it, create folders:
weather/raw/
weather/clean/

Step 3 — Create Lambda1_FetchRaw
Purpose: Fetch weather data and store in S3
Go to Lambda Console → Create function
Name: Lambda1_FetchRaw
Permissions:
Create new role with basic Lambda + S3 access
Add environment variables:
| Key           | Value                           |
| ------------- | ------------------------------- |
| `OWM_API_KEY` | `<your OpenWeatherMap API key>` |
| `BUCKET_NAME` | `omkar-weather-poc-2025`        |
| `CITIES`      | `Mumbai,London,New York`        |

Code- Please check Lambda1_FetchRaw code from the repo.
deploy function.


Step 4 — Schedule with CloudWatch
Go to CloudWatch → Rules → Create rule
Event source: Schedule
Choose rate expression → rate(1 day) (or 5 minutes for testing)
Target: select Lambda1_FetchRaw
Click Create rule and ensure it’s Enabled
This automates daily data fetching.


Step 5 — Create Lambda2_Transform
Purpose: Transform JSON → CSV automatically.
Go to Lambda → Create function
Name: Lambda2_Transform
Runtime: Python 3.9 or any newer version
Same IAM role as FetchRaw.
Add environment variable:
| Key           | Value                    |
| ------------- | ------------------------ |
| `BUCKET_NAME` | `omkar-weather-poc-2025` |
Add code: Check Lambda2_Transform code from repo.
Deploy.

Step 6 — Add S3 Trigger
Go to Lambda2_Transform → Configuration → Triggers → Add trigger
Source: S3
Bucket: omkar-weather-poc-2025
Event type: All object create events
Prefix: weather/raw/
Click Add
Now whenever a new raw file arrives, it auto-triggers transformation.


Step 7 — Test End-to-End

Go to Lambda1_FetchRaw → Test → click “Test”
Confirm file created in:
s3://omkar-weather-poc-2025/weather/raw/
Wait a few seconds — transformation runs automatically.
Confirm CSV file in:
s3://omkar-weather-poc-2025/weather/clean/

Logs:
Lambda → Monitor → View logs in CloudWatch Logs
Check both Lambdas for success messages


Step 8 — Query Using Athena
Go to AWS Glue → Crawlers → Create Crawler
Source: s3://omkar-weather-poc-2025/weather/clean/
Create a new database: weather_db
Run crawler → confirm table created.
Go to Athena → Query Editor

You now have a fully queryable weather data lake!
