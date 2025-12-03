import pandas as pd
from graph import build_graph_range, build_graph_service
from utils import plot_folium
MAXRANGEKM = 1.2  # ligações de proximidade (ajuste se necessário)
CSV = "dados/MTA_Subway_Stations.csv"
df = pd.read_csv(CSV)
df = df.dropna(subset=["GTFS Latitude", "GTFS Longitude"])

print("Selecione o método de construção do grafo:")
method = input("1 - Proximidade (distância)\n2 - Serviço (linhas comuns)\nEscolha 1 ou 2: ")
if method == "1":
    G = build_graph_range(df, MAXRANGEKM)
    plot_folium(G, "tests/subway_graph_range.html")
    print("Número de estações (nós):", G.number_of_nodes())
    print("Número de conexões (arestas):", G.number_of_edges())
elif method == "2":
    G = build_graph_service(df)
    plot_folium(G, "tests/subway_graph_service.html")
    print("Número de estações (nós):", G.number_of_nodes())
    print("Número de conexões (arestas):", G.number_of_edges())
else:
    print("Método inválido. Escolha 1 ou 2.")

print("Execução concluída.")
