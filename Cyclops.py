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
    CustomJSHover,
    WMTSTileSource,
    RadioButtonGroup,
    Div,
    GlobalInlineStyleSheet,
    InlineStyleSheet
)
from bokeh.plotting import figure
from bokeh.layouts import column,row

# ─── Helper: convert lat/lon to Web Mercator ───
def latlon_to_mercator(lat, lon):
    k = 6378137.0
    x = lon * (k * np.pi / 180.0)
    y = np.log(np.tan((90 + lat) * np.pi / 360.0)) * k
    return x, y

# Define different lists for each region
north_america = [
    {"name": "New York, US", "lat": 40.7128, "lon": -74.0060},
    {"name": "Los Angeles, US", "lat": 34.0522, "lon": -118.2437},
    {"name": "Chicago, US", "lat": 41.8781, "lon": -87.6298},
    {"name": "Houston, US", "lat": 29.7604, "lon": -95.3698},
    {"name": "Phoenix, US", "lat": 33.4484, "lon": -112.0740},
    {"name": "Philadelphia, US", "lat": 39.9526, "lon": -75.1652},
    {"name": "San Antonio, US", "lat": 29.4241, "lon": -98.4936},
    {"name": "San Diego, US", "lat": 32.7157, "lon": -117.1611},
    {"name": "Dallas, US", "lat": 32.7767, "lon": -96.7970},
    {"name": "San Jose, US", "lat": 37.3382, "lon": -121.8863},
    {"name": "Austin, US", "lat": 30.2672, "lon": -97.7431},
    {"name": "Jacksonville, US", "lat": 30.3322, "lon": -81.6557},
    {"name": "Fort Worth, US", "lat": 32.7555, "lon": -97.3308},
    {"name": "Columbus, US", "lat": 39.9612, "lon": -82.9988},
    {"name": "Charlotte, US", "lat": 35.2271, "lon": -80.8431},
    {"name": "Indianapolis, US", "lat": 39.7684, "lon": -86.1581},
    {"name": "San Francisco, US", "lat": 37.7749, "lon": -122.4194},
    {"name": "Seattle, US", "lat": 47.6062, "lon": -122.3321},
    {"name": "Denver, US", "lat": 39.7392, "lon": -104.9903},
    {"name": "Washington, DC, US", "lat": 38.9072, "lon": -77.0369},
    {"name": "Boston, US", "lat": 42.3601, "lon": -71.0589},
    {"name": "Detroit, US", "lat": 42.3314, "lon": -83.0458},
    {"name": "El Paso, US", "lat": 31.7619, "lon": -106.4850},
    {"name": "Nashville, US", "lat": 36.1627, "lon": -86.7816},
    {"name": "Portland, US", "lat": 45.5051, "lon": -122.6750},
    {"name": "Las Vegas, US", "lat": 36.1699, "lon": -115.1398},
    {"name": "Baltimore, US", "lat": 39.2904, "lon": -76.6122},
    {"name": "Louisville, US", "lat": 38.2527, "lon": -85.7585},
    {"name": "Milwaukee, US", "lat": 43.0389, "lon": -87.9065},
    {"name": "Albuquerque, US", "lat": 35.0844, "lon": -106.6504},
    {"name": "Tucson, US", "lat": 32.2226, "lon": -110.9747},
    {"name": "Fresno, US", "lat": 36.7378, "lon": -119.7871},
    {"name": "Sacramento, US", "lat": 38.5816, "lon": -121.4944},
    {"name": "Mesa, US", "lat": 33.4152, "lon": -111.8315},
    {"name": "Kansas City, US", "lat": 39.0997, "lon": -94.5786},
    {"name": "Atlanta, US", "lat": 33.7490, "lon": -84.3880},
    {"name": "Miami, US", "lat": 25.7617, "lon": -80.1918},
    {"name": "Omaha, US", "lat": 41.2565, "lon": -95.9345},
    {"name": "Raleigh, US", "lat": 35.7796, "lon": -78.6382},
    {"name": "Minneapolis, US", "lat": 44.9778, "lon": -93.2650},
    {"name": "Tulsa, US", "lat": 36.15398, "lon": -95.992775},
    # CANADA
    {"name": "Toronto, Canada", "lat": 43.7, "lon": -79.42},
    {"name": "Montreal, Canada", "lat": 45.5017, "lon": -73.5673},
    {"name": "Vancouver, Canada", "lat": 49.2827, "lon": -123.1207},
    {"name": "Calgary, Canada", "lat": 51.0447, "lon": -114.0719},
    {"name": "Ottawa, Canada", "lat": 45.4215, "lon": -75.6997},
    {"name": "Edmonton, Canada", "lat": 53.5461, "lon": -113.4938},
    {"name": "Winnipeg, Canada", "lat": 49.8951, "lon": -97.1384},
    {"name": "Quebec City, Canada", "lat": 46.8139, "lon": -71.2080},
    {"name": "Halifax, Canada", "lat": 44.6488, "lon": -63.5752},
    {"name": "Regina, Canada", "lat": 50.4452, "lon": -104.6189},
    {"name": "Victoria, Canada", "lat": 48.4284, "lon": -123.3656},
    # MEXICO
    {"name": "Mexico City, Mexico", "lat": 19.4326, "lon": -99.1332},
    {"name": "Guadalajara, Mexico", "lat": 20.6597, "lon": -103.3496},
    {"name": "Monterrey, Mexico", "lat": 25.6866, "lon": -100.3161},
    {"name": "Tijuana, Mexico", "lat": 32.5149, "lon": -117.0382},
    {"name": "Puebla, Mexico", "lat": 19.0414, "lon": -98.2063},
    {"name": "León, Mexico", "lat": 21.1619, "lon": -101.6830},
    {"name": "Mérida, Mexico", "lat": 20.9674, "lon": -89.5926},
    {"name": "Querétaro, Mexico", "lat": 20.5888, "lon": -100.3899},
    # SMALL TOWNS
    {"name": "Moose Jaw, Canada", "lat": 50.3910, "lon": -105.5340},
    {"name": "Driggs, US", "lat": 43.7238, "lon": -111.1111},
    {"name": "Valdez, US", "lat": 61.1308, "lon": -146.3483},
    {"name": "Uvalde, US", "lat": 29.2097, "lon": -99.7862},
    {"name": "Bayfield, US", "lat": 37.2258, "lon": -107.5973},
]


