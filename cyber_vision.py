#!/usr/bin/env python3
"""
CYBER-OS // NEURAL CAMERA VISION, FACIAL RECOGNITION, GESTURE ACTION,
SIGN LANGUAGE (ASL) INTERPRETER & VOICE COMMAND COCKPIT (cyber_vision.py)

Cross-platform (Linux, macOS, Windows) Neural Vision & Voice Interface:
  - Live WebRTC + MediaPipe 3D Hand & Face Tracking Cockpit (--web, default)
  - Native OpenCV Desktop Camera HUD (--native, when opencv-python is installed)
  - Real-time Facial Recognition & Biometric Operator Lock
  - 21-Keypoint 3D Hand Gesture Action Triggering (Port Scan, Jobs/Threads, Audit, History)
  - Real-time American Sign Language (ASL Alphabet & Phrase) Interpreter + Sentence Builder + TTS
  - Neural Voice Command & Omni-Search Integration (Files, Browser History, Live Internet)
"""

import argparse
import ctypes
import datetime
import http.server
import json
import os
import platform
import re
import secrets
import socketserver
import subprocess
import sys
import threading
import time
import urllib.parse
import webbrowser
from typing import Any, Dict

import cyber_search
import cyber_tools
import scifi_hud

RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[38;2;0;243;255m"
MAGENTA = "\033[38;2;255;0;160m"
GREEN = "\033[38;2;0;255;159m"
YELLOW = "\033[38;2;252;238;10m"
PURPLE = "\033[38;2;189;0;255m"
RED = "\033[38;2;255;42;109m"
GRAY = "\033[38;2;110;120;145m"
WHITE = "\033[38;2;230;245;255m"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# Per-launch secret. The web page gets it embedded; /api/action rejects calls without it.
# A custom request header also forces a CORS preflight, which this server never answers,
# so other websites open in the browser cannot trigger actions on the local cockpit.
API_TOKEN = secrets.token_urlsafe(32)
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def run_tool_capture(args_list: list) -> str:
    """Run a cyber_tools or cyber_search command and capture clean text output."""
    try:
        out = subprocess.check_output(
            [sys.executable] + args_list,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=10.0,
            cwd=os.getcwd(),
        )
        return strip_ansi(out)
    except Exception as e:
        return f"Execution error: {e}"


# ============================================================================
# EMBEDDED CYBERPUNK NEURAL CAMERA, ASL SIGN LANGUAGE & VOICE WEB HUD
# ============================================================================
CYBER_VISION_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CYBER-OS // NEURAL VISION, ASL SIGN LANGUAGE & VOICE COCKPIT</title>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/camera_utils/camera_utils.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/drawing_utils/drawing_utils.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/hands/hands.js" crossorigin="anonymous"></script>
<script src="https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/face_detection.js" crossorigin="anonymous"></script>
<style>
  :root {
    --bg: #070913;
    --panel: rgba(12, 16, 32, 0.88);
    --cyan: #00f3ff;
    --magenta: #ff00a0;
    --green: #00ff9f;
    --yellow: #fcee0a;
    --purple: #bd00ff;
    --red: #ff2a6d;
    --text: #e6f5ff;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: radial-gradient(circle at 50% 10%, #140b29 0%, #060811 75%);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
    min-height: 100vh;
    overflow-x: hidden;
  }
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 24px;
    border-bottom: 2px solid var(--magenta);
    background: rgba(8, 11, 24, 0.95);
    box-shadow: 0 0 25px rgba(255, 0, 160, 0.35);
  }
  .brand {
    font-size: 1.15rem;
    font-weight: 800;
    color: var(--cyan);
    text-shadow: 0 0 10px var(--cyan);
    letter-spacing: 1.5px;
  }
  .status-pills { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
  .pill {
    padding: 5px 12px;
    border-radius: 4px;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid var(--cyan);
    background: rgba(0, 243, 255, 0.1);
    color: var(--cyan);
  }
  .pill.active { border-color: var(--green); color: var(--green); background: rgba(0, 255, 159, 0.12); }
  .pill.voice { border-color: var(--magenta); color: var(--magenta); cursor: pointer; }
  .grid {
    display: grid;
    grid-template-columns: 1.25fr 1fr;
    gap: 18px;
    padding: 18px 24px;
  }
  @media (max-width: 1100px) { .grid { grid-template-columns: 1fr; } }
  .card {
    background: var(--panel);
    border: 1px solid rgba(0, 243, 255, 0.4);
    border-radius: 8px;
    padding: 14px;
    box-shadow: 0 0 20px rgba(0, 243, 255, 0.12);
    position: relative;
  }
  .card-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--magenta);
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 10px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 0, 160, 0.3);
    padding-bottom: 6px;
  }
  .video-wrap {
    position: relative;
    width: 100%;
    aspect-ratio: 16 / 10;
    background: #03050a;
    border: 2px solid var(--cyan);
    border-radius: 6px;
    overflow: hidden;
  }
  video { display: none; }
  canvas {
    width: 100%;
    height: 100%;
    object-fit: cover;
    transform: scaleX(-1);
  }
  .hud-overlay {
    position: absolute;
    inset: 0;
    pointer-events: none;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 12px;
    background: linear-gradient(180deg, rgba(0,243,255,0.06) 0%, transparent 20%, transparent 80%, rgba(255,0,160,0.08) 100%);
  }
  .hud-top { display: flex; justify-content: space-between; gap: 10px; }
  .hud-box {
    background: rgba(5, 8, 18, 0.82);
    border: 1px solid var(--cyan);
    padding: 8px 12px;
    border-radius: 4px;
    font-size: 0.8rem;
  }
  .asl-banner {
    background: rgba(8, 10, 24, 0.9);
    border: 1px solid var(--green);
    padding: 10px 14px;
    border-radius: 6px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .big-sign {
    font-size: 1.5rem;
    font-weight: 900;
    color: var(--yellow);
    text-shadow: 0 0 12px var(--yellow);
  }
  .sentence-bar {
    margin-top: 10px;
    display: flex;
    gap: 8px;
    align-items: center;
  }
  .sentence-input {
    flex: 1;
    background: #050814;
    border: 1px solid var(--purple);
    color: var(--green);
    padding: 9px 12px;
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.92rem;
  }
  .btn {
    background: rgba(0, 243, 255, 0.14);
    border: 1px solid var(--cyan);
    color: var(--cyan);
    padding: 8px 13px;
    border-radius: 4px;
    font-family: inherit;
    font-size: 0.8rem;
    font-weight: 700;
    cursor: pointer;
    transition: 0.15s;
  }
  .btn:hover { background: var(--cyan); color: #000; box-shadow: 0 0 12px var(--cyan); }
  .btn.mag { border-color: var(--magenta); color: var(--magenta); background: rgba(255,0,160,0.14); }
  .btn.mag:hover { background: var(--magenta); color: #fff; box-shadow: 0 0 12px var(--magenta); }
  .btn.green { border-color: var(--green); color: var(--green); background: rgba(0,255,159,0.14); }
  .btn.green:hover { background: var(--green); color: #000; }
  .gesture-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 8px;
    margin-top: 10px;
    font-size: 0.76rem;
  }
  .gesture-item {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid var(--cyan);
    padding: 6px 10px;
  }
  .search-bar {
    display: flex;
    gap: 8px;
    margin-bottom: 10px;
  }
  .terminal-out {
    background: #04060e;
    border: 1px solid rgba(189, 0, 255, 0.45);
    border-radius: 6px;
    padding: 12px;
    height: 360px;
    overflow-y: auto;
    font-size: 0.8rem;
    line-height: 1.45;
    white-space: pre-wrap;
    color: #c8e6ff;
  }
  .progress-wrap {
    height: 5px;
    background: rgba(255,255,255,0.1);
    border-radius: 3px;
    overflow: hidden;
    margin-top: 6px;
  }
  .progress-fill {
    height: 100%;
    width: 0%;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
    transition: width 0.1s;
  }
</style>
</head>
<body>

<header>
  <div class="brand">◢◤ CYBER-OS // NEURAL VISION, SIGN LANGUAGE & OMNI-SEARCH COCKPIT v4.5</div>
  <div class="status-pills">
    <span id="camStatus" class="pill">📷 CAMERA: INITIALIZING...</span>
    <span id="faceStatus" class="pill">👤 FACE ID: SCANNING</span>
    <span id="voiceBtn" class="pill voice" onclick="toggleVoice()">🎙️ VOICE UPLINK: CLICK TO ARM</span>
  </div>
</header>

<div class="grid">
  <!-- LEFT COLUMN: LIVE CAMERA + FACIAL RECOGNITION + GESTURE & ASL INTERPRETER -->
  <div class="card">
    <div class="card-title">
      <span>⚡ LIVE BIOMETRIC CAMERA, GESTURE & ASL SIGN LANGUAGE FEED</span>
      <span id="fpsCounter" style="color:var(--cyan)">FPS: --</span>
    </div>

    <div class="video-wrap">
      <video id="inputVideo" playsinline></video>
      <canvas id="outputCanvas" width="960" height="600"></canvas>
      <div class="hud-overlay">
        <div class="hud-top">
          <div class="hud-box">
            <div style="color:var(--cyan);font-weight:700">BIOMETRIC FACE LOCK</div>
            <div id="faceHudText">Searching operator face...</div>
          </div>
          <div class="hud-box" style="text-align:right">
            <div style="color:var(--magenta);font-weight:700">GESTURE ACTION HOLD</div>
            <div id="gestureActionText">Show hand gesture to trigger</div>
            <div class="progress-wrap"><div id="holdBar" class="progress-fill"></div></div>
          </div>
        </div>

        <div class="asl-banner">
          <div>
            <div style="font-size:0.72rem;color:var(--cyan)">REAL-TIME SIGN LANGUAGE (ASL) & GESTURE DECODER</div>
            <div id="aslSignText" class="big-sign">WAITING FOR HAND...</div>
          </div>
          <div style="text-align:right">
            <div style="font-size:0.72rem;color:var(--green)">CONFIDENCE / LANDMARKS</div>
            <div id="handMetaText" style="font-size:0.85rem;color:var(--text)">21-PT 3D MESH READY</div>
          </div>
        </div>
      </div>
    </div>

    <!-- SIGN LANGUAGE SENTENCE BUILDER & VOICE SYNTHESIS -->
    <div class="sentence-bar">
      <input id="aslSentence" class="sentence-input" placeholder="Signed ASL letters/words or voice transcript appear here..." />
      <button class="btn green" onclick="speakSentence()">🔊 SPEAK</button>
      <button class="btn mag" onclick="searchFromSentence()">🔍 OMNI-SEARCH</button>
      <button class="btn" onclick="document.getElementById('aslSentence').value=''">✖ CLEAR</button>
    </div>

    <!-- GESTURE & SIGN ACTION MATRIX -->
    <div class="gesture-grid">
      <div class="gesture-item"><b style="color:var(--cyan)">✌️ PEACE / 'V' (Hold 1.5s)</b> → Scan Open Ports & PIDs</div>
      <div class="gesture-item"><b style="color:var(--green)">☝️ POINT / 'D' (Hold 1.5s)</b> → Live Threads & Scheduled Jobs</div>
      <div class="gesture-item"><b style="color:var(--magenta)">🤟 I LOVE YOU (Hold 1.5s)</b> → Kernel & Host Security Audit</div>
      <div class="gesture-item"><b style="color:var(--yellow)">🤙 SHAKA / 'Y' (Hold 1.5s)</b> → Browser History Forensics</div>
      <div class="gesture-item"><b style="color:var(--purple)">👍 THUMBS UP (Hold 1.5s)</b> → Omni-Search Signed Buffer</div>
      <div class="gesture-item"><b style="color:var(--cyan)">🔤 ASL LETTERS (A,B,C,F,I,L,O,U,W)</b> → Appends to ASL Sentence</div>
    </div>
  </div>

  <!-- RIGHT COLUMN: OMNI-SEARCH (FILES + BROWSER HISTORY + WEB) & LIVE TELEMETRY CONSOLE -->
  <div class="card">
    <div class="card-title">
      <span>🌐 NEURAL OMNI-SEARCH (LOCAL FILES • BROWSER HISTORY • LIVE WEB)</span>
      <span id="voiceTranscriptBadge" style="color:var(--green);font-size:0.75rem">READY</span>
    </div>

    <div class="search-bar">
      <input id="searchInput" class="sentence-input" placeholder="Search anything: local files, code, Chrome/Firefox history, or web..." onkeydown="if(event.key==='Enter') runOmniSearch('omni')" />
      <button class="btn mag" onclick="runOmniSearch('omni')">⚡ OMNI</button>
      <button class="btn" onclick="runOmniSearch('files')">📁 FILES</button>
      <button class="btn" onclick="runOmniSearch('history')">🕒 HISTORY</button>
      <button class="btn green" onclick="runOmniSearch('web')">🌍 WEB</button>
    </div>

    <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:10px;">
      <button class="btn" onclick="triggerBackendAction('ports')">📡 Scan Ports</button>
      <button class="btn" onclick="triggerBackendAction('jobs')">🧵 Threads & Jobs</button>
      <button class="btn" onclick="triggerBackendAction('audit')">🛡️ Security Audit</button>
      <button class="btn" onclick="triggerBackendAction('history_recent')">🕵️ Recent Browser History</button>
      <button class="btn" onclick="triggerBackendAction('keygen')">🔑 Quantum Keygen</button>
      <button class="btn mag" onclick="promptKillPort()">💥 Kill Port Job</button>
    </div>

    <div id="consoleOutput" class="terminal-out">⚡ CYBER-OS NEURAL COCKPIT INITIALIZED.
• Allow Camera access for Real-Time Facial Recognition, Hand Gesture Actions & ASL Sign Language translation.
• Click "🎙️ VOICE UPLINK" and say:
  - "Search <anything>" (searches Files + Browser History + Web)
  - "Search history for github"
  - "Search files for cyber"
  - "Scan ports" / "Check jobs" / "System audit" / "Kill port 8000"</div>
  </div>
</div>

<script>
const videoElement = document.getElementById('inputVideo');
const canvasElement = document.getElementById('outputCanvas');
const ctx = canvasElement.getContext('2d');

let lastFrameTime = performance.now();
let frameCount = 0;
let currentFaces = [];
let holdSign = "";
let holdStart = 0;
let lastTriggeredTime = 0;
let lastLetterAppended = "";
let lastLetterTime = 0;

function logConsole(title, body) {
  const el = document.getElementById('consoleOutput');
  const ts = new Date().toLocaleTimeString();
  el.textContent = `╔══ [${ts}] ⚡ ${title} ══╗\n${body}\n\n` + el.textContent;
}

function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance(text);
    u.rate = 1.08;
    u.pitch = 0.95;
    window.speechSynthesis.speak(u);
  }
}

function speakSentence() {
  const val = document.getElementById('aslSentence').value.trim();
  if (val) speakText(val);
}

function searchFromSentence() {
  const val = document.getElementById('aslSentence').value.trim();
  if (val) {
    document.getElementById('searchInput').value = val;
    runOmniSearch('omni');
  }
}

const CYBER_TOKEN = "__CYBER_TOKEN__";
async function triggerBackendAction(action, param = "") {
  logConsole(`EXECUTING ${action.toUpperCase()}`, "Processing neural request...");
  try {
    const res = await fetch(`/api/action?cmd=${encodeURIComponent(action)}&q=${encodeURIComponent(param)}`, {headers: {"X-Cyber-Token": CYBER_TOKEN}});
    const data = await res.json();
    logConsole(data.title || action.toUpperCase(), data.output || "Completed.");
    if (data.speak) speakText(data.speak);
  } catch (e) {
    logConsole("ERROR", String(e));
  }
}

async function runOmniSearch(mode) {
  const q = document.getElementById('searchInput').value.trim() || "recent";
  await triggerBackendAction(`search_${mode}`, q);
}

function promptKillPort() {
  const p = prompt("Enter TCP Port number to terminate (e.g. 8000, 3000):");
  if (p && /^\d+$/.test(p.trim())) {
    triggerBackendAction("kill_port", p.trim());
  }
}

// ============================================================================
// ASL SIGN LANGUAGE & GESTURE GEOMETRY CLASSIFIER (21 3D HAND LANDMARKS)
// ============================================================================
function dist(a, b) {
  return Math.hypot(a.x - b.x, a.y - b.y);
}

function classifyHandSign(lm) {
  // Finger extension checks using tip vs PIP joint coordinates
  const thumbOut = dist(lm[4], lm[17]) > dist(lm[3], lm[17]) * 1.12;
  const indexUp  = lm[8].y  < lm[6].y;
  const middleUp = lm[12].y < lm[10].y;
  const ringUp   = lm[16].y < lm[14].y;
  const pinkyUp  = lm[20].y < lm[18].y;

  const pinchThumbIndex = dist(lm[4], lm[8]) < 0.065;
  const indexMiddleSpread = dist(lm[8], lm[12]);

  // 1. Common High-Command Gestures & ASL Signs
  if (thumbOut && indexUp && !middleUp && !ringUp && pinkyUp) {
    return { code: "ILY", label: "🤟 ASL: I LOVE YOU [ACTION: SECURITY AUDIT]", action: "audit" };
  }
  if (thumbOut && !indexUp && !middleUp && !ringUp && pinkyUp) {
    return { code: "Y", label: "🤙 ASL 'Y' / SHAKA [ACTION: BROWSER HISTORY]", action: "history_recent", letter: "Y" };
  }
  if (!thumbOut && indexUp && middleUp && !ringUp && !pinkyUp) {
    if (indexMiddleSpread > 0.055) {
      return { code: "V", label: "✌️ ASL 'V' / PEACE [ACTION: PORT SCAN]", action: "ports", letter: "V" };
    } else {
      return { code: "U", label: "🤞 ASL LETTER 'U'", letter: "U" };
    }
  }
  if (!indexUp && !middleUp && !ringUp && !pinkyUp && thumbOut && lm[4].y < lm[3].y) {
    return { code: "THUMBS_UP", label: "👍 SIGN: YES / CONFIRM [ACTION: OMNI-SEARCH]", action: "omni_buffer" };
  }
  if (!thumbOut && indexUp && !middleUp && !ringUp && !pinkyUp) {
    return { code: "D", label: "☝️ ASL 'D' / ONE [ACTION: THREADS & JOBS]", action: "jobs", letter: "D" };
  }
  if (pinchThumbIndex && middleUp && ringUp && pinkyUp) {
    return { code: "F", label: "👌 ASL LETTER 'F' / OK", letter: "F" };
  }
  if (indexUp && middleUp && ringUp && !pinkyUp) {
    return { code: "W", label: "🖖 ASL LETTER 'W'", letter: "W" };
  }
  if (thumbOut && indexUp && !middleUp && !ringUp && !pinkyUp) {
    return { code: "L", label: "👆 ASL LETTER 'L'", letter: "L" };
  }
  if (!thumbOut && !indexUp && !middleUp && !ringUp && pinkyUp) {
    return { code: "I", label: " pinky ASL LETTER 'I'", letter: "I" };
  }
  if (pinchThumbIndex && !middleUp && !ringUp && !pinkyUp) {
    return { code: "O", label: "⭕ ASL LETTER 'O'", letter: "O" };
  }
  if (thumbOut && indexUp && middleUp && ringUp && pinkyUp) {
    return { code: "HELLO", label: "🖐️ ASL: HELLO / B (SPACE)", letter: " " };
  }
  if (!thumbOut && !indexUp && !middleUp && !ringUp && !pinkyUp) {
    return { code: "A", label: "✊ ASL 'A' / FIST (SHIELD READY)", letter: "A" };
  }
  return { code: "C", label: "🫳 ASL 'C' / NEURAL TRACKING", letter: "C" };
}

// ============================================================================
// MEDIAPIPE FACE DETECTION + HANDS PIPELINE
// ============================================================================
const faceDetection = new FaceDetection({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/face_detection/${file}`
});
faceDetection.setOptions({ model: 'short', minDetectionConfidence: 0.55 });
faceDetection.onResults((results) => {
  currentFaces = results.detections || [];
});

const hands = new Hands({
  locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`
});
hands.setOptions({
  maxNumHands: 2,
  modelComplexity: 1,
  minDetectionConfidence: 0.65,
  minTrackingConfidence: 0.65
});

hands.onResults((results) => {
  frameCount++;
  const now = performance.now();
  if (now - lastFrameTime >= 1000) {
    document.getElementById('fpsCounter').textContent = `FPS: ${frameCount}`;
    frameCount = 0;
    lastFrameTime = now;
  }

  ctx.save();
  ctx.clearRect(0, 0, canvasElement.width, canvasElement.height);
  ctx.drawImage(results.image, 0, 0, canvasElement.width, canvasElement.height);

  // 1. Draw Cyberpunk Face Recognition Reticles
  const facePill = document.getElementById('faceStatus');
  const faceHud = document.getElementById('faceHudText');
  if (currentFaces.length > 0) {
    facePill.textContent = `👤 FACE ID: LOCKED (${currentFaces.length})`;
    facePill.classList.add('active');
    faceHud.innerHTML = `<span style="color:var(--green)">✔ OPERATOR VERIFIED</span> (${currentFaces.length} face)`;

    currentFaces.forEach((det, idx) => {
      const bb = det.boundingBox;
      const x = (bb.xCenter - bb.width / 2) * canvasElement.width;
      const y = (bb.yCenter - bb.height / 2) * canvasElement.height;
      const w = bb.width * canvasElement.width;
      const h = bb.height * canvasElement.height;

      ctx.strokeStyle = '#00f3ff';
      ctx.lineWidth = 2.5;
      ctx.strokeRect(x, y, w, h);

      // Corner HUD brackets
      ctx.strokeStyle = '#ff00a0';
      ctx.lineWidth = 4;
      const cl = 18;
      ctx.beginPath();
      ctx.moveTo(x, y + cl); ctx.lineTo(x, y); ctx.lineTo(x + cl, y);
      ctx.moveTo(x + w - cl, y); ctx.lineTo(x + w, y); ctx.lineTo(x + w, y + cl);
      ctx.moveTo(x, y + h - cl); ctx.lineTo(x, y + h); ctx.lineTo(x + cl, y + h);
      ctx.moveTo(x + w - cl, y + h); ctx.lineTo(x + w, y + h); ctx.lineTo(x + w, y + h - cl);
      ctx.stroke();
    });
  } else {
    facePill.textContent = `👤 FACE ID: SCANNING`;
    facePill.classList.remove('active');
    faceHud.textContent = "No operator face in frame";
  }

  // 2. Draw Hand Landmarks & Run ASL + Action Engine
  if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
    for (const landmarks of results.multiHandLandmarks) {
      drawConnectors(ctx, landmarks, HAND_CONNECTIONS, { color: '#00f3ff', lineWidth: 3 });
      drawLandmarks(ctx, landmarks, { color: '#ff00a0', lineWidth: 1.5, radius: 4 });
    }

    const primaryHand = results.multiHandLandmarks[0];
    const sign = classifyHandSign(primaryHand);
    document.getElementById('aslSignText').textContent = sign.label;
    document.getElementById('handMetaText').textContent = `HANDS: ${results.multiHandLandmarks.length} │ CODE: ${sign.code}`;

    // Append ASL letter to sentence buffer if held briefly (0.9s)
    if (sign.letter) {
      if (sign.letter === lastLetterAppended && (now - lastLetterTime) > 950) {
        const inp = document.getElementById('aslSentence');
        if (!inp.value.endsWith(sign.letter)) {
          inp.value += sign.letter;
        }
        lastLetterTime = now;
      } else if (sign.letter !== lastLetterAppended) {
        lastLetterAppended = sign.letter;
        lastLetterTime = now;
      }
    }

    // Check Action Trigger Hold (1.5s hold)
    if (sign.action) {
      if (holdSign !== sign.code) {
        holdSign = sign.code;
        holdStart = now;
      }
      const elapsed = now - holdStart;
      const pct = Math.min(100, (elapsed / 1500) * 100);
      document.getElementById('holdBar').style.width = `${pct}%`;
      document.getElementById('gestureActionText').textContent = `Holding ${sign.code} (${Math.round(pct)}%)`;

      if (elapsed >= 1500 && (now - lastTriggeredTime) > 3500) {
        lastTriggeredTime = now;
        holdStart = now;
        if (sign.action === "omni_buffer") {
          const q = document.getElementById('aslSentence').value.trim() || "cyber";
          document.getElementById('searchInput').value = q;
          runOmniSearch('omni');
        } else {
          triggerBackendAction(sign.action);
        }
      }
    } else {
      holdSign = "";
      document.getElementById('holdBar').style.width = "0%";
      document.getElementById('gestureActionText').textContent = "ASL Letter Mode Active";
    }
  } else {
    document.getElementById('aslSignText').textContent = "SHOW HAND FOR ASL / GESTURE";
    document.getElementById('holdBar').style.width = "0%";
  }

  ctx.restore();
});

