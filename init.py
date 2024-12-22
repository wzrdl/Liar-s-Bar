def simulate_game(player1, player2, current_player, history, results, depth, max_depth, initial_state):
    """
    Simulate the game recursively and store outcomes.
    """
    if depth > max_depth:
        return

    if player1[0] + player1[1] == 0 and player2[0] + player2[1] == 0:
        outcome = {
            "initial_state": initial_state,
            "history": history,
            "winner": 2 if current_player == 1 else 1
        }
        results.append(outcome)
        return

    if current_player == 1:
        true_cards, fake_cards = player1
        opponent_cards = player2
    else:
        true_cards, fake_cards = player2
        opponent_cards = player1

    # If current player has no cards left, must challenge
    if opponent_cards[0] + opponent_cards[1] == 0:
        challenge_success = history[-1]["type"] == "play_fake"
        history.append({"player": current_player, "type": "challenge", "success": challenge_success})
        outcome = {
            "initial_state": initial_state,
            "history": history,
            "winner": current_player if challenge_success else 3 - current_player
        }
        results.append(outcome)
        return

    # Actions: play true or fake cards
    for m in range(1, true_cards + 1):
        new_history = history + [{"player": current_player, "type": "play_true", "count": m}]
        if current_player == 1:
            simulate_game((true_cards - m, fake_cards), player2, 2, new_history, results, depth + 1, max_depth, initial_state)
        else:
            simulate_game(player1, (true_cards - m, fake_cards), 1, new_history, results, depth + 1, max_depth, initial_state)

    for n in range(1, fake_cards + 1):
        new_history = history + [{"player": current_player, "type": "play_fake", "count": n}]
        if current_player == 1:
            simulate_game((true_cards, fake_cards - n), player2, 2, new_history, results, depth + 1, max_depth, initial_state)
        else:
            simulate_game(player1, (true_cards, fake_cards - n), 1, new_history, results, depth + 1, max_depth, initial_state)


def find_all_game_outcomes(max_depth=100):
    results = []
    for k1 in range(6):
        for k2 in range(6):
            # Initial state of the game
            player1 = (k1, 5 - k1)  # True and fake cards
            player2 = (k2, 5 - k2)
            initial_state = (player1, player2)  # Keep initial states for reference

            simulate_game(player1, player2, 1, [], results, 0, max_depth, initial_state)
    return results


def calculate_statistics(outcomes):
    statistics = {}

    for outcome in outcomes:
        initial_state = outcome["initial_state"]
        winner = outcome["winner"]

        if initial_state not in statistics:
            statistics[initial_state] = {"P1_wins": 0, "P2_wins": 0, "total": 0}

        statistics[initial_state]["total"] += 1
        if winner == 1:
            statistics[initial_state]["P1_wins"] += 1
        elif winner == 2:
            statistics[initial_state]["P2_wins"] += 1

    return statistics

# Find outcomes and calculate statistics
outcomes = find_all_game_outcomes(max_depth=50)
statistics = calculate_statistics(outcomes)

# Output statistics
for state, stats in statistics.items():
    print(f"Initial State {state}: P1 Wins = {stats['P1_wins']}, P2 Wins = {stats['P2_wins']}, Total Games = {stats['total']}")