south_america = [
    {"name": "Buenos Aires, Argentina", "lat": -34.6037, "lon": -58.3816},
    {"name": "Córdoba, Argentina", "lat": -31.4201, "lon": -64.1888},
    {"name": "Rosario, Argentina", "lat": -32.9468, "lon": -60.6393},
    {"name": "Mendoza, Argentina", "lat": -32.8895, "lon": -68.8458},
    {"name": "Santiago, Chile", "lat": -33.4489, "lon": -70.6693},
    {"name": "Valparaíso, Chile", "lat": -33.0472, "lon": -71.6127},
    {"name": "Antofagasta, Chile", "lat": -23.6500, "lon": -70.4000},
    {"name": "Lima, Peru", "lat": -12.0464, "lon": -77.0428},
    {"name": "Arequipa, Peru", "lat": -16.4090, "lon": -71.5375},
    {"name": "Cusco, Peru", "lat": -13.5319, "lon": -71.9675},
    {"name": "Rio de Janeiro, Brazil", "lat": -22.9068, "lon": -43.1729},
    {"name": "São Paulo, Brazil", "lat": -23.5505, "lon": -46.6333},
    {"name": "Belo Horizonte, Brazil", "lat": -19.9167, "lon": -43.9345},
    {"name": "Brasília, Brazil", "lat": -15.8267, "lon": -47.9218},
    {"name": "Fortaleza, Brazil", "lat": -3.7172, "lon": -38.5431},
    {"name": "Recife, Brazil", "lat": -8.0476, "lon": -34.8770},
    {"name": "Caracas, Venezuela", "lat": 10.4806, "lon": -66.9036},
    {"name": "Maracaibo, Venezuela", "lat": 10.6545, "lon": -71.6520},
    {"name": "Bogotá, Colombia", "lat": 4.7110, "lon": -74.0721},
    {"name": "Medellín, Colombia", "lat": 6.2442, "lon": -75.5812},
    {"name": "Cali, Colombia", "lat": 3.4516, "lon": -76.5320},
    {"name": "Quito, Ecuador", "lat": -0.1807, "lon": -78.4678},
    {"name": "Guayaquil, Ecuador", "lat": -2.1709, "lon": -79.9224},
    {"name": "La Paz, Bolivia", "lat": -16.5000, "lon": -68.1500},
    {"name": "Santa Cruz, Bolivia", "lat": -17.7833, "lon": -63.1833},
    {"name": "Montevideo, Uruguay", "lat": -34.9011, "lon": -56.1645},
    {"name": "Punta del Este, Uruguay", "lat": -34.9614, "lon": -54.9514},
    {"name": "Asunción, Paraguay", "lat": -25.2637, "lon": -57.5759},
    {"name": "Ciudad del Este, Paraguay", "lat": -25.5167, "lon": -54.6167},
    {"name": "Paramaribo, Suriname", "lat": 5.8520, "lon": -55.2038},
    {"name": "Salvador, Brazil", "lat": -12.9777, "lon": -38.5016},
    {"name": "Porto Alegre, Brazil", "lat": -30.0346, "lon": -51.2177},
    {"name": "Manaus, Brazil", "lat": -3.1190, "lon": -60.0217},
    {"name": "Trujillo, Peru", "lat": -8.1120, "lon": -79.0288},
    # Small towns
    {"name": "Tafí del Valle, Argentina", "lat": -26.8667, "lon": -65.7000},
    {"name": "Chos Malal, Argentina", "lat": -37.3781, "lon": -70.2664},
    {"name": "Leticia, Colombia", "lat": -4.2153, "lon": -69.9406},
    {"name": "Pucallpa, Peru", "lat": -8.3791, "lon": -74.5539},
    {"name": "Ouro Preto, Brazil", "lat": -20.3864, "lon": -43.5033},
    {"name": "Fray Bentos, Uruguay", "lat": -33.1333, "lon": -58.3},
]
europe = [
    # --- Western Europe: UK, Ireland, France, Belgium, Netherlands, Luxembourg ---
    {"name": "London, UK", "lat": 51.5074, "lon": -0.1278},
    {"name": "Manchester, UK", "lat": 53.4808, "lon": -2.2426},
    {"name": "Birmingham, UK", "lat": 52.4862, "lon": -1.8904},
    {"name": "Glasgow, UK", "lat": 55.8642, "lon": -4.2518},
    {"name": "Edinburgh, UK", "lat": 55.9533, "lon": -3.1883},
    {"name": "Cardiff, UK", "lat": 51.4816, "lon": -3.1791},
    {"name": "Dublin, Ireland", "lat": 53.3498, "lon": -6.2603},
    {"name": "Cork, Ireland", "lat": 51.8985, "lon": -8.4756},
    {"name": "Galway, Ireland", "lat": 53.2707, "lon": -9.0568},
    # --- France: major and smaller cities ---
    {"name": "Paris, France", "lat": 48.8566, "lon": 2.3522},
    {"name": "Marseille, France", "lat": 43.2965, "lon": 5.3698},
    {"name": "Lyon, France", "lat": 45.7640, "lon": 4.8357},
    {"name": "Toulouse, France", "lat": 43.6047, "lon": 1.4442},
    {"name": "Nice, France", "lat": 43.7102, "lon": 7.2620},
    {"name": "Nantes, France", "lat": 47.2184, "lon": -1.5536},
    {"name": "Strasbourg, France", "lat": 48.5734, "lon": 7.7521},
    {"name": "Montpellier, France", "lat": 43.6108, "lon": 3.8767},
    {"name": "Bordeaux, France", "lat": 44.8378, "lon": -0.5792},
    {"name": "Lille, France", "lat": 50.6292, "lon": 3.0573},
    {"name": "Rennes, France", "lat": 48.1173, "lon": -1.6778},
    {"name": "Grenoble, France", "lat": 45.1885, "lon": 5.7245},
    {"name": "Dijon, France", "lat": 47.3220, "lon": 5.0415},
    {"name": "Clermont-Ferrand, France", "lat": 45.7772, "lon": 3.0870},
    {"name": "Le Havre, France", "lat": 49.4944, "lon": 0.1079},
    {"name": "Tours, France", "lat": 47.3941, "lon": 0.6848},
    {"name": "Limoges, France", "lat": 45.8336, "lon": 1.2611},
    {"name": "Reims, France", "lat": 49.2583, "lon": 4.0317},
    {"name": "Metz, France", "lat": 49.1193, "lon": 6.1757},
    {"name": "Biarritz, France", "lat": 43.4832, "lon": -1.5586},
    {"name": "Perpignan, France", "lat": 42.6887, "lon": 2.8948},
    {"name": "Pau, France", "lat": 43.2951, "lon": -0.3708},
    {"name": "Avignon, France", "lat": 43.9493, "lon": 4.8055},
    # --- Portugal: major and towns ---
    {"name": "Lisbon, Portugal", "lat": 38.7223, "lon": -9.1393},
    {"name": "Porto, Portugal", "lat": 41.1579, "lon": -8.6291},
    {"name": "Coimbra, Portugal", "lat": 40.2033, "lon": -8.4103},
    {"name": "Faro, Portugal", "lat": 37.0194, "lon": -7.9304},
    {"name": "Braga, Portugal", "lat": 41.5454, "lon": -8.4265},
    {"name": "Évora, Portugal", "lat": 38.5667, "lon": -7.9000},
    {"name": "Aveiro, Portugal", "lat": 40.6405, "lon": -8.6538},
    {"name": "Setúbal, Portugal", "lat": 38.5244, "lon": -8.8882},
    {"name": "Leiria, Portugal", "lat": 39.7436, "lon": -8.8070},
    # --- Benelux ---
    {"name": "Brussels, Belgium", "lat": 50.8503, "lon": 4.3517},
    {"name": "Antwerp, Belgium", "lat": 51.2194, "lon": 4.4025},
    {"name": "Ghent, Belgium", "lat": 51.0543, "lon": 3.7174},
    {"name": "Amsterdam, Netherlands", "lat": 52.3676, "lon": 4.9041},
    {"name": "Rotterdam, Netherlands", "lat": 51.9225, "lon": 4.4792},
    {"name": "The Hague, Netherlands", "lat": 52.0705, "lon": 4.3007},
    {"name": "Luxembourg City, Luxembourg", "lat": 49.6116, "lon": 6.1319},
    # --- Central Europe: Germany, Austria, Switzerland, Poland, Czechia, Hungary, Slovakia, Slovenia ---
    {"name": "Berlin, Germany", "lat": 52.5200, "lon": 13.4050},
    {"name": "Hamburg, Germany", "lat": 53.5511, "lon": 9.9937},
    {"name": "Munich, Germany", "lat": 48.1351, "lon": 11.5820},
    {"name": "Frankfurt, Germany", "lat": 50.1109, "lon": 8.6821},
    {"name": "Stuttgart, Germany", "lat": 48.7758, "lon": 9.1829},
    {"name": "Dresden, Germany", "lat": 51.0504, "lon": 13.7373},
    {"name": "Vienna, Austria", "lat": 48.2082, "lon": 16.3738},
    {"name": "Salzburg, Austria", "lat": 47.8095, "lon": 13.0550},
    {"name": "Innsbruck, Austria", "lat": 47.2692, "lon": 11.4041},
    {"name": "Zurich, Switzerland", "lat": 47.3769, "lon": 8.5417},
    {"name": "Geneva, Switzerland", "lat": 46.2044, "lon": 6.1432},
    {"name": "Basel, Switzerland", "lat": 47.5596, "lon": 7.5886},
    {"name": "Prague, Czechia", "lat": 50.0755, "lon": 14.4378},
    {"name": "Brno, Czechia", "lat": 49.1951, "lon": 16.6068},
    {"name": "Krakow, Poland", "lat": 50.0647, "lon": 19.9450},
    {"name": "Warsaw, Poland", "lat": 52.2297, "lon": 21.0122},
    {"name": "Wroclaw, Poland", "lat": 51.1079, "lon": 17.0385},
    {"name": "Gdansk, Poland", "lat": 54.3520, "lon": 18.6466},
    {"name": "Budapest, Hungary", "lat": 47.4979, "lon": 19.0402},
    {"name": "Debrecen, Hungary", "lat": 47.5316, "lon": 21.6273},
    {"name": "Bratislava, Slovakia", "lat": 48.1486, "lon": 17.1077},
    {"name": "Kosice, Slovakia", "lat": 48.7164, "lon": 21.2611},
    {"name": "Ljubljana, Slovenia", "lat": 46.0569, "lon": 14.5058},
    {"name": "Maribor, Slovenia", "lat": 46.5547, "lon": 15.6459},
    # --- Balkans: Greece (already covered in Greece list), Albania, Bulgaria, Romania, Serbia, Croatia, Montenegro, North Macedonia, Bosnia, Kosovo ---
    {"name": "Sofia, Bulgaria", "lat": 42.6977, "lon": 23.3219},
    {"name": "Plovdiv, Bulgaria", "lat": 42.1354, "lon": 24.7453},
    {"name": "Varna, Bulgaria", "lat": 43.2141, "lon": 27.9147},
    {"name": "Bucharest, Romania", "lat": 44.4268, "lon": 26.1025},
    {"name": "Cluj-Napoca, Romania", "lat": 46.7712, "lon": 23.6236},
    {"name": "Timișoara, Romania", "lat": 45.7489, "lon": 21.2087},
    {"name": "Belgrade, Serbia", "lat": 44.7866, "lon": 20.4489},
    {"name": "Novi Sad, Serbia", "lat": 45.2671, "lon": 19.8335},
    {"name": "Niš, Serbia", "lat": 43.3209, "lon": 21.8958},
    {"name": "Sarajevo, Bosnia and Herzegovina", "lat": 43.8563, "lon": 18.4131},
    {"name": "Banja Luka, Bosnia and Herzegovina", "lat": 44.7722, "lon": 17.1910},
    {"name": "Skopje, North Macedonia", "lat": 41.9973, "lon": 21.4280},
    {"name": "Tetovo, North Macedonia", "lat": 42.0106, "lon": 20.9715},
    {"name": "Podgorica, Montenegro", "lat": 42.4304, "lon": 19.2594},
    {"name": "Bar, Montenegro", "lat": 42.0938, "lon": 19.1003},
    {"name": "Tirana, Albania", "lat": 41.3275, "lon": 19.8187},
    {"name": "Durrës, Albania", "lat": 41.3231, "lon": 19.4414},
    {"name": "Pristina, Kosovo", "lat": 42.6629, "lon": 21.1655},
    {"name": "Zagreb, Croatia", "lat": 45.8150, "lon": 15.9819},
    {"name": "Split, Croatia", "lat": 43.5081, "lon": 16.4402},
    {"name": "Dubrovnik, Croatia", "lat": 42.6507, "lon": 18.0944},
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275},
    {"name": "Thessaloniki", "lat": 40.6401, "lon": 22.9444},
    {"name": "Patras", "lat": 38.2466, "lon": 21.7346},
    {"name": "Heraklion", "lat": 35.3387, "lon": 25.1442},
    {"name": "Larissa", "lat": 39.6390, "lon": 22.4191},
    {"name": "Volos", "lat": 39.3622, "lon": 22.9420},
    {"name": "Ioannina", "lat": 39.6650, "lon": 20.8537},
    # --- Ukraine, Belarus, Moldova ---
    {"name": "Kyiv, Ukraine", "lat": 50.4501, "lon": 30.5234},
    {"name": "Kharkiv, Ukraine", "lat": 49.9935, "lon": 36.2304},
    {"name": "Odesa, Ukraine", "lat": 46.4825, "lon": 30.7233},
    {"name": "Dnipro, Ukraine", "lat": 48.4647, "lon": 35.0462},
    {"name": "Lviv, Ukraine", "lat": 49.8397, "lon": 24.0297},
    {"name": "Zaporizhzhia, Ukraine", "lat": 47.8388, "lon": 35.1396},
    {"name": "Minsk, Belarus", "lat": 53.9006, "lon": 27.5590},
    {"name": "Gomel, Belarus", "lat": 52.4345, "lon": 30.9754},
    {"name": "Brest, Belarus", "lat": 52.0976, "lon": 23.7341},
    {"name": "Chisinau, Moldova", "lat": 47.0105, "lon": 28.8638},
    # --- Russia (European Russia, only cities west of Ural) ---
    {"name": "Moscow, Russia", "lat": 55.7558, "lon": 37.6176},
    {"name": "Saint Petersburg, Russia", "lat": 59.9343, "lon": 30.3351},
    {"name": "Nizhny Novgorod, Russia", "lat": 56.2965, "lon": 43.9361},
    {"name": "Kazan, Russia", "lat": 55.8304, "lon": 49.0661},
    {"name": "Samara, Russia", "lat": 53.1959, "lon": 50.1008},
    {"name": "Voronezh, Russia", "lat": 51.6615, "lon": 39.2003},
    {"name": "Rostov-on-Don, Russia", "lat": 47.2357, "lon": 39.7015},
    {"name": "Sochi, Russia", "lat": 43.6028, "lon": 39.7342},
    {"name": "Volgograd, Russia", "lat": 48.7080, "lon": 44.5133},
    {"name": "Kaliningrad, Russia", "lat": 54.7104, "lon": 20.4522},
    # --- Northern Europe: Scandinavia, Finland, Baltics, Iceland ---
    {"name": "Oslo, Norway", "lat": 59.9139, "lon": 10.7522},
    {"name": "Bergen, Norway", "lat": 60.3913, "lon": 5.3221},
    {"name": "Stockholm, Sweden", "lat": 59.3293, "lon": 18.0686},
    {"name": "Gothenburg, Sweden", "lat": 57.7089, "lon": 11.9746},
    {"name": "Malmö, Sweden", "lat": 55.604981, "lon": 13.003822},
    {"name": "Helsinki, Finland", "lat": 60.1699, "lon": 24.9384},
    {"name": "Turku, Finland", "lat": 60.4518, "lon": 22.2666},
    {"name": "Tallinn, Estonia", "lat": 59.4370, "lon": 24.7536},
    {"name": "Tartu, Estonia", "lat": 58.3776, "lon": 26.7290},
    {"name": "Riga, Latvia", "lat": 56.9496, "lon": 24.1052},
    {"name": "Vilnius, Lithuania", "lat": 54.6872, "lon": 25.2797},
    {"name": "Reykjavik, Iceland", "lat": 64.1466, "lon": -21.9426},
    {"name": "Akureyri, Iceland", "lat": 65.6839, "lon": -18.1105},
    # --- Southern Europe: Italy, Spain, Malta, etc. ---
    {"name": "Rome, Italy", "lat": 41.9028, "lon": 12.4964},
    {"name": "Milan, Italy", "lat": 45.4642, "lon": 9.19},
    {"name": "Naples, Italy", "lat": 40.8518, "lon": 14.2681},
    {"name": "Palermo, Italy", "lat": 38.1157, "lon": 13.3615},
    {"name": "Venice, Italy", "lat": 45.4408, "lon": 12.3155},
    {"name": "Florence, Italy", "lat": 43.7696, "lon": 11.2558},
    {"name": "Turin, Italy", "lat": 45.0703, "lon": 7.6869},
    {"name": "Madrid, Spain", "lat": 40.4168, "lon": -3.7038},
    {"name": "Barcelona, Spain", "lat": 41.3851, "lon": 2.1734},
    {"name": "Valencia, Spain", "lat": 39.4699, "lon": -0.3763},
    {"name": "Seville, Spain", "lat": 37.3891, "lon": -5.9845},
    {"name": "Malaga, Spain", "lat": 36.7213, "lon": -4.4214},
    {"name": "Zaragoza, Spain", "lat": 41.6488, "lon": -0.8891},
    {"name": "Palma de Mallorca, Spain", "lat": 39.5696, "lon": 2.6502},
    {"name": "Bilbao, Spain", "lat": 43.2630, "lon": -2.9350},
    {"name": "Porto, Portugal", "lat": 41.1579, "lon": -8.6291},
    {"name": "Lisbon, Portugal", "lat": 38.7223, "lon": -9.1393},
    {"name": "Funchal, Portugal (Madeira)", "lat": 32.6669, "lon": -16.9241},
    {"name": "Valletta, Malta", "lat": 35.8989, "lon": 14.5146},
    # --- Small and beautiful towns across Europe ---
    {"name": "Giethoorn, Netherlands", "lat": 52.7431, "lon": 6.0886},
    {"name": "Hallstatt, Austria", "lat": 47.5613, "lon": 13.6493},
    {"name": "Český Krumlov, Czechia", "lat": 48.8105, "lon": 14.3158},
    {"name": "Grindelwald, Switzerland", "lat": 46.6240, "lon": 8.0414},
    {"name": "Positano, Italy", "lat": 40.6281, "lon": 14.4849},
    {"name": "Sighișoara, Romania", "lat": 46.2194, "lon": 24.7922},
    {"name": "Meteora, Greece", "lat": 39.7217, "lon": 21.6317},
    {"name": "Kotor, Montenegro", "lat": 42.4247, "lon": 18.7712},
    {"name": "Santillana del Mar, Spain", "lat": 43.3877, "lon": -4.1085},
    {"name": "Ronda, Spain", "lat": 36.7423, "lon": -5.1671},
    {"name": "Rothenburg ob der Tauber, Germany", "lat": 49.3784, "lon": 10.1780},
    {"name": "Colmar, France", "lat": 48.0792, "lon": 7.3585},
    {"name": "Saint-Malo, France", "lat": 48.6493, "lon": -2.0257},
    {"name": "Sintra, Portugal", "lat": 38.8029, "lon": -9.3817},
    {"name": "Obidos, Portugal", "lat": 39.3600, "lon": -9.1567},
]


