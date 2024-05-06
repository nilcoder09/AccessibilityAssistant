from doctest import debug
from flask import Flask, request, jsonify, render_template
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import VisualFeatureTypes
from msrest.authentication import CognitiveServicesCredentials
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
import azure.cognitiveservices.speech as speechsdk
import requests


import os
from flask import Flask
endpoint = os.getenv("endpoint")
subscription_key = os.getenv("subscription_key")


computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))
client = ImageAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(subscription_key)
)

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/weather_report', methods=['POST'])
def weather_report():
    # Get the user's location input from the form
    location = request.form.get('location')

    # Call the weather API to fetch the weather forecast for the specified location
    weather_data = fetch_weather_data(location)

    # Process the weather data and extract relevant information
    if weather_data:
        # Extract relevant weather information from the API response
        temperature = weather_data['main']['temp']
        humidity = weather_data['main']['humidity']
        description = weather_data['weather'][0]['description']

        # Construct the weather report message
        report_message = f"The weather in {location} is currently {description} with a temperature of {temperature}°F and humidity of {humidity}%."

        # Generate spoken audio output using Azure Text-to-Speech
        speech_config = speechsdk.SpeechConfig(subscription="", region="eastus")
        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
        result = synthesizer.speak_text_async(report_message).get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            # Save the generated audio to a temporary file
            audio_file_path = 'static/weather_report.wav'
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(result.audio_data)

            # Render the weather report template with the audio file path
            return render_template('weather_report.html', audio_file_path=audio_file_path, weather_data=weather_data)
        else:
            return "Error: Unable to generate audio."

    else:
        # If weather data couldn't be fetched, display an error message
        error_message = f"Could not retrieve weather information for {location}. Please try again later."
        return render_template('weather_report.html', error_message=error_message)



def fetch_weather_data(location):
   # Replace 'YOUR_OPENWEATHERMAP_API_KEY' with your actual OpenWeatherMap API key
    api_key = ''
    # Replace 'YOUR_OPENWEATHERMAP_API_URL' with the base URL of the OpenWeatherMap API
    api_url = 'http://api.openweathermap.org/data/2.5/weather'

    # Construct the API request URL with the location and API key
    params = {'q': location, 'appid': api_key, 'units':'imperial'}

    # Send a GET request to the OpenWeatherMap API
    response = requests.get(api_url, params=params)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON response
        weather_data = response.json()

        # Return the weather data
        return weather_data
    else:
        # If the request was unsuccessful, return None
        return None


if __name__ == '__main__':
    app.run(debug=True)