import requests
import boto3
import json

# AWS S3 Configuration
BUCKET_NAME = "unique-demo-bucket-12345"     # Replace with your unique bucket name
AWS_REGION = "us-east-1"                     # Replace with your AWS region
LOCAL_FILENAME = "index.html"                # Local file to save the cloned HTML

# Step 1: Scrape the website and save HTML content
def scraping_website():
    url = input("Enter the valid website URL: ")
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors (e.g., 404, 500)
        with open(LOCAL_FILENAME, 'w', encoding='utf-8') as file:
            file.write(response.text)
        print(f"HTML content of {url} has been saved to {LOCAL_FILENAME}")
    except requests.exceptions.RequestException as e:
        print(f"Error fetching the webpage: {e}")

# Step 2: Upload the file to S3 and configure the bucket
def upload_to_s3_and_host(file_name, bucket_name, region):
    try:
        # Create the S3 client
        s3_client = boto3.client("s3", region_name=region)

        # Create the bucket
        try:
            if region == "us-east-1":
                s3_client.create_bucket(Bucket=bucket_name)  # No LocationConstraint for us-east-1
            else:
                s3_client.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )
            print(f"Bucket '{bucket_name}' created successfully.")
        except s3_client.exceptions.BucketAlreadyOwnedByYou:
            print(f"Bucket '{bucket_name}' already exists and is owned by you.")

        # Disable block public access
        s3_client.put_public_access_block(
            Bucket=bucket_name,
            PublicAccessBlockConfiguration={
                "BlockPublicAcls": False,
                "IgnorePublicAcls": False,
                "BlockPublicPolicy": False,
                "RestrictPublicBuckets": False
            }
        )
        print("Public access block disabled for the bucket.")

        # Upload index.html to the bucket
        s3_client.upload_file(
            Filename=file_name,
            Bucket=bucket_name,
            Key="index.html",
            ExtraArgs={"ContentType": "text/html"}
        )
        print(f"File '{file_name}' uploaded to bucket '{bucket_name}'.")

        # Enable static website hosting
        s3_client.put_bucket_website(
            Bucket=bucket_name,
            WebsiteConfiguration={
                'IndexDocument': {'Suffix': 'index.html'},
            }
        )
        print(f"Static website hosting enabled on bucket '{bucket_name}'.")

        # Set bucket policy for public read access
        bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": "*",
                    "Action": "s3:GetObject",
                    "Resource": f"arn:aws:s3:::{bucket_name}/*"
                }
            ]
        }
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(bucket_policy)
        )
        print("Bucket policy applied for public read access.")

        # Get the static website endpoint
        website_endpoint = f"http://{bucket_name}.s3-website-{region}.amazonaws.com"
        print(f"Your website is hosted at: {website_endpoint}")

    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

# Main function
if __name__ == "__main__":
    # Step 1: Scrape the website and save HTML
    scraping_website()

    # Step 2: Upload the cloned website to S3 and configure static hosting
    upload_to_s3_and_host(LOCAL_FILENAME, BUCKET_NAME, AWS_REGION)