africa = [
    {"name": "Cairo, Egypt", "lat": 30.0444, "lon": 31.2357},
    {"name": "Alexandria, Egypt", "lat": 31.2001, "lon": 29.9187},
    {"name": "Giza, Egypt", "lat": 30.0131, "lon": 31.2089},
    {"name": "Lagos, Nigeria", "lat": 6.5244, "lon": 3.3792},
    {"name": "Kano, Nigeria", "lat": 12.0022, "lon": 8.5919},
    {"name": "Ibadan, Nigeria", "lat": 7.3775, "lon": 3.9470},
    {"name": "Abuja, Nigeria", "lat": 9.0579, "lon": 7.4951},
    {"name": "Nairobi, Kenya", "lat": -1.286389, "lon": 36.817223},
    {"name": "Mombasa, Kenya", "lat": -4.0435, "lon": 39.6682},
    {"name": "Kisumu, Kenya", "lat": -0.0917, "lon": 34.7679},
    {"name": "Addis Ababa, Ethiopia", "lat": 9.03, "lon": 38.74},
    {"name": "Dire Dawa, Ethiopia", "lat": 9.6008, "lon": 41.8500},
    {"name": "Johannesburg, S. Africa", "lat": -26.2041, "lon": 28.0473},
    {"name": "Cape Town, S. Africa", "lat": -33.9249, "lon": 18.4241},
    {"name": "Durban, S. Africa", "lat": -29.8587, "lon": 31.0218},
    {"name": "Pretoria, S. Africa", "lat": -25.7479, "lon": 28.2293},
    {"name": "Port Elizabeth, S. Africa", "lat": -33.9608, "lon": 25.6022},
    {"name": "Algiers, Algeria", "lat": 36.7538, "lon": 3.0588},
    {"name": "Oran, Algeria", "lat": 35.6971, "lon": -0.6308},
    {"name": "Casablanca, Morocco", "lat": 33.5731, "lon": -7.5898},
    {"name": "Marrakesh, Morocco", "lat": 31.6295, "lon": -7.9811},
    {"name": "Rabat, Morocco", "lat": 34.0209, "lon": -6.8417},
    {"name": "Tunis, Tunisia", "lat": 36.8065, "lon": 10.1815},
    {"name": "Tripoli, Libya", "lat": 32.8872, "lon": 13.1913},
    {"name": "Bamako, Mali", "lat": 12.6392, "lon": -8.0029},
    {"name": "Dakar, Senegal", "lat": 14.7167, "lon": -17.4677},
    {"name": "Accra, Ghana", "lat": 5.6037, "lon": -0.1870},
    {"name": "Kumasi, Ghana", "lat": 6.6666, "lon": -1.6163},
    {"name": "Ouagadougou, Burkina Faso", "lat": 12.3714, "lon": -1.5197},
    {"name": "Kampala, Uganda", "lat": 0.3476, "lon": 32.5825},
    {"name": "Entebbe, Uganda", "lat": 0.0516, "lon": 32.4637},
    {"name": "Luanda, Angola", "lat": -8.8390, "lon": 13.2894},
    {"name": "Lobito, Angola", "lat": -12.3547, "lon": 13.5432},
    {"name": "Maputo, Mozambique", "lat": -25.9692, "lon": 32.5732},
    {"name": "Nampula, Mozambique", "lat": -15.1167, "lon": 39.2667},
    {"name": "Windhoek, Namibia", "lat": -22.5597, "lon": 17.0832},
    {"name": "Gaborone, Botswana", "lat": -24.6282, "lon": 25.9231},
    {"name": "Harare, Zimbabwe", "lat": -17.8252, "lon": 31.0335},
    {"name": "Bulawayo, Zimbabwe", "lat": -20.15, "lon": 28.5833},
    {"name": "Mogadishu, Somalia", "lat": 2.0469, "lon": 45.3182},
    {"name": "Djibouti, Djibouti", "lat": 11.5742, "lon": 43.1456},
    {"name": "Kigali, Rwanda", "lat": -1.9706, "lon": 30.1044},
    {"name": "Bujumbura, Burundi", "lat": -3.3869, "lon": 29.3611},
    # Small towns
    {"name": "Ouarzazate, Morocco", "lat": 30.9189, "lon": -6.8936},
    {"name": "Kasane, Botswana", "lat": -17.7981, "lon": 25.1557},
    {"name": "Victoria Falls, Zimbabwe", "lat": -17.9307, "lon": 25.8302},
    {"name": "St. Louis, Senegal", "lat": 16.0179, "lon": -16.4897},
    {"name": "Luderitz, Namibia", "lat": -26.6481, "lon": 15.1594},
]

