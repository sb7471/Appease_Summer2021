
# coding: utf-8

# # AppEase IoT data upload to Azure Storage Blobs using MQTT Protocol
#
# - This notebook requires an Azure IoT Hub that has been associated with
#  an Azure Storage Account Container and contains a device
# (follow this tutorial to associate them: https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-configure-file-upload)
# - This file also requires that the file to be uploaded is in the local directory
# - This script should be run by called "python appease_iot.py [conn_str] [file]"
# - where [device_conn_str] is the connection string of an IoT device created on the Azure IoT Hub and
# - [file] is the name of the file in the local directory to be uploaded.


# import packages
import os
from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient
import sys
file_name = sys.argv[1]


def store_blob(blob_info, file_name):  # create a function to upload the file to blob storage
    try:
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"], blob_info["containerName"], blob_info["blobName"], blob_info["sasToken"])
        print(sas_url)
        print("\nUploading file: {} to Azure Storage as blob: {} in container {}\n".format(
            file_name, blob_info["blobName"], blob_info["containerName"]))
        # Upload the specified file
        with BlobClient.from_blob_url(sas_url) as blob_client:
            with open(file_name, "rb") as f:
                result = blob_client.upload_blob(f, overwrite=True)
                return (True, result)
    except FileNotFoundError as ex:  # catch file not found and add an HTTP status code to return in notification to IoT Hub
        ex.status_code = 404
        return (False, ex)
    except AzureError as ex:
        # catch Azure errors that might result from the upload operation
        return (False, ex)


def main():  # function to connect the client and upload the file
    try:
        print("IoT Hub file upload sample, press Ctrl-C to exit")
        blob_name = os.path.basename(file_name)
        device_client = IoTHubDeviceClient.create_from_connection_string(
            sys.argv[0], websockets=True)
        device_client.connect()  # Connect the client
        storage_info = device_client.get_storage_info_for_blob(
            blob_name)  # Get the storage info for the blob
        sas_url = "https://{}/{}/{}{}".format(
            blob_info["hostName"], blob_info["containerName"], blob_info["blobName"], blob_info["sasToken"])
        print(sas_url)
        success, result = store_blob(storage_info, file_name)  # Upload to blob
        if success == True:
            print("Upload succeeded. Result is: \n")
            print(result)
            print()
            device_client.notify_blob_upload_status(
                storage_info["correlationId"], True, 200, "OK: {}".format(file_name))
        else:  # If the upload was not successful, the result is the exception object
            print("Upload failed. Exception is: \n")
            print(result)
            print()
            device_client.notify_blob_upload_status(
                storage_info["correlationId"], False, result.status_code, str(result))
    except Exception as ex:
        print("\nException:")
        print(ex)
    except KeyboardInterrupt:
        print("\nIoTHubDeviceClient sample stopped")
    # finally: device_client.disconnect() # Finally, disconnect the client


if __name__ == "__main__":
    main()
    #loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    # loop.close()
