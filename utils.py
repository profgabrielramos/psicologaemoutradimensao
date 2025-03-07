import swisseph as swe
from datetime import datetime
import pytz
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import requests
from pathlib import Path

def download_ephe_files():
    """Download and configure ephemeris files."""
    ephe_dir = Path("ephe")
    ephe_dir.mkdir(exist_ok=True)
    
    base_url = "https://raw.githubusercontent.com/aloistr/swisseph/master/ephe/"
    essential_files = ["seas_18.se1", "semo_18.se1", "sepl_18.se1"]
    
    for filename in essential_files:
        file_path = ephe_dir / filename
        if not file_path.exists():
            try:
                response = requests.get(f"{base_url}{filename}")
                response.raise_for_status()
                with open(file_path, "wb") as f:
                    f.write(response.content)
            except Exception:
                return False
    
    swe.set_ephe_path(str(ephe_dir))
    return True

def get_location_data(location_string):
    """Obtém coordenadas e fuso horário para uma localização."""
    geolocator = Nominatim(user_agent="mystical_chart", timeout=10)  # Aumentado o timeout para 10 segundos
    try:
        location = geolocator.geocode(location_string)
        if not location:
            raise ValueError("Localização não encontrada")

        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lat=location.latitude, lng=location.longitude)

        if not timezone_str:
            raise ValueError("Fuso horário não encontrado para esta localização")

        return {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timezone': timezone_str
        }
    except Exception as e:
        raise ValueError(f"Erro ao buscar localização: {str(e)}")

def calculate_julian_day(date, time, timezone_str):
    """Calculate Julian Day from date and time."""
    tz = pytz.timezone(timezone_str)
    datetime_obj = datetime.combine(date, time)
    local_dt = tz.localize(datetime_obj)
    utc_dt = local_dt.astimezone(pytz.UTC)
    
    jd = swe.utc_to_jd(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour, utc_dt.minute, utc_dt.second,
        swe.GREG_CAL
    )[1]
    
    return jd

def get_planet_positions(jd):
    """Calculate positions for all planets."""
    planets = {
        "Sun": swe.SUN,
        "Moon": swe.MOON,
        "Mercury": swe.MERCURY,
        "Venus": swe.VENUS,
        "Mars": swe.MARS,
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN,
        "Uranus": swe.URANUS,
        "Neptune": swe.NEPTUNE,
        "Pluto": swe.PLUTO
    }
    
    positions = {}
    for name, planet_id in planets.items():
        result = swe.calc_ut(jd, planet_id)
        positions[name] = {
            'longitude': result[0][0],
            'latitude': result[0][1],
            'distance': result[0][2]
        }
    
    return positions

def calculate_houses(jd, lat, lon):
    """Calculate house cusps using Placidus system."""
    houses, angles = swe.houses(jd, lat, lon, b'P')
    return {
        'cusps': houses,
        'ascendant': angles[0],
        'mc': angles[1],
        'armc': angles[2],
        'vertex': angles[3]
    }