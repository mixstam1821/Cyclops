# Cyclops.py
import os
import numpy as np
import requests
from datetime import datetime

from bokeh.io import curdoc
from bokeh.models import (
    ColumnDataSource,
    LinearColorMapper,
    ColorBar,
    BasicTicker,
    WheelZoomTool,
    HoverTool,
    CustomJSHover
)
from bokeh.plotting import figure
from bokeh.models import WMTSTileSource

def cusj():
    num=1
    return CustomJSHover(code=f"""
    special_vars.indices = special_vars.indices.slice(0,{num})
    return special_vars.indices.includes(special_vars.index) ? " " : " hidden "
    """)
def hovfun(tltl):
    return """<div @hidden{custom} style="background-color: #343838; padding: 5px; border-radius: 15px; box-shadow: 0px 0px 5px rgba(0,0,0,0.3);">        
    """+tltl+"""
    </div> <style> :host { --tooltip-border: transparent;  /* Same border color used everywhere */ --tooltip-color: transparent; --tooltip-text: #2f2f2f;} </style> """
# ─── Helper: convert lat/lon to Web Mercator ───────────────────────────────────
def latlon_to_mercator(lat, lon):
    """Convert (lat, lon) in degrees to Web Mercator (x, y)."""
    k = 6378137.0
    x = lon * (k * np.pi / 180.0)
    y = np.log(np.tan((90 + lat) * np.pi / 360.0)) * k
    return x, y

with open('ak.txt', 'r') as file:
    API_KEY0 = file.readline().strip()  # Remove '\n' or whitespace
    #print(API_KEY0)  # Debug check

API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", str(API_KEY0))
UPDATE_INTERVAL_MS = 60 * 1000  # 1 minute

