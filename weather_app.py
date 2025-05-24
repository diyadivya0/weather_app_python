import asyncio
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import geocoder
import platform
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import io
import base64
import urllib.request

# OpenWeatherMap API key
API_KEY = "add_api_key"  

# Base URLs for OpenWeatherMap API
WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
ICON_BASE_URL = "http://openweathermap.org/img/wn/{}@2x.png"

# Main application class
class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather App by Divya Reddy")
        self.root.geometry("890x470+300+300")
        self.root.configure(bg="#57adff")

        # Adding the Info button 
        self.info_button = tk.Button(self.root, text="Info", command=self.show_info)
        self.info_button.pack(pady=5)

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=("Helvetica", 12))
        self.style.configure("TLabel", font=("Helvetica", 12), background="#e0f7fa")
        self.style.configure("Header.TLabel", font=("Helvetica", 16, "bold"), background="#e0f7fa")

        # Location input
        self.location_label = ttk.Label(root, text="Enter Location (City, ZIP, or Lat,Lon):", style="Header.TLabel")
        self.location_label.pack(pady=10)

        self.location_entry = ttk.Entry(root, width=30, font=("Helvetica", 12))
        self.location_entry.pack(pady=5)

        # Buttons
        self.search_button = ttk.Button(root, text="Get Weather", command=self.get_weather)
        self.search_button.pack(pady=5)

        self.current_location_button = ttk.Button(root, text="Use Current Location", command=self.get_current_location_weather)
        self.current_location_button.pack(pady=5)

        # Current weather display
        self.current_weather_frame = tk.Frame(root, bg="#e0f7fa")
        self.current_weather_frame.pack(pady=10, fill="x", padx=20)

        self.weather_icon_label = tk.Label(self.current_weather_frame, bg="#e0f7fa")
        self.weather_icon_label.pack()

        self.current_weather_label = ttk.Label(self.current_weather_frame, text="", style="TLabel", wraplength=500)
        self.current_weather_label.pack()

        # Forecast display
        self.forecast_frame = tk.Frame(root, bg="#e0f7fa")
        self.forecast_frame.pack(pady=10, fill="x", padx=20)

        self.forecast_label = ttk.Label(self.forecast_frame, text="5-Day Forecast", style="Header.TLabel")
        self.forecast_label.pack()

        self.forecast_canvas = tk.Canvas(self.forecast_frame, bg="#e0f7fa", height=100, highlightthickness=0)
        self.forecast_canvas.pack(side="top", fill="both",expand=True)

        self.forecast_inner_frame = tk.Frame(self.forecast_canvas, bg="#e0f7fa")
        self.forecast_canvas.create_window((0, 0), window=self.forecast_inner_frame, anchor="nw")

        # Adjust this value based on your UI needs
        self.forecast_canvas.config(height=150)

    def show_info(self):
        messagebox.showinfo(
            "About",
            "By making industry-leading tools and education available to individuals from all backgrounds, we level the playing field for future PM leaders. "
            "This is the PM Accelerator motto, as we grant aspiring and experienced PMs what they need most – Access. We introduce you to industry leaders, "
            "surround you with the right PM ecosystem, and discover the new world of AI product management skills."
        )

    def get_current_location_weather(self):
        try:
            g = geocoder.ip('me')
            if g.ok:
                lat, lon = g.latlng
                self.get_weather_by_coords(lat, lon)
            else:
                messagebox.showerror("Error", "Unable to detect current location.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get current location: {str(e)}")

    def get_weather(self):
        location = self.location_entry.get().strip()
        if not location:
            messagebox.showwarning("Input Error", "Please enter a location.")
            return

        try:
            # Check if input is coordinates (e.g., "lat,lon")
            if "," in location:
                try:
                    lat, lon = map(float, location.split(","))
                    self.get_weather_by_coords(lat, lon)
                except ValueError:
                    self.get_weather_by_query(location)
            else:
                self.get_weather_by_query(location)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch weather data: {str(e)}")

    def get_weather_by_query(self, query):
        # First, get coordinates from city or ZIP
        params = {"q": query, "appid": API_KEY}
        response = requests.get(WEATHER_URL, params=params)
        data = response.json()

        if response.status_code != 200 or "coord" not in data:
            messagebox.showerror("Error", "Location not found or API error.")
            return

        lat = data["coord"]["lat"]
        lon = data["coord"]["lon"]
        self.get_weather_by_coords(lat, lon, data.get("name", query))

    def get_weather_by_coords(self, lat, lon, city_name=None):
        # Get current weather
        params = {"lat": lat, "lon": lon, "appid": API_KEY, "units": "metric"}
        current_response = requests.get(WEATHER_URL, params=params)
        current_data = current_response.json()

        # Get 5-day forecast
        forecast_response = requests.get(FORECAST_URL, params=params)
        forecast_data = forecast_response.json()

        if current_response.status_code != 200 or forecast_response.status_code != 200:
            messagebox.showerror("Error", "Failed to fetch weather data.")
            return

        self.display_weather(current_data, forecast_data, city_name)

    def display_weather(self, current_data, forecast_data, city_name):
        # Current weather
        city = city_name or current_data.get("name", "Unknown")
        temp = current_data["main"]["temp"]
        feels_like = current_data["main"]["feels_like"]
        humidity = current_data["main"]["humidity"]
        wind_speed = current_data["wind"]["speed"]
        description = current_data["weather"][0]["description"].capitalize()
        icon_code = current_data["weather"][0]["icon"]

        # Fetch and display weather icon
        try:
            icon_url = ICON_BASE_URL.format(icon_code)
            with urllib.request.urlopen(icon_url) as response:
                icon_data = response.read()
            image = Image.open(io.BytesIO(icon_data))
            image = image.resize((50, 50), Image.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self.weather_icon_label.configure(image=photo)
            self.weather_icon_label.image = photo  # Keep a reference
        except Exception as e:
            self.weather_icon_label.configure(image=None)
            print(f"Failed to load icon: {str(e)}")

        current_text = f"Current Weather in {city}\n"
        current_text += f"Temperature: {temp}°C\n"
        current_text += f"Feels Like: {feels_like}°C\n"
        current_text += f"Condition: {description}\n"
        current_text += f"Humidity: {humidity}%\n"
        current_text += f"Wind Speed: {wind_speed} m/s"
        self.current_weather_label.configure(text=current_text)

        # Clear previous forecast
        for widget in self.forecast_inner_frame.winfo_children():
            widget.destroy()

        # 5-day forecast
        
        daily_forecasts = {}
        for item in forecast_data["list"]:
            date = datetime.fromtimestamp(item["dt"]).date()
            if date not in daily_forecasts:
                daily_forecasts[date] = {
                    "temps": [],
                    "descriptions": [],
                    "icon": item["weather"][0]["icon"]
                }
            daily_forecasts[date]["temps"].append(item["main"]["temp"])
            daily_forecasts[date]["descriptions"].append(item["weather"][0]["description"])

        # Display up to 5 days
        for i, (date, data) in enumerate(list(daily_forecasts.items())[:5]):
            avg_temp = sum(data["temps"]) / len(data["temps"])
            common_desc = max(set(data["descriptions"]), key=data["descriptions"].count).capitalize()
            icon_code = data["icon"]

            # Create frame for each day
            day_frame = tk.Frame(self.forecast_inner_frame, bg="#e0f7fa")
            day_frame.grid(row=0, column=i, padx=10)

            # Fetch and display forecast icon
            try:
                icon_url = ICON_BASE_URL.format(icon_code)
                with urllib.request.urlopen(icon_url) as response:
                    icon_data = response.read()
                image = Image.open(io.BytesIO(icon_data))
                image = image.resize((40, 40), Image.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                icon_label = tk.Label(day_frame, image=photo, bg="#e0f7fa")
                icon_label.image = photo  # Keep a reference
                icon_label.pack()
            except Exception as e:
                print(f"Failed to load forecast icon: {str(e)}")

            # Display date, temperature, and description
            date_label = tk.Label(day_frame, text=date.strftime("%a, %b %d"), font=("Helvetica", 10), bg="#e0f7fa")
            date_label.pack()
            temp_label = tk.Label(day_frame, text=f"{avg_temp:.1f}°C", font=("Helvetica", 10), bg="#e0f7fa")
            temp_label.pack()
            desc_label = tk.Label(day_frame, text=common_desc, font=("Helvetica", 10), wraplength=100, bg="#e0f7fa")
            desc_label.pack()

async def main():
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())