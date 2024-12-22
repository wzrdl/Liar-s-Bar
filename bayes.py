import pandas as pd
from collections import defaultdict
import random

_global_node_id_counter = 0

def get_next_node_id():
    global _global_node_id_counter
    _global_node_id_counter += 1
    return _global_node_id_counter


def get_possible_moves(player, t_cards, f_cards, first_move=False):
    """
    示例：若有 t_cards 张真牌, f_cards 张假牌, 
    可 play_true(k)、play_fake(k) (k ≤各自数量),
    若不是第一步可以 challenge
    """
    moves = []
    if t_cards > 0:
        for c in range(1, t_cards + 1):
            moves.append({"player": player, "type": "play_true", "count": c})
    if f_cards > 0:
        for c in range(1, f_cards + 1):
            moves.append({"player": player, "type": "play_fake", "count": c})
    if not first_move:
        moves.append({"player": player, "type": "challenge"})
    return moves


def format_path(history, move):
    """
    跟之前类似，用来拼接 CSV path；你也可改成只输出数字或别的形式
    """
    all_moves = history + [move]
    strings = []
    for m in all_moves:
        c = m.get("count","")
        s = f"Player {m['player']} {m['type']} {c}".strip()
        strings.append(s)
    return " -> ".join(strings)


def build_game_tree(player1_hand, player2_hand, csv_file="game_results.csv", max_steps=10):
    """
    跟之前的示例类似，构建扩展式博弈树(完全信息)，并返回 (game_tree, node_lookup, root_id)。
    """
    data = pd.read_csv(csv_file)  # 若你没有CSV，注释掉即可

    game_tree = defaultdict(list)
    node_lookup = {}

    root_id = get_next_node_id()
    root_node = {
        "node_id": root_id,
        "current_player": 1,
        "p1_hand": player1_hand,
        "p2_hand": player2_hand,
        "history": [],
        "payoff": (0.0, 0.0),
        "steps": 0
    }
    node_lookup[root_id] = root_node

    stack = [root_id]

    while stack:
        nid = stack.pop()
        node = node_lookup[nid]
        if node["steps"] >= max_steps:
            continue

        cplayer = node["current_player"]
        p1_payoff_parent, p2_payoff_parent = node["payoff"]

        if cplayer == 1:
            t_cards, f_cards = node["p1_hand"]
        else:
            t_cards, f_cards = node["p2_hand"]

        # 如果没有可打的牌，就强制challenge当终局
        if (t_cards + f_cards) == 0:
            move = {"player": cplayer, "type": "challenge"}
            last_a = node["history"][-1] if node["history"] else None
            # 简化: 若对方上一步是 play_fake，则挑战成功
            success = (last_a and last_a["type"] == "play_fake")
            winner = cplayer if success else (3 - cplayer)

            # 示例: 胜者 +3, 负者 -3
            if winner == 1:
                sp1, sp2 = (3.0, -3.0)
            else:
                sp1, sp2 = (-3.0, 3.0)

            ch_id = get_next_node_id()
            child_node = {
                "node_id": ch_id,
                "current_player": 3 - cplayer,
                "p1_hand": node["p1_hand"],
                "p2_hand": node["p2_hand"],
                "history": node["history"] + [move],
                "payoff": (p1_payoff_parent + sp1, p2_payoff_parent + sp2),
                "steps": node["steps"] + 1
            }
            node_lookup[ch_id] = child_node
            game_tree[nid].append(ch_id)
            continue

        # 否则，生成所有可行动作
        first_move = (len(node["history"]) == 0)
        moves = get_possible_moves(cplayer, t_cards, f_cards, first_move)

        for mv in moves:
            path_str = format_path(node["history"], mv)
            matched = data[data["Path"] == path_str]
            if not matched.empty:
                v4 = matched.iloc[0,3]
                v5 = matched.iloc[0,4]
                prob = v4/(v4+v5) if (v4+v5)>0 else 0.5
            else:
                prob = 0.5  # 默认

            # 示例：本步即时收益 = (prob, 1 - prob)
            step_p1 = prob
            step_p2 = 1 - prob

            new_p1_hand = node["p1_hand"]
            new_p2_hand = node["p2_hand"]
            if cplayer == 1:
                if mv["type"] == "play_true":
                    new_p1_hand = (t_cards - mv["count"], f_cards)
                elif mv["type"] == "play_fake":
                    new_p1_hand = (t_cards, f_cards - mv["count"])
            else:
                if mv["type"] == "play_true":
                    new_p2_hand = (t_cards - mv["count"], f_cards)
                elif mv["type"] == "play_fake":
                    new_p2_hand = (t_cards, f_cards - mv["count"])

            child_payoff = (p1_payoff_parent + step_p1,
                            p2_payoff_parent + step_p2)

            cid = get_next_node_id()
            child_node = {
                "node_id": cid,
                "current_player": 3 - cplayer,
                "p1_hand": new_p1_hand,
                "p2_hand": new_p2_hand,
                "history": node["history"] + [mv],
                "payoff": child_payoff,
                "steps": node["steps"] + 1
            }
            node_lookup[cid] = child_node
            game_tree[nid].append(cid)

            # 若动作是 challenge，可视情况不再扩展
            if mv["type"] != "challenge":
                stack.append(cid)

    return game_tree, node_lookup, root_id


