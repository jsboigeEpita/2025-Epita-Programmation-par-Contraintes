import networkx as nx
import pickle
import itertools
import matplotlib.pyplot as plt

GRAPH_FILE = "paris_graph_180.pkl"

# def create_graph():
#     G = nx.Graph()

#     # AI Generated Paris Locations
#     known_locations = [
#         {"ID": 1,  "Nom": "Tour Eiffel",                    "Horaire": "09:00-23:00", "Type": "Touristique", "Interet": 10, "duree": 120, "cout": 25, "latitude": 48.8584, "longitude": 2.2945},
#         {"ID": 2,  "Nom": "Musée du Louvre",                "Horaire": "09:00-18:00", "Type": "Touristique", "Interet": 10, "duree": 180, "cout": 17, "latitude": 48.8606, "longitude": 2.3376},
#         {"ID": 3,  "Nom": "Cathédrale Notre-Dame de Paris", "Horaire": "08:00-18:45", "Type": "Touristique", "Interet": 9,  "duree": 90,  "cout": 0,  "latitude": 48.8530, "longitude": 2.3499},
#         {"ID": 4,  "Nom": "Basilique du Sacré-Cœur",         "Horaire": "06:00-22:30", "Type": "Touristique", "Interet": 9,  "duree": 60,  "cout": 0,  "latitude": 48.8867, "longitude": 2.3431},
#         {"ID": 5,  "Nom": "Arc de Triomphe",                "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 45,  "cout": 12, "latitude": 48.8738, "longitude": 2.2950},
#         {"ID": 6,  "Nom": "Musée d'Orsay",                  "Horaire": "09:30-18:00", "Type": "Touristique", "Interet": 10, "duree": 150, "cout": 14, "latitude": 48.8600, "longitude": 2.3266},
#         {"ID": 7,  "Nom": "Centre Pompidou",                "Horaire": "11:00-21:00", "Type": "Touristique", "Interet": 8,  "duree": 120, "cout": 14, "latitude": 48.8606, "longitude": 2.3522},
#         {"ID": 8,  "Nom": "Palais Garnier",                 "Horaire": "10:00-17:00", "Type": "Touristique", "Interet": 8,  "duree": 75,  "cout": 16, "latitude": 48.8719, "longitude": 2.3316},
#         {"ID": 9,  "Nom": "Panthéon",                       "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 60,  "cout": 11, "latitude": 48.8462, "longitude": 2.3459},
#         {"ID": 10, "Nom": "Place de la Concorde",           "Horaire": "09:00-20:00", "Type": "Touristique", "Interet": 7,  "duree": 30,  "cout": 0,  "latitude": 48.8656, "longitude": 2.3211},
#         {"ID": 11, "Nom": "Montmartre",                     "Horaire": "All day",     "Type": "Touristique", "Interet": 9,  "duree": 120, "cout": 0,  "latitude": 48.8867, "longitude": 2.3431},
#         {"ID": 12, "Nom": "Jardin du Luxembourg",           "Horaire": "07:30-21:00", "Type": "Touristique", "Interet": 8,  "duree": 90,  "cout": 0,  "latitude": 48.8462, "longitude": 2.3371},
#         {"ID": 13, "Nom": "Champs-Élysées",                  "Horaire": "All day",     "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8668, "longitude": 2.3110},
#         {"ID": 14, "Nom": "La Défense",                     "Horaire": "All day",     "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8924, "longitude": 2.2360},
#         {"ID": 15, "Nom": "Le Marais",                      "Horaire": "All day",     "Type": "Touristique", "Interet": 8,  "duree": 90,  "cout": 0,  "latitude": 48.8575, "longitude": 2.3622},
#         {"ID": 16, "Nom": "Quartier Latin",                 "Horaire": "All day",     "Type": "Touristique", "Interet": 8,  "duree": 120, "cout": 0,  "latitude": 48.8490, "longitude": 2.3450},
#         {"ID": 17, "Nom": "Sainte-Chapelle",                "Horaire": "09:00-18:00", "Type": "Touristique", "Interet": 9,  "duree": 45,  "cout": 10, "latitude": 48.8554, "longitude": 2.3444},
#         {"ID": 18, "Nom": "Grand Palais",                  "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 60,  "cout": 15, "latitude": 48.8660, "longitude": 2.3125},
#         {"ID": 19, "Nom": "Petit Palais",                  "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 12, "latitude": 48.8661, "longitude": 2.3126},
#         {"ID": 20, "Nom": "Les Invalides",                 "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 90,  "cout": 14, "latitude": 48.8566, "longitude": 2.3126},
#         {"ID": 21, "Nom": "Place Vendôme",                 "Horaire": "All day",     "Type": "Touristique", "Interet": 7,  "duree": 30,  "cout": 0,  "latitude": 48.8670, "longitude": 2.3290},
#         {"ID": 22, "Nom": "Opéra Bastille",                "Horaire": "10:00-17:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 13, "latitude": 48.8675, "longitude": 2.3240},
#         {"ID": 23, "Nom": "Parc des Buttes-Chaumont",      "Horaire": "08:00-21:00", "Type": "Touristique", "Interet": 7,  "duree": 90,  "cout": 0,  "latitude": 48.8790, "longitude": 2.3820},
#         {"ID": 24, "Nom": "Parc de la Villette",            "Horaire": "07:00-22:00", "Type": "Touristique", "Interet": 7,  "duree": 90,  "cout": 0,  "latitude": 48.8940, "longitude": 2.3930},
#         {"ID": 25, "Nom": "Musée Rodin",                   "Horaire": "10:00-17:45", "Type": "Touristique", "Interet": 8,  "duree": 75,  "cout": 12, "latitude": 48.8550, "longitude": 2.3150},
#         {"ID": 26, "Nom": "Musée de l'Orangerie",          "Horaire": "09:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 60,  "cout": 11, "latitude": 48.8600, "longitude": 2.3266},
#         {"ID": 27, "Nom": "Palais Royal",                  "Horaire": "10:00-19:00", "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 0,  "latitude": 48.8666, "longitude": 2.3310},
#         {"ID": 28, "Nom": "Bibliothèque Nationale de France","Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8330, "longitude": 2.3750},
#         {"ID": 29, "Nom": "La Sorbonne",                   "Horaire": "All day",     "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 0,  "latitude": 48.8480, "longitude": 2.3440},
#         {"ID": 30, "Nom": "Rue de Rivoli",                 "Horaire": "All day",     "Type": "Touristique", "Interet": 6,  "duree": 30,  "cout": 0,  "latitude": 48.8561, "longitude": 2.3522},
#         {"ID": 31, "Nom": "Le Bon Marché",                 "Horaire": "10:00-20:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8530, "longitude": 2.3240},
#         {"ID": 32, "Nom": "Galeries Lafayette",            "Horaire": "09:30-20:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8730, "longitude": 2.3310},
#         {"ID": 33, "Nom": "Printemps Haussmann",           "Horaire": "09:00-20:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8732, "longitude": 2.3321},
#         {"ID": 34, "Nom": "Place de la République",        "Horaire": "All day",     "Type": "Touristique", "Interet": 6,  "duree": 30,  "cout": 0,  "latitude": 48.8670, "longitude": 2.3630},
#         {"ID": 35, "Nom": "Canal Saint-Martin",            "Horaire": "All day",     "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 0,  "latitude": 48.8660, "longitude": 2.3740},
#         {"ID": 36, "Nom": "Parc Monceau",                  "Horaire": "07:00-20:00", "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 0,  "latitude": 48.8790, "longitude": 2.3130},
#         {"ID": 37, "Nom": "Cité de la Musique",            "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 13, "latitude": 48.8660, "longitude": 2.3330},
#         {"ID": 38, "Nom": "Philharmonie de Paris",         "Horaire": "10:00-19:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 13, "latitude": 48.8580, "longitude": 2.3400},
#         {"ID": 39, "Nom": "Fondation Louis Vuitton",       "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8,  "duree": 90,  "cout": 18, "latitude": 48.8840, "longitude": 2.2500},
#         {"ID": 40, "Nom": "Musée Picasso",                 "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 12, "latitude": 48.8590, "longitude": 2.3620},
#         {"ID": 41, "Nom": "Musée Jacquemart-André",         "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 12, "latitude": 48.8750, "longitude": 2.3270},
#         {"ID": 42, "Nom": "Musée Marmottan Monet",          "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 11, "latitude": 48.8662, "longitude": 2.3390},
#         {"ID": 43, "Nom": "Musée Guimet",                  "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 12, "latitude": 48.8600, "longitude": 2.3500},
#         {"ID": 44, "Nom": "Institut du Monde Arabe",       "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 11, "latitude": 48.8530, "longitude": 2.3500},
#         {"ID": 45, "Nom": "Les Catacombes",                "Horaire": "09:45-20:30", "Type": "Touristique", "Interet": 8,  "duree": 60,  "cout": 14, "latitude": 48.8339, "longitude": 2.3320},
#         {"ID": 46, "Nom": "Parc André Citroën",            "Horaire": "07:00-21:00", "Type": "Touristique", "Interet": 7,  "duree": 45,  "cout": 0,  "latitude": 48.8150, "longitude": 2.2500},
#         {"ID": 47, "Nom": "Jardin des Plantes",            "Horaire": "09:00-18:00", "Type": "Touristique", "Interet": 7,  "duree": 60,  "cout": 0,  "latitude": 48.8430, "longitude": 2.3600},
#         {"ID": 48, "Nom": "Cité des Sciences et de l'Industrie", 
#                  "Horaire": "10:00-18:00", "Type": "Touristique", "Interet": 8, "duree": 90, "cout": 15, "latitude": 48.8960, "longitude": 2.3930},
#         {"ID": 49, "Nom": "Gare du Nord",                 "Horaire": "All day",     "Type": "Touristique", "Interet": 6,  "duree": 30,  "cout": 0,  "latitude": 48.8800, "longitude": 2.3550},
#         {"ID": 50, "Nom": "Le Jules Verne",               "Horaire": "12:00-14:00, 19:00-22:00", "Type": "Restaurant", "Interet": 8, "duree": 90, "cout": 80, "latitude": 48.8584, "longitude": 2.2945}
#     ]

