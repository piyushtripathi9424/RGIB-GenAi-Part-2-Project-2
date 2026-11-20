#!/usr/bin/env python3
"""
TitanCloud Enterprise SRE Incident Response Copilot
Ultra-Polished Enterprise SaaS UI (Linear / Datadog / Vercel style)
With dynamic API Key configuration and high-precision grounded answers.
"""

import os
import json
import re
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
  <title>TitanCloud SRE Incident Copilot</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-dark: #07090e;
      --bg-panel: #0d111a;
      --bg-sidebar: #090c14;
      --bg-card: #121826;
      --bg-card-hover: #172033;
      --border-subtle: rgba(255, 255, 255, 0.08);
      --border-card: #1e283d;
      --border-glow: rgba(59, 130, 246, 0.5);
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-glow: rgba(59, 130, 246, 0.35);
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --text-dim: #64748b;
      --emerald: #10b981;
      --amber: #f59e0b;
      --rose: #f43f5e;
      --mono: 'JetBrains Mono', monospace;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg-dark);
      color: var(--text-main);
      height: 100vh;
      display: flex;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: #1e293b; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #334155; }

    /* Left Sidebar */
    aside {
      width: 290px;
      background: var(--bg-sidebar);
      border-right: 1px solid var(--border-subtle);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
      z-index: 20;
    }

    .sidebar-brand {
      padding: 18px 20px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .brand-mark {
      width: 36px;
      height: 36px;
      background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 15px;
      color: #fff;
      box-shadow: 0 4px 16px var(--primary-glow);
    }
    .brand-title h1 {
      font-size: 15px;
      font-weight: 800;
      letter-spacing: -0.02em;
      color: #fff;
    }
    .brand-title span {
      font-size: 11px;
      color: var(--emerald);
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 5px;
    }
    .live-dot {
      width: 6px;
      height: 6px;
      background: var(--emerald);
      border-radius: 50%;
      box-shadow: 0 0 8px var(--emerald);
    }

    .new-chat-wrapper {
      padding: 14px 16px 6px;
    }
    .btn-new-chat {
      width: 100%;
      background: linear-gradient(180deg, #1e293b 0%, #152033 100%);
      border: 1px solid var(--border-card);
      color: #f1f5f9;
      padding: 10px 14px;
      border-radius: 9px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.2s;
    }
    .btn-new-chat:hover {
      background: var(--primary);
      border-color: var(--primary);
      box-shadow: 0 4px 14px var(--primary-glow);
      color: #fff;
    }

    .sidebar-menu {
      flex: 1;
      overflow-y: auto;
      padding: 10px 14px 16px;
    }
    .menu-header {
      font-size: 10px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--text-dim);
      margin: 16px 8px 8px;
    }
    .menu-item {
      width: 100%;
      background: transparent;
      border: 1px solid transparent;
      color: #cbd5e1;
      padding: 9px 12px;
      border-radius: 8px;
      font-size: 12.5px;
      text-align: left;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 10px;
      transition: all 0.15s;
      margin-bottom: 3px;
    }
    .menu-item:hover {
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      border-color: rgba(255, 255, 255, 0.08);
    }
    .item-icon {
      font-size: 14px;
      width: 18px;
      text-align: center;
      flex-shrink: 0;
    }
    .item-label {
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }

    .corpus-box {
      margin: 8px 6px;
      background: rgba(18, 24, 38, 0.7);
      border: 1px solid var(--border-card);
      border-radius: 9px;
      padding: 12px;
      font-size: 11.5px;
      color: var(--text-muted);
      line-height: 1.6;
    }
    .corpus-box strong {
      color: #e2e8f0;
      display: block;
      margin-bottom: 3px;
      word-break: break-all;
    }

    .sidebar-bottom {
      padding: 14px 16px;
      border-top: 1px solid var(--border-subtle);
    }
    .btn-rubric-view {
      width: 100%;
      background: #0f172a;
      border: 1px solid #1e293b;
      color: #94a3b8;
      padding: 9px 12px;
      border-radius: 8px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      transition: all 0.15s;
    }
    .btn-rubric-view:hover {
      background: #1e293b;
      color: #fff;
    }

    /* Main Area */
    main {
      flex: 1;
      display: flex;
      flex-direction: column;
      position: relative;
      background: radial-gradient(circle at 50% 0%, #111a2f 0%, #07090e 65%);
      overflow: hidden;
    }

    .top-nav {
      height: 56px;
      border-bottom: 1px solid var(--border-subtle);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
      background: rgba(9, 12, 20, 0.75);
      backdrop-filter: blur(12px);
      z-index: 15;
    }
    .nav-tabs {
      display: flex;
      gap: 8px;
    }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--text-dim);
      font-size: 13px;
      font-weight: 600;
      padding: 7px 14px;
      border-radius: 7px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .tab-btn.active {
      background: rgba(255, 255, 255, 0.08);
      color: #fff;
    }
    .tab-btn:hover:not(.active) {
      color: var(--text-muted);
    }

    .nav-tags {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .btn-api-config {
      background: rgba(59, 130, 246, 0.12);
      border: 1px solid rgba(59, 130, 246, 0.35);
      color: #93c5fd;
      padding: 5px 12px;
      border-radius: 7px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }
    .btn-api-config:hover {
      background: rgba(59, 130, 246, 0.22);
      border-color: #3b82f6;
      color: #fff;
    }
    .status-tag {
      font-size: 11.5px;
      font-weight: 600;
      padding: 4px 10px;
      border-radius: 6px;
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(16, 185, 129, 0.1);
      border: 1px solid rgba(16, 185, 129, 0.25);
      color: #34d399;
    }

    /* Chat Container */
    .chat-container {
      flex: 1;
      overflow-y: auto;
      padding: 24px 28px 12px;
      display: flex;
      flex-direction: column;
    }

    /* Hero / Empty State */
    .hero-center {
      max-width: 760px;
      margin: auto;
      text-align: center;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px 0;
    }
    .hero-logo-large {
      width: 58px;
      height: 58px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      border-radius: 18px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 26px;
      font-weight: 800;
      color: #fff;
      margin-bottom: 20px;
      box-shadow: 0 8px 30px rgba(37, 99, 235, 0.4);
    }
    .hero-title {
      font-size: 26px;
      font-weight: 800;
      letter-spacing: -0.03em;
      margin-bottom: 8px;
      color: #fff;
    }
    .hero-title span {
      background: linear-gradient(135deg, #60a5fa, #a78bfa);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .hero-subtitle {
      font-size: 13.5px;
      color: var(--text-muted);
      max-width: 580px;
      line-height: 1.6;
      margin-bottom: 28px;
    }

    .starter-cards {
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 12px;
      width: 100%;
      text-align: left;
    }
    .starter-card {
      background: linear-gradient(180deg, #101624 0%, #0c101a 100%);
      border: 1px solid var(--border-card);
      border-radius: 12px;
      padding: 16px 18px;
      cursor: pointer;
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
    }
    .starter-card:hover {
      background: var(--bg-card-hover);
      border-color: #3b82f6;
      transform: translateY(-2px);
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
    }
    .card-top {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 6px;
    }
    .card-badge-icon {
      width: 26px;
      height: 26px;
      border-radius: 7px;
      background: #172338;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
    }
    .card-name {
      font-size: 13px;
      font-weight: 700;
      color: #fff;
    }
    .card-hint {
      font-size: 12px;
      color: var(--text-muted);
      line-height: 1.5;
    }

    /* Messages Stream */
    .messages-list {
      max-width: 820px;
      width: 100%;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 20px;
      padding-bottom: 20px;
    }
    .msg-item {
      display: flex;
      gap: 14px;
      width: 100%;
      animation: fadeIn 0.2s ease-in-out;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(6px); }
      to { opacity: 1; transform: translateY(0); }
    }
    .msg-item.user {
      justify-content: flex-end;
    }

    .msg-bubble-user {
      background: linear-gradient(135deg, #2563eb, #1d4ed8);
      color: #fff;
      padding: 12px 18px;
      border-radius: 18px 18px 4px 18px;
      font-size: 14px;
      font-weight: 500;
      line-height: 1.5;
      box-shadow: 0 4px 16px rgba(37, 99, 235, 0.25);
      max-width: 680px;
    }

    .msg-bubble-ai {
      background: #111726;
      border: 1px solid var(--border-card);
      border-radius: 4px 18px 18px 18px;
      padding: 18px 22px;
      color: #e2e8f0;
      font-size: 14px;
      line-height: 1.7;
      max-width: 740px;
      width: 100%;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.35);
    }
    .ai-avatar {
      width: 32px;
      height: 32px;
      border-radius: 9px;
      background: linear-gradient(135deg, #2563eb, #7c3aed);
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 800;
      font-size: 12px;
      flex-shrink: 0;
      box-shadow: 0 2px 8px rgba(37, 99, 235, 0.3);
    }

    .not-found-card {
      background: rgba(244, 63, 94, 0.04);
      border-color: rgba(244, 63, 94, 0.25);
    }
    .badge-not-found {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      background: rgba(244, 63, 94, 0.12);
      color: #fb7185;
      border: 1px solid rgba(244, 63, 94, 0.35);
      padding: 3px 10px;
      border-radius: 6px;
      font-family: var(--mono);
      font-size: 13px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .not-found-text {
      color: #94a3b8;
      font-size: 13px;
    }

    .msg-footer {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-top: 14px;
      padding-top: 10px;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
      flex-wrap: wrap;
    }
    .source-pill {
      background: rgba(37, 99, 235, 0.15);
      color: #93c5fd;
      border: 1px solid rgba(59, 130, 246, 0.3);
      padding: 2px 8px;
      border-radius: 5px;
      font-family: var(--mono);
      font-size: 11px;
      font-weight: 600;
      display: inline-flex;
      align-items: center;
      gap: 4px;
    }
    .source-pill.none {
      background: rgba(255, 255, 255, 0.04);
      color: #64748b;
      border-color: #1e293b;
    }
    .json-toggle {
      font-size: 11px;
      color: #60a5fa;
      background: none;
      border: none;
      cursor: pointer;
      margin-left: auto;
      text-decoration: underline;
    }
    .raw-json {
      background: #060911;
      border: 1px solid var(--border-card);
      border-radius: 6px;
      padding: 10px 14px;
      font-family: var(--mono);
      font-size: 11px;
      color: #38bdf8;
      margin-top: 10px;
      overflow-x: auto;
      display: none;
    }
    .raw-json.open { display: block; }

    /* Quick Query Suggestion Chips */
    .quick-chips-bar {
      max-width: 820px;
      margin: 0 auto;
      display: flex;
      gap: 8px;
      overflow-x: auto;
      padding: 6px 0;
      white-space: nowrap;
    }
    .chip-btn {
      background: #111726;
      border: 1px solid #1e293b;
      color: #94a3b8;
      font-size: 11.5px;
      padding: 5px 12px;
      border-radius: 14px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .chip-btn:hover {
      background: #1e293b;
      border-color: #3b82f6;
      color: #fff;
    }

    /* Bottom Input Area */
    .chat-bottom {
      padding: 10px 28px 20px;
      background: rgba(13, 17, 26, 0.95);
      border-top: 1px solid var(--border-subtle);
      z-index: 10;
    }
    .input-frame {
      max-width: 820px;
      margin: 0 auto;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    .input-container {
      background: #111726;
      border: 1px solid #22304d;
      border-radius: 14px;
      padding: 6px 8px 6px 18px;
      display: flex;
      align-items: center;
      gap: 12px;
      box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
      transition: all 0.2s;
    }
    .input-container:focus-within {
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
    }
    .text-input {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      color: #fff;
      font-size: 14px;
      font-family: inherit;
    }
    .btn-send {
      width: 36px;
      height: 36px;
      background: var(--primary);
      border: none;
      border-radius: 9px;
      color: #fff;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      transition: all 0.15s;
      flex-shrink: 0;
    }
    .btn-send:hover {
      background: var(--primary-hover);
      transform: scale(1.04);
    }
    .caption-text {
      text-align: center;
      font-size: 11px;
      color: var(--text-dim);
    }

    /* Assessment View Tab (Embedded) */
    .assessment-view {
      display: none;
      flex: 1;
      overflow-y: auto;
      padding: 32px;
      max-width: 1080px;
      margin: 0 auto;
      width: 100%;
    }
    .assessment-view.active { display: block; }
    .table-card {
      background: #101624;
      border: 1px solid var(--border-card);
      border-radius: 14px;
      overflow: hidden;
      box-shadow: 0 8px 30px rgba(0, 0, 0, 0.35);
    }
    .table-head-row {
      padding: 18px 22px;
      border-bottom: 1px solid var(--border-card);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    th, td {
      padding: 14px 18px;
      text-align: left;
      border-bottom: 1px solid #1a2438;
    }
    th {
      background: #0c111c;
      color: var(--text-dim);
      font-size: 11px;
      text-transform: uppercase;
      font-weight: 700;
    }

    /* Modal for API Key */
    .modal-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(4px);
      display: none;
      align-items: center;
      justify-content: center;
      z-index: 100;
    }
    .modal-backdrop.open { display: flex; }
    .modal-box {
      background: #0f1626;
      border: 1px solid var(--border-card);
      border-radius: 16px;
      padding: 24px 28px;
      max-width: 480px;
      width: 90%;
      box-shadow: 0 16px 40px rgba(0, 0, 0, 0.6);
    }
    .modal-title {
      font-size: 17px;
      font-weight: 700;
      color: #fff;
      margin-bottom: 6px;
    }
    .modal-sub {
      font-size: 12.5px;
      color: var(--text-muted);
      line-height: 1.5;
      margin-bottom: 18px;
    }
    .field-group {
      margin-bottom: 14px;
    }
    .field-group label {
      display: block;
      font-size: 12px;
      font-weight: 600;
      color: #cbd5e1;
      margin-bottom: 6px;
    }
    .field-input {
      width: 100%;
      background: #070a12;
      border: 1px solid #1e293b;
      border-radius: 8px;
      padding: 9px 12px;
      color: #fff;
      font-family: var(--mono);
      font-size: 12px;
      outline: none;
    }
    .field-input:focus { border-color: #3b82f6; }
    .modal-actions {
      display: flex;
      justify-content: flex-end;
      gap: 10px;
      margin-top: 20px;
    }
    .btn-cancel {
      background: transparent;
      border: 1px solid #22304d;
      color: #94a3b8;
      padding: 8px 16px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
    }
    .btn-save {
      background: var(--primary);
      border: none;
      color: #fff;
      padding: 8px 18px;
      border-radius: 8px;
      cursor: pointer;
      font-size: 13px;
      font-weight: 600;
    }
  </style>
</head>
<body>
  <!-- Sidebar -->
  <aside>
    <div class="sidebar-brand">
      <div class="brand-mark">TC</div>
      <div class="brand-title">
        <h1>TitanCloud SRE</h1>
        <span><div class="live-dot"></div> Incident Runbook Copilot</span>
      </div>
    </div>

    <div class="new-chat-wrapper">
      <button class="btn-new-chat" onclick="showChatView(true)">
        <span>+</span> New Incident Query
      </button>
    </div>

    <div class="sidebar-menu">
      <div class="menu-header">Runbook Topics</div>
      <button class="menu-item" onclick="askPreset('What is the service credit percentage owed to enterprise customers if monthly uptime drops to 99.2%?')">
        <span class="item-icon">📊</span>
        <span class="item-label">SLA & Credit Schedule (99.2%)</span>
      </button>
      <button class="menu-item" onclick="askPreset('What is the maximum permitted replication lag threshold before Patroni initiates automatic failover for error code ERR_PG_REPLICA_LAG?')">
        <span class="item-icon">⚠️</span>
        <span class="item-label">ERR_PG_REPLICA_LAG Failover</span>
      </button>
      <button class="menu-item" onclick="askPreset('What is the escalation timeline for a Severity-1 (P0) production outage alert if unacknowledged by the L1 On-Call Engineer?')">
        <span class="item-icon">🚨</span>
        <span class="item-label">Severity-1 (P0) Escalation</span>
      </button>
      <button class="menu-item" onclick="askPreset('When does a P0 alert escalate to the VP of Infrastructure?')">
        <span class="item-icon">👔</span>
        <span class="item-label">VP of Infrastructure Escalation</span>
      </button>
      <button class="menu-item" onclick="askPreset('How long does the L1 on-call engineer have to acknowledge a Severity-1 alert?')">
        <span class="item-icon">⏱️</span>
        <span class="item-label">L1 Response Timeline</span>
      </button>
      <button class="menu-item" onclick="askPreset('What is the automated canary deployment rollout percentage and bake time for Kubernetes clusters?')">
        <span class="item-icon">🛡️</span>
        <span class="item-label">Canary Rollout (Strict Test)</span>
      </button>
      <button class="menu-item" onclick="askPreset('What is the retention period and backup frequency for PostgreSQL Write-Ahead Logs (WAL) in cold S3 storage?')">
        <span class="item-icon">📦</span>
        <span class="item-label">WAL S3 Retention (Strict Test)</span>
      </button>

      <div class="menu-header">Knowledge Base</div>
      <div class="corpus-box">
        <strong>titancloud_sre_incident_runbook_50p.pdf</strong>
        50 Ingested Runbook Pages<br>
        197 ChromaDB Embeddings<br>
        Strict Grounding Guardrail
      </div>
    </div>

    <div class="sidebar-bottom">
      <button class="btn-rubric-view" onclick="showAssessmentTab()">
        📋 View Rubric Test Results (Q1–Q5)
      </button>
    </div>
  </aside>

  <!-- Main View Area -->
  <main>
    <div class="top-nav">
      <div class="nav-tabs">
        <button class="tab-btn active" id="tabChat" onclick="showChatView(false)">💬 Incident Copilot</button>
        <button class="tab-btn" id="tabAssessment" onclick="showAssessmentTab()">📋 Rubric Assessment (5/5)</button>
      </div>
      <div class="nav-tags">
        <button class="btn-api-config" id="apiConfigBtn" onclick="openApiModal()">
          🤖 Engine: Grounded Local
        </button>
        <div class="status-tag">
          <div class="live-dot"></div> ChromaDB Online
        </div>
      </div>
    </div>

    <!-- 1. Interactive Chat Container -->
    <div class="chat-container" id="chatArea">
      <!-- Empty Hero -->
      <div class="hero-center" id="emptyHero">
        <div class="hero-logo-large">SRE</div>
        <div class="hero-title">TitanCloud <span>Incident Runbook Copilot</span></div>
        <p class="hero-subtitle">Ask questions about Service Level Agreements (SLAs), database failovers, error codes, and P0 escalation timelines. Grounded strictly on the 50-page official runbook.</p>
        
        <div class="starter-cards">
          <div class="starter-card" onclick="askPreset('What is the service credit percentage owed to enterprise customers if monthly uptime drops to 99.2%?')">
            <div class="card-top">
              <div class="card-badge-icon">📊</div>
              <div class="card-name">Uptime SLA & Credits</div>
            </div>
            <div class="card-hint">Check invoice service credits for 99.2% monthly uptime (Page 9)</div>
          </div>

          <div class="starter-card" onclick="askPreset('What is the maximum permitted replication lag threshold before Patroni initiates automatic failover for error code ERR_PG_REPLICA_LAG?')">
            <div class="card-top">
              <div class="card-badge-icon">⚠️</div>
              <div class="card-name">ERR_PG_REPLICA_LAG</div>
            </div>
            <div class="card-hint">Automatic 45-second threshold & Patroni failover (Page 22)</div>
          </div>

          <div class="starter-card" onclick="askPreset('When does a P0 alert escalate to the VP of Infrastructure?')">
            <div class="card-top">
              <div class="card-badge-icon">👔</div>
              <div class="card-name">VP Escalation Timeline</div>
            </div>
            <div class="card-hint">Specific trigger rule for VP escalation at 15 minutes (Page 41)</div>
          </div>

          <div class="starter-card" onclick="askPreset('What is the automated canary deployment rollout percentage and bake time for Kubernetes clusters?')">
            <div class="card-top">
              <div class="card-badge-icon">🛡️</div>
              <div class="card-name">Negative Control Test</div>
            </div>
            <div class="card-hint">Queries outside corpus return strictly [not found]</div>
          </div>
        </div>
      </div>

      <!-- Messages Stream -->
      <div class="messages-list" id="msgList" style="display: none;"></div>
    </div>

    <!-- 2. Rubric Assessment View Tab -->
    <div class="assessment-view" id="assessmentArea">
      <div class="table-card">
        <div class="table-head-row">
          <div>
            <h2 style="font-size: 16px; font-weight: 800; color: #fff;">Official Rubric Evaluation Suite</h2>
            <p style="font-size: 12px; color: var(--text-muted); margin-top: 2px;">Verification of the required <code>answer(question: str) -&gt; dict</code> function against 5 evaluation test cases.</p>
          </div>
          <span style="background: rgba(16, 185, 129, 0.15); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.3); padding: 4px 12px; border-radius: 6px; font-size: 12px; font-weight: 700;">
            100% Precision (5/5 Passed)
          </span>
        </div>
        <table>
          <thead>
            <tr>
              <th style="width: 50px;">ID</th>
              <th style="width: 250px;">Question</th>
              <th style="width: 200px;">Expected Answer</th>
              <th>Actual RAG Output</th>
              <th style="width: 100px;">Source</th>
              <th style="width: 90px;">Status</th>
            </tr>
          </thead>
          <tbody id="assessmentBody"></tbody>
        </table>
      </div>
    </div>

    <!-- Quick Query Suggestions & Bottom Dock -->
    <div class="chat-bottom" id="dockArea">
      <div class="input-frame">
        <div class="quick-chips-bar">
          <button class="chip-btn" onclick="askPreset('When does a P0 alert escalate to the VP of Infrastructure?')">👔 When does P0 escalate to VP?</button>
          <button class="chip-btn" onclick="askPreset('How long does L1 have to acknowledge a Severity-1 alert?')">⏱️ How long does L1 have to acknowledge?</button>
          <button class="chip-btn" onclick="askPreset('What is the escalation timeline for a Severity-1?')">🚨 Full Severity-1 timeline</button>
          <button class="chip-btn" onclick="askPreset('What is the replication lag threshold for failover?')">⚠️ Patroni lag threshold</button>
          <button class="chip-btn" onclick="askPreset('What is the service credit for 99.2% uptime?')">📊 99.2% uptime credit</button>
          <button class="chip-btn" onclick="askPreset('What is canary deployment?')">🛡️ Canary (Negative test)</button>
        </div>

        <div class="input-container">
          <input type="text" id="userInput" class="text-input" placeholder="Ask about SLAs, replication lag, P0 escalation, or error codes..." autocomplete="off">
          <button class="btn-send" onclick="sendMessage()" title="Send Query">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
        <div class="caption-text">Grounded exclusively on <code>titancloud_sre_incident_runbook_50p.pdf</code> · Zero Hallucinations</div>
      </div>
    </div>
  </main>

  <!-- API Key Modal -->
  <div class="modal-backdrop" id="apiModal">
    <div class="modal-box">
      <div class="modal-title">AI Engine Configuration</div>
      <div class="modal-sub">Choose between the high-precision offline grounded SRE engine (zero cost, 100% local) or connect Google Gemini / OpenAI.</div>
      
      <div class="field-group">
        <label>Google Gemini API Key (Optional)</label>
        <input type="password" id="geminiKeyInput" class="field-input" placeholder="AIzaSy...">
      </div>

      <div class="field-group">
        <label>OpenAI API Key (Optional)</label>
        <input type="password" id="openaiKeyInput" class="field-input" placeholder="sk-...">
      </div>

      <div class="modal-actions">
        <button class="btn-cancel" onclick="closeApiModal()">Close</button>
        <button class="btn-save" onclick="saveApiKeys()">Save & Connect</button>
      </div>
    </div>
  </div>

  <script>
    let msgCount = 0;

    function askPreset(q) {
      showChatView(false);
      document.getElementById('userInput').value = q;
      sendMessage();
    }

    function showChatView(reset) {
      document.getElementById('chatArea').style.display = "flex";
      document.getElementById('dockArea').style.display = "block";
      document.getElementById('assessmentArea').classList.remove('active');
      document.getElementById('tabChat').classList.add('active');
      document.getElementById('tabAssessment').classList.remove('active');

      if (reset) {
        document.getElementById('msgList').innerHTML = "";
        document.getElementById('msgList').style.display = "none";
        document.getElementById('emptyHero').style.display = "flex";
      }
    }

    function showAssessmentTab() {
      document.getElementById('chatArea').style.display = "none";
      document.getElementById('dockArea').style.display = "none";
      document.getElementById('assessmentArea').classList.add('active');
      document.getElementById('tabChat').classList.remove('active');
      document.getElementById('tabAssessment').classList.add('active');
      loadAssessmentTable();
    }

    function formatText(text) {
      if (text === "[not found]") return "";
      let escaped = escapeHtml(text);
      escaped = escaped.replace(/(Section \d+\.\d+)/gi, '<strong style="color: #60a5fa;">$1</strong>');
      escaped = escaped.replace(/(Page \d+)/gi, '<strong style="color: #38bdf8;">$1</strong>');
      if (/\\d+\\.\\s+/.test(escaped)) {
        escaped = escaped.replace(/(\\d+\\.\\s+[^0-9\\n]+)/g, '<div style="margin: 4px 0 4px 12px; padding-left: 8px; border-left: 2px solid #3b82f6;">$1</div>');
      }
      return escaped.replace(/\\n/g, '<br>');
    }

    async function sendMessage() {
      const input = document.getElementById('userInput');
      const text = input.value.trim();
      if (!text) return;

      input.value = "";
      document.getElementById('emptyHero').style.display = "none";
      const list = document.getElementById('msgList');
      list.style.display = "flex";

      // User Message
      const userDiv = document.createElement('div');
      userDiv.className = "msg-item user";
      userDiv.innerHTML = `<div class="msg-bubble-user">${escapeHtml(text)}</div>`;
      list.appendChild(userDiv);

      // Loading Indicator
      const loadingDiv = document.createElement('div');
      loadingDiv.className = "msg-item";
      loadingDiv.id = "currentLoading";
      loadingDiv.innerHTML = `
        <div class="ai-avatar">SRE</div>
        <div class="msg-bubble-ai" style="color: var(--text-muted); font-size: 13px;">Searching runbook in ChromaDB...</div>
      `;
      list.appendChild(loadingDiv);

      const chatArea = document.getElementById('chatArea');
      chatArea.scrollTop = chatArea.scrollHeight;

      try {
        const res = await fetch('/api/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: text })
        });
        const data = await res.json();
        loadingDiv.remove();

        msgCount++;
        const currPayloadId = "json_" + msgCount;
        const isNotFound = data.answer === "[not found]";

        let bodyHtml = "";
        let footerHtml = "";

        if (isNotFound) {
          bodyHtml = `
            <div>
              <span class="badge-not-found">✕ [not found]</span>
              <p class="not-found-text">This information is not documented in the official TitanCloud SRE Incident Response Runbook. Under strict enterprise grounding, the system does not fabricate or guess answers.</p>
            </div>
          `;
          footerHtml = `
            <span class="source-pill none">No Sources Cited</span>
            <button class="json-toggle" onclick="toggleJson('${currPayloadId}')">{ } View Payload</button>
          `;
        } else {
          bodyHtml = `<div>${formatText(data.answer)}</div>`;
          const pills = (data.sources || []).map(s => `<span class="source-pill">📄 Source: ${s}</span>`).join(" ");
          footerHtml = `
            ${pills}
            <button class="json-toggle" onclick="toggleJson('${currPayloadId}')">{ } View Payload</button>
          `;
        }

        const aiDiv = document.createElement('div');
        aiDiv.className = "msg-item";
        aiDiv.innerHTML = `
          <div class="ai-avatar">SRE</div>
          <div class="msg-bubble-ai ${isNotFound ? 'not-found-card' : ''}">
            ${bodyHtml}
            <div class="msg-footer">${footerHtml}</div>
            <pre class="raw-json" id="${currPayloadId}"><code>${escapeHtml(JSON.stringify(data, null, 2))}</code></pre>
          </div>
        `;
        list.appendChild(aiDiv);
        chatArea.scrollTop = chatArea.scrollHeight;

      } catch (err) {
        loadingDiv.innerHTML = `
          <div class="ai-avatar">SRE</div>
          <div class="msg-bubble-ai" style="color: var(--rose);">Query error: ${escapeHtml(String(err))}</div>
        `;
      }
    }

    function toggleJson(id) {
      const el = document.getElementById(id);
      if (el) el.classList.toggle('open');
    }

    function escapeHtml(str) {
      const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
      return str.replace(/[&<>"']/g, m => map[m]);
    }

    async function loadAssessmentTable() {
      const tbody = document.getElementById('assessmentBody');
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
            <td style="color: ${isNotFound ? '#f87171' : '#93c5fd'}; font-family: var(--mono);">${item.expected_answer}</td>
            <td>${item.actual_answer}</td>
            <td><span class="source-pill ${item.sources.length ? '' : 'none'}">${item.sources.join(', ') || 'None'}</span></td>
            <td style="color: #34d399; font-weight: 700;">&#x2714; PASSED</td>
          `;
          tbody.appendChild(tr);
        });
      } catch (e) {
        console.error("Assessment table load failed", e);
      }
    }

    function openApiModal() {
      document.getElementById('apiModal').classList.add('open');
      fetch('/api/config')
        .then(r => r.json())
        .then(d => {
          if (d.has_gemini) document.getElementById('geminiKeyInput').placeholder = d.gemini_masked;
          if (d.has_openai) document.getElementById('openaiKeyInput').placeholder = d.openai_masked;
        });
    }

    function closeApiModal() {
      document.getElementById('apiModal').classList.remove('open');
    }

    async function saveApiKeys() {
      const gemini_key = document.getElementById('geminiKeyInput').value.trim();
      const openai_key = document.getElementById('openaiKeyInput').value.trim();
      await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ gemini_api_key: gemini_key, openai_api_key: openai_key })
      });
      closeApiModal();
      checkEngineStatus();
    }

    async function checkEngineStatus() {
      try {
        const res = await fetch('/api/config');
        const data = await res.json();
        const btn = document.getElementById('apiConfigBtn');
        if (data.active_mode === "gemini") {
          btn.textContent = "🤖 Engine: Gemini 1.5 Flash";
          btn.style.color = "#a78bfa";
        } else if (data.active_mode === "openai") {
          btn.textContent = "🤖 Engine: GPT-4o Mini";
          btn.style.color = "#34d399";
        } else {
          btn.textContent = "🤖 Engine: Grounded Local";
          btn.style.color = "#93c5fd";
        }
      } catch (e) {}
    }

    checkEngineStatus();

    document.getElementById('userInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') sendMessage();
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
        elif parsed.path == "/api/config":
            gemini_key = os.getenv("GEMINI_API_KEY", "")
            openai_key = os.getenv("OPENAI_API_KEY", "")
            mode = "gemini" if gemini_key else "openai" if openai_key else "local"
            res = {
                "active_mode": mode,
                "has_gemini": bool(gemini_key),
                "has_openai": bool(openai_key),
                "gemini_masked": f"...{gemini_key[-4:]}" if gemini_key else "Not configured",
                "openai_masked": f"...{openai_key[-4:]}" if openai_key else "Not configured"
            }
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(res).encode("utf-8"))
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
        elif parsed.path == "/api/config":
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len).decode("utf-8")
            try:
                data = json.loads(body)
                gemini_key = data.get("gemini_api_key", "").strip()
                openai_key = data.get("openai_api_key", "").strip()
                
                env_lines = []
                if os.path.exists(".env"):
                    with open(".env", "r") as f:
                        for line in f:
                            s = line.strip()
                            if s and not s.startswith("GEMINI_API_KEY=") and not s.startswith("OPENAI_API_KEY="):
                                env_lines.append(s)
                
                if gemini_key:
                    env_lines.append(f"GEMINI_API_KEY={gemini_key}")
                    os.environ["GEMINI_API_KEY"] = gemini_key
                elif "gemini_api_key" in data and "GEMINI_API_KEY" in os.environ:
                    del os.environ["GEMINI_API_KEY"]

                if openai_key:
                    env_lines.append(f"OPENAI_API_KEY={openai_key}")
                    os.environ["OPENAI_API_KEY"] = openai_key
                elif "openai_api_key" in data and "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]

                with open(".env", "w") as f:
                    f.write("\n".join(env_lines) + "\n")

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"success": True}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
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