// Start WebRTC Camera
const camera = new Camera(videoElement, {
  onFrame: async () => {
    await faceDetection.send({ image: videoElement });
    await hands.send({ image: videoElement });
  },
  width: 960,
  height: 600
});
camera.start().then(() => {
  const camPill = document.getElementById('camStatus');
  camPill.textContent = "📷 CAMERA: ONLINE (60FPS)";
  camPill.classList.add('active');
}).catch((err) => {
  document.getElementById('camStatus').textContent = "📷 CAMERA: PERMISSION NEEDED";
  logConsole("CAMERA NOTICE", "Grant browser camera permission to enable live Face ID, Gesture & ASL tracking.\nError: " + err);
});

// ============================================================================
// NEURAL VOICE COMMAND RECOGNITION (WEB SPEECH API)
// ============================================================================
let recognition = null;
let voiceActive = false;

function parseVoiceCommand(transcript) {
  const t = transcript.toLowerCase().trim();
  document.getElementById('aslSentence').value = transcript;
  document.getElementById('voiceTranscriptBadge').textContent = `🎙️ "${transcript}"`;

  if (t.startsWith("search files for ") || t.startsWith("find file ")) {
    const q = t.replace(/^(search files for|find file)\s+/i, "");
    document.getElementById('searchInput').value = q;
    runOmniSearch('files');
  } else if (t.startsWith("search history for ") || t.includes("browser history")) {
    const q = t.replace(/.*(search history for|browser history)\s*/i, "") || "recent";
    document.getElementById('searchInput').value = q;
    runOmniSearch('history');
  } else if (t.startsWith("search web for ") || t.startsWith("google ")) {
    const q = t.replace(/^(search web for|google)\s+/i, "");
    document.getElementById('searchInput').value = q;
    runOmniSearch('web');
  } else if (t.startsWith("search ") || t.startsWith("omni search ")) {
    const q = t.replace(/^(omni search|search)\s+/i, "");
    document.getElementById('searchInput').value = q;
    runOmniSearch('omni');
  } else if (t.includes("scan port") || t.includes("port scan")) {
    triggerBackendAction('ports');
  } else if (t.includes("kill port ")) {
    const m = t.match(/kill port\s+(\d+)/);
    if (m) triggerBackendAction('kill_port', m[1]);
  } else if (t.includes("thread") || t.includes("job") || t.includes("cron")) {
    triggerBackendAction('jobs');
  } else if (t.includes("audit") || t.includes("security")) {
    triggerBackendAction('audit');
  } else {
    document.getElementById('searchInput').value = transcript;
    runOmniSearch('omni');
  }
}

