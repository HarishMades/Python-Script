from function import *

from variable import *

scraping_website()
upload_to_s3_and_host(LOCAL_FILENAME, BUCKET_NAME, AWS_REGION)