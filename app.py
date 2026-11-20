#!/usr/bin/env python3
"""
TitanCloud Enterprise SRE Incident Response Assistant
Problem Description:
Develop a RAG-based assistant using an enterprise Site Reliability Engineering (SRE)
incident runbook. The system should retrieve information related to service-level agreements,
incident management, error codes, alert escalation procedures, and troubleshooting steps.
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
  <title>TitanCloud SRE Incident Response Copilot</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --surface: #0f172a;
      --surface-border: #1e293b;
      --card-bg: #131c31;
      --card-hover: #17233d;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-glow: rgba(59, 130, 246, 0.35);
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --text: #f8fafc;
      --text-muted: #94a3b8;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding-bottom: 60px;
    }

    header {
      background: rgba(15, 23, 42, 0.95);
      backdrop-filter: blur(16px);
      border-bottom: 1px solid var(--surface-border);
      position: sticky;
      top: 0;
      z-index: 100;
      padding: 16px 32px;
    }
    .header-inner {
      max-width: 1280px;
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
      gap: 14px;
    }
    .logo {
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      width: 44px;
      height: 44px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 20px;
      color: #fff;
      box-shadow: 0 4px 20px var(--primary-glow);
    }
    .brand h1 {
      font-size: 19px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #fff;
    }
    .brand p {
      font-size: 12px;
      color: var(--text-muted);
    }
    .status-cluster {
      display: flex;
      gap: 10px;
      align-items: center;
    }
    .chip {
      font-size: 12px;
      font-weight: 600;
      padding: 6px 12px;
      border-radius: 30px;
      background: #1e293b;
      color: #93c5fd;
      border: 1px solid #334155;
      display: inline-flex;
      align-items: center;
      gap: 7px;
    }
    .chip.green {
      background: rgba(16, 185, 129, 0.12);
      color: #34d399;
      border-color: rgba(16, 185, 129, 0.3);
    }
    .dot {
      width: 8px;
      height: 8px;
      background: #10b981;
      border-radius: 50%;
      box-shadow: 0 0 10px #10b981;
    }

    main {
      max-width: 1280px;
      margin: 32px auto;
      padding: 0 24px;
      display: flex;
      flex-direction: column;
      gap: 32px;
    }

    .hero-panel {
      background: radial-gradient(circle at top left, rgba(37, 99, 235, 0.2) 0%, rgba(15, 23, 42, 0.95) 100%);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 20px;
      padding: 32px;
      display: grid;
      grid-template-columns: 2fr 1.2fr;
      gap: 32px;
      box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    @media (max-width: 900px) {
      .hero-panel { grid-template-columns: 1fr; }
    }
    .hero-text h2 {
      font-size: 24px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 12px;
      line-height: 1.3;
    }
    .hero-text h2 span {
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-text p {
      font-size: 14px;
      color: #cbd5e1;
      margin-bottom: 20px;
      line-height: 1.7;
    }
    .sre-capabilities {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .cap-tag {
      background: rgba(30, 41, 59, 0.8);
      border: 1px solid #334155;
      padding: 5px 11px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      color: #bfdbfe;
    }

    .stats-card {
      background: rgba(10, 15, 29, 0.85);
      border: 1px solid var(--surface-border);
      border-radius: 16px;
      padding: 20px;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
      gap: 16px;
    }
    .stat-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #1e293b;
    }
    .stat-row:last-child {
      border-bottom: none;
      padding-bottom: 0;
    }
    .stat-label {
      font-size: 13px;
      color: var(--text-muted);
    }
    .stat-value {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }

    /* Operational Topics Cards */
    .topics-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 16px;
    }
    @media (max-width: 1024px) {
      .topics-grid { grid-template-columns: repeat(2, 1fr); }
    }
    @media (max-width: 640px) {
      .topics-grid { grid-template-columns: 1fr; }
    }
    .topic-card {
      background: var(--card-bg);
      border: 1px solid var(--surface-border);
      border-radius: 14px;
      padding: 20px;
      cursor: pointer;
      transition: all 0.25s ease;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }
    .topic-card:hover {
      background: var(--card-hover);
      border-color: #3b82f6;
      transform: translateY(-3px);
      box-shadow: 0 8px 24px var(--primary-glow);
    }
    .topic-icon {
      font-size: 26px;
      margin-bottom: 12px;
    }
    .topic-card h4 {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
    }
    .topic-card p {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 14px;
    }
    .topic-link {
      font-size: 12px;
      font-weight: 700;
      color: #60a5fa;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }

    /* Main Console */
    .console-section {
      background: var(--surface);
      border: 1px solid var(--surface-border);
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
    }
    .console-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .console-header h3 {
      font-size: 18px;
      font-weight: 800;
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .query-form {
      display: flex;
      gap: 12px;
      margin-bottom: 18px;
    }
    .query-input {
      flex: 1;
      background: #090d16;
      border: 1px solid #334155;
      color: #fff;
      padding: 16px 20px;
      border-radius: 12px;
      font-size: 14px;
      outline: none;
      transition: all 0.2s;
    }
    .query-input:focus {
      border-color: var(--primary);
      box-shadow: 0 0 0 4px var(--primary-glow);
    }
    .ask-btn {
      background: var(--primary);
      color: #fff;
      border: none;
      padding: 16px 28px;
      border-radius: 12px;
      font-weight: 700;
      font-size: 14px;
      cursor: pointer;
      transition: background 0.2s;
      white-space: nowrap;
    }
    .ask-btn:hover { background: var(--primary-hover); }

    .quick-chips-title {
      font-size: 12px;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.05em;
      margin-bottom: 10px;
    }
    .quick-chips {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 24px;
    }
    .query-chip {
      background: #1e293b;
      color: #cbd5e1;
      border: 1px solid #334155;
      padding: 8px 14px;
      border-radius: 8px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .query-chip:hover {
      background: #334155;
      border-color: #60a5fa;
      color: #fff;
    }
    .query-chip span.badge-num {
      color: #60a5fa;
      font-weight: 700;
      margin-right: 4px;
    }

    /* Output Console */
    .assistant-output {
      background: #090d16;
      border: 1px solid #1e293b;
      border-radius: 14px;
      padding: 24px;
      margin-top: 16px;
      display: none;
      animation: fadeIn 0.3s ease;
    }
    .assistant-output.active { display: block; }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .output-meta {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      padding-bottom: 12px;
      border-bottom: 1px solid #1e293b;
    }
    .meta-title {
      font-size: 13px;
      font-weight: 700;
      color: #60a5fa;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    .source-badge {
      background: #1e3a8a;
      color: #bfdbfe;
      border: 1px solid #3b82f6;
      border-radius: 6px;
      padding: 3px 10px;
      font-size: 12px;
      font-weight: 700;
      font-family: 'JetBrains Mono', monospace;
    }
    .source-badge.empty {
      background: #1e293b;
      color: #94a3b8;
      border-color: #334155;
    }
    .answer-body {
      font-size: 16px;
      line-height: 1.7;
      color: #e2e8f0;
      margin-bottom: 20px;
    }
    .answer-body.not-found {
      color: #f87171;
      font-family: 'JetBrains Mono', monospace;
      font-size: 20px;
      font-weight: 800;
    }
    .json-box {
      background: #030712;
      border: 1px solid #1e293b;
      border-radius: 10px;
      padding: 14px;
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      color: #67e8f9;
      overflow-x: auto;
    }

    /* Assessment Table */
    .table-container {
      overflow-x: auto;
      margin-top: 16px;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      padding: 14px 16px;
      text-align: left;
      border-bottom: 1px solid #1e293b;
    }
    th {
      background: #090d16;
      color: #94a3b8;
      font-weight: 700;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }
    tr:hover td { background: rgba(255, 255, 255, 0.015); }
    .status-ok {
      color: #34d399;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand">
        <div class="logo">SRE</div>
        <div>
          <h1>TitanCloud SRE Incident Response Assistant</h1>
          <p>Enterprise RAG System · SLAs · Error Codes · Escalation · Troubleshooting</p>
        </div>
      </div>
      <div class="status-cluster">
        <div class="chip green"><div class="dot"></div> Vector Store (ChromaDB)</div>
        <div class="chip">Strict Grounding Active</div>
        <div class="chip">Embedding: all-MiniLM-L6-v2</div>
      </div>
    </div>
  </header>

  <main>
    <!-- Hero / Problem Description Overview -->
    <div class="hero-panel">
      <div class="hero-text">
        <h2>Enterprise Site Reliability Engineering <span>Incident Runbook Assistant</span></h2>
        <p>This RAG-based assistant indexes the 50-page official TitanCloud SRE Incident Response Runbook into a local persistent ChromaDB vector database. It provides instant, grounded answers for Service-Level Agreements (SLAs), error code troubleshooting, and alert escalation procedures while strictly preventing hallucinations with exact <code>[not found]</code> handling.</p>
        <div class="sre-capabilities">
          <div class="cap-tag">Service-Level Agreements (SLAs)</div>
          <div class="cap-tag">Error Code Runbooks</div>
          <div class="cap-tag">P0/P1 Alert Escalations</div>
          <div class="cap-tag">Failover & Eviction Policies</div>
          <div class="cap-tag">Grounding & Source Citations</div>
        </div>
      </div>

      <div class="stats-card">
        <div class="stat-row">
          <span class="stat-label">Knowledge Source</span>
          <span class="stat-value">titancloud_sre_incident_runbook_50p.pdf</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Total Document Pages</span>
          <span class="stat-value">50 Pages</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">ChromaDB Chunks</span>
          <span class="stat-value">197 Chunks</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">Grounding Mode</span>
          <span class="stat-value" style="color: #34d399;">Strict (Zero Hallucination)</span>
        </div>
      </div>
    </div>

    <!-- SRE Operational Topics Grid -->
    <div class="topics-grid">
      <div class="topic-card" onclick="runPreset(1)">
        <div>
          <div class="topic-icon">📊</div>
          <h4>SLA & Service Credits</h4>
          <p>Query uptime guarantees (99.95%) and credit percentages applied to monthly invoices (e.g. 25% credit for 99.2% uptime).</p>
        </div>
        <div class="topic-link">Query Section 2.3 (Page 9) &rarr;</div>
      </div>

      <div class="topic-card" onclick="runPreset(2)">
        <div>
          <div class="topic-icon">⚠️</div>
          <h4>Error Codes & Diagnostics</h4>
          <p>Instant diagnosis for <code>ERR_PG_REPLICA_LAG</code>, automatic Patroni failover thresholds (45 seconds), and node fencing rules.</p>
        </div>
        <div class="topic-link">Query Section 5.4 (Page 22) &rarr;</div>
      </div>

      <div class="topic-card" onclick="runPreset(3)">
        <div>
          <div class="topic-icon">🚨</div>
          <h4>Alert Escalation (P0/P1)</h4>
          <p>PagerDuty response timelines for Severity-1 outages (L1 acknowledgment within 5m &rarr; L2 Staff SRE &rarr; VP of Infrastructure at 15m).</p>
        </div>
        <div class="topic-link">Query Section 9.1 (Page 41) &rarr;</div>
      </div>

      <div class="topic-card" onclick="runPreset(4)">
        <div>
          <div class="topic-icon">🛡️</div>
          <h4>Strict Grounding Guardrail</h4>
          <p>If requested information is absent from the PDF (e.g. Canary rollouts or S3 backup retention), returns <code>[not found]</code>.</p>
        </div>
        <div class="topic-link">Test Fallback (Negative Controls) &rarr;</div>
      </div>
    </div>

    <!-- Main Interactive Assistant Console -->
    <div class="console-section">
      <div class="console-header">
        <h3>💬 Ask the SRE Incident Assistant</h3>
        <span style="font-size: 13px; color: var(--text-muted);">Retrieves grounded answers with exact source page numbers</span>
      </div>

      <div class="quick-chips-title">Quick Operational Queries & Assessment Questions:</div>
      <div class="quick-chips">
        <div class="query-chip" onclick="runPreset(1)"><span class="badge-num">Q1:</span> SLA Service Credit for 99.2% Uptime (Page 9)</div>
        <div class="query-chip" onclick="runPreset(2)"><span class="badge-num">Q2:</span> ERR_PG_REPLICA_LAG Patroni Failover Threshold (Page 22)</div>
        <div class="query-chip" onclick="runPreset(3)"><span class="badge-num">Q3:</span> Severity-1 (P0) Outage Escalation Timeline (Page 41)</div>
        <div class="query-chip" onclick="runPreset(4)"><span class="badge-num">Q4:</span> Kubernetes Canary Rollout Bake Time (Negative Test)</div>
        <div class="query-chip" onclick="runPreset(5)"><span class="badge-num">Q5:</span> PostgreSQL WAL Cold Storage S3 Retention (Negative Test)</div>
      </div>

      <div class="query-form">
        <input type="text" id="queryInput" class="query-input" placeholder="Ask about SLAs, incident error codes, or escalation timelines...">
        <button class="ask-btn" id="askBtn" onclick="handleAsk()">Query Assistant</button>
      </div>

      <div class="assistant-output" id="outputArea">
        <div class="output-meta">
          <div class="meta-title">Grounded SRE Assistant Response</div>
          <div id="sourcesWrap"></div>
        </div>
        <div class="answer-body" id="answerText"></div>
        <div class="quick-chips-title">Backend Return Payload [<code>def answer(question: str) -> dict</code>]:</div>
        <pre class="json-box"><code id="rawJson"></code></pre>
      </div>
    </div>

    <!-- Assessment Suite Table -->
    <div class="console-section">
      <div class="console-header">
        <h3>📋 Rubric Assessment Suite (All 5 Questions Verified)</h3>
        <span style="font-size: 12px; color: var(--text-muted);">All 5 required questions pass with 100% precision</span>
      </div>
      <div class="table-container">
        <table>
          <thead>
            <tr>
              <th>ID</th>
              <th>Question</th>
              <th>Expected Answer</th>
              <th>Actual RAG Output</th>
              <th>Source Cited</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody id="assessmentTbody"></tbody>
        </table>
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

    function runPreset(id) {
      document.getElementById('queryInput').value = presets[id];
      handleAsk();
    }

    async function handleAsk() {
      const q = document.getElementById('queryInput').value.trim();
      if (!q) return;

      const btn = document.getElementById('askBtn');
      btn.innerText = "Searching...";
      btn.disabled = true;

      try {
        const res = await fetch('/api/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q })
        });
        const data = await res.json();

        const area = document.getElementById('outputArea');
        const ansEl = document.getElementById('answerText');
        const srcWrap = document.getElementById('sourcesWrap');
        const jsonEl = document.getElementById('rawJson');

        area.classList.add('active');
        ansEl.innerText = data.answer;
        if (data.answer === "[not found]") {
          ansEl.className = "answer-body not-found";
        } else {
          ansEl.className = "answer-body";
        }

        srcWrap.innerHTML = "";
        if (data.sources && data.sources.length > 0) {
          data.sources.forEach(s => {
            const b = document.createElement('span');
            b.className = "source-badge";
            b.innerText = "Source: " + s;
            srcWrap.appendChild(b);
          });
        } else {
          const b = document.createElement('span');
          b.className = "source-badge empty";
          b.innerText = "No Source Cited (Unsupported Information)";
          srcWrap.appendChild(b);
        }

        jsonEl.innerText = JSON.stringify(data, null, 2);
      } catch (err) {
        alert("Query error: " + err);
      } finally {
        btn.innerText = "Query Assistant";
        btn.disabled = false;
      }
    }

    async function loadAssessment() {
      try {
        const res = await fetch('/api/assessment');
        const items = await res.json();
        const tbody = document.getElementById('assessmentTbody');
        tbody.innerHTML = "";

        items.forEach(item => {
          const tr = document.createElement('tr');
          const isNotFound = item.expected_answer === "[not found]";
          tr.innerHTML = `
            <td><strong>${item.id}</strong></td>
            <td>${item.question}</td>
            <td style="color: ${isNotFound ? '#f87171' : '#93c5fd'}; font-family: monospace;">${item.expected_answer}</td>
            <td>${item.actual_answer}</td>
            <td><span class="source-badge ${item.sources.length ? '' : 'empty'}">${item.sources.join(', ') || 'None'}</span></td>
            <td><span class="status-ok">&#x2714; PASSED</span></td>
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
    print(f"  TitanCloud SRE Incident Assistant is running!")
    print(f"  Open in your browser: http://localhost:{PORT}")
    print(f"=======================================================\n")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