east_asia = [
    # China (major & secondary)
    {"name": "Beijing, China", "lat": 39.9042, "lon": 116.4074},
    {"name": "Shanghai, China", "lat": 31.2304, "lon": 121.4737},
    {"name": "Guangzhou, China", "lat": 23.1291, "lon": 113.2644},
    {"name": "Shenzhen, China", "lat": 22.5429, "lon": 114.0596},
    {"name": "Chengdu, China", "lat": 30.5728, "lon": 104.0668},
    {"name": "Wuhan, China", "lat": 30.5928, "lon": 114.3055},
    {"name": "Xi'an, China", "lat": 34.3416, "lon": 108.9398},
    {"name": "Harbin, China", "lat": 45.8038, "lon": 126.5349},
    {"name": "Hangzhou, China", "lat": 30.2741, "lon": 120.1551},
    {"name": "Suzhou, China", "lat": 31.2989, "lon": 120.5853},
    {"name": "Qingdao, China", "lat": 36.0671, "lon": 120.3826},
    {"name": "Nanjing, China", "lat": 32.0603, "lon": 118.7969},
    {"name": "Tianjin, China", "lat": 39.3434, "lon": 117.3616},
    {"name": "Dalian, China", "lat": 38.9140, "lon": 121.6147},
    {"name": "Chongqing, China", "lat": 29.4316, "lon": 106.9123},
    {"name": "Lhasa, China (Tibet)", "lat": 29.6520, "lon": 91.1721},
    # Japan (more cities)
    {"name": "Tokyo, Japan", "lat": 35.6895, "lon": 139.6917},
    {"name": "Osaka, Japan", "lat": 34.6937, "lon": 135.5023},
    {"name": "Yokohama, Japan", "lat": 35.4437, "lon": 139.6380},
    {"name": "Nagoya, Japan", "lat": 35.1815, "lon": 136.9066},
    {"name": "Sapporo, Japan", "lat": 43.0618, "lon": 141.3545},
    {"name": "Fukuoka, Japan", "lat": 33.5902, "lon": 130.4017},
    {"name": "Kobe, Japan", "lat": 34.6901, "lon": 135.1955},
    {"name": "Kyoto, Japan", "lat": 35.0116, "lon": 135.7681},
    {"name": "Hiroshima, Japan", "lat": 34.3853, "lon": 132.4553},
    {"name": "Sendai, Japan", "lat": 38.2682, "lon": 140.8694},
    {"name": "Naha, Japan (Okinawa)", "lat": 26.2124, "lon": 127.6809},
    {"name": "Nagano, Japan", "lat": 36.6486, "lon": 138.1948},
    {"name": "Niigata, Japan", "lat": 37.9162, "lon": 139.0365},
    {"name": "Hakodate, Japan", "lat": 41.7688, "lon": 140.7288},
    {"name": "Nagasaki, Japan", "lat": 32.7503, "lon": 129.8777},
    {"name": "Kanazawa, Japan", "lat": 36.5613, "lon": 136.6562},
    {"name": "Kumamoto, Japan", "lat": 32.8031, "lon": 130.7079},
    {"name": "Matsuyama, Japan", "lat": 33.8392, "lon": 132.7657},
    # South Korea
    {"name": "Seoul, South Korea", "lat": 37.5665, "lon": 126.9780},
    {"name": "Busan, South Korea", "lat": 35.1796, "lon": 129.0756},
    {"name": "Incheon, South Korea", "lat": 37.4563, "lon": 126.7052},
    {"name": "Daegu, South Korea", "lat": 35.8722, "lon": 128.6025},
    {"name": "Gwangju, South Korea", "lat": 35.1595, "lon": 126.8526},
    {"name": "Daejeon, South Korea", "lat": 36.3504, "lon": 127.3845},
    {"name": "Ulsan, South Korea", "lat": 35.5384, "lon": 129.3114},
    {"name": "Jeonju, South Korea", "lat": 35.8242, "lon": 127.1480},
    {"name": "Suwon, South Korea", "lat": 37.2636, "lon": 127.0286},
    # North Korea
    {"name": "Pyongyang, North Korea", "lat": 39.0392, "lon": 125.7625},
    {"name": "Wonsan, North Korea", "lat": 39.1606, "lon": 127.4371},
    {"name": "Chongjin, North Korea", "lat": 41.7956, "lon": 129.7758},
    # Taiwan
    {"name": "Taipei, Taiwan", "lat": 25.0329, "lon": 121.5654},
    {"name": "Kaohsiung, Taiwan", "lat": 22.6273, "lon": 120.3014},
    {"name": "Taichung, Taiwan", "lat": 24.1477, "lon": 120.6736},
    {"name": "Tainan, Taiwan", "lat": 22.9997, "lon": 120.2270},
    {"name": "Hualien, Taiwan", "lat": 23.9721, "lon": 121.6020},
    {"name": "Taitung, Taiwan", "lat": 22.7583, "lon": 121.1444},
    # Mongolia
    {"name": "Ulaanbaatar, Mongolia", "lat": 47.8864, "lon": 106.9057},
    {"name": "Darkhan, Mongolia", "lat": 49.4867, "lon": 105.9228},
    {"name": "Erdenet, Mongolia", "lat": 49.0275, "lon": 104.0444},
    # Hong Kong & Macau
    {"name": "Hong Kong", "lat": 22.3193, "lon": 114.1694},
    {"name": "Macau", "lat": 22.1987, "lon": 113.5439},
    # Small cities / cultural sites
    {"name": "Nikko, Japan", "lat": 36.7198, "lon": 139.6983},
    {"name": "Jeju City, South Korea", "lat": 33.4996, "lon": 126.5312},
    {"name": "Matsumoto, Japan", "lat": 36.2381, "lon": 137.9717},
    {"name": "Xiamen, China", "lat": 24.4798, "lon": 118.0894},
    {"name": "Nagasaki, Japan", "lat": 32.7503, "lon": 129.8777},
]


