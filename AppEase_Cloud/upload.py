from azure.storage.blob import BlobServiceClient

CONNECT_STR = "HostName=appeasecloud.azure-devices.net;DeviceId=mydeviceid;SharedAccessKey=JtfhBmsLTWWriXTJnpOyaJl0KBtYacaMCMtNCol0M9U="
CONTAINER_NAME = "appeasecloudml"
input_file_path = "/Users/sabrinazhang/documents/ITP/Appease_Summer2021/AppEase_Cloud/simulated_health_data.json"
output_blob_name = "output_blob.json"

blob_service_client = BlobServiceClient.from_connection_string(CONNECT_STR)
blob_client = blob_service_client.get_blob_client(
    container=CONTAINER_NAME, blob=output_blob_name)

# Upload file
with open(input_file_path, "rb") as data:
    blob_client.upload_blob(data=data)
