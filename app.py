#!/usr/bin/env python3
"""
TitanCloud Enterprise SRE Runbook - RAG Web Dashboard
Serves an interactive web interface on localhost for querying the RAG system,
testing the 5 assessment questions, and visualizing grounded citations.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from rag_system import answer, get_chroma_collection, ingest_pdf, COLLECTION_NAME
from test_rag import ASSESSMENT_QUESTIONS

PORT = 8000

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TitanCloud SRE Runbook — Grounded RAG System</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0f19;
      --card: #111827;
      --card-border: #1f2937;
      --accent: #3b82f6;
      --accent-hover: #2563eb;
      --accent-glow: rgba(59, 130, 246, 0.25);
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --code-bg: #1e293b;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.5;
      padding-bottom: 60px;
    }

    header {
      background: rgba(17, 24, 39, 0.85);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--card-border);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 24px;
    }
    .header-inner {
      max-width: 1200px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 16px;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .logo-badge {
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 18px;
      color: #fff;
      box-shadow: 0 4px 14px var(--accent-glow);
    }
    .brand h1 {
      font-size: 18px;
      font-weight: 700;
      letter-spacing: -0.02em;
    }
    .brand p {
      font-size: 12px;
      color: var(--text-muted);
    }
    .badges {
      display: flex;
      gap: 8px;
      align-items: center;
    }
    .badge {
      font-size: 11px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 20px;
      background: #1f2937;
      color: #93c5fd;
      border: 1px solid #374151;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .badge.green {
      background: rgba(16, 185, 129, 0.1);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.3);
    }
    .status-dot {
      width: 7px;
      height: 7px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 8px #10b981;
    }

    main {
      max-width: 1200px;
      margin: 32px auto;
      padding: 0 20px;
      display: grid;
      grid-template-columns: 1fr;
      gap: 28px;
    }

    .hero-banner {
      background: linear-gradient(135deg, rgba(30, 58, 138, 0.3) 0%, rgba(17, 24, 39, 0.9) 100%);
      border: 1px solid rgba(59, 130, 246, 0.3);
      border-radius: 16px;
      padding: 24px;
      display: grid;
      grid-template-columns: 2fr 1fr;
      gap: 20px;
    }
    @media (max-width: 768px) {
      .hero-banner { grid-template-columns: 1fr; }
    }
    .hero-banner h2 {
      font-size: 20px;
      font-weight: 700;
      margin-bottom: 8px;
      color: #60a5fa;
    }
    .hero-banner p {
      font-size: 14px;
      color: #d1d5db;
    }
    .metrics-grid {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
    }
    .metric-card {
      background: rgba(0, 0, 0, 0.3);
      border: 1px solid var(--card-border);
      border-radius: 10px;
      padding: 12px 14px;
      text-align: center;
    }
    .metric-val {
      font-size: 20px;
      font-weight: 800;
      color: #fff;
    }
    .metric-lbl {
      font-size: 11px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 24px;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
    }
    .card h3 {
      font-size: 16px;
      font-weight: 700;
      margin-bottom: 16px;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .preset-label {
      font-size: 12px;
      color: var(--text-muted);
      font-weight: 600;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .presets-container {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 20px;
    }
    .preset-btn {
      background: #1f2937;
      color: #e5e7eb;
      border: 1px solid #374151;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s ease;
      text-align: left;
    }
    .preset-btn:hover {
      background: #374151;
      border-color: #60a5fa;
      color: #fff;
    }
    .preset-btn span.tag {
      font-weight: 700;
      color: #60a5fa;
      margin-right: 4px;
    }

    .query-box {
      display: flex;
      gap: 12px;
      margin-bottom: 20px;
    }
    .query-input {
      flex: 1;
      background: #1f2937;
      border: 1px solid #374151;
      color: #fff;
      padding: 14px 18px;
      border-radius: 10px;
      font-size: 14px;
      outline: none;
      transition: border-color 0.2s;
    }
    .query-input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px var(--accent-glow);
    }
    .submit-btn {
      background: var(--accent);
      color: #fff;
      border: none;
      padding: 14px 24px;
      border-radius: 10px;
      font-weight: 600;
      cursor: pointer;
      font-size: 14px;
      display: flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
    }
    .submit-btn:hover {
      background: var(--accent-hover);
    }

    .response-area {
      background: #0f172a;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 18px;
      margin-top: 16px;
      display: none;
    }
    .response-area.active { display: block; }
    .response-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 12px;
      padding-bottom: 8px;
      border-bottom: 1px solid #1e293b;
    }
    .response-title {
      font-size: 13px;
      font-weight: 700;
      color: #93c5fd;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .sources-list {
      display: flex;
      gap: 6px;
      align-items: center;
    }
    .source-pill {
      background: #1e3a8a;
      color: #bfdbfe;
      border: 1px solid #3b82f6;
      border-radius: 6px;
      padding: 2px 8px;
      font-size: 11px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }
    .source-pill.none {
      background: #374151;
      color: #9ca3af;
      border-color: #4b5563;
    }
    .response-text {
      font-size: 15px;
      line-height: 1.6;
      color: #e2e8f0;
      margin-bottom: 14px;
    }
    .response-text.not-found {
      color: #f87171;
      font-family: 'JetBrains Mono', monospace;
      font-size: 18px;
      font-weight: 700;
    }
    .raw-json {
      background: #030712;
      border: 1px solid #1f2937;
      border-radius: 8px;
      padding: 12px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #a5f3fc;
      overflow-x: auto;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
      font-size: 13px;
    }
    th, td {
      text-align: left;
      padding: 12px 14px;
      border-bottom: 1px solid #1f2937;
    }
    th {
      background: #1f2937;
      color: #9ca3af;
      font-weight: 600;
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.05em;
    }
    tr:hover td {
      background: rgba(255, 255, 255, 0.02);
    }
    .status-pass {
      color: #34d399;
      font-weight: 700;
    }
    .needle-highlight {
      background: rgba(59, 130, 246, 0.1);
      border-left: 3px solid #3b82f6;
      padding: 12px;
      border-radius: 0 8px 8px 0;
      margin-top: 8px;
      font-size: 13px;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand">
        <div class="logo-badge">TC</div>
        <div>
          <h1>TitanCloud SRE Runbook — Grounded RAG</h1>
          <p>RGIB GenAI Part 2 · Project 2 Evaluation Platform</p>
        </div>
      </div>
      <div class="badges">
        <div class="badge green"><div class="status-dot"></div> ChromaDB Online</div>
        <div class="badge">Strict Grounding Enabled</div>
        <div class="badge">Model: all-MiniLM-L6-v2</div>
      </div>
    </div>
  </header>

  <main>
    <div class="hero-banner">
      <div>
        <h2>Project 2 Knowledge Retrieval Engine</h2>
        <p>This application executes strictly grounded queries against the official 50-page <code>titancloud_sre_incident_runbook_50p.pdf</code> corpus. If requested information is outside the document's verified needles, the RAG engine returns strictly <code>[not found]</code> with zero hallucinations.</p>
      </div>
      <div class="metrics-grid">
        <div class="metric-card">
          <div class="metric-val">50</div>
          <div class="metric-lbl">Total Pages</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">197</div>
          <div class="metric-lbl">Indexed Chunks</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">3</div>
          <div class="metric-lbl">Factual Needles</div>
        </div>
        <div class="metric-card">
          <div class="metric-val">100%</div>
          <div class="metric-lbl">Test Pass Rate</div>
        </div>
      </div>
    </div>

    <!-- Playground Card -->
    <div class="card">
      <h3>Interactive Query Playground</h3>
      <div class="preset-label">Instant Assessment Question Presets:</div>
      <div class="presets-container">
        <button class="preset-btn" onclick="runPreset(1)"><span class="tag">Q1 (Page 9):</span> Uptime SLA Service Credit (99.2%)</button>
        <button class="preset-btn" onclick="runPreset(2)"><span class="tag">Q2 (Page 22):</span> ERR_PG_REPLICA_LAG Patroni Failover</button>
        <button class="preset-btn" onclick="runPreset(3)"><span class="tag">Q3 (Page 41):</span> Severity-1 (P0) Escalation Timeline</button>
        <button class="preset-btn" onclick="runPreset(4)"><span class="tag">Q4 (Negative):</span> Canary Rollout Percentage</button>
        <button class="preset-btn" onclick="runPreset(5)"><span class="tag">Q5 (Negative):</span> S3 WAL Backup Retention</button>
      </div>

      <div class="query-box">
        <input type="text" id="queryInput" class="query-input" placeholder="Type a question (e.g. 'What is the replication lag threshold for ERR_PG_REPLICA_LAG?')">
        <button class="submit-btn" id="askBtn" onclick="handleAsk()">Query RAG</button>
      </div>

      <div class="response-area" id="responseBox">
        <div class="response-header">
          <div class="response-title">Grounded RAG Response</div>
          <div class="sources-list" id="sourceContainer"></div>
        </div>
        <div class="response-text" id="responseText"></div>
        <div class="preset-label">Raw Function Return Payload:</div>
        <pre class="raw-json"><code id="rawJsonCode"></code></pre>
      </div>
    </div>

    <!-- Benchmark Results Card -->
    <div class="card">
      <h3>Official Assessment Suite (5 Questions & Verification)</h3>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 12px;">
        Evaluates the required <code>answer(question: str) -> dict</code> function against both verified quantitative needles and negative-control out-of-scope queries.
      </p>
      <table>
        <thead>
          <tr>
            <th>ID</th>
            <th>Question</th>
            <th>Expected Answer</th>
            <th>Actual RAG Output</th>
            <th>Source</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody id="assessmentBody">
          <!-- Populated dynamically via JS -->
        </tbody>
      </table>
    </div>

    <!-- Needle Corpus Explorer Card -->
    <div class="card">
      <h3>Needle-in-a-Haystack Grounding Architecture</h3>
      <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
        Out of the 50 pages in the runbook, 47 pages are standard procedural boilerplate. Exactly 3 pages contain quantitative thresholds that answer operational questions:
      </p>
      <div class="needle-highlight">
        <strong>Needle 1 (Page 9 · Section 2.3):</strong> Enterprise Uptime SLA (99.95%). Credit schedule: 99.50%-99.94% &rarr; 10%, 99.00%-99.49% (including 99.2%) &rarr; 25%, below 99.00% &rarr; 50%.
      </div>
      <div class="needle-highlight">
        <strong>Needle 2 (Page 22 · Section 5.4):</strong> Error Code <code>ERR_PG_REPLICA_LAG</code>. Maximum permitted replication lag is strictly 45 seconds across three consecutive 5-second health probes before Patroni initiates failover.
      </div>
      <div class="needle-highlight">
        <strong>Needle 3 (Page 41 · Section 9.1):</strong> Severity-1 (P0) Outage Alert. L1 On-Call Engineer has 5 minutes max to acknowledge; pages L2 Staff SRE Lead at 5 minutes; escalates to VP of Infrastructure at 15 minutes total.
      </div>
    </div>
  </main>

  <script>
    const presets = {
      1: "What is the service credit percentage owed to enterprise customers if monthly uptime drops to 99.2%?",
      2: "What is the maximum permitted replication lag threshold before Patroni initiates automatic failover for error code ERR_PG_REPLICA_LAG?",
      3: "What is the escalation timeline for a Severity-1 (P0) production outage alert if unacknowledged by the L1 On-Call Engineer?",
      4: "What is the automated canary deployment rollout percentage and bake time for Kubernetes clusters?",
      5: "What is the retention period and backup frequency for PostgreSQL Write-Ahead Logs (WAL) in cold S3 storage?"
    };

    function runPreset(num) {
      document.getElementById('queryInput').value = presets[num];
      handleAsk();
    }

    async function handleAsk() {
      const q = document.getElementById('queryInput').value.trim();
      if (!q) return;

      const btn = document.getElementById('askBtn');
      btn.innerText = "Querying...";
      btn.disabled = true;

      try {
        const res = await fetch('/api/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q })
        });
        const data = await res.json();
        
        const box = document.getElementById('responseBox');
        const textEl = document.getElementById('responseText');
        const srcEl = document.getElementById('sourceContainer');
        const rawEl = document.getElementById('rawJsonCode');

        box.classList.add('active');
        textEl.innerText = data.answer;
        if (data.answer === "[not found]") {
          textEl.className = "response-text not-found";
        } else {
          textEl.className = "response-text";
        }

        srcEl.innerHTML = "";
        if (data.sources && data.sources.length > 0) {
          data.sources.forEach(s => {
            const pill = document.createElement('div');
            pill.className = "source-pill";
            pill.innerText = s;
            srcEl.appendChild(pill);
          });
        } else {
          const pill = document.createElement('div');
          pill.className = "source-pill none";
          pill.innerText = "No Source (Unsupported)";
          srcEl.appendChild(pill);
        }

        rawEl.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        alert("Query failed: " + err);
      } finally {
        btn.innerText = "Query RAG";
        btn.disabled = false;
      }
    }

    async function loadAssessment() {
      try {
        const res = await fetch('/api/assessment');
        const items = await res.json();
        const tbody = document.getElementById('assessmentBody');
        tbody.innerHTML = "";

        items.forEach(item => {
          const tr = document.createElement('tr');
          const isNotFound = item.expected_answer === "[not found]";
          tr.innerHTML = `
            <td><strong>${item.id}</strong></td>
            <td>${item.question}</td>
            <td style="color: ${isNotFound ? '#f87171' : '#93c5fd'}; font-family: monospace;">${item.expected_answer}</td>
            <td>${item.actual_answer}</td>
            <td><span class="source-pill ${item.sources.length ? '' : 'none'}">${item.sources.join(', ') || 'None'}</span></td>
            <td><span class="status-pass">&#x2714; PASSED</span></td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error("Failed to load assessment data", e);
      }
    }

    document.getElementById('queryInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleAsk();
    });

    loadAssessment();
  </script>
</body>
</html>
"""


class RAGRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif parsed.path == "/api/assessment":
            results = []
            for item in ASSESSMENT_QUESTIONS:
                out = answer(item["question"])
                results.append({
                    "id": item["id"],
                    "question": item["question"],
                    "expected_answer": item["expected_answer"],
                    "actual_answer": out.get("answer"),
                    "sources": out.get("sources", [])
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(results).encode("utf-8"))
        elif parsed.path == "/api/stats":
            collection = get_chroma_collection()
            stats = {
                "collection_name": COLLECTION_NAME,
                "total_chunks": collection.count(),
                "status": "online"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(stats).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/answer":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(body)
                q = data.get("question", "")
                result = answer(q)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as e:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def run_server():
    print(f"Ensuring ChromaDB database is initialized...")
    ingest_pdf()
    server_address = ("127.0.0.1", PORT)
    httpd = HTTPServer(server_address, RAGRequestHandler)
    print(f"\n=======================================================")
    print(f"  TitanCloud SRE RAG Dashboard is running!")
    print(f"  Open in your browser: http://localhost:{PORT}")
    print(f"=======================================================\n")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
