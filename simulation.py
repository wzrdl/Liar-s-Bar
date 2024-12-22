import random
import pandas as pd

# 定义获取所有可能移动的函数
def get_possible_moves(player, true_cards, fake_cards, first_player_move):
    moves = []
    if true_cards > 0:
        for count in range(1, true_cards + 1):
            moves.append({"player": player, "type": "play_true", "count": count})
    if fake_cards > 0:
        for count in range(1, fake_cards + 1):
            moves.append({"player": player, "type": "play_fake", "count": count})
    if not first_player_move:
        moves.append({"player": player, "type": "challenge"})
    return moves



# 格式化路径为字符串
def format_path(history, current_action):
    all_actions = history + [current_action]
    return " -> ".join(
        [f"Player {action['player']} {action['type']} {action.get('count', '')}".strip() for action in all_actions]
    )

def update_probabilities_with_csv(possible_moves, history, data, current_player):
    all_equal_prob = True
    for move in possible_moves:
        path = format_path(history, move)
        if current_player == 1:
            matched_row = data[data["Path"] == path]
            if not matched_row.empty:
                row4 = matched_row.iloc[0, 3]
                row5 = matched_row.iloc[0, 4]
                probability = row5 / (row4 + row5) if (row4 + row5) > 0 else 0
                move["probability"] = probability
                if probability != 0.5:
                    all_equal_prob = False
            else:
                move["probability"] = 0
        else:
            move["probability"] = 0.5  # Player 2固定概率
    return all_equal_prob

# 单局游戏模拟函数
def single_game_simulation_with_probabilities(player1, player2, csv_file, max_moves=10):
    # 加载CSV文件
    data = pd.read_csv(csv_file)

    history = []
    current_player = 1
    p1 = list(player1)
    p2 = list(player2)
    first_player_move = True

    for step in range(max_moves):
        if p1[0] + p1[1] == 0 or p2[0] + p2[1] == 0:
            # 必须进行挑战
            challenger = current_player
            last_action = history[-1] if history else None
            challenge_success = last_action["type"] == "play_fake" if last_action else False
            winner = challenger if challenge_success else current_player
            history.append({"player": challenger, "type": "challenge", "success": challenge_success})
            return {
                "initial_state": (player1, player2),
                "history": history,
                "winner": winner
            }

        if current_player == 1:
            true_cards, fake_cards = p1
        else:
            true_cards, fake_cards = p2

        # 获取可能的行动
        possible_moves = get_possible_moves(current_player, true_cards, fake_cards, first_player_move)
        
        # 更新行动概率
        update_probabilities_with_csv(possible_moves, history, data, current_player)

        # 打印可能的行动及其概率
        print(f"\nStep {step + 1}: Player {current_player}'s possible actions:")
        for move in possible_moves:
            print(f"  {move['type']} {move.get('count', '')}: {move['probability']:.4f}")
            path = format_path(history, move)
            # 在CSV中查找路径并打印第四列和第五列
            matched_row = data[data["Path"] == path]
            if not matched_row.empty:
                fourth_col = matched_row.iloc[0, 3]
                fifth_col = matched_row.iloc[0, 4]
                print(f"    Matching path in CSV: {path}")
                print(f"    Column 4: {fourth_col}, Column 5: {fifth_col}")

        all_equal_prob = update_probabilities_with_csv(possible_moves, history, data, current_player)
        # 选择概率最大的行动
        if all_equal_prob:
            selected_move = random.choice(possible_moves)
            print(f"Selected action randomly: {selected_move['type']} {selected_move.get('count', '')}")
        else:
            selected_move = min(possible_moves, key=lambda x: x["probability"])
            print(f"Selected action: {selected_move['type']} {selected_move.get('count', '')} with probability {selected_move['probability']:.4f}")
        
        

        if selected_move["type"] == "play_true":
            true_cards -= selected_move["count"]
        elif selected_move["type"] == "play_fake":
            fake_cards -= selected_move["count"]
        elif selected_move["type"] == "challenge":
            challenge_success = history[-1]["type"] == "play_fake" if history else False
            winner = current_player if challenge_success else 3 - current_player
            return {
                "initial_state": (player1, player2),
                "history": history + [selected_move],
                "winner": winner
            }

        if current_player == 1:
            p1 = [true_cards, fake_cards]
        else:
            p2 = [true_cards, fake_cards]

        history.append(selected_move)
        current_player = 3 - current_player
        first_player_move = False

    raise ValueError("游戏未以挑战结束。")

# 格式化历史输出
def format_history(history):
    return " -> ".join(
        [f"Player {action['player']} {action['type']} {action.get('count', '')}".strip() for action in history]
    )

# 初始化游戏
player1_start = (3, 2)  # 玩家1初始手牌
player2_start = (2, 3)  # 玩家2初始手牌

# CSV 文件路径
csv_file = "game_results.csv"

# 运行模拟
outcome = single_game_simulation_with_probabilities(player1_start, player2_start, csv_file, max_moves=15)

# 输出格式化历史和胜者
formatted_history = format_history(outcome["history"])
print(f"\nGame History: {formatted_history}")
print(f"Winner: Player {outcome['winner']}")
