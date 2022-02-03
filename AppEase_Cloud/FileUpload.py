import os
from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient

CONNECTION_STRING = "HostName=AppEase-IoT-hub.azure-devices.net;DeviceId=AppEaseDeviceID;SharedAccessKey=55Qnee+A5BbHBSCCczNr5ekT7rveUiRWZ1eRAcvUn5U="
PATH_TO_FILE = r"/Users/sabrinazhang/Documents/ITP/Appease_Summer2021/AppEase_Cloud/Sample_Data/random_labels.json"


def store_blob(blob_info, file_name):
    try:
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"],
            blob_info["containerName"],
            blob_info["blobName"],
            blob_info["sasToken"]
        )

        print("\nUploading file: {} to Azure Storage as blob: {} in container {}\n".format(
            file_name, blob_info["blobName"], blob_info["containerName"]))

        # Upload the specified file
        with BlobClient.from_blob_url(sas_url) as blob_client:
            with open(file_name, "rb") as f:
                result = blob_client.upload_blob(f, overwrite=True)
                return (True, result)

    except FileNotFoundError as ex:
        # catch file not found and add an HTTP status code to return in notification to IoT Hub
        ex.status_code = 404
        return (False, ex)

    except AzureError as ex:
        # catch Azure errors that might result from the upload operation
        return (False, ex)


def run_sample(device_client):
    # Connect the client
    device_client.connect()

    # Get the storage info for the blob
    blob_name = os.path.basename(PATH_TO_FILE)
    storage_info = device_client.get_storage_info_for_blob(blob_name)

    # Upload to blob
    success, result = store_blob(storage_info, PATH_TO_FILE)

    if success == True:
        print("Upload succeeded. Result is: \n")
        print(result)
        print()

        device_client.notify_blob_upload_status(
            storage_info["correlationId"], True, 200, "OK: {}".format(
                PATH_TO_FILE)
        )

    else:
        # If the upload was not successful, the result is the exception object
        print("Upload failed. Exception is: \n")
        print(result)
        print()

        device_client.notify_blob_upload_status(
            storage_info["correlationId"], False, result.status_code, str(
                result)
        )


def main():
    device_client = IoTHubDeviceClient.create_from_connection_string(
        CONNECTION_STRING)

    try:
        print("IoT Hub file upload sample, press Ctrl-C to exit")
        run_sample(device_client)
    except KeyboardInterrupt:
        print("IoTHubDeviceClient sample stopped")
    finally:
        # Graceful exit
        device_client.shutdown()


if __name__ == "__main__":
    main()
