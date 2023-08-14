import json
import os

import requests
import urllib.parse
import boto3
from botocore.exceptions import NoCredentialsError


def generate_access_token(client_id, client_secret):
    oauth_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=partenaire"
    headers = {
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    try:
        encoded_data = urllib.parse.urlencode(data)

        response = requests.post(oauth_url, data=encoded_data, headers=headers)
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print("An error occurred during the oauth call:", e)


def upload_file(file_name, destination_name):

    s3 = boto3.client("s3")
    bucket_name = "jobs-analysis"
    try:
        s3.upload_file(file_name, bucket_name, file_name)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': file_name
            },
            ExpiresIn=24 * 3600
        )
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File uploaded successfully"
            })
        }
    except FileNotFoundError as e:
        print("File not found.", e)
    except NoCredentialsError as e:
        print("Check your credentials", e)


def get_jobs_by_domain(domain, creation_date_from, creation_date_to, client_id, client_secret):
    filename = creation_date_to.split("T")[0] + ".json"
    token = generate_access_token(client_id, client_secret)
    bearer = token["access_token"]
    url = "https://api.pole-emploi.io/partenaire/offresdemploi/v2/offres/search"
    query_params = {
        "domaine": domain,
        "minCreationDate": creation_date_from,
        "maxCreationDate": creation_date_to
    }
    headers = {
        "Authorization": f"Bearer {bearer}",
        "Accept": "application/json"
    }
    try:
        response = requests.get(url=url, headers=headers, params=query_params)
        response_data = response.json()
        temp_dir_path = "/tmp/"
        os.makedirs(temp_dir_path, exist_ok=True)
        temp_file_path = os.path.join(temp_dir_path, filename)
        with open(temp_file_path, "w") as json_file:
            json.dump(response_data, json_file)

        return upload_file(file_name=temp_file_path, destination_name=filename)
    except requests.exceptions.RequestException as e:
        print("An error occurred during the api call:", e)
