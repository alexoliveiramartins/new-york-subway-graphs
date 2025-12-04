import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from utils import makeGraphLista

CSV = "dados/MTA_Subway_Stations.csv"
df = pd.read_csv(CSV)

lines = df['Line'].unique()
ids1 = sorted(df[df["Line"] == 'West End']["Station ID"].tolist())
graph1 = makeGraphLista(ids1)

ids2 = sorted(df[df["Line"] == 'Staten Island']["Station ID"].tolist())
graph2 = makeGraphLista(ids2)

for line in lines:
    ids = sorted(df[df["Line"] == line]["Station ID"].tolist())
    graph = makeGraphLista(ids)
    G = nx.Graph(graph)
    pos = {
        row["Station ID"]: (row["GTFS Longitude"], row["GTFS Latitude"])
        for _, row in df.iterrows()
    }
    nx.draw(G, pos, with_labels=False, node_size=10)

# lista com todos os Station ID's
# list = [id for id in df["Station ID"]]
# list.sort()

# Montar o grafo (lista de adjacencia)

# graph = makeGraphLista(list)
# G = nx.Graph(graph)

# pos = {
#     row["Station ID"]: (row["GTFS Longitude"], row["GTFS Latitude"])
#     for _, row in df.iterrows()
# }

# for position in range(1, len(pos)):
#     print(pos[position])

# nx.draw(G, pos, with_labels=False, node_size=10)
plt.figure(figsize=(10, 8))
plt.show()