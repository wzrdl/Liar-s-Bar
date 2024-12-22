import pandas as pd
from collections import defaultdict
n = 2
m = 3
k = 5
p = 0
###############################################################################
# 全局自增节点ID，用于给每个节点分配唯一ID
###############################################################################
_global_node_id_counter = 0

def get_next_node_id():
    global _global_node_id_counter
    _global_node_id_counter += 1
    return _global_node_id_counter


###############################################################################
# 工具函数：动作生成、路径格式化
###############################################################################
def get_possible_moves(player, true_cards, fake_cards, first_move=False):
    """
    根据当前玩家手里剩余的真牌(true_cards)和假牌(fake_cards)，
    生成所有可能动作: 
      - play_true(k)，k=1..true_cards
      - play_fake(k)，k=1..fake_cards
      - 如果不是第一步，则可以"challenge"挑战
    """
    moves = []
    if true_cards > 0:
        for count in range(1, true_cards + 1):
            moves.append({"player": player, "type": "play_true", "count": count})
    if fake_cards > 0:
        for count in range(1, fake_cards + 1):
            moves.append({"player": player, "type": "play_fake", "count": count})
    if not first_move:
        moves.append({"player": player, "type": "challenge"})
    return moves


def format_path(history, current_action):
    """
    将 'history + 当前动作' 拼接成字符串，以在CSV中匹配对应概率。
    history 和 current_action 都是 dict, 如: {"player":1, "type":"play_true", "count":2}
    格式化成: "Player 1 play_true 2 -> Player 2 challenge -> ..."
    """
    all_actions = history + [current_action]
    formatted_actions = []
    for action in all_actions:
        count_str = str(action["count"]) if "count" in action else ""
        action_str = f"Player {action['player']} {action['type']} {count_str}".strip()
        formatted_actions.append(action_str)
    return " -> ".join(formatted_actions)


