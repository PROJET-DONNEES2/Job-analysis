import uuid
import requests
import json
import datetime
from s3_service import upload
import os

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/json"
        },
        "body": json.dumps(get_jobs())
    }


def get_jobs():

    # This function collects the jobs offers in adzuna's database
    # @params
    # any
    # @returns
    # Directly the response body from adzuna when getting the list of job offers

    url = "https://api.adzuna.com/v1/api/jobs/fr/search/10"

    response = requests.get(url)

    if response.status_code == 200:
        response_json = response.json()
        temp_dir_path = "/tmp/adzuna/"

        os.makedirs(temp_dir_path, exist_ok=True)  # Create the directory if it doesn't exist

        # Get the actual date in the following format: YYYY-MM-DD_HH-MM-SS
        current_date = datetime.datetime.now()
        formatted_date = current_date.strftime('%Y-%m-%d_%H-%M-%S')

        generated_uuid = str(uuid.uuid4())

        file_name = f"{formatted_date}-{generated_uuid}.json"

        temp_file_path = os.path.join(temp_dir_path, file_name)

        with open(temp_file_path, 'w') as json_file:
            json.dump(response_json, json_file, indent=4)


        upload(temp_file_path, temp_file_path.lstrip("/tmp/"))

        return response_json

    print("Erreur lors de la requête :", response.status_code)
    return None



if __name__ == '__main__':
    get_jobs()
