import boto3
from botocore.exceptions import NoCredentialsError


def upload(local_file, s3_file):

    # This function aims at uploading a file to s3
    # @params
    # local_file: the path to the file to upload
    # s3_file: the destination path of the uploaded file
    # @returns
    # the pre-signed url of the uploaded file on s3

    s3 = boto3.client('s3')
    bucket_name = "jobs-analysis"
    try:
        print("Prcessing upload file")

        s3.upload_file(local_file, bucket_name, s3_file)
        url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={
                'Bucket': bucket_name,
                'Key': s3_file
            },
            ExpiresIn=24 * 3600
        )

        print("Upload Successful", url)
        return url
    except FileNotFoundError:
        raise Exception("The file was not found")
    except NoCredentialsError:
        raise Exception("Credentials not available")
