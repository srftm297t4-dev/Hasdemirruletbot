from collections import Counter
from typing import List, Dict

Spin = Dict

def basic_stats(spins: List[Spin]) -> Dict:
    nums = [s["number"] for s in spins]
    colors = [s["color"] for s in spins]
    cnum = Counter(nums); ccol = Counter(colors)

    hot = sorted(cnum.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
    cold = sorted(cnum.items(), key=lambda kv: (kv[1], kv[0]))[:5]

    streak_len = 0; streak_col = None
    if colors:
        streak_col = colors[0]; streak_len = 1
        for i in range(1, len(colors)):
            if colors[i] == colors[i-1]: streak_len += 1
            else: break

    evens = sum(1 for x in nums if x != 0 and x % 2 == 0)
    odds  = sum(1 for x in nums if x % 2 == 1)
    zeros = nums.count(0)

    return {
        "count": len(nums),
        "nums": nums,
        "color_counts": dict(ccol),
        "hot_nums": hot,
        "cold_nums": cold,
        "streak": {"color": streak_col, "length": streak_len},
        "parity": {"even": evens, "odd": odds, "zero": zeros},
    }

def suggestion(stats: Dict) -> Dict:
    picks = []
    st = stats.get("streak", {})
    if st.get("color") in ("red","black") and st.get("length",0) >= 3:
        picks.append({"type":"color","value": "red" if st["color"]=="black" else "black"})
    hot = [n for n,_ in stats.get("hot_nums",[])][:3]
    if hot: picks.insert(0, {"type":"number","value": hot[0]})
    if stats.get("parity",{}).get("zero",0) >= 2:
        picks.append({"type":"number","value":0})
    return {"picks": picks}
