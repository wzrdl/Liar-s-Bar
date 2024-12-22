import pandas as pd
from collections import defaultdict

def parse_outcomes(input_file, output_file):
    # Load the initial data from CSV using pandas
    data = pd.read_csv(input_file)

    # Dictionary to store results for each starting hand combination
    grouped_results = defaultdict(lambda: defaultdict(lambda: {'P1_win': 0, 'P2_win': 0}))

    # Normalize paths to remove trailing challenge actions
    def normalize_path(outcome_path):
        if outcome_path[-1] in ['Player 2 challenge ', 'Player 1 challenge ']:
            return outcome_path[:-1]
        return outcome_path

    # Recursive function to record win counts for all prefixes of a path
    def record_path_counts(key, outcome_path, winner, current_path=""):
        if not outcome_path:
            return

        # Extend the current path
        next_action = outcome_path[0]
        new_path = f"{current_path} -> {next_action}".strip(" -> ")

        # Update win counts for the current path
        if winner == 'P1':
            grouped_results[key][new_path]['P1_win'] += 1
        elif winner == 'P2':
            grouped_results[key][new_path]['P2_win'] += 1

        # Recur for the remaining path
        record_path_counts(key, outcome_path[1:], winner, new_path)

    # Analyze each row in the input file
    for _, row in data.iterrows():
        initial_p1, initial_p2, outcome_path, winner = row['P1 Hand'], row['P2 Hand'], row['Action Sequence'], row['Winner']
        outcome_path = outcome_path.split(' -> ')

        # Normalize the path to remove trailing challenge actions
        normalized_path = normalize_path(outcome_path)

        # Normalize the key for grouped results
        key = (initial_p1, initial_p2)

        # Record counts for the full path and all its prefixes
        record_path_counts(key, normalized_path, winner)

    # Prepare results for writing
    rows = []
    for (p1_hand, p2_hand), paths in grouped_results.items():
        for path, counts in paths.items():
            rows.append({
                'P1_start': p1_hand,
                'P2_start': p2_hand,
                'Path': path,
                'P1_win': counts['P1_win'],
                'P2_win': counts['P2_win']
            })

    # Convert results to a DataFrame and write to a new CSV file
    results_df = pd.DataFrame(rows)
    results_df.to_csv(output_file, index=False)

# Example usage
input_file = './game_outcomes.csv'  # Replace with your input file
output_file = 'game_results.csv'  # Replace with your output file
parse_outcomes(input_file, output_file)
