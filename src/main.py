import pandas as pd
from graph import build_graph
from utils import plot_folium
MAXRANGEKM = 0.7  # ligações de proximidade (ajuste se necessário)
CSV = "dados/MTA_Subway_Stations.csv"


df = pd.read_csv(CSV)
# filtrar linhas sem coords
df = df.dropna(subset=["GTFS Latitude", "GTFS Longitude"])
G = build_graph(df, MAXRANGEKM)
plot_folium(G)

