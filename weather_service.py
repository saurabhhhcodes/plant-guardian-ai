import requests
import json
from typing import Dict, Any, Optional

class WeatherService:
    """Service to fetch weather data using wttr.in."""
    
    @staticmethod
    def get_location_from_ip() -> Optional[str]:
        """Automatically detect the user's city via IP geolocation."""
        try:
            # Using ip-api.com (free, no key required for low volume)
            response = requests.get("http://ip-api.com/json/", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'success':
                    return data.get('city')
            return None
        except Exception as e:
            print(f"Error detecting location: {e}")
            return None

    @staticmethod
    def get_soil_insights(location: str) -> str:
        """Provide regional soil insights based on location (Heuristic)."""
        location_lower = location.lower()
        if "lucknow" in location_lower or "uttar pradesh" in location_lower:
            return "Alluvial soil: Rich in potash and lime, slightly alkaline, good moisture retention (ideal for sugar cane, rice)."
        elif "mumbai" in location_lower or "maharashtra" in location_lower:
            return "Black soil (Regur): Volcanic origin, clayey, rich in iron/calcium, highly water-retentive (ideal for cotton)."
        elif "bangalore" in location_lower or "karnataka" in location_lower:
            return "Red soil: Sandy-clayey, rich in iron, well-draining but requires organic boost (ideal for pulses, fruits)."
        elif "rajasthan" in location_lower or "jaipur" in location_lower:
            return "Arid/Sandy soil: Low organic content, alkaline, high permeability (ideal for drought-resistant crops)."
        else:
            return "Regional soil data unavailable. Suggesting general loam-based care based on visual cues."

    @staticmethod
    def get_weather(location: str) -> Optional[Dict[str, Any]]:
        """Fetch weather data for a given location using wttr.in.
        
        Args:
            location: The name of the city or region.
            
        Returns:
            Dictionary containing weather data or None if fetch fails.
        """
        try:
            # format=j1 returns JSON data
            url = f"https://wttr.in/{location}?format=j1"
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                current = data.get('current_condition', [{}])[0]
                return {
                    'temp_C': current.get('temp_C'),
                    'humidity': current.get('humidity'),
                    'weatherDesc': current.get('weatherDesc', [{}])[0].get('value'),
                    'precipMM': current.get('precipMM'),
                    'feelsLikeC': current.get('FeelsLikeC')
                }
            return None
        except Exception as e:
            print(f"Error fetching weather: {e}")
            return None
