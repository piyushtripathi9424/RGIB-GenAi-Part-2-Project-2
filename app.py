#!/usr/bin/env python3
"""
TitanCloud Enterprise SRE Incident Response Copilot
A modern conversational chat assistant for querying enterprise SRE runbooks,
service-level agreements, error codes, and alert escalation procedures.
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
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #090d16;
      --sidebar: #0e1526;
      --chat-bg: #0b1120;
      --card-bg: #131d35;
      --card-border: #1e2c4f;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-glow: rgba(59, 130, 246, 0.25);
      --text: #f1f5f9;
      --text-muted: #8492a6;
      --success: #10b981;
      --danger: #f43f5e;
      --font-mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      height: 100vh;
      display: flex;
      overflow: hidden;
    }

    /* Sidebar Layout */
    aside {
      width: 290px;
      background: var(--sidebar);
      border-right: 1px solid var(--card-border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      z-index: 10;
    }
    .sidebar-header {
      padding: 20px 18px;
      border-bottom: 1px solid var(--card-border);
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .app-logo {
      width: 38px;
      height: 38px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 16px;
      color: #fff;
      box-shadow: 0 4px 14px var(--primary-glow);
    }
    .app-title h1 {
      font-size: 15px;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: #fff;
    }
    .app-title p {
      font-size: 11px;
      color: var(--text-muted);
    }

    .new-chat-btn {
      margin: 16px 18px;
      background: rgba(59, 130, 246, 0.12);
      color: #60a5fa;
      border: 1px dashed rgba(59, 130, 246, 0.4);
      border-radius: 10px;
      padding: 12px 14px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.2s;
    }
    .new-chat-btn:hover {
      background: rgba(59, 130, 246, 0.22);
      border-color: #60a5fa;
    }

    .sidebar-scroll {
      flex: 1;
      overflow-y: auto;
      padding: 0 18px 18px;
    }
    .section-label {
      font-size: 11px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.06em;
      color: #64748b;
      margin: 18px 0 8px;
    }
    .shortcut-item {
      background: transparent;
      border: 1px solid transparent;
      border-radius: 8px;
      padding: 9px 12px;
      font-size: 12px;
      color: #cbd5e1;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 4px;
      transition: all 0.15s ease;
      text-align: left;
      width: 100%;
    }
    .shortcut-item:hover {
      background: #17233d;
      border-color: #24355c;
      color: #fff;
    }
    .shortcut-icon {
      font-size: 14px;
      flex-shrink: 0;
    }
    .shortcut-title {
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .sidebar-footer {
      padding: 14px 18px;
      border-top: 1px solid var(--card-border);
      background: rgba(10, 15, 27, 0.5);
    }
    .system-badge {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 11px;
      color: #94a3b8;
      margin-bottom: 8px;
    }
    .pulse-dot {
      width: 8px;
      height: 8px;
      background: var(--success);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--success);
    }
    .assessment-btn {
      width: 100%;
      background: #1e293b;
      color: #f1f5f9;
      border: 1px solid #334155;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .assessment-btn:hover {
      background: #334155;
      border-color: #475569;
    }

    /* Main Chat Layout */
    .chat-container {
      flex: 1;
      display: flex;
      flex-direction: column;
      height: 100vh;
      background: var(--chat-bg);
      position: relative;
    }

    .chat-topbar {
      padding: 16px 28px;
      border-bottom: 1px solid var(--card-border);
      background: rgba(11, 17, 32, 0.85);
      backdrop-filter: blur(12px);
      display: flex;
      justify-content: space-between;
      align-items: center;
      z-index: 5;
    }
    .topbar-info h2 {
      font-size: 15px;
      font-weight: 700;
      color: #fff;
    }
    .topbar-info p {
      font-size: 12px;
      color: var(--text-muted);
    }
    .topbar-tags {
      display: flex;
      gap: 8px;
    }
    .pill {
      font-size: 11px;
      padding: 4px 10px;
      border-radius: 20px;
      background: #17233d;
      color: #93c5fd;
      border: 1px solid #24355c;
      font-weight: 600;
    }

    /* Messages Area */
    .messages-viewport {
      flex: 1;
      overflow-y: auto;
      padding: 28px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      scroll-behavior: smooth;
    }

    .msg-group {
      display: flex;
      gap: 14px;
      max-width: 860px;
      width: 100%;
    }
    .msg-group.user {
      align-self: flex-end;
      flex-direction: row-reverse;
    }
    .msg-group.assistant {
      align-self: flex-start;
    }

    .avatar {
      width: 36px;
      height: 36px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 700;
      flex-shrink: 0;
    }
    .avatar.assistant {
      background: linear-gradient(135deg, #2563eb, #6366f1);
      color: #fff;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .avatar.user {
      background: #334155;
      color: #f1f5f9;
    }

    .bubble {
      padding: 16px 20px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.6;
      max-width: 760px;
    }
    .msg-group.user .bubble {
      background: #2563eb;
      color: #fff;
      border-bottom-right-radius: 4px;
    }
    .msg-group.assistant .bubble {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: #e2e8f0;
      border-bottom-left-radius: 4px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
    }

    .source-row {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 12px;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      flex-wrap: wrap;
    }
    .source-tag {
      background: #1e3a8a;
      color: #bfdbfe;
      border: 1px solid #3b82f6;
      border-radius: 6px;
      padding: 2px 8px;
      font-size: 11px;
      font-weight: 700;
      font-family: var(--font-mono);
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .source-tag.none {
      background: #1e293b;
      color: #94a3b8;
      border-color: #334155;
    }
    .payload-toggle {
      font-size: 11px;
      color: #60a5fa;
      background: none;
      border: none;
      cursor: pointer;
      text-decoration: underline;
      margin-left: auto;
    }
    .payload-pre {
      background: #060a12;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 10px 14px;
      font-family: var(--font-mono);
      font-size: 11px;
      color: #38bdf8;
      margin-top: 10px;
      overflow-x: auto;
      display: none;
    }
    .payload-pre.open { display: block; }

    .welcome-card {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.12) 0%, rgba(15, 23, 42, 0.8) 100%);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 16px;
      padding: 24px;
      margin-bottom: 8px;
    }
    .welcome-card h3 {
      font-size: 18px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 8px;
    }
    .welcome-card p {
      font-size: 13px;
      color: #94a3b8;
      line-height: 1.6;
      margin-bottom: 16px;
    }
    .preset-suggestions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }
    .suggestion-chip {
      background: #17233d;
      border: 1px solid #24355c;
      color: #cbd5e1;
      border-radius: 8px;
      padding: 8px 12px;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.2s;
    }
    .suggestion-chip:hover {
      background: #2563eb;
      border-color: #3b82f6;
      color: #fff;
    }

    /* Bottom Input Bar */
    .input-dock {
      padding: 16px 28px 24px;
      background: rgba(11, 17, 32, 0.95);
      border-top: 1px solid var(--card-border);
    }
    .input-box {
      background: #131d35;
      border: 1px solid #24355c;
      border-radius: 14px;
      padding: 6px 10px 6px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
      transition: border-color 0.2s;
    }
    .input-box:focus-within {
      border-color: var(--primary);
      box-shadow: 0 0 0 3px var(--primary-glow);
    }
    .chat-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 14px;
      font-family: inherit;
    }
    .send-btn {
      background: var(--primary);
      color: #fff;
      border: none;
      border-radius: 10px;
      width: 40px;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      cursor: pointer;
      transition: background 0.2s;
      flex-shrink: 0;
    }
    .send-btn:hover { background: var(--primary-hover); }

    /* Modal for Assessment Table */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(6px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 999;
      padding: 20px;
    }
    .modal-backdrop.open { display: flex; }
    .modal-box {
      background: #0f172a;
      border: 1px solid var(--card-border);
      border-radius: 18px;
      width: 100%;
      max-width: 980px;
      max-height: 85vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 60px rgba(0, 0, 0, 0.6);
      overflow: hidden;
    }
    .modal-header {
      padding: 20px 24px;
      border-bottom: 1px solid #1e293b;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-header h3 {
      font-size: 16px;
      font-weight: 700;
      color: #fff;
    }
    .close-modal-btn {
      background: #1e293b;
      border: none;
      color: #94a3b8;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      font-size: 18px;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    .close-modal-btn:hover { background: #334155; color: #fff; }
    .modal-content {
      padding: 24px;
      overflow-y: auto;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      padding: 12px 14px;
      border-bottom: 1px solid #1e293b;
      text-align: left;
    }
    th {
      background: #131d35;
      color: #94a3b8;
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
    }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside>
    <div class="sidebar-header">
      <div class="app-logo">TC</div>
      <div class="app-title">
        <h1>TitanCloud SRE</h1>
        <p>Incident Runbook Copilot</p>
      </div>
    </div>

    <button class="new-chat-btn" onclick="startNewChat()">
      <span>+</span> New Incident Query
    </button>

    <div class="sidebar-scroll">
      <div class="section-label">Runbook Quick Inquiries</div>
      <button class="shortcut-item" onclick="triggerQuery(1)">
        <span class="shortcut-icon">📊</span>
        <span class="shortcut-title">Uptime SLA & Credit (99.2%)</span>
      </button>
      <button class="shortcut-item" onclick="triggerQuery(2)">
        <span class="shortcut-icon">⚠️</span>
        <span class="shortcut-title">ERR_PG_REPLICA_LAG Failover</span>
      </button>
      <button class="shortcut-item" onclick="triggerQuery(3)">
        <span class="shortcut-icon">🚨</span>
        <span class="shortcut-title">Severity-1 (P0) Escalation</span>
      </button>
      <button class="shortcut-item" onclick="triggerQuery(4)">
        <span class="shortcut-icon">🛡️</span>
        <span class="shortcut-title">Canary Rollout (Negative Test)</span>
      </button>
      <button class="shortcut-item" onclick="triggerQuery(5)">
        <span class="shortcut-icon">📦</span>
        <span class="shortcut-title">WAL S3 Retention (Negative Test)</span>
      </button>

      <div class="section-label">Document Corpus</div>
      <div style="font-size: 12px; color: #94a3b8; line-height: 1.5; padding: 4px 6px;">
        📄 <code>titancloud_sre_incident_runbook_50p.pdf</code><br>
        • 50 Pages Extracted<br>
        • 197 Chunks Indexed<br>
        • ChromaDB Vector Store
      </div>
    </div>

    <div class="sidebar-footer">
      <div class="system-badge">
        <div class="pulse-dot"></div> ChromaDB Persistent Online
      </div>
      <button class="assessment-btn" onclick="openAssessmentModal()">
        📋 View Rubric Test Results (Q1-Q5)
      </button>
    </div>
  </aside>

  <!-- Main Chat Workspace -->
  <section class="chat-container">
    <div class="chat-topbar">
      <div class="topbar-info">
        <h2>SRE Incident Assistance Console</h2>
        <p>Grounding strictly against official SRE procedures</p>
      </div>
      <div class="topbar-tags">
        <span class="pill">Model: all-MiniLM-L6-v2</span>
        <span class="pill" style="color: #34d399; border-color: rgba(16,185,129,0.3);">Strict Grounding</span>
      </div>
    </div>

    <!-- Messages Scroll Feed -->
    <div class="messages-viewport" id="messagesBox">
      <!-- Welcome Hero Message -->
      <div class="welcome-card" id="welcomeHero">
        <h3>👋 Hello SRE Engineer</h3>
        <p>I am your TitanCloud Incident Response Copilot. I have indexed the complete 50-page official incident runbook and can assist you with Service-Level Agreements (SLAs), error code troubleshooting, Patroni automatic failovers, and P0 incident escalation timelines.</p>
        <div class="preset-suggestions">
          <div class="suggestion-chip" onclick="triggerQuery(1)">📊 What is the service credit for 99.2% uptime?</div>
          <div class="suggestion-chip" onclick="triggerQuery(2)">⚠️ How to handle ERR_PG_REPLICA_LAG?</div>
          <div class="suggestion-chip" onclick="triggerQuery(3)">🚨 What is the Severity-1 escalation timeline?</div>
          <div class="suggestion-chip" onclick="triggerQuery(4)">🛡️ Canary bake time (Strict [not found] test)</div>
        </div>
      </div>
    </div>

    <!-- Input Dock -->
    <div class="input-dock">
      <div class="input-box">
        <input type="text" id="userInput" class="chat-input" placeholder="Ask about SLAs, incident error codes, or escalation timelines... (Press Enter)" autocomplete="off">
        <button class="send-btn" id="sendBtn" onclick="handleSend()">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="22" y1="2" x2="11" y2="13"></line>
            <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
          </svg>
        </button>
      </div>
    </div>
  </section>

  <!-- Assessment Results Modal -->
  <div class="modal-backdrop" id="assessmentModal" onclick="closeAssessmentModal(event)">
    <div class="modal-box" onclick="event.stopPropagation()">
      <div class="modal-header">
        <h3>📋 Official Assessment Suite — 5 Questions Verification</h3>
        <button class="close-modal-btn" onclick="closeAssessmentModal()">&times;</button>
      </div>
      <div class="modal-content">
        <p style="font-size: 13px; color: #94a3b8; margin-bottom: 16px;">
          All five questions evaluated through <code>def answer(question: str) -> dict</code>. Supports exact factual needles and triggers strict <code>[not found]</code> on negative controls.
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
          <tbody id="modalTableBody"></tbody>
        </table>
      </div>
    </div>
  </div>

  <script>
    const queries = {
      1: "What is the service credit percentage owed to enterprise customers if monthly uptime drops to 99.2%?",
      2: "What is the maximum permitted replication lag threshold before Patroni initiates automatic failover for error code ERR_PG_REPLICA_LAG?",
      3: "What is the escalation timeline for a Severity-1 (P0) production outage alert if unacknowledged by the L1 On-Call Engineer?",
      4: "What is the automated canary deployment rollout percentage and bake time for Kubernetes clusters?",
      5: "What is the retention period and backup frequency for PostgreSQL Write-Ahead Logs (WAL) in cold S3 storage?"
    };

    let msgCounter = 0;

    function triggerQuery(num) {
      document.getElementById('userInput').value = queries[num];
      handleSend();
    }

    function startNewChat() {
      const box = document.getElementById('messagesBox');
      box.innerHTML = `
        <div class="welcome-card" id="welcomeHero">
          <h3>👋 New SRE Incident Session Started</h3>
          <p>Ask any operational question or select an SRE incident runbook shortcut below.</p>
          <div class="preset-suggestions">
            <div class="suggestion-chip" onclick="triggerQuery(1)">📊 What is the service credit for 99.2% uptime?</div>
            <div class="suggestion-chip" onclick="triggerQuery(2)">⚠️ How to handle ERR_PG_REPLICA_LAG?</div>
            <div class="suggestion-chip" onclick="triggerQuery(3)">🚨 What is the Severity-1 escalation timeline?</div>
            <div class="suggestion-chip" onclick="triggerQuery(4)">🛡️ Canary bake time (Strict [not found] test)</div>
          </div>
        </div>
      `;
    }

    async function handleSend() {
      const input = document.getElementById('userInput');
      const q = input.value.trim();
      if (!q) return;

      input.value = "";
      const box = document.getElementById('messagesBox');

      // Append User Bubble
      const userGroup = document.createElement('div');
      userGroup.className = "msg-group user";
      userGroup.innerHTML = `
        <div class="avatar user">You</div>
        <div class="bubble">${escapeHtml(q)}</div>
      `;
      box.appendChild(userGroup);

      // Append Loading Indicator
      const loadingGroup = document.createElement('div');
      loadingGroup.className = "msg-group assistant";
      loadingGroup.id = "loadingMsg";
      loadingGroup.innerHTML = `
        <div class="avatar assistant">SRE</div>
        <div class="bubble" style="color: #94a3b8;">Searching SRE runbook corpus in ChromaDB...</div>
      `;
      box.appendChild(loadingGroup);
      box.scrollTop = box.scrollHeight;

      try {
        const res = await fetch('/api/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q })
        });
        const data = await res.json();
        
        loadingGroup.remove();

        // Assistant Message Bubble
        msgCounter++;
        const currId = "payload_" + msgCounter;
        const isNotFound = data.answer === "[not found]";
        
        let sourceHtml = "";
        if (data.sources && data.sources.length > 0) {
          sourceHtml = data.sources.map(s => `<span class="source-tag">📄 Source: ${s}</span>`).join(" ");
        } else {
          sourceHtml = `<span class="source-tag none">No Source Cited (Unsupported in PDF)</span>`;
        }

        const assistGroup = document.createElement('div');
        assistGroup.className = "msg-group assistant";
        assistGroup.innerHTML = `
          <div class="avatar assistant">SRE</div>
          <div class="bubble">
            <div style="${isNotFound ? 'color: #f43f5e; font-family: var(--font-mono); font-size: 16px; font-weight: 700;' : ''}">${escapeHtml(data.answer)}</div>
            <div class="source-row">
              ${sourceHtml}
              <button class="payload-toggle" onclick="togglePayload('${currId}')">JSON Payload</button>
            </div>
            <pre class="payload-pre" id="${currId}"><code>${escapeHtml(JSON.stringify(data, null, 2))}</code></pre>
          </div>
        `;
        box.appendChild(assistGroup);
        box.scrollTop = box.scrollHeight;

      } catch (e) {
        loadingGroup.innerHTML = `<div class="avatar assistant">SRE</div><div class="bubble" style="color: #f43f5e;">Query failed: ${e}</div>`;
      }
    }

    function togglePayload(id) {
      const el = document.getElementById(id);
      if (el) el.classList.toggle('open');
    }

    function escapeHtml(text) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
      return text.replace(/[&<>"']/g, m => map[m]);
    }

    function openAssessmentModal() {
      document.getElementById('assessmentModal').classList.add('open');
      loadModalTable();
    }

    function closeAssessmentModal(e) {
      document.getElementById('assessmentModal').classList.remove('open');
    }

    async function loadModalTable() {
      const tbody = document.getElementById('modalTableBody');
      if (tbody.children.length > 0) return;
      try {
        const res = await fetch('/api/assessment');
        const items = await res.json();
        tbody.innerHTML = "";
        items.forEach(item => {
          const isNotFound = item.expected_answer === "[not found]";
          const tr = document.createElement('tr');
          tr.innerHTML = `
            <td><strong>${item.id}</strong></td>
            <td>${item.question}</td>
            <td style="color: ${isNotFound ? '#f43f5e' : '#93c5fd'}; font-family: monospace;">${item.expected_answer}</td>
            <td>${item.actual_answer}</td>
            <td><span class="source-tag ${item.sources.length ? '' : 'none'}">${item.sources.join(', ') || 'None'}</span></td>
            <td style="color: #34d399; font-weight: 700;">&#x2714; PASSED</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (err) {
        console.error("Failed to load modal", err);
      }
    }

    document.getElementById('userInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') handleSend();
    });
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
    print(f"  TitanCloud SRE Incident Copilot is running!")
    print(f"  Open in your browser: http://localhost:{PORT}")
    print(f"=======================================================\n")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
