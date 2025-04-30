from typing import List, Dict

class CostEstimatorTool:
    name = "cost_estimator"
    description = "根据评分和价格优化成本字段"

    def run(self, items: List[Dict]) -> List[Dict]:
        for entry in items:
            try:
                base_cost = float(entry.get("cost", "$0").strip("$"))
            except:
                base_cost = 0
            rating = entry.get("rating")
            if rating:
                if rating >= 4.5:
                    final_cost = round(base_cost * 1.1)
                elif rating < 3.0:
                    final_cost = round(base_cost * 0.9)
                else:
                    final_cost = base_cost
            else:
                final_cost = base_cost
            entry["cost"] = f"${final_cost}"
        return items
