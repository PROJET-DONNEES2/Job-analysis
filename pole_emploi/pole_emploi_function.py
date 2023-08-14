import json

import requests
import urllib.parse


def generate_access_token():
    oauth_url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=partenaire"
    headers = {
        "Content-type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "client_credentials",
        "client_id": "PAR_donnees2_a6e55f3e89ca02d880edf0078f125ba378595958adc69d39711f50ceecc3d45c",
        "client_secret": "e11090ffa1722172da3fd0399d1f72513e46ba0e43780a658d2f9d84877a4dd6",
        "scope": "api_offresdemploiv2 o2dsoffre"
    }
    try:
        encoded_data = urllib.parse.urlencode(data)

        response = requests.post(oauth_url, data=encoded_data, headers=headers)

        return response.json()
    except requests.exceptions.RequestException as e:
        print("An error occurred during the oauth call:", e)

