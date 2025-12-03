import pandas as pd
from graph import build_graph_range, build_graph_service
from utils import plot_folium
MAXRANGEKM = 1.2  # ligações de proximidade (ajuste se necessário)
CSV = "dados/MTA_Subway_Stations.csv"


df = pd.read_csv(CSV)
# filtrar linhas sem coords
df = df.dropna(subset=["GTFS Latitude", "GTFS Longitude"])
G = build_graph_range(df, MAXRANGEKM)
plot_folium(G, "tests/subway_graph_range.html")
print("Número de estações (nós):", G.number_of_nodes())
print("Número de conexões (arestas):", G.number_of_edges())

F = build_graph_service(df)
plot_folium(F, "tests/subway_graph_service.html")
print("Número de estações (nós):", F.number_of_nodes())
print("Número de conexões (arestas):", F.number_of_edges())
