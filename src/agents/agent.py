from dotenv import load_dotenv
import os
import requests
from uagents import Agent
from pushbullet import Pushbullet

load_dotenv()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
PUSHBULLET_API_KEY = os.getenv("PUSHBULLET_API_KEY")

if WEATHER_API_KEY is None or PUSHBULLET_API_KEY is None:
    raise ValueError("API keys not found in .env file")

class WeatherAgent(Agent):
    key = WEATHER_API_KEY
    weather_api_url = "http://api.weatherapi.com/v1/forecast.json"

    def __init__(self):
        super().__init__()
        self.pb = Pushbullet(PUSHBULLET_API_KEY)

    def send_notification(self, message):
        self.pb.push_note("Weather Alert", message)

    def forecast(self, data):
        forecast = data["forecast"]["forecastday"]
        forecast_text = ""
        for day in forecast:
            date = day["date"]
            maxtemp_c = day["day"]["maxtemp_c"]
            condition = day["day"]["condition"]["text"]
            forecast_text += f"Date: {date}, Temp: {maxtemp_c}°C, Condition: {condition}\n"
        return forecast_text

    def run(self):
        try:
            print("WeatherAgent is running...")
            while True:
                city = input("Enter a city: ")
                min_temp = float(input("Enter the minimum temperature: "))
                max_temp = float(input("Enter the maximum temperature: "))

                response = requests.get(
                    self.weather_api_url,
                    params={
                        "days": "5",
                        "aqi": "yes",
                        "q": city,
                        "units": "metric",
                        "key": self.key,
                        "alerts": "yes",
                    },
                )
                response.raise_for_status()
                data = response.json()

                temperature = data["current"]["temp_c"]
                feelslike = data["current"]["feelslike_c"]
                wind_speed = data["current"]["wind_kph"]
                humidity = data["current"]["humidity"]
                display_text = data["current"]["condition"]["text"]

                print(f"---------------------------------------------")
                print(f"Today's weather will be `{display_text}` ")
                print(f"Current weather in {city}: {temperature} °C ")
                print(f"Feels Like: {feelslike} °C")
                print(f"Wind speed: {wind_speed} km/hr")
                print(f"Humidity: {humidity} g/m³")
                print(f"---------------------------------------------")
                print("\n")
                print(f"***********************************************")
                print(f"5 days forcast of {city}")
                forecast_text = self.forecast(data)
                print(forecast_text)
                print(f"***********************************************")

                if temperature < min_temp:
                    message = f"It's cold outside in {city} temp is below {min_temp}°C!."
                    print(f"Notification sent to the user")
                    self.send_notification(message)
                elif temperature > max_temp:
                    message = f"It's hot outside in {city} temp is above {max_temp}°C!."
                    print(f"Notification sent to the user")
                    self.send_notification(message)

        except KeyboardInterrupt:
            print("WeatherAgent stopped by the user.")
        except Exception as e:
            print(f"An error occurred: {e}")