def backward_induction(game_tree, node_lookup):
    """
    完全信息下的逆推, 返回:
      best_payoff[node_id] = (p1, p2)
      best_child[node_id]  = child_id or None
    """
    best_payoff = {}
    best_child = {}

    # 终端节点: 没有子节点
    terminal_nodes = [ nid for nid in node_lookup if len(game_tree[nid])==0 ]

    for t in terminal_nodes:
        best_payoff[t] = node_lookup[t]["payoff"]
        best_child[t] = None

    def compute_best(nid):
        if nid in best_payoff:
            return best_payoff[nid]
        node = node_lookup[nid]
        cplayer = node["current_player"]
        children = game_tree[nid]
        if not children:
            # 无后继 => 终端
            best_payoff[nid] = node["payoff"]
            best_child[nid] = None
            return best_payoff[nid]

        best_val = None
        best_cid = None
        for cid in children:
            cp = compute_best(cid)
            if best_val is None:
                best_val = cp
                best_cid = cid
            else:
                # 谁决策就看谁的收益更大
                if cplayer == 1:
                    if cp[0] > best_val[0]:
                        best_val = cp
                        best_cid = cid
                else:
                    if cp[1] > best_val[1]:
                        best_val = cp
                        best_cid = cid

        best_payoff[nid] = best_val
        best_child[nid] = best_cid
        return best_val

    # 所有节点都算一次
    for nid in node_lookup:
        compute_best(nid)

    return best_payoff, best_child


def build_and_solve_game(player1_hand, player2_hand, csv_file="game_results.csv"):
    """
    一次性做: 构建 + 逆推
    返回 (game_tree, node_lookup, root_id, best_payoff, best_child)
    """
    gt, nl, rid = build_game_tree(player1_hand, player2_hand, csv_file)
    bp, bc = backward_induction(gt, nl)
    return gt, nl, rid, bp, bc


