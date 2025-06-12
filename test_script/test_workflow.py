import os
import time
import requests

API_BASE_URL = "http://api_gateway:8000"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"
STATUS_ENDPOINT = f"{API_BASE_URL}/status"
DOWNLOAD_ENDPOINT = f"{API_BASE_URL}/download"

test_video_path = os.path.join(
    os.path.dirname(__file__), "SampleVideo_1280x720_1mb.mp4"
)
user_id = "45c0d605-4b1f-4aef-bc7a-0ff819c49398"


def test_upload():
    # open test video file in binary mode and send as multipart form-data
    with open(test_video_path, "rb") as f:
        files = {"file": ("SampleVideo_1280x720_1mb.mp4", f, "video/mp4")}
        params = {"user_id": user_id}

        # upload video via POST /upload through API Gateway
        res = requests.post(UPLOAD_ENDPOINT, files=files, params=params)

    print("Upload Response: ", res.status_code, res.json())
    res.raise_for_status()  # throw error if response status not 2xx

    return res.json()["transaction_id"]


def test_query_status_till_completion(user_id, transaction_id, timeout=300, interval=5):
    print("Polling status...")
    params = {"user_id": user_id, "transaction_id": transaction_id}
    elapsed = 0

    # loop to poll status until "Completed" or "Failed" or timeout
    while elapsed < timeout:
        res = requests.get(STATUS_ENDPOINT, params=params)

        res.raise_for_status()  # throw error if response status not 2xx

        status = res.json()["status"]
        print(f"Status after {elapsed}s: {status}")

        if status == "Completed":
            return True
        elif status == "Failed":
            raise Exception("Conversion failed.")

        time.sleep(interval)
        elapsed += interval

    raise TimeoutError("Timed out waiting for conversion to complete.")


def test_download(user_id, transaction_id):
    params = {"user_id": user_id, "transaction_id": transaction_id}

    res = requests.get(DOWNLOAD_ENDPOINT, params=params)

    print("Download Response Status: ", res.status_code)
    res.raise_for_status()  # throw error if response status not 2xx

    # save downloaded converted video
    with open("downloaded.mp4", "wb") as f:
        f.write(res.content)

    print("Download complete and saved to downloaded.mp4")


if __name__ == "__main__":
    print("--- Starting Integration Test ---")

    try:
        # Upload -> Poll Status -> Download file
        transaction_id = test_upload()
        test_query_status_till_completion(user_id, transaction_id)
        test_download(user_id, transaction_id)
    except Exception as e:
        print("Test failed: ", str(e))

    print("--- Test Completed ---")
