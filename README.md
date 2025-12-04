# New-York-Subway-Graphs
# Trabalho para a matéria de AED2.

Este projeto aplica a Teoria dos Grafos para modelar e analisar a rede de metrô de Nova York. O foco principal é identificar conexões baseadas na proximidade geográfica entre estações, além das conexões de serviço padrão, permitindo visualizações interativas da malha de transporte.

#  Sobre o Projeto
O objetivo é explorar a conectividade do sistema de transporte público utilizando dados reais da MTA (Metropolitan Transportation Authority). A aplicação constrói grafos onde as estações são nós e as conexões são arestas, ponderadas por distância ou rota.

As principais funcionalidades incluem:

Construção de grafos baseados em distância geográfica (Fórmula de Haversine).

Construção de grafos baseados em rotas de serviço.

Visualização interativa em mapas HTML utilizando a biblioteca folium.

#  Tecnologias Utilizadas
Python 3.8+

Pandas: Manipulação e limpeza do dataset CSV.

NetworkX: Modelagem e algoritmos de grafos.

Folium: Visualização de mapas geoespaciais.

Math: Cálculos de distância geodésica.

# Participantes:

- Alex Benjamim de Oliveira Martins 202301419
- Felipe Sucupira de Oliveira 202301439
- Luis Renato Pinto Cordeiro 202301466
- João Pedro Beltrão Cortes 202301456
- Marco Antônio Martins Fernandes 202301468

# Como executar:
```bash
git clone https://github.com/alexoliveiramartins/new-york-subway-graphs.git
```
```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
pip install -r requirements.txt
```
```bash
python3 src/main.py
```
**Interação**
O programa solicitará que você escolha o método de construção do grafo:

*Opção 1* (Proximidade): Conecta estações que estão a uma distância física de até 1.2 km (distância Euclidiana Haversine). Ideal para analisar mobilidade a pé entre estações.

*Opção 2* (Serviço): Conecta estações que compartilham a mesma linha de metrô.

*Opção 3* (GTFS): (Requer arquivos adicionais GTFS) Constrói o grafo baseado em horários e viagens reais.

# Visualização dos Resultados
Após a execução, o script gerará um arquivo HTML na pasta tests/ (ex: subway_graph_range.html). Abra este arquivo em qualquer navegador web para interagir com o mapa.

Legenda do Mapa:

🔴 Nós (Pontos Vermelhos): Estações de metrô.

🔵 Arestas Azuis: Transferências internas (mesmo complexo físico).

🟠 Arestas Laranjas: Conexões por proximidade geográfica ou rota (dependendo do modo escolhido).

# Lógica do Algoritmo
Fórmula de Haversine
Para calcular a distância precisa entre duas coordenadas GPS (latitude/longitude), utilizamos a fórmula de Haversine, que leva em consideração a curvatura da Terra
*Complexidade*
Para a construção por proximidade, o algoritmo compara cada estação com todas as outras subsequentes, resultando em uma complexidade de tempo de O(V²), onde V é o número de estações.