###############################################################################
# 第1部分：构建博弈树，并将收益累加存储在节点的 "payoff" 中
###############################################################################
def build_game_tree(
    player1_start=(n, m), 
    player2_start=(k, p), 
    csv_file="game_results.csv", 
    max_moves=15
):
    """
    构建游戏树(序贯博弈树)并返回 (game_tree, node_lookup, root_id):
      - game_tree[node_id] = [child_id1, child_id2, ...]
        表示从 node_id 这个节点可以走向哪些子节点
        
      - node_lookup[node_id] = {
           "node_id": int,
           "current_player": 1 or 2,
           "p1_hand": (true_cards1, fake_cards1),
           "p2_hand": (true_cards2, fake_cards2),
           "history": [ {action1}, {action2}, ... ],
           "payoff": (p1_payoff, p2_payoff),   # 累积收益(根->该节点)
           "steps": int
        }
        
      - root_id : 根节点ID。
    """
    data = pd.read_csv(csv_file)

    # 存储： node_id -> [child_id, child_id...]
    game_tree = defaultdict(list)
    # 存储： node_id -> node 信息
    node_lookup = {}

    # 构造根节点
    root_node_id = get_next_node_id()
    root_node = {
        "node_id": root_node_id,
        "current_player": 1,                   # 先手玩家
        "p1_hand": player1_start,
        "p2_hand": player2_start,
        "history": [],                         # 动作历史
        "payoff": (0.0, 0.0),                  # 根节点收益设为0(累积基准)
        "steps": 0
    }
    node_lookup[root_node_id] = root_node

    # 用栈进行DFS扩展
    stack = [root_node_id]

    while stack:
        current_id = stack.pop()
        node = node_lookup[current_id]

        # 如果超出最大步数，就不再扩展
        if node["steps"] >= max_moves:
            continue

        current_player = node["current_player"]
        parent_payoff_p1, parent_payoff_p2 = node["payoff"]

        if current_player == 1:
            t_cards, f_cards = node["p1_hand"]
        else:
            t_cards, f_cards = node["p2_hand"]

        # 如果该玩家手里没牌，则默认为只能挑战(或直接终局, 根据你游戏规则)
        # 这里演示：自动发起challenge
        if (t_cards + f_cards) == 0:
            # 当前玩家无牌可打，只能 challenge（或你手动构造 challenge 分支）
            move = {"player": current_player, "type": "challenge"}
            path_str = format_path(node["history"], move)

            # 读取 CSV(若有)或其它逻辑，算 probability
            matched_row = data[data["Path"] == path_str]
            if not matched_row.empty:
                row4 = matched_row.iloc[0, 3]
                row5 = matched_row.iloc[0, 4]
                prob = row4 / (row4 + row5) if (row4 + row5) > 0 else 0.5
            else:
                prob = 0.5

            # 根据上一手是否是 play_fake 判断挑战是否成功
            last_a = node["history"][-1] if len(node["history"]) > 0 else None
            challenge_succ = (last_a is not None and last_a["type"] == "play_fake")
            winner = current_player if challenge_succ else (3 - current_player)

            # 这里改成胜者 +3，输者 -3
            if winner == 1:
                payoff_step_p1, payoff_step_p2 = (3.0, -3.0)
            else:
                payoff_step_p1, payoff_step_p2 = (-3.0, 3.0)

            # 累加到父节点的收益
            parent_payoff_p1, parent_payoff_p2 = node["payoff"]
            child_payoff_p1 = parent_payoff_p1 + payoff_step_p1
            child_payoff_p2 = parent_payoff_p2 + payoff_step_p2

            # 构造子节点(终局)
            child_node = {
                "node_id": get_next_node_id(),
                "current_player": 3 - current_player,  # 挑战结束后通常不再行动
                "p1_hand": node["p1_hand"],
                "p2_hand": node["p2_hand"],
                "history": node["history"] + [move],
                "payoff": (child_payoff_p1, child_payoff_p2),  # 终局收益
                "steps": node["steps"] + 1
            }
            node_lookup[child_node["node_id"]] = child_node
            game_tree[node["node_id"]].append(child_node["node_id"])
            # 挑战一般是终局，不再扩展后续
            continue


        # 否则，获取所有可行动作
        first_move = (len(node["history"]) == 0)
        moves = get_possible_moves(current_player, t_cards, f_cards, first_move)

        for mv in moves:
            path_str = format_path(node["history"], mv)
            matched = data[data["Path"] == path_str]
            if not matched.empty:
                row4 = matched.iloc[0, 3]
                row5 = matched.iloc[0, 4]
                prob = row4 / (row4 + row5) if (row4 + row5) > 0 else 0.5
            else:
                prob = 0.5

            # 这里示例：将 "prob" 作为本步的即时收益给 P1，(1-prob) 给 P2
            # 实际游戏中可根据规则计算更复杂/多样的收益
            payoff_step_p1 = prob
            payoff_step_p2 = 1.0 - prob

            # 累加到父节点收益
            child_payoff_p1 = parent_payoff_p1 + payoff_step_p1
            child_payoff_p2 = parent_payoff_p2 + payoff_step_p2

            # 更新手牌
            new_p1_hand = node["p1_hand"]
            new_p2_hand = node["p2_hand"]
            if current_player == 1:
                if mv["type"] == "play_true":
                    new_p1_hand = (node["p1_hand"][0] - mv["count"], node["p1_hand"][1])
                elif mv["type"] == "play_fake":
                    new_p1_hand = (node["p1_hand"][0], node["p1_hand"][1] - mv["count"])
            else:  # current_player == 2
                if mv["type"] == "play_true":
                    new_p2_hand = (node["p2_hand"][0] - mv["count"], node["p2_hand"][1])
                elif mv["type"] == "play_fake":
                    new_p2_hand = (node["p2_hand"][0], node["p2_hand"][1] - mv["count"])

            child_id = get_next_node_id()
            child_node = {
                "node_id": child_id,
                "current_player": 3 - current_player,
                "p1_hand": new_p1_hand,
                "p2_hand": new_p2_hand,
                "history": node["history"] + [mv],
                # payoff 存储 累积收益(父节点 + 本步)
                "payoff": (child_payoff_p1, child_payoff_p2),
                "steps": node["steps"] + 1
            }
            node_lookup[child_id] = child_node
            game_tree[current_id].append(child_id)

            # 如果动作是 challenge，一般终局，也可视情况再判断是否压栈
            if mv["type"] != "challenge":
                stack.append(child_id)

    return game_tree, node_lookup, root_node_id