west_asia = [
    # Turkey (expanded)
    {"name": "Istanbul, Turkey", "lat": 41.0082, "lon": 28.9784},
    {"name": "Ankara, Turkey", "lat": 39.9334, "lon": 32.8597},
    {"name": "Izmir, Turkey", "lat": 38.4192, "lon": 27.1287},
    {"name": "Bursa, Turkey", "lat": 40.1950, "lon": 29.0601},
    {"name": "Adana, Turkey", "lat": 37.0, "lon": 35.3213},
    {"name": "Gaziantep, Turkey", "lat": 37.0662, "lon": 37.3833},
    {"name": "Konya, Turkey", "lat": 37.8746, "lon": 32.4932},
    {"name": "Kayseri, Turkey", "lat": 38.7312, "lon": 35.4787},
    {"name": "Mersin, Turkey", "lat": 36.8121, "lon": 34.6415},
    {"name": "Antalya, Turkey", "lat": 36.8969, "lon": 30.7133},
    # Iran (expanded)
    {"name": "Tehran, Iran", "lat": 35.6892, "lon": 51.3890},
    {"name": "Mashhad, Iran", "lat": 36.2605, "lon": 59.6168},
    {"name": "Isfahan, Iran", "lat": 32.6525, "lon": 51.6746},
    {"name": "Karaj, Iran", "lat": 35.8327, "lon": 50.9916},
    {"name": "Shiraz, Iran", "lat": 29.5918, "lon": 52.5837},
    {"name": "Tabriz, Iran", "lat": 38.0700, "lon": 46.2993},
    {"name": "Qom, Iran", "lat": 34.6416, "lon": 50.8746},
    {"name": "Ahvaz, Iran", "lat": 31.3203, "lon": 48.6691},
    {"name": "Kermanshah, Iran", "lat": 34.3142, "lon": 47.0650},
    {"name": "Urmia, Iran", "lat": 37.5527, "lon": 45.0760},
    # Iraq
    {"name": "Baghdad, Iraq", "lat": 33.3152, "lon": 44.3661},
    {"name": "Basra, Iraq", "lat": 30.5085, "lon": 47.7804},
    {"name": "Mosul, Iraq", "lat": 36.3456, "lon": 43.1575},
    {"name": "Erbil, Iraq", "lat": 36.1911, "lon": 44.0091},
    {"name": "Sulaymaniyah, Iraq", "lat": 35.5646, "lon": 45.4322},
    {"name": "Najaf, Iraq", "lat": 32.0004, "lon": 44.3354},
    # Saudi Arabia (major + secondary)
    {"name": "Riyadh, Saudi Arabia", "lat": 24.7136, "lon": 46.6753},
    {"name": "Jeddah, Saudi Arabia", "lat": 21.4858, "lon": 39.1925},
    {"name": "Mecca, Saudi Arabia", "lat": 21.3891, "lon": 39.8579},
    {"name": "Medina, Saudi Arabia", "lat": 24.5247, "lon": 39.5692},
    {"name": "Dammam, Saudi Arabia", "lat": 26.4207, "lon": 50.0888},
    {"name": "Tabuk, Saudi Arabia", "lat": 28.3838, "lon": 36.5550},
    # UAE
    {"name": "Dubai, UAE", "lat": 25.2048, "lon": 55.2708},
    {"name": "Abu Dhabi, UAE", "lat": 24.4539, "lon": 54.3773},
    {"name": "Sharjah, UAE", "lat": 25.3463, "lon": 55.4209},
    {"name": "Ajman, UAE", "lat": 25.4052, "lon": 55.5136},
    {"name": "Ras Al Khaimah, UAE", "lat": 25.8007, "lon": 55.9762},
    # Qatar, Bahrain, Oman, Kuwait
    {"name": "Doha, Qatar", "lat": 25.276987, "lon": 51.520008},
    {"name": "Al Rayyan, Qatar", "lat": 25.2917, "lon": 51.4244},
    {"name": "Manama, Bahrain", "lat": 26.2285, "lon": 50.5860},
    {"name": "Muscat, Oman", "lat": 23.5880, "lon": 58.3829},
    {"name": "Salalah, Oman", "lat": 17.0194, "lon": 54.0897},
    {"name": "Kuwait City, Kuwait", "lat": 29.3759, "lon": 47.9774},
    {"name": "Hawalli, Kuwait", "lat": 29.3321, "lon": 48.0286},
    # Jordan, Lebanon, Syria
    {"name": "Amman, Jordan", "lat": 31.9454, "lon": 35.9284},
    {"name": "Zarqa, Jordan", "lat": 32.0728, "lon": 36.0880},
    {"name": "Aqaba, Jordan", "lat": 29.5320, "lon": 35.0060},
    {"name": "Irbid, Jordan", "lat": 32.5556, "lon": 35.85},
    {"name": "Beirut, Lebanon", "lat": 33.8938, "lon": 35.5018},
    {"name": "Tripoli, Lebanon", "lat": 34.4367, "lon": 35.8497},
    {"name": "Sidon, Lebanon", "lat": 33.5606, "lon": 35.3756},
    {"name": "Damascus, Syria", "lat": 33.5138, "lon": 36.2765},
    {"name": "Aleppo, Syria", "lat": 36.2021, "lon": 37.1343},
    {"name": "Homs, Syria", "lat": 34.7269, "lon": 36.7234},
    {"name": "Latakia, Syria", "lat": 35.5196, "lon": 35.7915},
    # Israel & Palestine
    {"name": "Jerusalem, Israel", "lat": 31.7683, "lon": 35.2137},
    {"name": "Tel Aviv, Israel", "lat": 32.0853, "lon": 34.7818},
    {"name": "Haifa, Israel", "lat": 32.7940, "lon": 34.9896},
    {"name": "Beersheba, Israel", "lat": 31.2518, "lon": 34.7913},
    {"name": "Gaza City, Palestine", "lat": 31.5017, "lon": 34.4668},
    {"name": "Hebron, Palestine", "lat": 31.5326, "lon": 35.0998},
    {"name": "Nablus, Palestine", "lat": 32.2211, "lon": 35.2544},
    # Armenia, Azerbaijan, Georgia
    {"name": "Yerevan, Armenia", "lat": 40.1792, "lon": 44.4991},
    {"name": "Gyumri, Armenia", "lat": 40.7894, "lon": 43.8475},
    {"name": "Stepanakert, Artsakh", "lat": 39.8177, "lon": 46.7513},
    {"name": "Baku, Azerbaijan", "lat": 40.4093, "lon": 49.8671},
    {"name": "Ganja, Azerbaijan", "lat": 40.6828, "lon": 46.3606},
    {"name": "Sumqayit, Azerbaijan", "lat": 40.5897, "lon": 49.6686},
    {"name": "Tbilisi, Georgia", "lat": 41.7151, "lon": 44.8271},
    {"name": "Batumi, Georgia", "lat": 41.6168, "lon": 41.6367},
    {"name": "Kutaisi, Georgia", "lat": 42.2500, "lon": 42.7000},
    # Yemen, Cyprus
    {"name": "Sanaa, Yemen", "lat": 15.3694, "lon": 44.1910},
    {"name": "Aden, Yemen", "lat": 12.7856, "lon": 45.0187},
    {"name": "Nicosia, Cyprus", "lat": 35.1856, "lon": 33.3823},
    {"name": "Limassol, Cyprus", "lat": 34.7071, "lon": 33.0226},
    # Small towns, heritage, and border towns
    {"name": "Şanlıurfa, Turkey", "lat": 37.1674, "lon": 38.7955},
    {"name": "Petra, Jordan", "lat": 30.3285, "lon": 35.4444},
    {"name": "Bandar Abbas, Iran", "lat": 27.1832, "lon": 56.2666},
    {"name": "Jazan, Saudi Arabia", "lat": 16.8898, "lon": 42.5511},
    {"name": "Dohuk, Iraq", "lat": 36.8663, "lon": 42.9881},
]
south_asia = [
    # India (pan-India, many cities/regions)
    {"name": "Mumbai, India", "lat": 19.0760, "lon": 72.8777},
    {"name": "Delhi, India", "lat": 28.6139, "lon": 77.2090},
    {"name": "Bangalore, India", "lat": 12.9716, "lon": 77.5946},
    {"name": "Hyderabad, India", "lat": 17.3850, "lon": 78.4867},
    {"name": "Ahmedabad, India", "lat": 23.0225, "lon": 72.5714},
    {"name": "Chennai, India", "lat": 13.0827, "lon": 80.2707},
    {"name": "Kolkata, India", "lat": 22.5726, "lon": 88.3639},
    {"name": "Pune, India", "lat": 18.5204, "lon": 73.8567},
    {"name": "Jaipur, India", "lat": 26.9124, "lon": 75.7873},
    {"name": "Lucknow, India", "lat": 26.8467, "lon": 80.9462},
    {"name": "Kanpur, India", "lat": 26.4499, "lon": 80.3319},
    {"name": "Nagpur, India", "lat": 21.1458, "lon": 79.0882},
    {"name": "Indore, India", "lat": 22.7196, "lon": 75.8577},
    {"name": "Bhopal, India", "lat": 23.2599, "lon": 77.4126},
    {"name": "Visakhapatnam, India", "lat": 17.6868, "lon": 83.2185},
    {"name": "Thane, India", "lat": 19.2183, "lon": 72.9781},
    {"name": "Pimpri-Chinchwad, India", "lat": 18.6298, "lon": 73.7997},
    {"name": "Patna, India", "lat": 25.5941, "lon": 85.1376},
    {"name": "Vadodara, India", "lat": 22.3072, "lon": 73.1812},
    {"name": "Ghaziabad, India", "lat": 28.6692, "lon": 77.4538},
    {"name": "Ludhiana, India", "lat": 30.9005, "lon": 75.8573},
    {"name": "Agra, India", "lat": 27.1767, "lon": 78.0081},
    {"name": "Varanasi, India", "lat": 25.3176, "lon": 82.9739},
    {"name": "Srinagar, India", "lat": 34.0837, "lon": 74.7973},
    {"name": "Amritsar, India", "lat": 31.6340, "lon": 74.8723},
    {"name": "Coimbatore, India", "lat": 11.0168, "lon": 76.9558},
    {"name": "Vijayawada, India", "lat": 16.5062, "lon": 80.6480},
    {"name": "Guwahati, India", "lat": 26.1445, "lon": 91.7362},
    {"name": "Goa, India", "lat": 15.2993, "lon": 74.1240},
    {"name": "Madurai, India", "lat": 9.9252, "lon": 78.1198},
    {"name": "Kochi, India", "lat": 9.9312, "lon": 76.2673},
    {"name": "Kozhikode, India", "lat": 11.2588, "lon": 75.7804},
    {"name": "Trivandrum, India", "lat": 8.5241, "lon": 76.9366},
    # Pakistan
    {"name": "Karachi, Pakistan", "lat": 24.8607, "lon": 67.0011},
    {"name": "Lahore, Pakistan", "lat": 31.5204, "lon": 74.3587},
    {"name": "Faisalabad, Pakistan", "lat": 31.4504, "lon": 73.1350},
    {"name": "Rawalpindi, Pakistan", "lat": 33.5651, "lon": 73.0169},
    {"name": "Islamabad, Pakistan", "lat": 33.6844, "lon": 73.0479},
    {"name": "Peshawar, Pakistan", "lat": 34.0150, "lon": 71.5805},
    {"name": "Multan, Pakistan", "lat": 30.1575, "lon": 71.5249},
    # Bangladesh
    {"name": "Dhaka, Bangladesh", "lat": 23.8103, "lon": 90.4125},
    {"name": "Chittagong, Bangladesh", "lat": 22.3569, "lon": 91.7832},
    {"name": "Khulna, Bangladesh", "lat": 22.8456, "lon": 89.5403},
    {"name": "Rajshahi, Bangladesh", "lat": 24.3636, "lon": 88.6241},
    {"name": "Sylhet, Bangladesh", "lat": 24.9045, "lon": 91.8611},
    {"name": "Mymensingh, Bangladesh", "lat": 24.7471, "lon": 90.4203},
    # Nepal
    {"name": "Kathmandu, Nepal", "lat": 27.7172, "lon": 85.3240},
    {"name": "Pokhara, Nepal", "lat": 28.2096, "lon": 83.9856},
    {"name": "Lalitpur, Nepal", "lat": 27.6676, "lon": 85.3206},
    {"name": "Biratnagar, Nepal", "lat": 26.4525, "lon": 87.2718},
    {"name": "Birgunj, Nepal", "lat": 27.0110, "lon": 84.8678},
    # Sri Lanka
    {"name": "Colombo, Sri Lanka", "lat": 6.9271, "lon": 79.8612},
    {"name": "Kandy, Sri Lanka", "lat": 7.2906, "lon": 80.6337},
    {"name": "Jaffna, Sri Lanka", "lat": 9.6684, "lon": 80.0074},
    {"name": "Galle, Sri Lanka", "lat": 6.0326, "lon": 80.2170},
    # Afghanistan, Bhutan, Maldives
    {"name": "Kabul, Afghanistan", "lat": 34.5553, "lon": 69.2075},
    {"name": "Herat, Afghanistan", "lat": 34.3529, "lon": 62.2040},
    {"name": "Kandahar, Afghanistan", "lat": 31.6289, "lon": 65.7372},
    {"name": "Thimphu, Bhutan", "lat": 27.4728, "lon": 89.6390},
    {"name": "Paro, Bhutan", "lat": 27.4305, "lon": 89.4167},
    {"name": "Malé, Maldives", "lat": 4.1755, "lon": 73.5093},
]

australia = [
    {"name": "Sydney, Australia", "lat": -33.8688, "lon": 151.2093},
    {"name": "Melbourne, Australia", "lat": -37.8136, "lon": 144.9631},
    {"name": "Brisbane, Australia", "lat": -27.4698, "lon": 153.0251},
    {"name": "Perth, Australia", "lat": -31.9505, "lon": 115.8605},
    {"name": "Adelaide, Australia", "lat": -34.9285, "lon": 138.6007},
    {"name": "Hobart, Australia", "lat": -42.8821, "lon": 147.3272},
    {"name": "Darwin, Australia", "lat": -12.4634, "lon": 130.8456},
    {"name": "Canberra, Australia", "lat": -35.2809, "lon": 149.1300},
    {"name": "Gold Coast, Australia", "lat": -28.0167, "lon": 153.4000},
    {"name": "Newcastle, Australia", "lat": -32.9283, "lon": 151.7817},
    {"name": "Geelong, Australia", "lat": -38.1471, "lon": 144.3607},
    {"name": "Auckland, New Zealand", "lat": -36.8485, "lon": 174.7633},
    {"name": "Wellington, New Zealand", "lat": -41.2865, "lon": 174.7762},
    {"name": "Christchurch, New Zealand", "lat": -43.5321, "lon": 172.6362},
    {"name": "Dunedin, New Zealand", "lat": -45.8788, "lon": 170.5028},
    {"name": "Hamilton, New Zealand", "lat": -37.7833, "lon": 175.2833},
    {"name": "Suva, Fiji", "lat": -18.1248, "lon": 178.4501},
    {"name": "Port Vila, Vanuatu", "lat": -17.7333, "lon": 168.3167},
    {"name": "Honiara, Solomon Islands", "lat": -9.4333, "lon": 159.9500},
    {"name": "Apia, Samoa", "lat": -13.8333, "lon": -171.7667},
    {"name": "Nuku'alofa, Tonga", "lat": -21.1394, "lon": -175.2044},
    {"name": "Funafuti, Tuvalu", "lat": -8.5243, "lon": 179.1947},
    {"name": "Majuro, Marshall Islands", "lat": 7.1164, "lon": 171.1850},
    {"name": "Nouméa, New Caledonia", "lat": -22.2758, "lon": 166.4580},
    # Small towns
    {"name": "Queenstown, New Zealand", "lat": -45.0312, "lon": 168.6626},
    {"name": "Broken Hill, Australia", "lat": -31.9530, "lon": 141.4535},
    {"name": "Coober Pedy, Australia", "lat": -29.0066, "lon": 134.7558},
    {"name": "Devonport, Australia", "lat": -41.1769, "lon": 146.3500},
    {"name": "Katoomba, Australia", "lat": -33.7128, "lon": 150.3119},
]