# ─── Expanded List of >50 Cities ───────────────────────────────────────────────
cities = [ {"name": "New York, US", "lat": 40.7128, "lon": -74.0060}, {"name": "Los Angeles, US", "lat": 34.0522, "lon": -118.2437}, {"name": "Chicago, US", "lat": 41.8781, "lon": -87.6298}, {"name": "Houston, US", "lat": 29.7604, "lon": -95.3698}, {"name": "Toronto, CA", "lat": 43.6532, "lon": -79.3832}, {"name": "Vancouver, CA", "lat": 49.2827, "lon": -123.1207}, {"name": "Montreal, CA", "lat": 45.5017, "lon": -73.5673}, {"name": "Calgary, CA", "lat": 51.0447, "lon": -114.0719}, {"name": "Ottawa, CA", "lat": 45.4215, "lon": -75.6997}, {"name": "Mexico City, MX", "lat": 19.4326, "lon": -99.1332}, {"name": "Guadalajara, MX", "lat": 20.6597, "lon": -103.3496}, {"name": "Monterrey, MX", "lat": 25.6866, "lon": -100.3161}, {"name": "Cancún, MX", "lat": 21.1619, "lon": -86.8515}, {"name": "Miami, US", "lat": 25.7617, "lon": -80.1918}, {"name": "Dallas, US", "lat": 32.7767, "lon": -96.7970}, {"name": "San Francisco, US", "lat": 37.7749, "lon": -122.4194}, {"name": "Washington, D.C., US", "lat": 38.8951, "lon": -77.0364}, {"name": "Atlanta, US", "lat": 33.7490, "lon": -84.3880}, {"name": "Minneapolis, US", "lat": 44.9778, "lon": -93.2650}, {"name": "Denver, US", "lat": 39.7392, "lon": -104.9903}, {"name": "Seattle, US", "lat": 47.6062, "lon": -122.3321}, {"name": "Phoenix, US", "lat": 33.4484, "lon": -112.0740}, {"name": "São Paulo, BR", "lat": -23.5505, "lon": -46.6333}, {"name": "Rio de Janeiro, BR", "lat": -22.9068, "lon": -43.1729}, {"name": "Brasília, BR", "lat": -15.7939, "lon": -47.8828}, {"name": "Fortaleza, BR", "lat": -3.7319, "lon": -38.5267}, {"name": "Manaus, BR", "lat": -3.1190, "lon": -60.0217}, {"name": "Recife, BR", "lat": -8.0476, "lon": -34.8770}, {"name": "Buenos Aires, AR", "lat": -34.6037, "lon": -58.3816}, {"name": "Córdoba, AR", "lat": -31.4201, "lon": -64.1888}, {"name": "Rosario, AR", "lat": -32.9442, "lon": -60.6505}, {"name": "Lima, PE", "lat": -12.0464, "lon": -77.0428}, {"name": "Arequipa, PE", "lat": -16.4090, "lon": -71.5375}, {"name": "Santiago, CL", "lat": -33.4489, "lon": -70.6693}, {"name": "Valparaíso, CL", "lat": -33.0472, "lon": -71.6127}, {"name": "Quito, EC", "lat": -0.1807, "lon": -78.4678}, {"name": "Guayaquil, EC", "lat": -2.1700, "lon": -79.9224}, {"name": "Caracas, VE", "lat": 10.4806, "lon": -66.9036}, {"name": "Bogotá, CO", "lat": 4.7110, "lon": -74.0721}, {"name": "Medellín, CO", "lat": 6.2442, "lon": -75.5812}, {"name": "La Paz, BO", "lat": -16.5000, "lon": -68.1500}, {"name": "Montevideo, UY", "lat": -34.9011, "lon": -56.1645}, {"name": "Asunción, PY", "lat": -25.2637, "lon": -57.5759}, {"name": "London, UK", "lat": 51.5074, "lon": -0.1278}, {"name": "Manchester, UK", "lat": 53.4808, "lon": -2.2426}, {"name": "Paris, FR", "lat": 48.8566, "lon": 2.3522}, {"name": "Marseille, FR", "lat": 43.2965, "lon": 5.3698}, {"name": "Berlin, DE", "lat": 52.5200, "lon": 13.4050}, {"name": "Munich, DE", "lat": 48.1351, "lon": 11.5820}, {"name": "Madrid, ES", "lat": 40.4168, "lon": -3.7038}, {"name": "Barcelona, ES", "lat": 41.3851, "lon": 2.1734}, {"name": "Rome, IT", "lat": 41.9028, "lon": 12.4964}, {"name": "Milan, IT", "lat": 45.4642, "lon": 9.1900}, {"name": "Istanbul, TR", "lat": 41.0082, "lon": 28.9784}, {"name": "Athens, GR", "lat": 37.9838, "lon": 23.7275}, {"name": "Vienna, AT", "lat": 48.2082, "lon": 16.3738}, {"name": "Prague, CZ", "lat": 50.0755, "lon": 14.4378}, {"name": "Moscow, RU", "lat": 55.7558, "lon": 37.6173}, {"name": "Saint Petersburg, RU", "lat": 59.9343, "lon": 30.3351}, {"name": "Oslo, NO", "lat": 59.9139, "lon": 10.7522}, {"name": "Stockholm, SE", "lat": 59.3293, "lon": 18.0686}, {"name": "Helsinki, FI", "lat": 60.1699, "lon": 24.9384}, {"name": "Copenhagen, DK", "lat": 55.6761, "lon": 12.5683}, {"name": "Dublin, IE", "lat": 53.3498, "lon": -6.2603}, {"name": "Warsaw, PL", "lat": 52.2297, "lon": 21.0122}, {"name": "Zurich, CH", "lat": 47.3769, "lon": 8.5417}, {"name": "Novosibirsk, RU", "lat": 55.0084, "lon": 82.9357}, {"name": "Krasnoyarsk, RU", "lat": 56.0153, "lon": 92.8932}, {"name": "Irkutsk, RU", "lat": 52.2870, "lon": 104.3050}, {"name": "Yakutsk, RU", "lat": 62.0355, "lon": 129.6755}, {"name": "Vladivostok, RU", "lat": 43.1155, "lon": 131.8855}, {"name": "Murmansk, RU", "lat": 68.9585, "lon": 33.0827}, {"name": "Barrow (Utqiaġvik), US", "lat": 71.2906, "lon": -156.7886}, {"name": "Longyearbyen, Svalbard", "lat": 78.2232, "lon": 15.6469}, {"name": "Cairo, EG", "lat": 30.0444, "lon": 31.2357}, {"name": "Alexandria, EG", "lat": 31.2001, "lon": 29.9187}, {"name": "Lagos, NG", "lat": 6.5244, "lon": 3.3792}, {"name": "Abuja, NG", "lat": 9.0765, "lon": 7.3986}, {"name": "Nairobi, KE", "lat": -1.2921, "lon": 36.8219}, {"name": "Addis Ababa, ET", "lat": 9.0301, "lon": 38.7427}, {"name": "Johannesburg, ZA", "lat": -26.2041, "lon": 28.0473}, {"name": "Cape Town, ZA", "lat": -33.9249, "lon": 18.4241}, {"name": "Durban, ZA", "lat": -29.8587, "lon": 31.0218}, {"name": "Algiers, DZ", "lat": 36.7538, "lon": 3.0588}, {"name": "Casablanca, MA", "lat": 33.5731, "lon": -7.5898}, {"name": "Dakar, SN", "lat": 14.7167, "lon": -17.4677}, {"name": "Accra, GH", "lat": 5.6037, "lon": -0.1870}, {"name": "Kampala, UG", "lat": 0.3476, "lon": 32.5825}, {"name": "Maputo, MZ", "lat": -25.9692, "lon": 32.5732}, {"name": "Luanda, AO", "lat": -8.8390, "lon": 13.2894}, {"name": "Harare, ZW", "lat": -17.8252, "lon": 31.0335}, {"name": "Istanbul, TR", "lat": 41.0082, "lon": 28.9784}, {"name": "Ankara, TR", "lat": 39.9334, "lon": 32.8597}, {"name": "Jerusalem, IL", "lat": 31.7683, "lon": 35.2137}, {"name": "Tel Aviv, IL", "lat": 32.0853, "lon": 34.7818}, {"name": "Riyadh, SA", "lat": 24.7136, "lon": 46.6753}, {"name": "Jeddah, SA", "lat": 21.4858, "lon": 39.1925}, {"name": "Dubai, AE", "lat": 25.2048, "lon": 55.2708}, {"name": "Abu Dhabi, AE", "lat": 24.4539, "lon": 54.3773}, {"name": "Baghdad, IQ", "lat": 33.3128, "lon": 44.3615}, {"name": "Tehran, IR", "lat": 35.6892, "lon": 51.3890}, {"name": "Doha, QA", "lat": 25.276987, "lon": 51.520008}, {"name": "Muscat, OM", "lat": 23.5859, "lon": 58.4059}, {"name": "Amman, JO", "lat": 31.9539, "lon": 35.9106}, {"name": "Beirut, LB", "lat": 33.8938, "lon": 35.5018}, {"name": "Damascus, SY", "lat": 33.5138, "lon": 36.2765}, {"name": "Beijing, CN", "lat": 39.9042, "lon": 116.4074}, {"name": "Shanghai, CN", "lat": 31.2304, "lon": 121.4737}, {"name": "Guangzhou, CN", "lat": 23.1291, "lon": 113.2644}, {"name": "Shenzhen, CN", "lat": 22.5431, "lon": 114.0579}, {"name": "Hong Kong, HK", "lat": 22.3193, "lon": 114.1694}, {"name": "Tokyo, JP", "lat": 35.6895, "lon": 139.6917}, {"name": "Osaka, JP", "lat": 34.6937, "lon": 135.5023}, {"name": "Seoul, KR", "lat": 37.5665, "lon": 126.9780}, {"name": "Busan, KR", "lat": 35.1796, "lon": 129.0756}, {"name": "Singapore, SG", "lat": 1.3521, "lon": 103.8198}, {"name": "Bangkok, TH", "lat": 13.7563, "lon": 100.5018}, {"name": "Hanoi, VN", "lat": 21.0285, "lon": 105.8542}, {"name": "Jakarta, ID", "lat": -6.2088, "lon": 106.8456}, {"name": "Manila, PH", "lat": 14.5995, "lon": 120.9842}, {"name": "Kuala Lumpur, MY", "lat": 3.1390, "lon": 101.6869}, {"name": "Delhi, IN", "lat": 28.7041, "lon": 77.1025}, {"name": "Mumbai, IN", "lat": 19.0760, "lon": 72.8777}, {"name": "Bangalore, IN", "lat": 12.9716, "lon": 77.5946}, {"name": "Chennai, IN", "lat": 13.0827, "lon": 80.2707}, {"name": "Dhaka, BD", "lat": 23.8103, "lon": 90.4125}, {"name": "Islamabad, PK", "lat": 33.6844, "lon": 73.0479}, {"name": "Karachi, PK", "lat": 24.8607, "lon": 67.0011}, {"name": "Sydney, AU", "lat": -33.8688, "lon": 151.2093}, {"name": "Melbourne, AU", "lat": -37.8136, "lon": 144.9631}, {"name": "Brisbane, AU", "lat": -27.4698, "lon": 153.0251}, {"name": "Perth, AU", "lat": -31.9505, "lon": 115.8605}, {"name": "Auckland, NZ", "lat": -36.8485, "lon": 174.7633}, {"name": "Wellington, NZ", "lat": -41.2865, "lon": 174.7762}, {"name": "Port Moresby, PG", "lat": -9.4438, "lon": 147.1803}, {"name": "Suva, FJ", "lat": -18.1248, "lon": 178.4501}, {"name": "Nouméa, NC", "lat": -22.2758, "lon": 166.4580}, {"name": "Honiara, SB", "lat": -9.4319, "lon": 159.9565}, {"name": "Majuro, MH", "lat": 7.1167, "lon": 171.3667}, {"name": "McMurdo Station, AQ", "lat": -77.8419, "lon": 166.6863}, {"name": "Amundsen-Scott South Pole Station, AQ", "lat": -90.0000, "lon": 0.0000}, {"name": "Vostok Station, AQ", "lat": -78.4648, "lon": 106.8369}, {"name": "Alert, CA", "lat": 82.5018, "lon": -62.3481}, ]
# Precompute mercator coordinates
merc_x, merc_y = zip(*(latlon_to_mercator(c["lat"], c["lon"]) for c in cities))