#     for loc in known_locations:
#         G.add_node(loc["ID"], **loc)

#     # Add edges without travel times - they will be calculated on demand
#     for u, v in itertools.combinations(G.nodes(), 2):
#         G.add_edge(u, v)
    
#     return G

def save_graph(G, filename=GRAPH_FILE):
    with open(filename, "wb") as f:
        pickle.dump(G, f)
    print(f"Graph saved to {filename}")

def load_graph(filename=GRAPH_FILE):
    """Load the Paris graph from a file or create it if not found."""
    try:
        with open(filename, 'rb') as f:
            G = pickle.load(f)
        print(f"Loaded existing Paris graph with {len(G.nodes())} nodes")
        return G
    except (FileNotFoundError, IOError):
        print("Creating new Paris graph")
        G = create_graph()
        save_graph(G, filename)
        return G

def display_graph_window(G):
    pos = {n: (G.nodes[n]["longitude"], G.nodes[n]["latitude"]) for n in G.nodes()}
    plt.figure(figsize=(10, 8))
    
    # Extract node attributes for visualization
    node_types = [G.nodes[n].get("Type", "Unknown") for n in G.nodes()]
    node_interest = [G.nodes[n].get("Interet", 5) for n in G.nodes()]
    node_sizes = [max(30, n * 10) for n in node_interest]  # Scale interest to node size
    
    # Color nodes by type
    color_map = {"Touristique": "blue", "Restaurant": "red", "Unknown": "gray"}
    node_colors = [color_map.get(t, "gray") for t in node_types]
    
    # Draw the graph
    nx.draw_networkx_edges(G, pos, alpha=0.2)
    nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.7)
    
    # Add labels for important nodes
    labels = {n: G.nodes[n]["Nom"] for n in G.nodes() if n <= 50}
    nx.draw_networkx_labels(G, pos, labels, font_size=8)
    
    # Add legend
    for type_name, color in color_map.items():
        plt.plot([], [], 'o', color=color, label=type_name)
    plt.legend(loc="best")
    
    plt.title("Paris Locations Graph (Positioned by Latitude and Longitude)")
    plt.xlabel("Longitude")
    plt.ylabel("Latitude")
    plt.axis("equal")
    plt.show()

if __name__ == "__main__":
    G=load_graph("new-york_graph.pkl")
    for node in G.nodes(data=True):
        print(node)