poles = [
    {"name": "Longyearbyen, Svalbard", "lat": 78.2232, "lon": 15.6469},
    {"name": "Alert, Canada", "lat": 82.5018, "lon": -62.3481},
    {"name": "Ny-Ålesund, Svalbard", "lat": 78.9236, "lon": 11.9231},
    {"name": "Tiksi, Russia", "lat": 71.6872, "lon": 128.8647},
    {"name": "Barrow (Utqiaġvik), Alaska", "lat": 71.2906, "lon": -156.7887},
    {"name": "McMurdo Station, Antarctica", "lat": -77.8419, "lon": 166.6863},
    {"name": "Vostok Station, Antarctica", "lat": -78.4648, "lon": 106.8372},
    {"name": "Amundsen-Scott South Pole Station", "lat": -90.0000, "lon": 0.0000},
    {"name": "Esperanza Base, Antarctica", "lat": -63.4, "lon": -56.9833},
    {"name": "Resolute, Canada", "lat": 74.6973, "lon": -94.8293},
    {"name": "Qaanaaq, Greenland", "lat": 77.4667, "lon": -69.2333},
    {"name": "Ushuaia, Argentina", "lat": -54.8019, "lon": -68.3030},
    # Small settlements
    {"name": "Murmansk, Russia", "lat": 68.9730, "lon": 33.0856},
    {"name": "Nome, Alaska", "lat": 64.5011, "lon": -165.4064},
    {"name": "South Georgia, UK", "lat": -54.2811, "lon": -36.5092},
    {"name": "Tromsø, Norway", "lat": 69.6496, "lon": 18.9560},
    {"name": "Inuvik, Canada", "lat": 68.3605, "lon": -133.7218},
    {"name": "Srednekolymsk, Russia", "lat": 67.4500, "lon": 153.6833},
    {"name": "Barentsburg, Svalbard", "lat": 78.0667, "lon": 14.2167},
]

greece = [
    {"name": "Athens", "lat": 37.9838, "lon": 23.7275},
    {"name": "Thessaloniki", "lat": 40.6401, "lon": 22.9444},
    {"name": "Patras", "lat": 38.2466, "lon": 21.7346},
    {"name": "Heraklion", "lat": 35.3387, "lon": 25.1442},
    {"name": "Larissa", "lat": 39.6390, "lon": 22.4191},
    {"name": "Volos", "lat": 39.3622, "lon": 22.9420},
    {"name": "Ioannina", "lat": 39.6650, "lon": 20.8537},
    {"name": "Chania", "lat": 35.5138, "lon": 24.0180},
    {"name": "Rhodes", "lat": 36.4349, "lon": 28.2176},
    {"name": "Alexandroupoli", "lat": 40.8457, "lon": 25.8746},
    {"name": "Kavala", "lat": 40.9369, "lon": 24.4129},
    {"name": "Kalamata", "lat": 37.0386, "lon": 22.1142},
    {"name": "Trikala", "lat": 39.5556, "lon": 21.7675},
    {"name": "Serres", "lat": 41.0850, "lon": 23.5476},
    {"name": "Agrinio", "lat": 38.6218, "lon": 21.4078},
    {"name": "Katerini", "lat": 40.2697, "lon": 22.5061},
    {"name": "Drama", "lat": 41.1528, "lon": 24.1474},
    {"name": "Lamia", "lat": 38.9009, "lon": 22.4348},
    {"name": "Piraeus", "lat": 37.9421, "lon": 23.6465},
    {"name": "Corfu", "lat": 39.6243, "lon": 19.9217},
    {"name": "Mytilene", "lat": 39.1071, "lon": 26.5551},
    {"name": "Chalcis", "lat": 38.4636, "lon": 23.6027},
    {"name": "Rethymno", "lat": 35.3644, "lon": 24.4822},
    {"name": "Kos", "lat": 36.8938, "lon": 27.2877},
    {"name": "Sparta", "lat": 37.0745, "lon": 22.4301},
    {"name": "Edessa", "lat": 40.8014, "lon": 22.0471},
    {"name": "Florina", "lat": 40.7821, "lon": 21.4094},
    {"name": "Preveza", "lat": 38.9561, "lon": 20.7517},
    {"name": "Argos", "lat": 37.6333, "lon": 22.7333},
    {"name": "Nafplio", "lat": 37.5676, "lon": 22.8066},
    {"name": "Sitia", "lat": 35.2076, "lon": 26.1026},
    {"name": "Gythio", "lat": 36.7569, "lon": 22.5708},
    {"name": "Amfissa", "lat": 38.5283, "lon": 22.3852},
    {"name": "Kalambaka", "lat": 39.7082, "lon": 21.6307},
    {"name": "Thiva", "lat": 38.3252, "lon": 23.3186},
    {"name": "Elassona", "lat": 39.8888, "lon": 22.1887},
    {"name": "Orestiada", "lat": 41.5031, "lon": 26.5295},
    {"name": "Megara", "lat": 37.9956, "lon": 23.3457},
    {"name": "Kilkis", "lat": 40.9936, "lon": 22.8733},
    {"name": "Giannitsa", "lat": 40.7910, "lon": 22.4071},
    {"name": "Ptolemaida", "lat": 40.5147, "lon": 21.6787},
    {"name": "Nea Ionia", "lat": 39.3739, "lon": 22.9320},
    {"name": "Karditsa", "lat": 39.3642, "lon": 21.9210},
    {"name": "Myrina", "lat": 39.8750, "lon": 25.0586},
    {"name": "Kastoria", "lat": 40.5200, "lon": 21.2631},
    {"name": "Veria", "lat": 40.5244, "lon": 22.2024},
    {"name": "Pyrgos", "lat": 37.6751, "lon": 21.4410},
    {"name": "Ierapetra", "lat": 35.0139, "lon": 25.7412},
    {"name": "Levadia", "lat": 38.4369, "lon": 22.8778},
    {"name": "Korinthos", "lat": 37.9411, "lon": 22.9519},
    {"name": "Komotini", "lat": 41.1200, "lon": 25.4053},
    {"name": "Arta", "lat": 39.1607, "lon": 20.9851},
    {"name": "Tripoli", "lat": 37.5089, "lon": 22.3794},
    {"name": "Poligiros", "lat": 40.3777, "lon": 23.4403},
    {"name": "Naxos", "lat": 37.1030, "lon": 25.3762},
    {"name": "Samos", "lat": 37.7548, "lon": 26.9776},
    {"name": "Kastellorizo", "lat": 36.1514, "lon": 29.5917},
    {"name": "Kalamata", "lat": 37.0386, "lon": 22.1142},
    {"name": "Lefkada", "lat": 38.8333, "lon": 20.7000},
    {"name": "Zakynthos", "lat": 37.7799, "lon": 20.8950},
    {"name": "Skiathos", "lat": 39.1621, "lon": 23.4917},
    {"name": "Samos", "lat": 37.7548, "lon": 26.9776},
    {"name": "Paros", "lat": 37.0850, "lon": 25.1518},
    {"name": "Milos", "lat": 36.7398, "lon": 24.4194},
    {"name": "Kea", "lat": 37.6612, "lon": 24.3341},
    {"name": "Kythira", "lat": 36.1550, "lon": 22.9994},
    {"name": "Limnos", "lat": 39.9104, "lon": 25.2366},
    {"name": "Sifnos", "lat": 36.9762, "lon": 24.6936},
    {"name": "Amorgos", "lat": 36.8340, "lon": 25.9001},
    {"name": "Sitia", "lat": 35.2076, "lon": 26.1026},
    {"name": "Karpenisi", "lat": 39.0222, "lon": 21.7972},
    {"name": "Preveza", "lat": 38.9561, "lon": 20.7517},
    {"name": "Edessa", "lat": 40.8014, "lon": 22.0471},
    {"name": "Drama", "lat": 41.1528, "lon": 24.1474},
    {"name": "Elounda", "lat": 35.2641, "lon": 25.7227},
    {"name": "Methoni", "lat": 36.8180, "lon": 21.7031},
    {"name": "Porto Heli", "lat": 37.3268, "lon": 23.1456},
    {"name": "Neapoli Voion", "lat": 36.5017, "lon": 22.9733},
    {"name": "Vouliagmeni", "lat": 37.8065, "lon": 23.7765},
    {"name": "Nea Smyrni", "lat": 37.9457, "lon": 23.7148},
    {"name": "Chios", "lat": 38.3680, "lon": 26.1358},
    {"name": "Galaxidi", "lat": 38.3786, "lon": 22.3842},
    {"name": "Metsovo", "lat": 39.7697, "lon": 21.1822},
    {"name": "Oia", "lat": 36.4615, "lon": 25.3753},
    {"name": "Fira", "lat": 36.4167, "lon": 25.4333},
    {"name": "Ialysos", "lat": 36.4190, "lon": 28.1346},
    {"name": "Eretria", "lat": 38.3951, "lon": 23.7955},
    {"name": "Karditsa", "lat": 39.3642, "lon": 21.9210},
    {"name": "Pylos", "lat": 36.9142, "lon": 21.6952},
    {"name": "Myrina", "lat": 39.8750, "lon": 25.0586},
    {"name": "Kilkis", "lat": 40.9936, "lon": 22.8733},
    {"name": "Nea Moudania", "lat": 40.2442, "lon": 23.2878},
    {"name": "Samos Town", "lat": 37.7548, "lon": 26.9776},
    {"name": "Naousa", "lat": 40.6297, "lon": 22.0683},
    {"name": "Polygyros", "lat": 40.3777, "lon": 23.4403},
    {"name": "Xanthi", "lat": 41.1349, "lon": 24.8880},
    {"name": "Kastoria", "lat": 40.5200, "lon": 21.2631},
    {"name": "Skiros", "lat": 38.9056, "lon": 24.5669},
    {"name": "Kardamyli", "lat": 36.8871, "lon": 22.2275},
    {"name": "Arta", "lat": 39.1607, "lon": 20.9851},
]

