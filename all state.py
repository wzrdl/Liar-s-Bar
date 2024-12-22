def simulate_game(player1, player2, current_player, history, results, depth, max_depth, initial_state, step_wins):
    """
    Simulate the game recursively, tracking the outcomes at each step and storing the full sequence of actions.
    """
    if depth > max_depth:
        return

    if player1[0] + player1[1] == 0 or player2[0] + player2[1] == 0:
        # If the game ends, record the outcome and track the history of actions
        challenge_success = history[-1]["type"] == "play_fake"
        #history.append({"player": current_player, "type": "challenge", "success": challenge_success})
        new_history = history + [{"player": current_player, "type": "challenge", "success": challenge_success}]
        outcome = {
            "initial_state": initial_state,
            "history": new_history,
            "winner": current_player if challenge_success else 3 - current_player
        }
        results.append(outcome)

        # Update step_wins with win statistics at each step
        for i, action in enumerate(history):
            current_state = f"{action['player']}p{action.get('count', '')}"  # e.g., '1p3'
            if current_state not in step_wins:
                step_wins[current_state] = {"P1_wins": 0, "P2_wins": 0}
            if outcome["winner"] == 1:
                step_wins[current_state]["P1_wins"] += 1
            elif outcome["winner"] == 2:
                step_wins[current_state]["P2_wins"] += 1
        return

    if current_player == 1:
        true_cards, fake_cards = player1
        opponent_cards = player2
    else:
        true_cards, fake_cards = player2
        opponent_cards = player1


    # Actions: play true or fake cards
    for m in range(1, true_cards + 1):
        new_history = history + [{"player": current_player, "type": "play_true", "count": m}]
        if current_player == 1:
            simulate_game((true_cards - m, fake_cards), player2, 2, new_history, results, depth + 1, max_depth, initial_state, step_wins)
        else:
            simulate_game(player1, (true_cards - m, fake_cards), 1, new_history, results, depth + 1, max_depth, initial_state, step_wins)

    for n in range(1, fake_cards + 1):
        new_history = history + [{"player": current_player, "type": "play_fake", "count": n}]
        if current_player == 1:
            simulate_game((true_cards, fake_cards - n), player2, 2, new_history, results, depth + 1, max_depth, initial_state, step_wins)
        else:
            simulate_game(player1, (true_cards, fake_cards - n), 1, new_history, results, depth + 1, max_depth, initial_state, step_wins)

    # Include a challenge action (except for Player 1's first move)
    if depth > 0:
        challenge_success = history[-1]["type"] == "play_fake" if history else False
        new_history = history + [{"player": current_player, "type": "challenge", "success": challenge_success}]
        outcome = {
            "initial_state": initial_state,
            "history": new_history,
            "winner": current_player if challenge_success else 3 - current_player
        }
        results.append(outcome)

        # Update step_wins with win statistics at each step
        for i, action in enumerate(new_history):
            current_state = f"{action['player']}p{action.get('count', '')}"  # e.g., '1p3'
            if current_state not in step_wins:
                step_wins[current_state] = {"P1_wins": 0, "P2_wins": 0}
            if outcome["winner"] == 1:
                step_wins[current_state]["P1_wins"] += 1
            elif outcome["winner"] == 2:
                step_wins[current_state]["P2_wins"] += 1


def find_all_game_outcomes(max_depth=100):
    results = []
    step_wins = {}  # Dictionary to track wins at each step
    for k1 in range(6):
        for k2 in range(6):
            # Initial state of the game
            player1 = (k1, 5 - k1)  # True and fake cards
            player2 = (k2, 5 - k2)
            initial_state = (player1, player2)  # Keep initial states for reference

            simulate_game(player1, player2, 1, [], results, 0, max_depth, initial_state, step_wins)
    
    return results, step_wins


# Find outcomes and calculate step statistics
outcomes, step_wins = find_all_game_outcomes(max_depth=50)

# Output the entire process and statistics
for outcome in outcomes:
    initial_state = outcome["initial_state"]
    history = outcome["history"]
    winner = outcome["winner"]

    # Print the full game sequence
    print(f"Initial State: P1 {initial_state[0]}, P2 {initial_state[1]}")
    print("Game Sequence:")
    for action in history:
        print(f"  Player {action['player']} {action['type']} {action.get('count', '')}")
    print(f"Winner: P{winner}")
    print()
# Calculate the total number of different outcomes
total_outcomes = len(outcomes)
print(f"Total number of different outcomes: {total_outcomes}")

import pandas as pd

def save_outcomes_to_csv_with_pandas(outcomes, filename="game_outcomes.csv"):
    # Create a list of dictionaries to hold each outcome row
    data = []
    
    for outcome in outcomes:
        initial_state = outcome["initial_state"]
        history = outcome["history"]
        winner = outcome["winner"]
        
        # Format the action sequence
        action_sequence = " -> ".join(
            [f"Player {action['player']} {action['type']} {action.get('count', '')}" for action in history]
        )
        
        # Merge the hands into two columns for Player 1 and Player 2
        p1_hand = f"({initial_state[0][0]},{initial_state[0][1]})"
        p2_hand = f"({initial_state[1][0]},{initial_state[1][1]})"
        
        # Create a row with merged hands, action sequence, and the winner
        row = {
            "P1 Hand": p1_hand,
            "P2 Hand": p2_hand,
            "Action Sequence": action_sequence,
            "Winner": f"P{winner}"
        }
        data.append(row)
    
    # Create a pandas DataFrame from the list of rows
    df = pd.DataFrame(data)
    
    # Save the DataFrame to a CSV file
    df.to_csv(filename, index=False)

# Example of finding outcomes and saving to CSV using pandas
outcomes, step_wins = find_all_game_outcomes(max_depth=50)
save_outcomes_to_csv_with_pandas(outcomes, "game_outcomes.csv")

# You can now check the "game_outcomes.csv" file for the saved data.


