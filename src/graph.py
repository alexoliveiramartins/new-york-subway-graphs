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

def build_graph_gtfs(df, stop_times_path, trips_path, stops_path, add_transfers=True):
    """
    Constrói grafo usando GTFS (stop_times.txt, trips.txt e stops.txt).
    Mapeia paradas do GTFS pelo NOME (stop_name) para nossos nós locais.
    Conecta paradas consecutivas (stop_sequence) com arestas.
    """
    G = nx.Graph()
    
    # Adicionar nós a partir de df
    for _, r in df.iterrows():
        sid = str(r["Station ID"])
        G.add_node(sid, 
                   name=r["Stop Name"], 
                   lat=float(r["GTFS Latitude"]), 
                   lon=float(r["GTFS Longitude"]),
                   complex_id=str(r["Complex ID"]), 
                   routes=str(r.get("Daytime Routes", "")))
    
    # Carregar GTFS
    try:
        st = pd.read_csv(stop_times_path, dtype=str)
        trips = pd.read_csv(trips_path, dtype=str)
        stops = pd.read_csv(stops_path, dtype=str)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Arquivo GTFS não encontrado: {e}")
    
    # Mapeamento: GTFS stop_id -> stop_name
    stop_id_to_name = dict(zip(stops["stop_id"], stops["stop_name"]))
    
    # Mapeamento: Stop Name (local) -> Station ID
    name_to_sid = dict(zip(df["Stop Name"].str.strip(), df["Station ID"].astype(str)))
    
    # Debug: contar overlaps
    gtfs_names = set(stop_id_to_name.values())
    local_names = set(name_to_sid.keys())
    overlap = gtfs_names & local_names
    print(f"[GTFS Debug] GTFS paradas: {len(gtfs_names)}, Local estações: {len(local_names)}, Overlap: {len(overlap)}")
    
    # Mesclar route_id dos trips
    st = st.merge(trips[["trip_id", "route_id"]], on="trip_id", how="left")
    
    # Converter stop_sequence para int
    st["stop_sequence"] = pd.to_numeric(st["stop_sequence"], errors="coerce")
    st = st.dropna(subset=["stop_sequence"])
    st["stop_sequence"] = st["stop_sequence"].astype(int)
    
    # Para cada trip, conectar paradas consecutivas
    edge_count = 0
    skipped = 0
    for trip_id, grp in st.groupby("trip_id"):
        grp = grp.sort_values("stop_sequence")
        route_id = grp["route_id"].iloc[0] if "route_id" in grp.columns else "unknown"
        stop_ids = grp["stop_id"].tolist()
        
        # Conectar pares consecutivos
        for stop_a_id, stop_b_id in zip(stop_ids[:-1], stop_ids[1:]):
            # Mapear GTFS stop_id -> stop_name -> Station ID
            stop_a_name = stop_id_to_name.get(stop_a_id)
            stop_b_name = stop_id_to_name.get(stop_b_id)
            
            if not stop_a_name or not stop_b_name:
                skipped += 1
                continue
            
            # Encontrar nos nossos nós
            stop_a_name_clean = stop_a_name.strip()
            stop_b_name_clean = stop_b_name.strip()
            
            sid_a = name_to_sid.get(stop_a_name_clean)
            sid_b = name_to_sid.get(stop_b_name_clean)
            
            if sid_a is None or sid_b is None or sid_a == sid_b:
                skipped += 1
                continue
            
            # Calcular distância
            u, v = str(sid_a), str(sid_b)
            if u not in G.nodes or v not in G.nodes:
                skipped += 1
                continue
            
            lat_u, lon_u = G.nodes[u]["lat"], G.nodes[u]["lon"]
            lat_v, lon_v = G.nodes[v]["lat"], G.nodes[v]["lon"]
            dist = haversine(lat_u, lon_u, lat_v, lon_v)
            
            # Adicionar aresta
            if G.has_edge(u, v):
                if "routes" not in G[u][v]:
                    G[u][v]["routes"] = set()
                G[u][v]["routes"].add(route_id)
            else:
                G.add_edge(u, v, type="rail", routes={route_id}, distance_km=round(dist, 3))
                edge_count += 1
    
    print(f"[GTFS] Adicionadas {edge_count} arestas de adjacência (skipped {skipped} pares inválidos)")
    
    # Adicionar transferências
    if add_transfers:
        transfer_count = 0
        groups = df.groupby("Complex ID")
        for cid, group in groups:
            ids = [str(x) for x in group["Station ID"].tolist()]
            for i in range(len(ids)):
                for j in range(i+1, len(ids)):
                    u, v = ids[i], ids[j]
                    if not G.has_edge(u, v):
                        G.add_edge(u, v, type="transfer")
                        transfer_count += 1
                    else:
                        G[u][v]["type"] = "rail+transfer"
        print(f"[GTFS] Adicionadas {transfer_count} arestas de transferência")
    
    return G

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.asin(math.sqrt(a))
