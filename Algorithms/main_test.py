########################################################
#                                                       #
# Created on: 11/01/2025                                #
# Created by: Dennis Botman                             #
#                                                       #
# Updated on: 16/01/2025                                #
# Updated by: Dennis Botman                             #
#                                                       #
#########################################################


from Algorithms.distance_calculator import RoadDistanceCalculator
from Algorithms.solver_pyvrp import VRPSolver
from Candidate_Ranking.Rankings import CandidateRanking
from Algorithms.algorithm_evaluation import AlgorithmEvaluation
import pandas as pd
import time


#######INPUTS FROM THE MODEL VARIABLES
TRUCK_CAPACITY =  2
CHOSEN_COMPANY = "Pioneer Networks"
CHOSEN_CANDIDATE = "Global Group"
LONG_DEPOT = 5.26860985
LAT_DEPOT = 52.2517788

if __name__ == "__main__":

    ###get the data
    input_df = pd.read_csv("Data/mini.csv")
    input_df['name'] = input_df.groupby('name').cumcount().add(1).astype(str).radd(input_df['name'] + "_")

    ###get distance matrix for chosen company
    distance_calc = RoadDistanceCalculator()
    distance_matrix_ranking = distance_calc.calculate_distance_matrix(input_df, chosen_company=CHOSEN_COMPANY,
        candidate_name=None, method="osrm", computed_distances_df=None)

    ###get candidate ranking
    ranking = CandidateRanking()
    algorithm1 = ranking.greedy(distance_matrix_ranking)

    ###get the full distance matrix of best company
    input_df = distance_calc.add_depot(input_df, LAT_DEPOT, LONG_DEPOT)
    distance_matrix_vrp= distance_calc.calculate_distance_matrix(input_df, chosen_company=CHOSEN_COMPANY,
        candidate_name=CHOSEN_CANDIDATE, method="osrm", computed_distances_df=distance_matrix_ranking)

    ###get best route
    # Initialize the solver
    # Initialize the VRP solver
    vrp_solver = VRPSolver()

    # --- Single Company ---
    print("Solving VRP for Single Company...")
    model_single, current_names_single = vrp_solver.build_model(
        input_df=input_df,
        chosen_company=CHOSEN_COMPANY,
        distance_matrix=distance_matrix_vrp,
        truck_capacity=TRUCK_CAPACITY
    )
    solution_single, routes_single = vrp_solver.solve(
        m=model_single,
        max_runtime=2,
        display=False,
        current_names=current_names_single
    )
    total_distance_single, avg_distance_per_order_single = vrp_solver.calculate_distance_per_order(
        routes=routes_single,
        distance_matrix=distance_matrix_vrp
    )
    vrp_solver.plotRoute(routes_single, input_df)

    # --- Collaboration ---
    print("Solving VRP for Collaboration...")
    model_collab, current_names_collab = vrp_solver.build_model(
        input_df=input_df,
        chosen_company=CHOSEN_COMPANY,
        chosen_candidate=CHOSEN_CANDIDATE,
        distance_matrix=distance_matrix_vrp,
        truck_capacity=TRUCK_CAPACITY
    )
    solution_collab, routes_collab = vrp_solver.solve(
        m=model_collab,
        max_runtime=2,
        display=False,
        current_names=current_names_collab
    )
    total_distance_collab, avg_distance_per_order_collab = vrp_solver.calculate_distance_per_order(
        routes=routes_collab,
        distance_matrix=distance_matrix_vrp
    )
    vrp_solver.plotRoute(routes_collab, input_df)

    # --- Evaluation ---
    print("Evaluating Expected Gain...")
    algorithm_eval = AlgorithmEvaluation()
    expected_gain = algorithm_eval.evaluate_expected_gain(
        total_distance_single=total_distance_single,
        total_distance_collab=total_distance_collab,
        num_orders_single=len(routes_single)
    )

    # Print final summary
    print("\nSummary:")
    print(
        f"Single Company: Total Distance = {total_distance_single}, Avg Distance per Order = {avg_distance_per_order_single}")
    print(
        f"Collaboration: Total Distance = {total_distance_collab}, Avg Distance per Order = {avg_distance_per_order_collab}")
    print(f"Gain: {-expected_gain} km")




