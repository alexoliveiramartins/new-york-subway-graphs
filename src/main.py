import math
import pandas as pd
import networkx as nx
import folium

CSV = "dados/MTA_Subway_Stations.csv"
DIST_THRESHOLD_KM = 0.7  # ligações de proximidade (ajuste se necessário)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def build_graph(df, distance_threshold_km=DIST_THRESHOLD_KM):
    G = nx.Graph()
    # adicionar nós
    for _, r in df.iterrows():
        sid = str(r["Station ID"])
        G.add_node(sid, name=r["Stop Name"], lat=float(r["GTFS Latitude"]), lon=float(r["GTFS Longitude"]),
                   complex_id=str(r["Complex ID"]), routes=str(r.get("Daytime Routes", "")))
    # arestas de transferência (mesmo Complex ID)
    groups = df.groupby("Complex ID")
    for cid, group in groups:
        ids = [str(x) for x in group["Station ID"].tolist()]
        for i in range(len(ids)):
            for j in range(i+1, len(ids)):
                G.add_edge(ids[i], ids[j], type="transfer")
    # arestas por proximidade (distância euclidiana haversine)
    nodes = list(G.nodes(data=True))
    n = len(nodes)
    for i in range(n):
        id_i, d_i = nodes[i][0], nodes[i][1]
        for j in range(i+1, n):
            id_j, d_j = nodes[j][0], nodes[j][1]
            dist = haversine(d_i["lat"], d_i["lon"], d_j["lat"], d_j["lon"])
            if dist <= distance_threshold_km:
                # não duplicar transfer edges (pode haver ambas)
                if G.has_edge(id_i, id_j):
                    G[id_i][id_j]["type"] = G[id_i][id_j].get("type", "") + "+proximity"
                else:
                    G.add_edge(id_i, id_j, type="proximity", distance_km=round(dist,3))
    return G

def plot_folium(G, out_html="tests/subway_graph.html"):
    # centro do mapa = média das coords
    lats = [d["lat"] for _, d in G.nodes(data=True)]
    lons = [d["lon"] for _, d in G.nodes(data=True)]
    center = (sum(lats)/len(lats), sum(lons)/len(lons))
    m = folium.Map(location=center, zoom_start=11, tiles="CartoDB positron")

    # desenhar arestas
    for u, v, data in G.edges(data=True):
        p1 = (G.nodes[u]["lat"], G.nodes[u]["lon"])
        p2 = (G.nodes[v]["lat"], G.nodes[v]["lon"])
        color = "blue" if "transfer" in data.get("type","") else "orange"
        weight = 3 if "transfer" in data.get("type","") else 1
        folium.PolyLine([p1, p2], color=color, weight=weight, opacity=0.7).add_to(m)

    # desenhar nós
    for nid, d in G.nodes(data=True):
        folium.CircleMarker(
            location=(d["lat"], d["lon"]),
            radius=3,
            color="red",
            fill=True,
            tooltip=f'{d["name"]} ({nid})\n{d.get("routes","")}'
        ).add_to(m)

    m.save(out_html)
    print("Mapa salvo em", out_html)

df = pd.read_csv(CSV)
# filtrar linhas sem coords
df = df.dropna(subset=["GTFS Latitude", "GTFS Longitude"])
G = build_graph(df)
plot_folium(G)

