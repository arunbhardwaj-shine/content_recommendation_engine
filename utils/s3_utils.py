import boto3
from botocore.exceptions import ClientError
from typing import Optional
from dotenv import load_dotenv
import os
from urllib.parse import urlparse
import requests
import json
from sqlalchemy import text
from helpers.sql_helpers import docintel_query
load_dotenv()

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION")
STATIC_AUTH = os.getenv("API_AUTH")
INTERNAL_API_URL = os.getenv("API_URL")
PREVIEW_ID = os.getenv("PREVIEW_ID")
class S3Client:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
    def read_bytes(self, bucket: str, key: str) -> Optional[bytes]:
        try:
            response = self.client.get_object(Bucket=bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] in ("NoSuchKey", "404"):
                return None
            raise

    @staticmethod
    def parse_s3_url(s3_url: str):
        parsed = urlparse(s3_url)

        # s3://bucket/key
        if parsed.scheme == "s3":
            return parsed.netloc, parsed.path.lstrip("/")

        host = parsed.netloc
        path = parsed.path.lstrip("/")

        # Virtual-hosted–style
        # bucket.s3.amazonaws.com
        # bucket.s3-eu-west-1.amazonaws.com
        if host.startswith("s3.") is False and ".s3" in host:
            bucket = host.split(".s3", 1)[0]
            return bucket, path

        # Path-style
        # s3.amazonaws.com/bucket/key
        # s3.eu-west-1.amazonaws.com/bucket/key
        if host.startswith("s3"):
            parts = path.split("/", 1)
            if len(parts) != 2:
                raise ValueError("Invalid S3 URL format")
            return parts[0], parts[1]

        raise ValueError(f"Unsupported S3 URL format: {s3_url}")

def fetch_s3_url(payload: dict) -> str:
    try:
        headers = {
            "Authorization": STATIC_AUTH,
            "Content-Type": "application/json"
        }
        response = requests.post(
            INTERNAL_API_URL,
            headers=headers,
            json=payload,
            timeout=100
        )
        if not response.ok:
            return None, {
                "status_code": response.status_code,
                "detail": response.text
            }, [], 0
        response.raise_for_status()
        data = response.json()
        raw_tags = data["data"].get("tags")
        if not raw_tags:
            tags = []
        elif isinstance(raw_tags, list):
            tags = raw_tags
        elif isinstance(raw_tags, str):
            try:
                tags = json.loads(raw_tags)
            except json.JSONDecodeError:
                tags = []
        else:
            tags = []
        print(tags,"tags",type(tags))
        s3_urls = []
        print(data["data"]["file_type"])
        print(data["data"])
        if data["data"]["popup_email_content_language"] != 0:
            return s3_urls,{
            "status_code": 460,
            "detail": "Non English PDF's not supported"
        },tags,len(s3_urls)
        if data["data"]["file_type"] == "pdf":
            s3_urls.append(data["data"]["pdf_link"])
        if data["data"]["file_type"] == "ebook":
            s3_urls.extend(item["file_name"]
            for item in data["data"]["ebook_pdf"]
            if "file_name" in item
            )
        if data["data"]["file_type"] == "video":
            return s3_urls,{
            "status_code": 406,
            "detail": "Video file type not supported"
        },tags,len(s3_urls)
        return s3_urls,None,tags,len(s3_urls)
    except requests.exceptions.RequestException as e:
        return None, {
            "status_code": 502,
            "detail": f"Upstream API error: {str(e)}"
        }, [], 0
    except Exception as e:
        return None, {
            "status_code": 404,
            "detail": f"File Not Found"
        }, [], 0     

def get_bytes_from_url(url: str) -> bytes:
    response = requests.get(url)
    response.raise_for_status()  # Raise error if request failed
    return response.content

def docintel_code_generator(engine, pdf_id: int) -> str | None:
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text(docintel_query),
                {"pdf_id": pdf_id}
            ).mappings().fetchone()

        print(result, "RES")

        if not result:
            return None

        folder_name = result.get("folder_name")
        ibu = result.get("ibu")
        code = result.get("code")

        print(
            f"DocIntel query result for pdf_id={pdf_id}: "
            f"folder_name={folder_name}, code={code}"
        )

        if not folder_name or not code:
            return None

        # Clean IBU if present
        if ibu:
            ibu = ibu.replace(" ", "_").strip()
            return f"https://docintel.app/{ibu}_{folder_name}/{code}{PREVIEW_ID}"

        return f"https://docintel.app/{folder_name}/{code}{PREVIEW_ID}"

    except Exception as e:
        print(str(e), "ERROR")
        return None