globe = [ {"name": "New York, US", "lat": 40.7128, "lon": -74.0060}, {"name": "Los Angeles, US", "lat": 34.0522, "lon": -118.2437}, {"name": "Chicago, US", "lat": 41.8781, "lon": -87.6298}, {"name": "Houston, US", "lat": 29.7604, "lon": -95.3698}, {"name": "Toronto, CA", "lat": 43.6532, "lon": -79.3832}, {"name": "Vancouver, CA", "lat": 49.2827, "lon": -123.1207}, {"name": "Montreal, CA", "lat": 45.5017, "lon": -73.5673}, {"name": "Calgary, CA", "lat": 51.0447, "lon": -114.0719}, {"name": "Ottawa, CA", "lat": 45.4215, "lon": -75.6997}, {"name": "Mexico City, MX", "lat": 19.4326, "lon": -99.1332}, {"name": "Guadalajara, MX", "lat": 20.6597, "lon": -103.3496}, {"name": "Monterrey, MX", "lat": 25.6866, "lon": -100.3161}, {"name": "Cancún, MX", "lat": 21.1619, "lon": -86.8515}, {"name": "Miami, US", "lat": 25.7617, "lon": -80.1918}, {"name": "Dallas, US", "lat": 32.7767, "lon": -96.7970}, {"name": "San Francisco, US", "lat": 37.7749, "lon": -122.4194}, {"name": "Washington, D.C., US", "lat": 38.8951, "lon": -77.0364}, {"name": "Atlanta, US", "lat": 33.7490, "lon": -84.3880}, {"name": "Minneapolis, US", "lat": 44.9778, "lon": -93.2650}, {"name": "Denver, US", "lat": 39.7392, "lon": -104.9903}, {"name": "Seattle, US", "lat": 47.6062, "lon": -122.3321}, {"name": "Phoenix, US", "lat": 33.4484, "lon": -112.0740}, {"name": "São Paulo, BR", "lat": -23.5505, "lon": -46.6333}, {"name": "Rio de Janeiro, BR", "lat": -22.9068, "lon": -43.1729}, {"name": "Brasília, BR", "lat": -15.7939, "lon": -47.8828}, {"name": "Fortaleza, BR", "lat": -3.7319, "lon": -38.5267}, {"name": "Manaus, BR", "lat": -3.1190, "lon": -60.0217}, {"name": "Recife, BR", "lat": -8.0476, "lon": -34.8770}, {"name": "Buenos Aires, AR", "lat": -34.6037, "lon": -58.3816}, {"name": "Córdoba, AR", "lat": -31.4201, "lon": -64.1888}, {"name": "Rosario, AR", "lat": -32.9442, "lon": -60.6505}, {"name": "Lima, PE", "lat": -12.0464, "lon": -77.0428}, {"name": "Arequipa, PE", "lat": -16.4090, "lon": -71.5375}, {"name": "Santiago, CL", "lat": -33.4489, "lon": -70.6693}, {"name": "Valparaíso, CL", "lat": -33.0472, "lon": -71.6127}, {"name": "Quito, EC", "lat": -0.1807, "lon": -78.4678}, {"name": "Guayaquil, EC", "lat": -2.1700, "lon": -79.9224}, {"name": "Caracas, VE", "lat": 10.4806, "lon": -66.9036}, {"name": "Bogotá, CO", "lat": 4.7110, "lon": -74.0721}, {"name": "Medellín, CO", "lat": 6.2442, "lon": -75.5812}, {"name": "La Paz, BO", "lat": -16.5000, "lon": -68.1500}, {"name": "Montevideo, UY", "lat": -34.9011, "lon": -56.1645}, {"name": "Asunción, PY", "lat": -25.2637, "lon": -57.5759}, {"name": "London, UK", "lat": 51.5074, "lon": -0.1278}, {"name": "Manchester, UK", "lat": 53.4808, "lon": -2.2426}, {"name": "Paris, FR", "lat": 48.8566, "lon": 2.3522}, {"name": "Marseille, FR", "lat": 43.2965, "lon": 5.3698}, {"name": "Berlin, DE", "lat": 52.5200, "lon": 13.4050}, {"name": "Munich, DE", "lat": 48.1351, "lon": 11.5820}, {"name": "Madrid, ES", "lat": 40.4168, "lon": -3.7038}, {"name": "Barcelona, ES", "lat": 41.3851, "lon": 2.1734}, {"name": "Rome, IT", "lat": 41.9028, "lon": 12.4964}, {"name": "Milan, IT", "lat": 45.4642, "lon": 9.1900}, {"name": "Istanbul, TR", "lat": 41.0082, "lon": 28.9784}, {"name": "Athens, GR", "lat": 37.9838, "lon": 23.7275}, {"name": "Vienna, AT", "lat": 48.2082, "lon": 16.3738}, {"name": "Prague, CZ", "lat": 50.0755, "lon": 14.4378}, {"name": "Moscow, RU", "lat": 55.7558, "lon": 37.6173}, {"name": "Saint Petersburg, RU", "lat": 59.9343, "lon": 30.3351}, {"name": "Oslo, NO", "lat": 59.9139, "lon": 10.7522}, {"name": "Stockholm, SE", "lat": 59.3293, "lon": 18.0686}, {"name": "Helsinki, FI", "lat": 60.1699, "lon": 24.9384}, {"name": "Copenhagen, DK", "lat": 55.6761, "lon": 12.5683}, {"name": "Dublin, IE", "lat": 53.3498, "lon": -6.2603}, {"name": "Warsaw, PL", "lat": 52.2297, "lon": 21.0122}, {"name": "Zurich, CH", "lat": 47.3769, "lon": 8.5417}, {"name": "Novosibirsk, RU", "lat": 55.0084, "lon": 82.9357}, {"name": "Krasnoyarsk, RU", "lat": 56.0153, "lon": 92.8932}, {"name": "Irkutsk, RU", "lat": 52.2870, "lon": 104.3050}, {"name": "Yakutsk, RU", "lat": 62.0355, "lon": 129.6755}, {"name": "Vladivostok, RU", "lat": 43.1155, "lon": 131.8855}, {"name": "Murmansk, RU", "lat": 68.9585, "lon": 33.0827}, {"name": "Barrow (Utqiaġvik), US", "lat": 71.2906, "lon": -156.7886}, {"name": "Longyearbyen, Svalbard", "lat": 78.2232, "lon": 15.6469}, {"name": "Cairo, EG", "lat": 30.0444, "lon": 31.2357}, {"name": "Alexandria, EG", "lat": 31.2001, "lon": 29.9187}, {"name": "Lagos, NG", "lat": 6.5244, "lon": 3.3792}, {"name": "Abuja, NG", "lat": 9.0765, "lon": 7.3986}, {"name": "Nairobi, KE", "lat": -1.2921, "lon": 36.8219}, {"name": "Addis Ababa, ET", "lat": 9.0301, "lon": 38.7427}, {"name": "Johannesburg, ZA", "lat": -26.2041, "lon": 28.0473}, {"name": "Cape Town, ZA", "lat": -33.9249, "lon": 18.4241}, {"name": "Durban, ZA", "lat": -29.8587, "lon": 31.0218}, {"name": "Algiers, DZ", "lat": 36.7538, "lon": 3.0588}, {"name": "Casablanca, MA", "lat": 33.5731, "lon": -7.5898}, {"name": "Dakar, SN", "lat": 14.7167, "lon": -17.4677}, {"name": "Accra, GH", "lat": 5.6037, "lon": -0.1870}, {"name": "Kampala, UG", "lat": 0.3476, "lon": 32.5825}, {"name": "Maputo, MZ", "lat": -25.9692, "lon": 32.5732}, {"name": "Luanda, AO", "lat": -8.8390, "lon": 13.2894}, {"name": "Harare, ZW", "lat": -17.8252, "lon": 31.0335}, {"name": "Istanbul, TR", "lat": 41.0082, "lon": 28.9784}, {"name": "Ankara, TR", "lat": 39.9334, "lon": 32.8597}, {"name": "Jerusalem, IL", "lat": 31.7683, "lon": 35.2137}, {"name": "Tel Aviv, IL", "lat": 32.0853, "lon": 34.7818}, {"name": "Riyadh, SA", "lat": 24.7136, "lon": 46.6753}, {"name": "Jeddah, SA", "lat": 21.4858, "lon": 39.1925}, {"name": "Dubai, AE", "lat": 25.2048, "lon": 55.2708}, {"name": "Abu Dhabi, AE", "lat": 24.4539, "lon": 54.3773}, {"name": "Baghdad, IQ", "lat": 33.3128, "lon": 44.3615}, {"name": "Tehran, IR", "lat": 35.6892, "lon": 51.3890}, {"name": "Doha, QA", "lat": 25.276987, "lon": 51.520008}, {"name": "Muscat, OM", "lat": 23.5859, "lon": 58.4059}, {"name": "Amman, JO", "lat": 31.9539, "lon": 35.9106}, {"name": "Beirut, LB", "lat": 33.8938, "lon": 35.5018}, {"name": "Damascus, SY", "lat": 33.5138, "lon": 36.2765}, {"name": "Beijing, CN", "lat": 39.9042, "lon": 116.4074}, {"name": "Shanghai, CN", "lat": 31.2304, "lon": 121.4737}, {"name": "Guangzhou, CN", "lat": 23.1291, "lon": 113.2644}, {"name": "Shenzhen, CN", "lat": 22.5431, "lon": 114.0579}, {"name": "Hong Kong, HK", "lat": 22.3193, "lon": 114.1694}, {"name": "Tokyo, JP", "lat": 35.6895, "lon": 139.6917}, {"name": "Osaka, JP", "lat": 34.6937, "lon": 135.5023}, {"name": "Seoul, KR", "lat": 37.5665, "lon": 126.9780}, {"name": "Busan, KR", "lat": 35.1796, "lon": 129.0756}, {"name": "Singapore, SG", "lat": 1.3521, "lon": 103.8198}, {"name": "Bangkok, TH", "lat": 13.7563, "lon": 100.5018}, {"name": "Hanoi, VN", "lat": 21.0285, "lon": 105.8542}, {"name": "Jakarta, ID", "lat": -6.2088, "lon": 106.8456}, {"name": "Manila, PH", "lat": 14.5995, "lon": 120.9842}, {"name": "Kuala Lumpur, MY", "lat": 3.1390, "lon": 101.6869}, {"name": "Delhi, IN", "lat": 28.7041, "lon": 77.1025}, {"name": "Mumbai, IN", "lat": 19.0760, "lon": 72.8777}, {"name": "Bangalore, IN", "lat": 12.9716, "lon": 77.5946}, {"name": "Chennai, IN", "lat": 13.0827, "lon": 80.2707}, {"name": "Dhaka, BD", "lat": 23.8103, "lon": 90.4125}, {"name": "Islamabad, PK", "lat": 33.6844, "lon": 73.0479}, {"name": "Karachi, PK", "lat": 24.8607, "lon": 67.0011}, {"name": "Sydney, AU", "lat": -33.8688, "lon": 151.2093}, {"name": "Melbourne, AU", "lat": -37.8136, "lon": 144.9631}, {"name": "Brisbane, AU", "lat": -27.4698, "lon": 153.0251}, {"name": "Perth, AU", "lat": -31.9505, "lon": 115.8605}, {"name": "Auckland, NZ", "lat": -36.8485, "lon": 174.7633}, {"name": "Wellington, NZ", "lat": -41.2865, "lon": 174.7762}, {"name": "Port Moresby, PG", "lat": -9.4438, "lon": 147.1803}, {"name": "Suva, FJ", "lat": -18.1248, "lon": 178.4501}, {"name": "Nouméa, NC", "lat": -22.2758, "lon": 166.4580}, {"name": "Honiara, SB", "lat": -9.4319, "lon": 159.9565}, {"name": "Majuro, MH", "lat": 7.1167, "lon": 171.3667}, {"name": "McMurdo Station, AQ", "lat": -77.8419, "lon": 166.6863}, {"name": "Amundsen-Scott South Pole Station, AQ", "lat": -90.0000, "lon": 0.0000}, {"name": "Vostok Station, AQ", "lat": -78.4648, "lon": 106.8369}, {"name": "Alert, CA", "lat": 82.5018, "lon": -62.3481}, ]