###############################################################################
# 第2部分：逆推法 (Backward Induction) 求子博弈精炼纳什均衡
###############################################################################
def backward_induction_spe(game_tree, node_lookup):
    """
    逆推法：对已构建好的 game_tree 执行子博弈精炼纳什均衡 (SPE) 求解。
    
    返回两个字典：
      best_payoff[node_id] = (p1_best, p2_best)
          表示从 node_id 出发，若后续都按照最优策略，得到的收益
          
      best_child[node_id] = child_id or None
          表示 node_id 在最优策略下会选择走向哪个子节点(没有子节点则为None)
    """
    all_node_ids = list(node_lookup.keys())
    game_tree_keys = set(game_tree.keys())

    # 1) 找到“终端节点”，即在 game_tree 中没有孩子的节点
    #    这些节点的 payoff 就是它们本身的累积收益，不需要再往下推
    terminal_nodes = [nid for nid in all_node_ids if len(game_tree[nid]) == 0]

    best_payoff = {}
    best_child = {}

    # 先把终端节点的 payoff 定好
    for tid in terminal_nodes:
        node = node_lookup[tid]
        best_payoff[tid] = node["payoff"]  # (p1, p2)
        best_child[tid] = None            # 没有后续子节点

    # 2) 递归函数：若 best_payoff[nid] 未计算，则对其孩子做递归后，再选最优
    def compute_best_response(nid):
        if nid in best_payoff:
            return best_payoff[nid]

        node = node_lookup[nid]
        current_player = node["current_player"]
        children = game_tree[nid]

        # 如果没有孩子(意外情况)，视作终端
        if not children:
            best_payoff[nid] = node["payoff"]
            best_child[nid] = None
            return best_payoff[nid]

        # 否则，对所有子节点算出 best_payoff，再挑选当前玩家最优
        best_val = None
        best_c = None
        for c in children:
            cp = compute_best_response(c)  # (p1, p2)
            if best_val is None:
                best_val = cp
                best_c = c
            else:
                if current_player == 1:
                    # 玩家1看 p1 收益来选
                    if cp[0] > best_val[0]:
                        best_val = cp
                        best_c = c
                else:
                    # 玩家2看 p2 收益来选
                    if cp[1] > best_val[1]:
                        best_val = cp
                        best_c = c
        
        best_payoff[nid] = best_val
        best_child[nid] = best_c
        return best_val

    # 3) 对所有节点做一次 compute_best_response (或只对根节点做，也会下探到全部)
    for nid in all_node_ids:
        compute_best_response(nid)

    return best_payoff, best_child


###############################################################################
# 第3部分：打印SPE均衡路径
###############################################################################
def trace_equilibrium_path(root_id, best_child):
    """
    从 root_id 出发，沿着 best_child 的选择，一直走到终端，得到节点ID序列
    """
    path = []
    cur = root_id
    while True:
        path.append(cur)
        nxt = best_child[cur]
        if nxt is None:
            break
        cur = nxt
    return path

def print_equilibrium_path(path_ids, node_lookup):
    """
    打印节点ID序列所代表的均衡路径上的节点信息
    """
    print("\n==== 子博弈精炼纳什均衡路径 (SPE Path) ====\n")
    for i, nid in enumerate(path_ids):
        node = node_lookup[nid]
        print(f"--- Path Step {i} | NodeID={nid} ---")
        print("  current_player :", node["current_player"])
        print("  steps          :", node["steps"])
        print("  p1_hand        :", node["p1_hand"])
        print("  p2_hand        :", node["p2_hand"])
        print("  payoff (累积)  :", node["payoff"])
        print("  history        :")
        for h in node["history"]:
            print("    ", h)
        print("")

