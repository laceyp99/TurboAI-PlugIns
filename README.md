# TurboAI-PlugIns
A python script using OpenAI's 'gpt-3.5-turbo' model that uses function calling to create a plug-in like feature. Linked with Wolfram Alpha, OpenWeather, and other common python libraries, this allows the model to supply users with verified answers as well as real-time data.

## Prerequisites

- Python 3.x
- Multiple common python libraries ('pip install os json requests datetime psutil')
- OpenAI library ('pip install openai')
- Wolfram library ('pip install wolfram')
- OpenAI, Wolfram Alpha, and OpenWeather API keys

## Installation

1. **Clone this repository:**

    ```bash
    git clone https://github.com/laceyp99/TurboAI-PlugIns.git
    cd TurboAI-PlugIns
    ```

2. **Install the required libraries:**

    ```bash
    pip install os json requests datetime psutil openai wolfram
    ```

3. **Get API Keys:**

    - Go to [OpenAI's API Page](https://platform.openai.com/account/api-keys). Login or create an OpenAI account
    - Create an secret key and save it as an eviroment variable on your device as OPENAI_API_KEY.
    - Go to [Wolfram's API Page](https://developer.wolframalpha.com/access). Login or create a free personal Wolfram account.
    - Create an API key and save it as an eviroment variable on your device as WolframAPI_Key.
    - Go to [OpenWeather's API Page](https://home.openweathermap.org/api_keys). Login or create a free personal OpenWeather account.
    - Create an API key and save it as an enviroment variable on your device as OpenWeatherAPI_Key.

## Usage

1. **Run the script:**

    ```bash
    python v1.py
    ```

2. **Enter in a prompt.**

3. **The script will respond in a conversational manner back and forth until the user decides to quit.**

## Pricing

If you read through my write up (which is the file 'TurboAI-PlugIns.pdf' in this repository) you can see that this plug-in feature is usually only available using the GPT 4 model which requires a monthly subscription. This script notably reduces the price. The only cost of running this script is the usage prices that are associated with the respective API keys. OpenWeather and Wolfram both have free plans that come with usage limits. Wolfram has a limit of 2,000 non commercial API calls per month, and OpenWeather limits users to 60 calls per minute. The OpenAI API pricing doesn't have a free plan, but using model 'gpt-3.5-turbo' costs about a tenth of a cent per every thousand tokens which is pretty insignificant for a personal use chatbot.

## Future Improvements

I will be working on adding more useful APIs and other libraries to this script to create a more full rounded AI model. Another improvement I'm looking forward to adding in the next version is reducing the prompt token size with a method to shorten the function calling descriptions passed into the model.