gstyle = GlobalInlineStyleSheet(css=""" html, body, .bk, .bk-root {background-color: #2F2F2F; margin: 0; padding: 0; height: 100%; color: white; font-family: 'Consolas', 'Courier New', monospace; } .bk { color: white; } .bk-input, .bk-btn, .bk-select, .bk-slider-title, .bk-headers, .bk-label, .bk-title, .bk-legend, .bk-axis-label { color: white !important; } .bk-input::placeholder { color: #aaaaaa !important; } """)
radio_style = InlineStyleSheet(css=""" /* Outer container */ :host { background: #2F2F2F !important; border-radius: 16px !important; padding: 0px 0px 0px 0px !important; max-width: 1600px !important; } /* Title */ :host .bk-input-group label, :host .bk-radiobuttongroup-title { color: #f59e0b !important; font-size: 1.16em !important; font-family: 'Fira Code', monospace; font-weight: bold !important; margin-bottom: 16px !important; text-shadow: 0 2px 10px #f59e0b99; letter-spacing: 0.5px; } /* Button group: wrap on small screens */ :host .bk-btn-group { display: flex !important; gap: 10px !important; flex-wrap: wrap !important; justify-content: flex-start; margin-bottom: 4px; } /* Each radio button - pill shape, full text, no ellipsis */ :host button.bk-btn { background: #23233c !important; color: #f9fafb !important; border: 2.5px solid #f59e0b !important; border-radius: 999px !important; padding: 0.7em 2.2em !important; min-width: 60px !important; font-size: 1.09em !important; font-family: 'Fira Code', monospace; font-weight: 600 !important; transition: border 0.13s, box-shadow 0.14s, color 0.12s, background 0.13s; box-shadow: 0 2px 10px #0002 !important; cursor: pointer !important; outline: none !important; white-space: nowrap !important; overflow: visible !important; text-overflow: unset !important; } /* Orange glow on hover */ :host button.bk-btn:hover:not(.bk-active) { border-color: #ffa733 !important; color: #ffa733 !important; box-shadow: 0 0 0 2px #ffa73399, 0 0 13px #ffa73388 !important; background: #2e2937 !important; } /* Red glow on active/focus */ :host button.bk-btn:focus, :host button.bk-btn.bk-active { border-color: #ff3049 !important; color: #ff3049 !important; background: #322d36 !important; box-shadow: 0 0 0 2px #ff304999, 0 0 19px #ff304988 !important; } /* Remove focus outline */ :host button.bk-btn:focus { outline: none !important; } """)

# Add 'region' key to each
for c in north_america: c["region"] = "north_america"
for c in south_america: c["region"] = "south_america"
for c in europe:       c["region"] = "europe"
for c in africa:       c["region"] = "africa"
for c in east_asia:    c["region"] = "east_asia"
for c in west_asia:    c["region"] = "west_asia"
for c in south_asia:   c["region"] = "south_asia"
for c in australia:    c["region"] = "australia"
for c in poles:        c["region"] = "poles"
for c in greece:       c["region"] = "greece"
for c in globe:        c["region"] = "globe"

# Create master list for lookup
all_cities_dict = {
    "north_america": north_america,
    "south_america": south_america,
    "europe": europe,
    "africa": africa,
    "east_asia": east_asia,
    "west_asia": west_asia,
    "south_asia": south_asia,
    "australia": australia,
    "poles": poles,
    "greece": greece,
    "globe": globe,
}

# Button labels and region keys in same order
region_labels = [
    "North America", "South America", "Europe", "Africa", "East Asia", "West Asia","South Asia", "Australia", "Poles", "Greece", "Globe"
]
region_keys = [
    "north_america", "south_america", "europe", "africa", "east_asia", "west_asia", "south_asia", "australia", "poles", "greece", "globe"
]

# -- API KEY LOADING --
# with open('ak.txt', 'r') as file:
#     API_KEY0 = file.readline().strip()
API_KEY = os.getenv("OPENWEATHERMAP_API_KEY", '6a449acfde38bcfa4a4465168a4b1a14')
UPDATE_INTERVAL_MS = 60 * 1000  # 1 minute

# -- Start with globe
active_region_key = "globe"
current_cities = list(all_cities_dict[active_region_key])

# Precompute mercator coordinates for current cities
def city_coords(city_list):
    merc_x, merc_y = zip(*(latlon_to_mercator(c["lat"], c["lon"]) for c in city_list))
    return list(merc_x), list(merc_y)

merc_x, merc_y = city_coords(current_cities)

# Build ColumnDataSource
source = ColumnDataSource(
    data=dict(
        x=merc_x,
        y=merc_y,
        name=[c["name"] for c in current_cities],
        cloud=[0] * len(current_cities),
        temp=[0] * len(current_cities),
        humidity=[0] * len(current_cities),
        pressure=[0] * len(current_cities),        hidden=np.ones(len(list(merc_x)))*np.min(list(merc_y))

    )
)

# -- Build Map
title_str = f"Cyclops: Live Weather Map — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} -- Data from openweathermap.org"
p = figure(match_aspect=True,
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

wheel_zoom = WheelZoomTool()
p.add_tools(wheel_zoom)
p.toolbar.active_scroll = wheel_zoom
p.title.text_color = "deepskyblue"
p.title.text_font = "Helvetica"
p.title.text_font_style = "bold"
p.title.text_font_size = "25pt"

for axis in (p.xaxis, p.yaxis):
    axis.axis_line_color = "white"
    axis.major_tick_line_color = "white"
    axis.major_label_text_color = "white"
    axis.minor_tick_line_color = "white"
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None

color_mapper = LinearColorMapper(palette="Turbo256", low=-10, high=40)
circles = p.scatter(
    "x", "y", source=source, size=20,
    fill_color={"field": "temp", "transform": color_mapper},
    fill_alpha=0.9, line_color=None,
)

# -- Enhanced HoverTool
def cusj():
    num=1
    return CustomJSHover(code=f"""
    special_vars.indices = special_vars.indices.slice(0,{num})
    return special_vars.indices.includes(special_vars.index) ? " " : " hidden "
    """)
def hovfun(tltl):
    return """<div @hidden{custom} style="background-color: #2F2F2F; padding: 5px; border-radius: 15px; box-shadow: 0px 0px 5px rgba(0,0,0,0.3);">        
    """+tltl+"""
    </div> <style> :host { --tooltip-border: transparent;  /* Same border color used everywhere */ --tooltip-color: transparent; --tooltip-text: #2f2f2f;} </style> """
tltl = """
      <div style='font-size:27px; color:#FFD700; font-weight:bold;'>@name</div>
      <div style='font-size:23px; color:#FFFFFF;'>☁️ @cloud{0.0}%</div>
      <div style='font-size:23px; color:#FFFFFF;'>🌡️ @temp{0.0}°C</div>
      <div style='font-size:23px; color:#FFFFFF;'>💧 @humidity{0.0}%</div>
      <div style='font-size:23px; color:#FFFFFF;'>🕛 @pressure{0.0}hPa</div>
"""
hover = HoverTool(
    renderers=[circles], point_policy="follow_mouse",
    tooltips=hovfun(tltl), formatters={"@hidden": cusj()}, mode="mouse"
)
p.add_tools(hover)

color_bar = ColorBar(
    title_text_font_size="16pt", major_label_text_font_size="14pt",
    background_fill_color="#2F2F2F",
    color_mapper=color_mapper,
    title_text_color="white",
    major_label_text_color="white",
    label_standoff=10,
    ticker=BasicTicker(desired_num_ticks=5),
    title="Temperature (°C)", location=(0, 0),
)
p.add_layout(color_bar, "right")

# -- Weather Data Fetch/Update --
def fetch_and_update():
    # Get the current region
    cur_names = source.data['name']
    new_cloud, new_temp, new_hum, new_pressure = [], [], [], []
    for city_name in cur_names:
        # Find city in master list (any region)
        city = next((c for region in all_cities_dict.values() for c in region if c["name"] == city_name), None)
        if not city:
            new_cloud.append(0)
            new_temp.append(0)
            new_hum.append(0)
            new_pressure.append(0)
            continue
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
    source.data.update(
        cloud=new_cloud, temp=new_temp, humidity=new_hum, pressure=new_pressure
    )

fetch_and_update()
curdoc().add_periodic_callback(fetch_and_update, UPDATE_INTERVAL_MS)

# -- Region Filter Button --
def region_callback(attr, old, new):
    idx = new
    reg_key = region_keys[idx]
    cities_list = all_cities_dict[reg_key]
    mx, my = city_coords(cities_list)
    # Fill the source with current region's cities
    source.data = dict(
        x=mx,
        y=my,
        name=[c["name"] for c in cities_list],
        cloud=[0] * len(mx),
        temp=[0] * len(mx),
        humidity=[0] * len(mx),
        pressure=[0] * len(mx),
    )
    fetch_and_update()  # Fetch new data immediately

radio_group = RadioButtonGroup(labels=region_labels, active=10, stylesheets = [radio_style])  # default 'Globe'
radio_group.on_change('active', region_callback)

# Info
info = Div(text="<b>Select region:</b>", styles={"color": "#FFD700", "font-size": "18px", 'background-color': '#2F2F2F', 'margin-top':'10px'})

# -- Layout --
layout = column(p, row(info, radio_group), sizing_mode="stretch_both",stylesheets=[gstyle])
curdoc().add_root(layout)
curdoc().title = "Cyclops"


