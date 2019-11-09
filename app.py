# app.py
import os, base64, json, requests
from flask import Flask, render_template, request

# Load system variables with dotenv
from dotenv import load_dotenv
load_dotenv()

# Load keys
endpoint = os.environ["COGSVCS_CLIENTURL"]
key = os.environ["COGSVCS_KEY"]

# Create vision_client
from msrest.authentication import CognitiveServicesCredentials
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import ComputerVisionErrorException

vision_credentials = CognitiveServicesCredentials(key)
vision_client = ComputerVisionClient(endpoint, vision_credentials)

# Create the application
app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    # Load image or placeholder
    image = get_image(request)

    # If it"s a GET, just return the form
    if request.method == "GET":
        return render_template("index.html", image_uri=image.uri)

    # Create a placeholder for messages
    messages = []

    # TODO: Add code to retrieve text from picture
    messages = extract_text_from_image(image.blob, vision_client)

    return render_template("index.html", image_uri=image.uri, messages=messages)

def get_image(request):
    # Helper class 
    from image import Image
    if request.files:
        return Image(request.files["file"])
    else:
        return Image()

def extract_text_from_image(image, client):
    try:
        result = client.recognize_printed_text_in_stream(image=image)

        lines=[]
        if len(result.regions) == 0:
            lines.append("Photo contains no text")
        else:
            for line in result.regions[0].lines:
                text = " ".join([word.text for word in line.words])
                lines.append(text)
        return lines
    except ComputerVisionErrorException as e:
        print(e)
        return ["Computer Vision API error: " + e.message]

    except Exception as e:
        print(e)
        return ["Error calling the Computer Vision API"]
