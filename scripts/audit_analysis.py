"""Script to analyze traces, inspect errors, and generate audit reports
for the 5 evaluation dimensions:
1. Retrieval Accuracy
2. Chunk Coherence (10 common source locations, score 0-2)
3. Metadata Usefulness (5 test queries x top-3 = 15 chunks)
4. Grounding Quality (5 test queries, score 0-2)
5. Strategy Impact & Error Analysis (A-B and B-C trade-offs)
"""
import json
from pathlib import Path

with open("results/traces_strategy_a.json", "r", encoding="utf-8") as f:
    ta = json.load(f)
with open("results/traces_strategy_b.json", "r", encoding="utf-8") as f:
    tb = json.load(f)
with open("results/traces_strategy_c.json", "r", encoding="utf-8") as f:
    tc = json.load(f)

print("=" * 70)
print("FAILURE ANALYSIS FOR STRATEGY A:")
print("=" * 70)
for t in ta:
    if not t["hit_at_3"]:
        print(f"[{t['id']}] ({t['split']}) Question: {t['question']}")
        print(f"  Gold Page: {t['gold_page']}")
        print(f"  Evidence: {t['evidence_quote']}")
        print("  Top-3 hits returned:")
        for h in t["hits"]:
            print(f"    Rank {h['rank']}: Page {h['page']} | Score: {h['score']} | Chunk: {h['chunk_id']}")
            print(f"    Snippet: {h.get('text', h.get('text_snippet', ''))[:180]}")
        print("-" * 50)

print("\n" + "=" * 70)
print("TEST QUERIES COMPARISON ACROSS STRATEGIES:")
print("=" * 70)
for i in range(15, 20):
    qa = ta[i]
    qb = tb[i]
    qc = tc[i]
    print(f"Query {qa['id']} (Page {qa['gold_page']}): {qa['question']}")
    print(f"  Strat A: Hit@1={qa['hit_at_1']}, Hit@3={qa['hit_at_3']}")
    print(f"  Strat B: Hit@1={qb['hit_at_1']}, Hit@3={qb['hit_at_3']}")
    print(f"  Strat C: Hit@1={qc['hit_at_1']}, Hit@3={qc['hit_at_3']} | Filter Compliant={qc['filter_compliant']}")
