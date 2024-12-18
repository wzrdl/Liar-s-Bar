def simulate_game(player1, player2, current_player, history, results, depth, max_depth, initial_state):
    """
    Simulate the game recursively and store outcomes.
    """
    if depth > max_depth:
        return

    if player1[0] + player1[1] == 0 and player2[0] + player2[1] == 0:
        outcome = f"P1({initial_state[0][0]},{initial_state[0][1]}) P2({initial_state[1][0]},{initial_state[1][1]}): " + " -> ".join([f"{step['player']}{step['type'][0]}{step.get('count', int(step.get('success', False)))}" for step in history])
        results.append(outcome)
        return

    # 根据当前玩家切换设置对手信息
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
        outcome = f"P1({initial_state[0][0]},{initial_state[0][1]}) P2({initial_state[1][0]},{initial_state[1][1]}): " + " -> ".join([f"{step['player']}{step['type'][0]}{step.get('count', int(step.get('success', False)))}" for step in history])
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

# Output results
outcomes = find_all_game_outcomes(max_depth=50)
for i, outcome in enumerate(outcomes):
    print(f"Outcome {i + 1}: {outcome}")
