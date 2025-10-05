import os
import sys
import json
import tempfile
import boto3
import urllib.parse
import requests

s3 = boto3.client("s3")

def uploadToDefectDojo(is_new_import, token, url, product_name, engagement_name, filename):
    """
    Upload Semgrep JSON report to DefectDojo.
    https://semgrep.dev/docs/kb/integrations/defect-dojo-integration
    """
    multipart_form_data = {
        'file': (filename, open(filename, 'rb')),
        'scan_type': (None, 'Semgrep JSON Report'),
        'product_name': (None, product_name),
        'engagement_name': (None, engagement_name),
    }

    endpoint = '/api/v2/import-scan/' if is_new_import else '/api/v2/reimport-scan/'
    r = requests.post(
        url + endpoint,
        files=multipart_form_data,
        headers={
            'Authorization': 'Token ' + token,
        }
    )
    if r.status_code != 201:
        sys.exit(f'Post failed: {r.text}')
    print(r.text)


def lambda_handler(event, context):
    """
    Retrieves Semgrep JSON uploaded via S3 Put event and
    performs new import or reimport to DefectDojo.
    """

    # --- Environment variables ---
    dojo_url         = os.environ["DOJO_URL"]
    dojo_token       = os.environ["DOJO_TOKEN"]
    product_name     = os.environ["PRODUCT_NAME"]
    engagement_name  = os.environ["ENGAGEMENT_NAME"]
    is_new_import    = os.environ.get("IS_NEW_IMPORT", "true").lower() == "true"

    # --- Get bucket and key from S3 event ---
    record = event["Records"][0]
    bucket = record["s3"]["bucket"]["name"]
    key    = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

    # --- Download to temporary file ---
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as tmp:
        tmp_path = tmp.name
    s3.download_file(bucket, key, tmp_path)

    # --- Upload to DefectDojo ---
    try:
        uploadToDefectDojo(
            is_new_import=is_new_import,
            token=dojo_token,
            url=dojo_url,
            product_name=product_name,
            engagement_name=engagement_name,
            filename=tmp_path,
        )
    finally:
        # Clean up temporary file (ignore if fails)
        try:
            os.remove(tmp_path)
        except Exception:
            pass

    return {"status": "ok", "bucket": bucket, "key": key, "import": "new" if is_new_import else "reimport"}
