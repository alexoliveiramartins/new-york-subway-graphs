import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from utils import makeGraphLista

CSV = "dados/MTA_Subway_Stations.csv"
df = pd.read_csv(CSV)

plt.figure(figsize=(10, 8))
pos = {
    row["Station ID"]: (row["GTFS Longitude"], row["GTFS Latitude"])
    for _, row in df.iterrows()
}

lines = df['Line'].unique()
colors = plt.cm.tab20(range(len(lines)))

for color, line in zip(colors, lines):
    ids = sorted(df[df["Line"] == line]["Station ID"].tolist())
    graph = makeGraphLista(ids)
    G = nx.Graph(graph)
    nx.draw(G, pos, with_labels=True, node_size=10, node_color=[color] * len(ids), edge_color=color,)

plt.show()