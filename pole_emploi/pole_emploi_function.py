import json
import os

import requests
import urllib.parse
import boto3
from botocore.exceptions import NoCredentialsError


def generate_access_token(client_id, client_secret):

    # This function is used to generate an access token through the oauth connexion of Pole Emploi
    # @params
    # client_id: the client access key id
    # client_secret: the client access key secret
    # These parameters are compulsory for this function
    # @return
    # This function returns a json containing the new access_token, the scope, its type and duration

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

    # This function is used to upload a file to s3
    # @params
    # file_name: the path to the file to upload
    # destination_name: the path of the destination directory in the s3 bucket
    # @return
    # it just returns a simple json which says that the file has successfully been uploaded and the presigned url

    s3 = boto3.client("s3")
    bucket_name = "jobs-analysis"
    try:
        s3.upload_file(file_name, bucket_name, destination_name)
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
                "message": f"File uploaded successfully to {url}"
            })
        }
    except FileNotFoundError as e:
        print("File not found.", e)
    except NoCredentialsError as e:
        print("Check your credentials", e)


def get_jobs_by_domain(domain, creation_date_from, creation_date_to, client_id, client_secret):

    # This function is used to get the job offers by its domain (IT, Marketing, ...)
    # @params
    # domain: the domain to filter the job offers
    # creation_date_from and creation_date_to: a range of date between which the job offers have been created
    # client_id: the client access key id
    # client_secret: the client access key secret
    # @returns
    # this just returns the result pf the upload_file function above

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
