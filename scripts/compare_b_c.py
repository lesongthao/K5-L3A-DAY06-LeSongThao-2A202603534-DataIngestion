import json

with open("results/traces_strategy_b.json", "r", encoding="utf-8") as f:
    tb = json.load(f)
with open("results/traces_strategy_c.json", "r", encoding="utf-8") as f:
    tc = json.load(f)

for q in tb:
    if q["id"] in ["q08", "q11", "q19"]:
        print(f"=== STRATEGY B FOR {q['id']} ({q['question']}) ===")
        for h in q["hits"]:
            print(f"  Rank {h['rank']}: Page {h['page']} | Section: {h['section']} | Score: {h['score']} | ID: {h['chunk_id']}")

for q in tc:
    if q["id"] in ["q08", "q11", "q19"]:
        print(f"=== STRATEGY C FOR {q['id']} ({q['question']}) ===")
        for h in q["hits"]:
            print(f"  Rank {h['rank']}: Page {h['page']} | Section: {h['section']} | Score: {h['score']} | ID: {h['chunk_id']}")
