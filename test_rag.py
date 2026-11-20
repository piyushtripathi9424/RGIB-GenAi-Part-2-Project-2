"""
Automated Test Runner for TitanCloud SRE RAG System
Tests all five assessment questions against the required function:
def answer(question: str) -> dict
"""

import json
from rag_system import answer, ingest_pdf

ASSESSMENT_QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the service credit percentage owed to enterprise customers if monthly uptime drops to 99.2%?",
        "expected_answer": "25% service credit (Page 9 Section 2.3)",
        "expected_source": "Page 9",
        "type": "Supported (Needle Page 9)"
    },
    {
        "id": "Q2",
        "question": "What is the maximum permitted replication lag threshold before Patroni initiates automatic failover for error code ERR_PG_REPLICA_LAG?",
        "expected_answer": "Strictly 45 seconds across three consecutive 5-second health probes (Page 22 Section 5.4)",
        "expected_source": "Page 22",
        "type": "Supported (Needle Page 22)"
    },
    {
        "id": "Q3",
        "question": "What is the escalation timeline for a Severity-1 (P0) production outage alert if unacknowledged by the L1 On-Call Engineer?",
        "expected_answer": "L1 has 5 min to acknowledge; pages L2 Staff SRE Lead at 5 min; escalates to VP of Infrastructure at 15 min total (Page 41 Section 9.1)",
        "expected_source": "Page 41",
        "type": "Supported (Needle Page 41)"
    },
    {
        "id": "Q4",
        "question": "What is the automated canary deployment rollout percentage and bake time for Kubernetes clusters?",
        "expected_answer": "[not found]",
        "expected_source": "None",
        "type": "Unsupported (Negative Control / Fallback)"
    },
    {
        "id": "Q5",
        "question": "What is the retention period and backup frequency for PostgreSQL Write-Ahead Logs (WAL) in cold S3 storage?",
        "expected_answer": "[not found]",
        "expected_source": "None",
        "type": "Unsupported (Negative Control / Fallback)"
    }
]


def run_tests():
    print("=" * 80)
    print("RGIB GenAI Part 2 - Project 2 Assessment Evaluation")
    print("Corpus: TitanCloud Enterprise SRE & Incident Response Runbook (50 Pages)")
    print("=" * 80)

    # Ingest if not already persisted
    ingest_pdf()

    results = []
    print("\nExecuting test queries through `answer(question)`:\n")

    for item in ASSESSMENT_QUESTIONS:
        qid = item["id"]
        q_text = item["question"]
        print("-" * 80)
        print(f"[{qid}] Assessment Question: {q_text}")
        print(f"Type: {item['type']}")
        print(f"Expected Answer: {item['expected_answer']}")
        print(f"Expected Source: {item['expected_source']}")
        
        output = answer(q_text)
        
        actual_answer = output.get("answer", "")
        sources = output.get("sources", [])
        
        print(f"\n-> RAG Output Answer: {actual_answer}")
        print(f"-> Sources Cited: {sources}")

        # Check correctness
        if item["expected_answer"] == "[not found]":
            passed = actual_answer.strip() == "[not found]" and len(sources) == 0
        else:
            passed = (item["expected_source"] in sources) and (actual_answer.strip() != "[not found]")

        status = "PASSED (MATCH)" if passed else "FAILED"
        print(f"-> Status: {status}\n")

        results.append({
            "question_id": qid,
            "question": q_text,
            "category": item["type"],
            "expected_answer": item["expected_answer"],
            "expected_sources": item["expected_source"],
            "rag_answer": actual_answer,
            "rag_sources": sources,
            "status": status
        })

    # Save to JSON
    with open("assessment_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 80)
    print("EVALUATION SUMMARY TABLE")
    print("=" * 80)
    print(f"{'ID':<4} | {'Status':<14} | {'Source Cited':<12} | {'Answer Preview'}")
    print("-" * 80)
    for r in results:
        preview = r['rag_answer'][:60] + ("..." if len(r['rag_answer']) > 60 else "")
        src = ", ".join(r['rag_sources']) if r['rag_sources'] else "None"
        print(f"{r['question_id']:<4} | {r['status']:<14} | {src:<12} | {preview}")
    print("=" * 80)
    print("All results saved to `assessment_results.json`")


if __name__ == "__main__":
    run_tests()