# ColumnDataSource for our plot
source = ColumnDataSource(
    data=dict(
        x=list(merc_x),
        y=list(merc_y),
        name=[c["name"] for c in cities],
        cloud=[0] * len(cities),  # placeholder, will be updated
        temp=[0] * len(cities),  # temperature °C
        humidity=[0] * len(cities),  # humidity %
        pressure=[0] * len(cities),  # pressure hPa
        hidden=np.ones(len(list(merc_x)))*np.min(list(merc_y))
    )
)

# ─── Build dark-background map figure ──────────────────────────────────────────
# Generate dynamic title with current datetime
title_str = f"Live Weather Map — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
p = figure(
    x_axis_type="mercator",
    y_axis_type="mercator",
    sizing_mode="stretch_both",
    title=title_str,
    background_fill_color="#2F2F2F",
    border_fill_color="#2F2F2F",
    outline_line_color="#444444",
)
dark_url = "https://basemaps.cartocdn.com/dark_all/{Z}/{X}/{Y}.png"
tile_provider = WMTSTileSource(url=dark_url)
p.add_tile(tile_provider)

# Enable wheel zoom by default
wheel_zoom = WheelZoomTool()
p.add_tools(wheel_zoom)
p.toolbar.active_scroll = wheel_zoom

# style title & axes for dark theme
p.title.text_color = "deepskyblue"
p.title.text_font = "Helvetica"
p.title.text_font_style = "bold"
p.title.text_font_size = "25pt"


