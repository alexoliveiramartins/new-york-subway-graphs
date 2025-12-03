import folium

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
