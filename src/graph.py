import pandas as pd
import math
import networkx as nx
from collections import defaultdict

def build_graph_range(df, distance_threshold_km):
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

def build_graph_service(df):
    G = nx.Graph()
    # adicionar nós
    for _, r in df.iterrows():
        sid = str(r["Station ID"])
        G.add_node(sid, name=r["Stop Name"], lat=float(r["GTFS Latitude"]), lon=float(r["GTFS Longitude"]),
                   complex_id=str(r["Complex ID"]), routes=str(r.get("Daytime Routes", "")))
    # arestas de serviço (mesmo Daytime Routes)
    route_map = defaultdict(list)
    for _, r in df.iterrows():
        sid = str(r["Station ID"])
        routes = str(r.get("Daytime Routes", ""))
        for route in routes.split(","):
            route_map[route.strip()].append(sid)
    for route, stations in route_map.items():
        for i in range(len(stations)):
            for j in range(i+1, len(stations)):
                G.add_edge(stations[i], stations[j], type="service", route=route)
    return G


def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.asin(math.sqrt(a))
