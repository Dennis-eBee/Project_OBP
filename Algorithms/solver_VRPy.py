from networkx import DiGraph
from vrpy import VehicleRoutingProblem
# from Algorithms.distance_calculator import RoadDistanceCalculator
# from Candidate_Ranking.Rankings import CandidateRanking
# import pandas as pd
import math
import matplotlib.pyplot as plt

class vrpy_solver():

    def __init__(self, distance_matrix_vrp):
        self.distance_matrix = distance_matrix_vrp

        self.locations = distance_matrix_vrp.columns
        self.filtered_locations = [loc for loc in self.locations if loc != "Depot"]

        self.loc_to_integer = {name: i for i, name in enumerate(self.filtered_locations)}
        self.integer_to_loc = {value: key for key, value in self.loc_to_integer.items()}

    def build_graph(self):

        added_edges = set()

        # initialize network
        G = DiGraph()

        # add edges to network
        # vrpy requires integer names for location, use dictionaries for mapping to names
        for frm in self.locations:
            for to in self.locations:
                if frm != to:
                    distance = self.distance_matrix.loc[frm][to]
                    edge = (frm, to)
                    reverse_edge = (to, frm)
                    if frm == "Depot":
                        G.add_edge("Source", self.loc_to_integer[to], cost=distance)
                        added_edges.add(edge)
                    if to == "Depot":
                        G.add_edge(self.loc_to_integer[frm], "Sink", cost=distance)
                        added_edges.add(reverse_edge)

                    if edge not in added_edges and reverse_edge not in added_edges:
                        G.add_edge(self.loc_to_integer[frm], self.loc_to_integer[to], cost=distance)
        return G

    def solve(self, capacity, max_iter, time_limit):
        G = self.build_graph()
        m = VehicleRoutingProblem(G)
        for v in G.nodes():
            if v not in ["Source", "Sink"]:
                G.nodes[v]["demand"] = 1

        total_demand = len(self.filtered_locations)

        num_vehicles = max(1, math.ceil(total_demand / capacity))  # Amount of needed trucks (ceil)

        m.load_capacity = capacity
        m.num_vehicles = num_vehicles
        m.solve(max_iter=max_iter, time_limit=time_limit)

        return m

    def returnDistance(self, m):
        return m.best_routes_cost

    def returnRoutes(self, m):
        routes_dict = m.best_routes
        routes = []

        for i in range(1, len(routes_dict) + 1):
            route = []
            for loc in routes_dict[i]:
                if loc == "Source" or loc == "Sink":
                    route.append("Depot")
                else:
                    route.append(self.integer_to_loc[loc])
            routes.append(route)

        for idx, route in enumerate(routes):
           print(f"Route for Vehicle {idx + 1}: {route}")

        return routes

    def calculate_distance_per_order(self, routes):
        total_distance = 0
        total_orders = 0
        for route in routes:
            route_distance = 0
            for i in range(len(route) - 1):
                route_distance += self.distance_matrix.loc[route[i], route[i + 1]]
            total_distance += route_distance
            total_orders += len(route) - 2  # Exclude depot at start and end

        distance_per_order = total_distance / total_orders if total_orders > 0 else 0
        print(f"Total Distance: {total_distance}, Total Orders: {total_orders}, Distance per Order: {distance_per_order}")
        return total_distance, distance_per_order

    def plotRoute(self, routes, input_df):
        plt.figure(figsize=(12, 8))

        truck_colors = [
            "darkblue", "darkgreen", "darkorange", "black",
            "blue", "purple", "orange", "darkred",
            "cyan", "magenta", "lime", "brown", "pink", "teal",
            "gold", "silver", "darkcyan", "indigo"
        ]

        # Plot each route
        for idx, route in enumerate(routes):
            route_df = input_df[input_df['name'].isin(route)]
            depot = route_df[route_df['name'] == 'Depot']
            other_locations = route_df[route_df['name'] != 'Depot']

            # Plot other locations
            plt.scatter(other_locations['lon'], other_locations['lat'], label=f'Route {idx + 1}',
                        alpha=0.6, marker='o', color=truck_colors[idx])

            # Plot the route
            for i in range(1, len(route)):
                start = route_df[route_df.name == route[i - 1]].iloc[0]
                end = route_df[route_df.name == route[i]].iloc[0]

                plt.arrow(start['lon'], start['lat'], end['lon'] - start['lon'], end['lat'] - start['lat'],
                          head_width=0.025, head_length=0.025, fc=truck_colors[idx], ec=truck_colors[idx], alpha=0.6)

        # Plot the depot
        plt.scatter(depot['lon'], depot['lat'], color='red', label=f'Depot', alpha=1, marker='D', s=100)

        # Labels and Title
        plt.title('Optimal Routes with Locations and Depot', fontsize=16)
        plt.xlabel('Longitude')
        plt.ylabel('Latitude')
        plt.legend()
        plt.grid(True)
        plt.show()