def my_bayesian_best_move(
    my_nodeA,       # 在 TypeA 树中的节点id
    my_nodeB,       # 在 TypeB 树中的节点id
    best_payoffA,   # typeA下的 best_payoff
    best_payoffB,   # typeB下的 best_payoff
    game_treeA,     # typeA的game_tree
    game_treeB,     # typeB的game_tree
    node_lookupA,
    node_lookupB,
    pA, pB
):
    """
    如果这是 *我的决策* 节点，那么我想在 move 中选: 
       argmax_{m} [pA * payoffA(m) + pB * payoffB(m)],
    其中 payoffA(m) 表示我在 TypeA下若执行m后最终能得到的收益,
         payoffB(m) 同理。
    返回: (best_move, best_expected_payoff)
    """
    nodeA = node_lookupA[my_nodeA]
    nodeB = node_lookupB[my_nodeB]

    # 确保 nodeA 和 nodeB 的 current_player == 1 (我)
    # 否则说明这不是我的决策节点

    childrenA = game_treeA[my_nodeA]
    childrenB = game_treeB[my_nodeB]

    # 收集 potential_moves: 这里可以根据 nodeA["history"][-1] 等匹配
    # 但简化: 直接看 children
    # childrenA中的每个childA, 其"history"[-1] 就是这一步move
    # 但要怎么对应到childB? 需要看childB中最后一步move是否一样
    # => 这里要有个"对照" 或 "映射" 机制: move -> child_id
    # 为了演示, 我们做个笨方法: 
    possible_moves_A = []
    for cidA in childrenA:
        last_moveA = node_lookupA[cidA]["history"][-1]
        possible_moves_A.append((last_moveA, cidA))

    # 同理 for B
    possible_moves_B = []
    for cidB in childrenB:
        last_moveB = node_lookupB[cidB]["history"][-1]
        possible_moves_B.append((last_moveB, cidB))

    # 现在我们尝试对齐 moves
    # 可能 A 树/B 树 并不一定都有完全相同的 moves(因对手牌不同, 可能有些动作不合法)
    # 你可以用 move 的dict 比较, 
    # 这里举例: match "type" 和 "count" 都相同 => 同一招
    best_move = None
    best_value = None
    for mA, cA in possible_moves_A:
        # 查找 B 树里有没有同样的 move
        # (对不完全信息, 可能 B 树允许/不允许的一些动作不一样, 这里只是演示)
        foundB = [(mB, cB) for (mB, cB) in possible_moves_B 
                  if (mB["type"]==mA["type"] and mB.get("count",0)==mA.get("count",0))]
        if not foundB:
            # 说明在 B 树里没有对应的这个move (可能不合法)
            # 你可以决定跳过,或把 B 树收益视为 -∞, ...
            continue
        
        # 这里假设只有一个B child(或者选第一个)
        (mB, cB) = foundB[0]

        # payoffA: best_payoffA[cA] => (p1A, p2A)
        p1A, _ = best_payoffA[cA]
        # payoffB: best_payoffB[cB] => (p1B, p2B)
        p1B, _ = best_payoffB[cB]

        # 期望: pA * p1A + pB * p1B
        ev = pA * p1A + pB * p1B

        if best_value is None or ev > best_value:
            best_value = ev
            best_move = mA

    return best_move, best_value


if __name__ == "__main__":
    # 对手可能是 (2,3) 还是 (3,2), 各 50%
    opponent_types = [ ((2,3), 0.5), ((3,2), 0.5) ]
    my_hand = (3,2)

    # 分别构建 TypeA, TypeB 两个完全信息树
    results = []
    for opp_hand, prob in opponent_types:
        g, nl, rid, bp, bc = build_and_solve_game(my_hand, opp_hand, "game_results.csv")
        results.append((opp_hand, prob, g, nl, rid, bp, bc))

    # 现在看 "根节点" 处, 我方(玩家1)有哪些动作
    # 对 TypeA 树的根节点 => rootA,  TypeB 树的根节点 => rootB
    # 在 root 节点, possible moves 在 TypeA, TypeB 可能略有区别
    # 我们用上面的 my_bayesian_best_move 做一次 "期望收益" 比较

    rootA = results[0][2:]  # (gA, nlA, ridA, bpA, bcA)
    rootB = results[1][2:]  # (gB, nlB, ridB, bpB, bcB)

    gA, nlA, ridA, bpA, bcA = rootA
    gB, nlB, ridB, bpB, bcB = rootB

    pA = opponent_types[0][1]  # 0.5
    pB = opponent_types[1][1]  # 0.5

    # 取出 rootA_id, rootB_id
    rootA_id = ridA
    rootB_id = ridB

    # 我在根节点(玩家1决策), 查看 "期望收益" 最高的动作
    best_move, best_value = my_bayesian_best_move(
        rootA_id, rootB_id,
        bpA, bpB,
        gA, gB,
        nlA, nlB,
        pA, pB
    )
    print("在根节点(玩家1决策), 期望收益最大的动作 =", best_move)
    print("期望收益(对我方) =", best_value)
    