for axis in (p.xaxis, p.yaxis):
    axis.axis_line_color = "white"
    axis.major_tick_line_color = "white"
    axis.major_label_text_color = "white"
    axis.minor_tick_line_color = "white"
# remove grid lines for a cleaner map
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
# Color mapper and circles
color_mapper = LinearColorMapper(palette="Turbo256", low=-10, high=40)
circles = p.scatter(
    "x",
    "y",
    source=source,
    size=20,
    fill_color={"field": "temp", "transform": color_mapper},
    fill_alpha=0.9,
    line_color=None,
)


# ─── Enhanced HoverTool with HTML styling ─────────────────────────────────────

tltl = """
      <div style='font-size:27px; color:#FFD700; font-weight:bold;'>@name</div>
      <div style='font-size:23px; color:#FFFFFF;'>☁️ @cloud{0.0}%</div>
      <div style='font-size:23px; color:#FFFFFF;'>🌡️ @temp{0.0}°C</div>
      <div style='font-size:23px; color:#FFFFFF;'>💧 @humidity{0.0}%</div>
      <div style='font-size:23px; color:#FFFFFF;'>🕛 @pressure{0.0}hPa</div>
"""

hover = HoverTool(
    renderers=[circles],
    point_policy="follow_mouse",
    tooltips=hovfun(tltl),formatters={"@hidden": cusj()},mode="mouse"
)
p.add_tools(hover)

# color bar for reference
color_bar = ColorBar(
    title_text_font_size="16pt",
    major_label_text_font_size="14pt",
    background_fill_color="#2F2F2F",
    color_mapper=color_mapper,
    title_text_color="white",
    major_label_text_color="white",
    label_standoff=10,
    ticker=BasicTicker(desired_num_ticks=5),
    title="Temperature (°C)",
    location=(0, 0),
)
p.add_layout(color_bar, "right")


# ─── Data fetch + update ───────────────────────────────────────────────────────
def fetch_and_update():
    new_cloud, new_temp, new_hum, new_pressure = [], [], [], []
    for city in cities:
        params = {
            "lat": city["lat"],
            "lon": city["lon"],
            "appid": API_KEY,
            "units": "metric",
        }
        try:
            data = requests.get(
                "https://api.openweathermap.org/data/2.5/weather", params=params
            ).json()
            clouds = data.get("clouds", {}).get("all", 0)
            temp = data.get("main", {}).get("temp", 0)
            hum = data.get("main", {}).get("humidity", 0)
            pressure = data.get("main", {}).get("pressure", 0)
        except Exception:
            clouds, temp, hum, pressure = 0, 0, 0, 0

        new_cloud.append(clouds)
        new_temp.append(temp)
        new_hum.append(hum)
        new_pressure.append(pressure)
    # Update all three columns at once
    source.data.update(
        cloud=new_cloud, temp=new_temp, humidity=new_hum, pressure=new_pressure
    )


# Initial load + periodic refresh
fetch_and_update()
curdoc().add_periodic_callback(fetch_and_update, UPDATE_INTERVAL_MS)

# Add to document
curdoc().add_root(p)
