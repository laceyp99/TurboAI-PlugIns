import openai, os, datetime, requests, json, psutil, wolframalpha

# ALL API KEYS THAT ARE NEEDED FOR THIS SCRIPT 
openai.api_key = os.getenv("OPENAI_API_KEY") # go to https://platform.openai.com/account/api-keys to get your API key
api_key = os.getenv("OpenWeatherAPI_Key")  # Replace with your OpenWeatherMap API key
wolfram_api_key = os.getenv("WolframAPI_Key") # Replace with your Wolfram Alpha API key

messages = [] # initialize an empty list to store the messages

# function calling format for openai's ChatCompletion function
multiple_function_descriptions = [
    {
        "name": "get_weather_info",
        "description": "Gets the current weather of a specific location.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city of the location, ex. Albany",
                    # giving examples like above is optional but seems to help the AI understand the parameters better
                    # also in some cases, it will default to the example parameters if it can't find the parameter in the prompt
                },
                "state": {
                    "type": "string",
                    "description": "The state of the location, ex. New York",
                },
            },
            "required": ["city", "state"], # could just require city but state gets rid of the issue of the same city name in different states
        },
    },
    {
        "name": "answer_complex_question",
        "description": "Gets the answer of a complex mathematical or computational question.", # using wolfram alpha's full result API
        "parameters": {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": "The question that is being asked", # prompt wolfram with practically the inputted prompt
                },
            },
            "required": ["question"],
        },
    },
    {
        "name": "get_battery_info",
        "description": "Gets the current status of the devices battery (the percentage and whether it's charging).",
        "parameters": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "The device that is being checked, ex. laptop",
                },
            },
            "required": [], # no requirements because this param is ultimately a placeholder
            # placeholder is necessary to fufill the correct OpenAI function calling format
        },
    },
    {
        "name": "get_time_and_day", 
        # when using GPT the cutoff date for data is January 2022 (GPT4) or September 2021 (GPT 3.5 turbo)
        # this function allows for the AI to get the current time and day
        "description": "Gets the current time and day.",
        "parameters": {
            "type": "object",
            "properties": {
                "now": {
                    "type": "string",
                    "description": "The current time and day.",
                },
            },
            "required": [], # same situation here as above
        },
    },
]

def get_weather(city, state): # gets the weather data from the OpenWeatherMap API and returns it as a JSON object
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": city,
        "state": state,
        "appid": api_key,
        "units": "metric"
    }
    response = requests.get(base_url, params=params)
    weather_data = response.json()
    return weather_data

def get_weather_info(city, state):
    # Get the weather information
    try:
        weather_data = get_weather(city, state) # JSON formatted data
    except:
        answer = ("Sorry, I couldn't find weather information for that city.")
    if "weather" not in weather_data:
        answer = ("Sorry, I couldn't find weather information for that city.")
    else:
        # parse the weather data
        weather_description = weather_data["weather"][0]["description"]
        temperature_celsius = weather_data["main"]["temp"]
        temperature_fahrenheit = (temperature_celsius * 9/5) + 32
        rounded_temperature = round(temperature_fahrenheit)
        humidity = weather_data["main"]["humidity"]
        # create the answer
        answer = (f"The weather in {city}, {state} is {weather_description}. The temperature is {rounded_temperature} degrees Fahrenheit, and the humidity is {humidity}%.")
    return answer

def get_battery_info(device_name): # added param to use in function calling
    battery = psutil.sensors_battery() # finds battery information of this device the script is running on
    if battery:
        plugged = battery.power_plugged
        percent = battery.percent
        if plugged:
            answer = (f"The {device_name} is plugged in and the battery percentage is {percent}%")
        else:
            answer = (f"The {device_name} is running on battery and the battery percentage is {percent}%")
    else:
        answer = ("Unable to retrieve battery information.")
    return answer

def get_time_and_day(now): # added param to use in function calling 
    # Get the current time and day in readable format
    now = datetime.datetime.now()
    current_time = now.strftime("%I:%M %p")
    current_day = now.strftime("%A, %B %d")
    answer = (f"The current time is {current_time}. Today is {current_day}.")
    return answer

def answer_complex_question(question):
    # Create a Wolfram Alpha client object
    client = wolframalpha.Client(wolfram_api_key)
    response = client.query(question, output='full') # full results API
    if (response['@success'] == True):
        answer = ""  # Initialize an empty string
        numpods = int(response['@numpods']) # number of pods in the response
        for i in range(1, numpods): # iterate through the pods and parse data
            pods = response['pod'][i]
            title = pods['@title']
            answer += f"{title}:\n" # add the title of the pod to the answer
            num_subpods = pods['@numsubpods'] # number of subpods in the pod
            if (num_subpods == 1): # if just one subpod, just parse the data once
                if (pods['subpod']['plaintext'] != None): # add the plaintext to the answer
                    plaintext = pods['subpod']['plaintext']
                    answer += f"{plaintext}\n"
                else: # if there isn't plaintext, it will be an image. add the image source to the answer
                    src = pods['subpod']['img']['@src']
                    answer += f"Image Source: {src}\n"
            else: # if more than one subpod, iterate through the subpods and parse the data
                for p in range(0, num_subpods):
                    if (pods['subpod'][p]['plaintext'] != None):
                        plaintext = pods['subpod'][p]['plaintext']
                        answer += f"{plaintext}\n"
                    else:
                        src = pods['subpod'][p]['img']['@src']
                        answer += f"Image Source: {src}\n"
    else: # wolfram alpha query failed
        answer = "Query failed. Try again."
    return answer

def ask_and_reply(prompt): # the main function that asks the prompt and replies with the answer
    messages.append({"role": "user", "content": prompt}) # add the prompt to the messages list above
    response = openai.ChatCompletion.create( 
        model="gpt-3.5-turbo",
        messages=messages,
        functions = multiple_function_descriptions,
        function_call="auto" # the model can choose which function to call based on the prompt
    )
    # determine whether the model called a function or not
    if "function_call" in response["choices"][0]["message"]:
        chosen_function = eval(response["choices"][0]["message"]["function_call"]["name"])
        # lists the arguments of the function call in a JSON object in the case of multiple arguments
        chosen_args = json.loads(response["choices"][0]["message"]["function_call"]["arguments"]) 
        if (chosen_function == get_weather_info):
            answer = chosen_function(chosen_args["city"], chosen_args["state"])
        elif (chosen_function == get_battery_info):
            if "device" not in chosen_args:     # if the model didn't supply a device, default to "computer"
                answer = chosen_function("computer")
            else:
                answer = chosen_function(chosen_args["device"])
        elif (chosen_function == get_time_and_day):
            if "now" not in chosen_args:        # if the model didn't supply this placeholder param, default to "now"
                answer = chosen_function("now")
            else:
                answer = chosen_function(chosen_args["now"])
        elif (chosen_function == answer_complex_question):
            answer = chosen_function(chosen_args["question"])
        else:   # if the model called a function name that isn't the name of any functions above, answer with an error message
            answer = ("Sorry, I couldn't find that function.") # this shouldn't happen but just in case
    else:
        # this is the case where the model didn't call a function and just responded with a string 
        answer = response["choices"][0]["message"]["content"]
    print(answer) # print the answer for the user to read
    # append the answer to the messages list above for the model to build the conversational context
    messages.append({"role": "assistant", "content": answer})

def main(): # the conversational loop
    while True:
        prompt = input("Enter prompt: ")
        ask_and_reply(prompt)
        next = input("Continue? [y/n] ")
        if next == 'n':
            break
        else:
            continue

if __name__ == "__main__":
    main()