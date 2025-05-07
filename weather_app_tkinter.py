import tkinter as tk
from tkinter import messagebox
import requests  
from dotenv import load_dotenv
import json
import os

API_KEY = os.getenv("API_KEY")
FAVORITES_FILE = "favorites.json"

def get_weather(city, api_key):
    """Fetch weather data from the API."""
    base_url = "https://api.tomorrow.io/v4/weather/realtime"
    params = {
        "location": city,
        "apikey": api_key,
        "units": "imperial"  
    }

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        data = response.json()
        # Debug: Print the response to verify structure
        print("API Response:", data)

        # Ensure correct keys are used to extract data
        values = data.get("data", {}).get("values", {})
        return {
            "weather_code": values.get("weatherCode", "N/A"),
            "temperature": values.get("temperature", "N/A"),
            "humidity": values.get("humidity", "N/A"),
            "wind_speed": values.get("windSpeed", "N/A")
        }
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

class WeatherApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Weather App")

        # Initialize favorites
        self.favorites = self.load_favorites()

        # UI Elements
        self.city_label = tk.Label(root, text="Enter City:")
        self.city_label.pack()

        self.city_input = tk.Entry(root)
        self.city_input.pack()

        self.get_weather_btn = tk.Button(root, text="Get Weather", command=self.fetch_weather)
        self.get_weather_btn.pack()

        self.weather_info = tk.Label(root, text="Weather information will appear here.", justify="left")
        self.weather_info.pack()

        self.add_favorite_btn = tk.Button(root, text="⭐ Add to Favorites", command=self.add_to_favorites)
        self.add_favorite_btn.pack()

        self.favorites_label = tk.Label(root, text="Favorites:")
        self.favorites_label.pack()

        self.favorites_listbox = tk.Listbox(root)
        self.favorites_listbox.pack()
        self.favorites_listbox.bind("<<ListboxSelect>>", self.display_favorite_weather)

        self.update_favorites_list()

    def fetch_weather(self):
        """Fetch weather data for the entered city."""
        city = self.city_input.get().strip()
        if not city:
            messagebox.showerror("Error", "Please enter a city name.")
            return

        # Debug: Print the city being fetched
        print(f"Fetching weather for city: {city}")

        # Load the weather code mapping from the JSON file
        with open("weathercode.json", "r") as file:
            weather_code_mapping = json.load(file)

        weather_data = self.get_weather(city)
        if weather_data:
            # Replace weather code with description
            weather_code = str(weather_data.get("weather_code", "N/A"))
            weather_description = weather_code_mapping["weatherCode"].get(weather_code, "Unknown")

            # Debug: Print the weather data received
            print(f"Weather data received: {weather_data}")
            self.weather_info.config(
                text=(
                    f"Weather in {city}:\n"
                    f"- Weather: {weather_description}\n"
                    f"- Temperature: {weather_data.get('temperature', 'N/A')}°F\n"
                    f"- Humidity: {weather_data.get('humidity', 'N/A')}%\n"
                    f"- Wind Speed: {weather_data.get('wind_speed', 'N/A')} mph"
                )
            )
        else:
            self.weather_info.config(text="Error: Unable to fetch weather data.")
            print("Error: Unable to fetch weather data.")

    def add_to_favorites(self):
        """Add the current city to favorites."""
        city = self.city_input.get().strip()
        if city and city not in self.favorites:
            self.favorites.append(city)
            self.save_favorites()
            self.update_favorites_list()

    def display_favorite_weather(self, event):
        """Display weather for the selected favorite city."""
        selection = self.favorites_listbox.curselection()
        if selection:
            selected_city = self.favorites_listbox.get(selection[0])
            self.city_input.delete(0, tk.END)
            self.city_input.insert(0, selected_city)
            self.fetch_weather()

    def get_weather(self, city: str):
        return get_weather(city, API_KEY)

    def update_favorites_list(self):
        """Update the favorites listbox."""
        self.favorites_listbox.delete(0, tk.END)
        for city in self.favorites:
            self.favorites_listbox.insert(tk.END, city)

    def save_favorites(self):
        """Save favorites to a JSON file."""
        with open(FAVORITES_FILE, "w") as f:
            json.dump(self.favorites, f)

    def load_favorites(self):
        """Load favorites from a JSON file."""
        if os.path.exists(FAVORITES_FILE):
            with open(FAVORITES_FILE, "r") as f:
                return json.load(f)
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