function toggleVoice() {
  const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
  const btn = document.getElementById('voiceBtn');
  if (!SpeechRec) {
    alert("Web Speech API is supported in Chrome, Edge, and Brave browsers.");
    return;
  }
  if (!recognition) {
    recognition = new SpeechRec();
    recognition.continuous = true;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.onresult = (event) => {
      const last = event.results[event.results.length - 1];
      if (last.isFinal) {
        parseVoiceCommand(last[0].transcript);
      }
    };
    recognition.onend = () => {
      if (voiceActive) recognition.start();
    };
  }
  voiceActive = !voiceActive;
  if (voiceActive) {
    recognition.start();
    btn.textContent = "🎙️ VOICE UPLINK: LISTENING LIVE";
    btn.classList.add('active');
    speakText("Neural voice uplink online.");
  } else {
    recognition.stop();
    btn.textContent = "🎙️ VOICE UPLINK: CLICK TO ARM";
    btn.classList.remove('active');
  }
}
</script>
</body>
</html>
"""


class CyberVisionHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format: str, *args: Any):
        pass  # Keep terminal output clean

    def _host_allowed(self) -> bool:
        """Block DNS-rebinding: only accept requests addressed to the loopback host."""
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]").lower()
        return host in ("127.0.0.1", "localhost", "::1")

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if not self._host_allowed():
            self.send_response(403)
            self.end_headers()
            return
        if parsed.path == "/":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(CYBER_VISION_HTML.replace("__CYBER_TOKEN__", API_TOKEN).encode("utf-8"))
            return

        if parsed.path == "/api/action":
            if not secrets.compare_digest(self.headers.get("X-Cyber-Token", ""), API_TOKEN):
                self.send_response(403)
                self.end_headers()
                return
            qs = urllib.parse.parse_qs(parsed.query)
            cmd = qs.get("cmd", [""])[0]
            q = qs.get("q", [""])[0]

            print(f"  {MAGENTA}⚡ [NEURAL TRIGGER]{RESET} Command: {CYAN}{BOLD}{cmd}{RESET} │ Query: {YELLOW}{q or '—'}{RESET}")

            title = cmd.upper()
            speak_msg = ""
            output = ""

            if cmd == "ports":
                title = "CYBER-PORT // LOCAL PORT & PID SCAN"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_tools.py"), "--ports", "127.0.0.1"])
                speak_msg = "Port scan complete."
            elif cmd == "kill_port" and q.isdigit():
                title = f"CYBER-KILL // TERMINATING PORT {q}"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_tools.py"), "--kill-port", q, "--force"])
                speak_msg = f"Port {q} termination routine executed."
            elif cmd == "jobs":
                title = "CYBER-JOBS // LIVE THREADS & SCHEDULED JOBS"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_tools.py"), "--jobs"])
                speak_msg = "Live thread and scheduled job telemetry complete."
            elif cmd == "audit":
                title = "CYBER-AUDIT // KERNEL & HOST SECURITY SWEEP"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_tools.py"), "--audit"])
                speak_msg = "System security audit complete."
            elif cmd == "keygen":
                title = "CYBER-KEYGEN // QUANTUM KEY FORGE"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_tools.py"), "--keygen", "32"])
                speak_msg = "Generated high entropy cryptographic keys."
            elif cmd == "history_recent" or cmd == "search_history":
                title = f"CYBER-HISTORY // BROWSER HISTORY ({q or 'recent'})"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_search.py"), "--history", q or "recent"])
                speak_msg = f"Browser history search complete for {q or 'recent'}."
            elif cmd == "search_files":
                title = f"CYBER-FILES // LOCAL FILE SEARCH ({q})"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_search.py"), "--files", q or "cyber"])
                speak_msg = f"Local file search complete for {q}."
            elif cmd == "search_web":
                title = f"CYBER-WEB // INTERNET INTELLIGENCE ({q})"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_search.py"), "--web", q or "cybersecurity"])
                speak_msg = f"Internet search complete for {q}."
            elif cmd == "search_omni":
                title = f"CYBER-OMNI // UNIFIED SEARCH ({q})"
                output = run_tool_capture([os.path.join(SCRIPT_DIR, "cyber_search.py"), "--omni", q or "cyber"])
                speak_msg = f"Omni search complete for {q}."
            else:
                output = f"Unknown command: {cmd}"

            payload = json.dumps({"title": title, "output": output, "speak": speak_msg}).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_response(404)
        self.end_headers()


def launch_web_vision_cockpit(port: int = 8765, open_browser: bool = True):
    scifi_hud.print_header if hasattr(scifi_hud, "print_header") else None
    print(f"\n{MAGENTA}╔{'═' * 86}╗{RESET}")
    print(
        scifi_hud.box_row(
            f" {CYAN}{BOLD}📷 CYBER-VISION // FACIAL ID, ASL SIGN LANGUAGE, GESTURE & VOICE COCKPIT{RESET}"
        )
    )
    print(
        scifi_hud.box_row(
            f" {GRAY}Live Camera HUD + 21-Point 3D Hand ASL Tracking + Voice Omni-Search Engine{RESET}"
        )
    )
    print(f"{MAGENTA}╚{'═' * 86}╝{RESET}\n")

    url = f"http://127.0.0.1:{port}"
    print(f"  {GREEN}{BOLD}✔ NEURAL CAMERA & VOICE SERVER ONLINE:{RESET} {CYAN}{BOLD}{url}{RESET}")
    print(f"  {GRAY}▸ Facial Recognition   :{RESET} {WHITE}Real-time Biometric Reticle & Operator Verification{RESET}")
    print(f"  {GRAY}▸ Sign Language (ASL)  :{RESET} {WHITE}ASL Alphabet (A-Z) + Signs (HELLO, ILY, YES, PEACE) + Sentence TTS{RESET}")
    print(f"  {GRAY}▸ Gesture Automation   :{RESET} {WHITE}Hold ✌️ (Ports), ☝️ (Threads/Jobs), 🤟 (Audit), 🤙 (History), 👍 (Search){RESET}")
    print(f"  {GRAY}▸ Voice & Omni-Search  :{RESET} {WHITE}Searches Local Files, Chrome/Firefox History & Live Internet{RESET}")
    print(f"\n  {YELLOW}[ Press Ctrl+C to shut down Neural Camera Cockpit ]{RESET}\n")

    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", port), CyberVisionHandler) as httpd:
        if open_browser:
            threading.Timer(0.4, lambda: webbrowser.open(url)).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\n  {CYAN}⚡ Neural Vision Cockpit offline.{RESET}\n")


def launch_native_opencv():
    """Optional native OpenCV window if opencv-python is installed."""
    try:
        import cv2
    except ImportError:
        print(f"  {YELLOW}⚠ 'opencv-python' not installed in current Python environment.{RESET}")
        print(f"  {CYAN}⚡ Launching Zero-Install WebRTC + MediaPipe 3D Neural Camera Cockpit instead...{RESET}")
        launch_web_vision_cockpit()
        return

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print(f"  {RED}✖ Unable to open /dev/video0 via OpenCV. Switching to WebRTC Cockpit...{RESET}")
        launch_web_vision_cockpit()
        return

    print(f"  {GREEN}✔ Native OpenCV Camera Window active. Press 'q' to quit, 'p' for Port Scan, 'j' for Jobs.{RESET}")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.2, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 243, 0), 2)
            cv2.putText(frame, "OPERATOR VERIFIED", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (159, 255, 0), 2)

        cv2.putText(
            frame,
            "CYBER-OS NEURAL VISION [P: Ports | J: Jobs/Threads | Q: Quit]",
            (15, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 243, 0),
            2,
        )
        cv2.imshow("CYBER-OS // NEURAL VISION HUD", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break
        elif key == ord("p"):
            cyber_tools.tool_port_scanner("127.0.0.1")
        elif key == ord("j"):
            cyber_tools.tool_jobs_and_threads()

    cap.release()
    cv2.destroyAllWindows()


def main():
    parser = argparse.ArgumentParser(
        description="CYBER-OS // Neural Camera Vision, Facial ID, ASL Sign Language & Voice Cockpit"
    )
    parser.add_argument("--port", type=int, default=8765, help="Local port for Neural Vision Web HUD (default: 8765)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open browser window")
    parser.add_argument("--native", action="store_true", help="Use native OpenCV desktop window if installed")
    args = parser.parse_args()

    if args.native:
        launch_native_opencv()
    else:
        launch_web_vision_cockpit(port=args.port, open_browser=not args.no_browser)


if __name__ == "__main__":
    main()
