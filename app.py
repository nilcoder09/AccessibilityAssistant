from doctest import debug
from flask import Flask, request, jsonify, render_template
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
import os
from flask import Flask
endpoint = "YOUR_ENDPOINT_URL"
subscription_key = "YOUR_SUBSCRIPTION_KEY"

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/image_upload', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        # Handle image upload here
        # You can save the uploaded image file if needed
        return render_template('picture.html')
    else:
        return render_template('picture.html')


@app.route('/image_recognition_results', methods=['POST'])
def image_recognition_results():
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        image_file = request.files['image']
        image_data = image_file.read()
        image_features = [VisualFeatureTypes.tags, VisualFeatureTypes.description]

        # Analyze image using Azure Computer Vision API
        analysis = computervision_client.analyze_image_in_stream(image_data, visual_features=image_features)

        # Extract relevant information from analysis
        tags = [tag.name for tag in analysis.tags]
        description = analysis.description.captions[0].text if analysis.description.captions else "No description available"

        # Render HTML template with image recognition results
        return render_template('image_recognition_results.html', tags=tags, description=description)


if __name__ == '__main__':
    app.run(debug=True)