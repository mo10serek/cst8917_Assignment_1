import logging
import os
from azure.storage.blob import BlobServiceClient
from io import BytesIO
import azure.functions as func
import azure.durable_functions as df
from azure.functions.decorators.core import DataType
from PIL import Image
import uuid

my_app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
blob_service_client = BlobServiceClient.from_connection_string(os.environ.get("BLOB_STORAGE_ENDPOINT"))

@my_app.function_name(name="blob_trigger")
@my_app.blob_trigger(arg_name="myblob", path="input", connection="BLOB_STORAGE_ENDPOINT")
@my_app.durable_client_input(client_name="client")
async def blob_trigger(myblob: func.InputStream, client):
    logging.info(f"Python blob trigger function processed blob"
                f"Name: {myblob.name}"
                f"Blob Size: {myblob.length} bytes")

    blobName = myblob.name.split("/")[1]
    await client.start_new("process_image", client_input=blobName)

# Orchestrator
@my_app.function_name(name="process_image")
@my_app.orchestration_trigger(context_name="context")
def process_image(context):
    blobName: str = context.get_input()
    
    logging.info(f"got the image")

    first_retry_interval_in_milliseconds = 5000
    max_number_of_attempts = 3
    retry_options = df.RetryOptions(first_retry_interval_in_milliseconds, max_number_of_attempts)

    # Download the PDF from Blob Storage and use Document Intelligence Form Recognizer to analyze its contents.
    logging.info(f"Getting the Metadata")
    imageMetadata = yield context.call_activity_with_retry("extract_metadata", retry_options, blobName)
    logging.info(f"got the metadata of {imageMetadata}")
    # Send the analyzed contents to Azure OpenAI to generate a summary.
    yield context.call_activity_with_retry("send_to_SQL", retry_options, imageMetadata)

    return logging.info(f"Successfully uploaded summary to SQL database")

@my_app.function_name(name="extract_metadata")
@my_app.activity_trigger(input_name='blobName')
def extract_metadata(blobName):
    logging.info(f"in analyze_text activity")
    global blob_service_client
    container_client = blob_service_client.get_container_client("input")
    blob_client = container_client.get_blob_client(blobName)
    blob =  blob_client.download_blob().read()

    image_stream = BytesIO(blob)
    image = Image.open(image_stream)

    image_size_kb = len(image.fp.read()) / 1024

    width, height = image.size

    image_format = image.format

    logging.info(f'image name: {blobName} image size kb: {image_size_kb}, width: {width}, height: {height}, image format: {image_format}')

    image_data = {'image name': blobName, 'image size kb': image_size_kb, 'width': width, 'height': height, 'image format': image_format}

    return image_data

@my_app.function_name(name="send_to_SQL")
@my_app.activity_trigger(input_name='imageMetadata')
@my_app.generic_output_binding(arg_name="toDoItems", type="sql", CommandText="dbo.MetricData", ConnectionStringSetting="SqlConnectionString",data_type=DataType.STRING)
def send_to_SQL(imageMetadata, toDoItems: func.Out[func.SqlRow]):
    logging.info('function is run to processed a request.')
    name = imageMetadata.get("image name")
    size_kb = imageMetadata.get("image size kb")
    width = imageMetadata.get("width")
    height = imageMetadata.get("height")
    image_format = imageMetadata.get("image format")

    if name:
        toDoItems.set(func.SqlRow({"Id": str(uuid.uuid4()),"Name": name, "SizeKB": size_kb, "Width": width, "Height": height, "Format": image_format}))
        return "Metadata send"
    else:
        return "Please pass a name on the query string or in the request body"