# # AppEase IoT data upload to Azure Storage Blobs using MQTT Protocol
# - This script requires an Azure IoT Hub that has been associated with a publicly-accessibly Azure Storage Account Container and contains a device (follow this tutorial to associate them: https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-configure-file-upload).
# - This script also requires that the file to be uploaded is in the local directory.
# - This script should be run by called "python3 client_iot.py [device_conn_str] [file]" where [device_conn_str] is the connection string of the IoT device created on the Azure IoT Hub and [file] is the name of the file in the local directory to be uploaded.

# import packages
from twisted.internet.protocol import DatagramProtocol
from twisted.internet import reactor
from random import randint
import os
from azure.iot.device import IoTHubDeviceClient
from azure.core.exceptions import AzureError
from azure.storage.blob import BlobClient
import sys
file_name = sys.argv[2]

class Client(DatagramProtocol):
    def __init__(self, host, port):
        if host == "localhost":
            host = "127.0.0.1"
            
        self.id = host, port
        self.address = None
        self.server = '127.0.0.1', 9999
        print("Working on id:", self.id)
        
    def startProtocol(self):
        self.transport.write("ready".encode('utf-8'), self.server)
        
    def datagramReceived(self, datagram, addr):
        datagram = datagram.decode('utf-8')
        
        if addr == self.server:
            print("Choose a client from these\n", datagram)
            self.address = input("write host:"), int(input("write port:"))
            reactor.callInThread(self.send_message, 'This is the IoT client')
        else:
            print(addr, ":", datagram)
            if datagram == 'This is the ML client':
                reactor.callInThread(self.send_message, 'Is the model ready?')
            elif datagram == "The model is ready":
                outcome = self.main()
                if outcome:
                    reactor.callInThread(self.send_message, "URL:"+url)
                else:
                    reactor.callInThread(self.send_message, 'IoT upload failed')
    
    def send_message(self, message):
        self.transport.write(message.encode('utf-8'), self.address)
    
    def store_blob(self, blob_info, file_name): # create a function to upload the file to blob storage
        try:
            global url
            url = "https://{}/{}/{}".format(blob_info["hostName"],blob_info["containerName"],blob_info["blobName"])
            sas_url = "https://{}/{}/{}{}".format(blob_info["hostName"],blob_info["containerName"],blob_info["blobName"],blob_info["sasToken"])
            with BlobClient.from_blob_url(sas_url) as blob_client: # Upload the specified file
                with open(file_name, "rb") as f:
                    result = blob_client.upload_blob(f, overwrite=True)
                    return (True, result)
        except FileNotFoundError as ex: # catch file not found and add an HTTP status code to return in notification to IoT Hub
            ex.status_code = 404
            return (False, ex)
        except AzureError as ex: return (False, ex) # catch Azure errors that might result from the upload operation
        
    def main(self): # function to connect the client and upload the file
        try:
            blob_name = os.path.basename(file_name)
            device_client = IoTHubDeviceClient.create_from_connection_string(sys.argv[1])
            device_client.connect() # Connect the client
            storage_info = device_client.get_storage_info_for_blob(blob_name) # Get the storage info for the blob
            success, result = self.store_blob(storage_info, file_name) # Upload to blob
            if success == True:
                outcome = True
                device_client.notify_blob_upload_status(storage_info["correlationId"], True, 200, "OK: {}".format(file_name))
            else : # If the upload was not successful, the result is the exception object
                outcome = False
                device_client.notify_blob_upload_status(storage_info["correlationId"], False, result.status_code, str(result))
        except Exception as ex:
            outcome = False
        finally: device_client.disconnect() # Finally, disconnect the client
        return outcome
    
            
if __name__ == '__main__':
    port = randint(1000,5000)
    reactor.listenUDP(port, Client('127.0.0.1',port))
    reactor.run()
