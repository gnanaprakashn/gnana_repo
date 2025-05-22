import json
import boto3
import requests
import os


dynamodb = boto3.resource('dynamodb')
TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "ResumeData")  
table = dynamodb.Table(TABLE_NAME)


JOOBLE_API_URL = "https://jooble.org/api/"
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")  


BREVO_API_KEY = os.getenv("BREVO_API_KEY")  
BREVO_URL = "https://api.brevo.com/v3/smtp/email"

def get_job_recommendations(job_role, location):
    """Fetch job recommendations from Jooble API."""
    try:
        if not JOOBLE_API_KEY:
            print("Error: Jooble API Key is missing!")
            return []

        headers = {"Content-Type": "application/json"}
        payload = {"keywords": job_role, "location": location}
        url = f"{JOOBLE_API_URL}{JOOBLE_API_KEY}"

        print(f"Making request to Jooble API: {url} with payload {json.dumps(payload)}")
        response = requests.post(url, headers=headers, json=payload)
        print(f"Jooble API Response: {response.status_code} - {response.text}")

        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if not jobs:
                print("No jobs found for the given role and location.")
            return jobs
        else:
            print(f"Error fetching jobs: {response.text}")
            return []
    except Exception as e:
        print(f"Jooble API Error: {str(e)}")
        return []

def lambda_handler(event, context):
    """AWS Lambda handler function."""
    try:
        print(f"Raw event: {json.dumps(event)}")

        
        if "body" in event:
            try:
                body = json.loads(event["body"]) if isinstance(event["body"], str) else event["body"]
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in request body")
                return generate_response(400, {"error": "Invalid JSON format"})
        else:
            body = event  

        print(f"Parsed body: {json.dumps(body)}")

        name = body.get("name", "Unknown")
        email = body.get("email")
        phone = body.get("phone", "")
        address = body.get("address", "")
        education = body.get("education", {})
        work_experience = body.get("experience", [])
        skills = body.get("skills", [])
        job_role = body.get("jobRole", "Data Scientist")
        job_location = body.get("jobLocation", "India")

        if not email:
            print("Error: Email is required")
            return generate_response(400, {"error": "Email is required"})

        print(f"Fetching jobs for role: {job_role}, location: {job_location}")

        job_recommendations = get_job_recommendations(job_role, job_location)

        item = {
            "email": email,
            "name": name,
            "phone": phone,
            "address": address,
            "education": education,
            "work_experience": work_experience,
            "skills": skills,
            "job_role": job_role,
            "job_location": job_location,
            "job_recommendations": job_recommendations
        }

        table.put_item(Item=item)
        print(f"Stored user data in DynamoDB: {item}")

        
        job_links = [job.get("link", "No link available") for job in job_recommendations]
        email_status = send_email(email, name, job_links)

        return generate_response(200, {
            "message": "Job recommendations retrieved successfully!",
            "jobs": job_recommendations,
            "email_status": email_status
        })

    except Exception as e:
        print(f"Lambda execution error: {str(e)}")
        return generate_response(500, {"error": str(e)})

def send_email(user_email, user_name, job_links):
    """Send job recommendations via Brevo email service"""
    try:
        if not BREVO_API_KEY:
            print("Error: Brevo API Key is missing!")
            return "Brevo API Key missing"

        if not job_links:
            return "No job recommendations found."

        job_list_html = "".join(f'<li><a href="{link}">{link}</a></li>' for link in job_links)
        email_body = f"""
        <p>Hello {user_name},</p>
        <p>Here are some job recommendations for you:</p>
        <ul>{job_list_html}</ul>
        <p>Best of luck!</p>
        """

        email_data = {
            "sender": {"name": "Job Recommender", "email": "nagarajgnana@gmail.com"},
            "to": [{"email": user_email, "name": user_name}],
            "subject": "Your Job Recommendations",
            "htmlContent": email_body
        }

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        response = requests.post(BREVO_URL, headers=headers, json=email_data)
        print(f"Brevo API Response: {response.status_code} - {response.text}")

        if response.status_code == 201:
            return "Email sent successfully!"
        else:
            return f"Failed to send email: {response.text}"
    except Exception as e:
        print("Email sending error:", str(e))
        return f"Email sending error: {str(e)}"

def generate_response(status_code, body):
    """Generate an HTTP response."""
    return {
        "statusCode": status_code,
        "headers": {"Access-Control-Allow-Origin": "*"},
        "body": json.dumps(body)
    }