import random

def random_path_from_root_to_leaf(game_tree, node_lookup, root_id):
    """
    从 root_id 出发，随机地挑选子节点走下去，直到走到某个无子节点(叶)为止。
    返回这条路径上所有节点ID的列表(从根到终端)。
    """
    path_ids = []
    current_id = root_id
    while True:
        path_ids.append(current_id)
        children = game_tree[current_id]
        if not children:
            # 到达终端节点，没有后继
            break
        # 随机选一个子节点
        next_id = random.choice(children)
        current_id = next_id
    return path_ids

def print_path_info(path_ids, node_lookup):
    """
    给定一条节点ID序列，打印各节点上的动作历史和最后节点的收益。
    """
    print("\n===== 随机路径节点信息 =====\n")
    for i, nid in enumerate(path_ids):
        node = node_lookup[nid]
        print(f"NodeID={nid}, steps={node['steps']}, current_player={node['current_player']}")
        print("  p1_hand :", node["p1_hand"])
        print("  p2_hand :", node["p2_hand"])
        print("  payoff  :", node["payoff"])
        print("  history :")
        for h in node["history"]:
            print("    ", h)
        print("")

    # 最后一个节点是终端节点，node['payoff'] 就是整盘的总收益(或你定义的终局收益)
    final_payoff = node_lookup[path_ids[-1]]["payoff"]
    print(">>> 该条路径终局节点 payoff =", final_payoff)

def print_average_payoff(paths, node_lookup):
    """
    打印多条路径的平均 payoff。
    """
    total_p1_payoff = 0
    total_p2_payoff = 0

    for path in paths:
        final_node = node_lookup[path[-1]]  # 终局节点
        p1_payoff, p2_payoff = final_node["payoff"]
        total_p1_payoff += p1_payoff
        total_p2_payoff += p2_payoff

    num_paths = len(paths)
    avg_p1_payoff = total_p1_payoff / num_paths
    avg_p2_payoff = total_p2_payoff / num_paths

    print("\n===== 平均 Payoff =====")
    print(f"Player 1 平均收益: {avg_p1_payoff:.2f}")
    print(f"Player 2 平均收益: {avg_p2_payoff:.2f}\n")
###############################################################################
# 主函数：运行示例
###############################################################################
if __name__ == "__main__":
    # 假设我们有一个 game_results.csv，包含列: 
    #   Path, X, Y, V4, V5
    # 其中 Path 为动作序列，V4, V5 用于计算概率
    # 你可根据自己实际CSV进行调整
    n = 2
    m = 3
    k = 5
    p = 0
    # 1) 构建博弈树
    game_tree, node_lookup, root_id = build_game_tree(

        player1_start=(n, m), 
        player2_start=(k, p), 
        csv_file="game_results.csv", 
        max_moves=15
    )
    print("博弈树构建完成，节点总数 =", len(node_lookup))

    # 2) 逆推求子博弈精炼纳什均衡
    best_payoff, best_child = backward_induction_spe(game_tree, node_lookup)

    # 3) 打印均衡路径
    eq_path = trace_equilibrium_path(root_id, best_child)
    print_equilibrium_path(eq_path, node_lookup)


     # 4) 随机挑选10条路径并打印
    random_paths = [random_path_from_root_to_leaf(game_tree, node_lookup, root_id) for _ in range(100)]
    for i, rpath in enumerate(random_paths, 1):
        print(f"\n===== 随机路径 {i} =====")
        print_path_info(rpath, node_lookup)

    # 5) 计算并打印随机路径的平均 payoff
    print_average_payoff(random_paths, node_lookup)
    
    # 3) 打印均衡路径
    eq_path = trace_equilibrium_path(root_id, best_child)
    print_equilibrium_path(eq_path, node_lookup)
