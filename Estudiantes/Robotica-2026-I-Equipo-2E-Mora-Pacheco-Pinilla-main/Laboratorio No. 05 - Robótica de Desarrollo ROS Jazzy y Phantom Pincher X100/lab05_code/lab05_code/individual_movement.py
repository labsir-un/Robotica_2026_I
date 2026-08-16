#!/usr/bin/env python3
import json
import math
import os
import queue
import signal
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from functools import partial
import shutil
from urllib.parse import urlparse

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy, HistoryPolicy
from sensor_msgs.msg import JointState
from std_srvs.srv import Trigger
from visualization_msgs.msg import Marker
from geometry_msgs.msg import Point
import tf2_ros
from tf2_ros.buffer import Buffer
from tf2_ros.transform_listener import TransformListener

try:
    import yaml
except ImportError:
    yaml = None

DEG = math.pi / 180.0

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']
JOINT_LABELS = {'waist': 'Base', 'shoulder': 'Hombro', 'elbow': 'Codo', 'wrist': 'Muñeca', 'gripper': 'Pinza'}

JOINT_LIMITS_DEG = {
    'waist':    (-150, 150),
    'shoulder': (-150, 150),
    'elbow':    (-150, 150),
    'wrist':    (-150, 150),
    'gripper':  (-90, 90),
}

PRESETS_DEG = {
    'waist':    [-90, 0, 45, 90, -45],
    'shoulder': [-90, 0, 45, 90, -45],
    'elbow':    [-90, 0, 45, 90, -45],
    'wrist':    [-90, 0, 45, 90, -45],
    'gripper':  [-30, 0, 30, 60, -60],
}

HOME_POS = {name: 0.0 for name in JOINT_NAMES}

POSES_FILE = os.path.expanduser('~/.ros/teach_repeat_poses.yaml')

command_queue = queue.Queue()
current_state = {name: 0.0 for name in JOINT_NAMES}
state_lock = threading.Lock()

poses = []
poses_lock = threading.Lock()

playback_running = False
playback_stop = threading.Event()
playback_target = {'playing': False, 'current': 0, 'total': 0, 'pose_name': '—'}

DANCE_MP3 = '/home/dvn-portatil/ros2_jazzy/la canción de pedro PEDRO - Raffaella Carrà, Jaxomy, Agatino Romero (Remix) [sub. español] - Marinosaurio (128k).mp3'
_dance_cache = None

HTML = r'''<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
<meta http-equiv="Pragma" content="no-cache">
<meta http-equiv="Expires" content="0">
<title>Lab 05 &mdash; Control Phantom X</title>
<style>
  :root {
    --bg: #f5f6f8; --surface: #ffffff; --border: #dce0e6;
    --border-light: #e9ecf0; --text: #1a202c; --text-muted: #88909c;
    --primary: #1a365d; --accent: #2b6cb0; --success: #2f855a;
    --danger: #c53030; --radius: 7px;
    --white: #ffffff;
  }
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: 'Inter', 'Segoe UI', system-ui, sans-serif;
    background: var(--bg); color: var(--text);
    display: flex; justify-content: center; padding: 16px; line-height: 1.4;
  }
  .app {
    width: 100%; max-width: 1200px;
    background: var(--surface); border-radius: var(--radius);
    box-shadow: 0 4px 16px rgba(0,0,0,.07); overflow: hidden;
  }
  .header {
    padding: 14px 24px 12px;
    border-bottom: 1px solid var(--border-light);
    display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;
  }
  .header h1 { font-size: 1rem; font-weight: 700; color: var(--primary); }
  .header-right {
    display: flex; align-items: center; gap: 18px; font-size: .73rem; color: var(--text-muted);
  }
  .dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; margin-right: 4px; }
  .dot.green { background: var(--success); }
  .dot.amber { background: #d69e2e; }
  .dot.red { background: var(--danger); }

  .tabs { display: flex; border-bottom: 2px solid var(--border-light); padding: 0 24px; }
  .tab { padding: 10px 18px; font-size: .8rem; font-weight: 500; cursor: pointer; border: none; background: none; color: var(--text-muted); font-family: inherit; border-bottom: 2px solid transparent; margin-bottom: -2px; transition: all .12s; }
  .tab:hover { color: var(--text); }
  .tab.active { color: var(--primary); border-bottom-color: var(--primary); }
  .tab-content { display: none; }
  .tab-content.active { display: block; }

  .body { padding: 12px 24px 16px; }
  .joint-card {
    border: 1px solid var(--border-light);
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 8px;
  }
  .joint-top {
    display: flex; align-items: center; gap: 12px;
  }
  .joint-label {
    min-width: 80px; font-size: .85rem; font-weight: 600; color: var(--text);
  }
  .joint-label .en { font-weight: 400; color: var(--text-muted); font-size: .63rem; display: block; }
  .joint-input {
    width: 76px;
    background: var(--white);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 5px 7px;
    color: var(--text);
    font-size: .85rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    text-align: center;
    outline: none;
  }
  .joint-input:focus { border-color: var(--accent); }
  .joint-cur {
    min-width: 58px; font-size: .85rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    color: var(--accent); text-align: right; font-weight: 500;
  }
  .slider-el {
    flex: 1; -webkit-appearance: none; appearance: none;
    height: 10px; background: var(--border); border-radius: 99px;
    outline: none; cursor: pointer; min-width: 100px;
  }
  .slider-el::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--primary);
    border: 3px solid var(--white);
    box-shadow: 0 1px 4px rgba(0,0,0,.2);
    cursor: pointer;
  }
  .slider-el::-moz-range-thumb {
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--primary);
    border: 3px solid var(--white);
    box-shadow: 0 1px 4px rgba(0,0,0,.2);
    cursor: pointer;
  }
  .joint-bottom {
    display: flex; align-items: center; gap: 14px; margin-top: 8px;
  }
  .range-labels {
    display: flex; justify-content: space-between;
    font-size: .6rem; color: var(--text-muted); min-width: 60px; gap: 4px;
  }
  .spark { display: block; border-radius: 3px; border: 1px solid var(--border-light); flex-shrink: 0; }
  .action-row { margin: 12px 0 0; display: flex; gap: 5px; }
  .btn-home {
    flex: 1;
    background: var(--white);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 5px;
    padding: 8px;
    font-weight: 500;
    font-size: .75rem;
    cursor: pointer;
    transition: all .12s;
    font-family: inherit;
  }
  .btn-home:hover { background: var(--primary); border-color: var(--primary); color: var(--white); }
  .log {
    border-top: 1px solid var(--border-light);
    margin-top: 8px; padding-top: 6px;
  }
  .log .entries {
    max-height: 64px; overflow-y: auto;
    font-size: .65rem;
    font-family: 'SF Mono', 'Fira Code', monospace;
    color: var(--text-muted);
  }
  .log .entries::-webkit-scrollbar { width: 3px; }
  .log .entries::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
  .log .entries div { padding: 1px 0; }
  .log .entries .time { color: var(--accent); margin-right: 6px; }

  .tr-body { padding: 12px 24px 16px; display: flex; gap: 16px; flex-wrap: wrap; }
  .tr-col { flex: 1; min-width: 320px; }
  .card { border: 1px solid var(--border-light); border-radius: 6px; padding: 12px 16px; margin-bottom: 8px; }
  .card-title { font-size: .8rem; font-weight: 600; color: var(--primary); margin-bottom: 8px; }
  .joint-row { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .joint-row label { min-width: 65px; font-size: .75rem; font-weight: 500; }
  .joint-row .en { font-weight: 400; color: var(--text-muted); font-size: .6rem; }
  .joint-row input[type=range] { flex: 1; -webkit-appearance: none; appearance: none; height: 8px; background: var(--border); border-radius: 99px; outline: none; cursor: pointer; }
  .joint-row input[type=range]::-webkit-slider-thumb { -webkit-appearance: none; width: 18px; height: 18px; border-radius: 50%; background: var(--primary); border: 2px solid #fff; box-shadow: 0 1px 3px rgba(0,0,0,.2); cursor: pointer; }
  .joint-row input[type=range]::-moz-range-thumb { width: 18px; height: 18px; border-radius: 50%; background: var(--primary); border: 2px solid #fff; box-shadow: 0 1px 3px rgba(0,0,0,.2); cursor: pointer; }
  .joint-row .val { min-width: 50px; font-size: .8rem; font-family: 'SF Mono','Fira Code',monospace; color: var(--accent); text-align: right; }
  .joint-row .actual { min-width: 50px; font-size: .7rem; font-family: 'SF Mono','Fira Code',monospace; color: var(--text-muted); text-align: right; }
  .btn { padding: 6px 14px; border-radius: 5px; border: 1px solid var(--border); font-size: .75rem; font-weight: 500; cursor: pointer; font-family: inherit; transition: all .12s; background: var(--white); color: var(--text); }
  .btn:hover { background: var(--primary); border-color: var(--primary); color: #fff; }
  .btn-sm { padding: 4px 10px; font-size: .7rem; }
  .btn-danger { color: var(--danger); }
  .btn-danger:hover { background: var(--danger); border-color: var(--danger); color: #fff; }
  .btn-success { color: var(--success); }
  .btn-success:hover { background: var(--success); border-color: var(--success); color: #fff; }
  .btn-play { background: var(--success); color: #fff; border-color: var(--success); }
  .btn-play:hover { background: #276749; border-color: #276749; }
  .btn-stop { background: var(--danger); color: #fff; border-color: var(--danger); }
  .btn-stop:hover { background: #9b2c2c; border-color: #9b2c2c; }
  .btn:disabled { opacity: .5; cursor: not-allowed; }
  .pose-list { max-height: 300px; overflow-y: auto; }
  .pose-item { display: flex; align-items: center; justify-content: space-between; padding: 6px 8px; border-bottom: 1px solid var(--border-light); font-size: .75rem; }
  .pose-item .name { font-weight: 500; }
  .pose-item .joints { font-family: 'SF Mono','Fira Code',monospace; color: var(--text-muted); font-size: .65rem; }
  .pose-item .actions { display: flex; gap: 4px; }
  .save-row { display: flex; gap: 6px; margin-bottom: 8px; }
  .save-row input { flex: 1; padding: 6px 8px; border: 1px solid var(--border); border-radius: 4px; font-size: .75rem; outline: none; }
  .save-row input:focus { border-color: var(--accent); }
  .play-row { display: flex; align-items: center; gap: 10px; margin-top: 6px; flex-wrap: wrap; }
  .play-row label { font-size: .75rem; font-weight: 500; }
  .play-row input[type=range] { width: 120px; }
  .play-row .time-val { font-family: 'SF Mono','Fira Code',monospace; font-size: .75rem; min-width: 35px; }
  .status-bar { padding: 8px 24px; border-top: 1px solid var(--border-light); font-size: .73rem; color: var(--text-muted); display: flex; justify-content: space-between; }
  .status-bar .cur-pose { font-weight: 500; color: var(--primary); }
  .empty { color: var(--text-muted); font-style: italic; font-size: .75rem; padding: 8px; }
  .count { font-size: .7rem; color: var(--text-muted); margin-left: 4px; }
</style>
</head>
<body>
<div class="app">
  <div class="header">
    <div><h1>Lab 05 &mdash; Phantom X Pincher</h1></div>
    <div class="header-right">
      <span><span class="dot green" id="statusDot"></span><span id="statusText">OK</span></span>
      <span id="stateDisplay" style="font-family:'SF Mono','Fira Code',monospace;">0.0 0.0 0.0 0.0 0.0</span>
    </div>
  </div>
  <div class="tabs">
    <button class="tab active" data-tab="act4">Act 4</button>
    <button class="tab" data-tab="act7">Act 7</button>
    <button class="tab" data-tab="act8">Act 8</button>
    <button class="tab" data-tab="act9">Act 9</button>
    <button class="tab" data-tab="sinusoidal">Act 10</button>
    <button class="tab" data-tab="act11">Act 11</button>
    <button class="tab" data-tab="act12">Act 12</button>
    <button class="tab" data-tab="act13">Act 13</button>
    <button class="tab" data-tab="tracing">Act 14</button>
    <button class="tab" data-tab="dance">Act 15</button>
  </div>

  <div id="act4" class="tab-content active">
    <div class="body" id="jointList"></div>
    <div style="padding:0 24px 8px;">
      <canvas id="act4Traj" style="width:100%;height:200px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
    </div>
    <div style="padding:0 24px 14px;">
      <div class="action-row"><button class="btn-home" id="homeBtn">Home (todas a 0&deg;)</button></div>
      <div class="log"><div class="entries" id="logEntries"></div></div>
    </div>
  </div>

  <div id="act7" class="tab-content">
    <div class="body" id="act7Body">
      <div class="card">
        <div class="card-title">Configuraciones predefinidas</div>
        <div style="font-size:.75rem;color:var(--text-muted);margin-bottom:10px;">
          Las 5 configuraciones se envían simultáneamente a todas las articulaciones.
          Valores en grados: [Base, Hombro, Codo, Muñeca, Pinza].
        </div>
        <div id="presetList"></div>
      </div>
      <div class="card">
        <div class="card-title">Configuración personalizada</div>
        <div id="customRow" style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;margin-bottom:8px;"></div>
        <button class="btn btn-sm btn-success" id="sendCustomBtn" style="margin-top:4px;">Enviar configuración</button>
      </div>
      <div class="log" style="margin-top:8px;">
        <div class="card-title">Historial</div>
        <div class="entries" id="act7Log"></div>
      </div>
    </div>
  </div>

  <div id="act8" class="tab-content">
    <div class="body" id="act8Body">
      <div class="card">
        <div class="card-title">Configuración</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
          <label style="font-size:.75rem;font-weight:500;">Seleccionar:</label>
          <select id="configSelect" style="padding:5px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;"></select>
          <label style="font-size:.75rem;font-weight:500;margin-left:8px;">Delay entre articulaciones:</label>
          <input type="range" id="seqDelay" min="0.5" max="3" step="0.1" value="1.0" style="width:100px;">
          <span class="time-val" id="seqDelayVal" style="font-size:.75rem;">1.0s</span>
        </div>
        <div id="configValues" style="display:flex;gap:6px;flex-wrap:wrap;margin-bottom:8px;"></div>
        <div style="display:flex;gap:6px;">
          <button class="btn btn-play btn-sm" id="runSeqBtn">Ejecutar secuencial</button>
          <button class="btn btn-success btn-sm" id="runSimBtn8">Ejecutar simultáneo</button>
          <button class="btn btn-sm btn-home" id="homeAct8Btn">Home</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Estado</div>
        <div style="font-size:.85rem;font-family:'SF Mono','Fira Code',monospace;">
          <div>Articulación actual: <span id="currentJoint" style="color:var(--accent);font-weight:600;">—</span></div>
          <div>Tiempo transcurrido: <span id="elapsedTime" style="color:var(--accent);font-weight:600;">0.0 s</span></div>
          <div>Progreso: <span id="seqProgress" style="color:var(--accent);font-weight:600;">0 / 5</span></div>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Comparación</div>
        <div style="display:flex;gap:20px;flex-wrap:wrap;font-size:.75rem;">
          <div><strong>Secuencial:</strong> <span id="seqTimeResult">—</span></div>
          <div><strong>Simultáneo:</strong> <span id="simTimeResult8">—</span></div>
        </div>
      </div>
      <div class="log" style="margin-top:8px;">
        <div class="card-title">Historial</div>
        <div class="entries" id="act8Log"></div>
      </div>
    </div>
  </div>

  <div id="act9" class="tab-content">
    <div class="body" id="act9Body">
      <div class="card">
        <div class="card-title">Configuración de trayectoria</div>
        <div style="display:flex;gap:16px;flex-wrap:wrap;">
          <div style="flex:1;min-width:250px;">
            <label style="font-size:.75rem;font-weight:600;">Inicio</label>
            <select id="trajStartSelect" style="width:100%;padding:4px 6px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;margin-bottom:4px;"></select>
            <div id="trajStartVals" style="display:flex;gap:3px;flex-wrap:wrap;"></div>
          </div>
          <div style="flex:1;min-width:250px;">
            <label style="font-size:.75rem;font-weight:600;">Final</label>
            <select id="trajEndSelect" style="width:100%;padding:4px 6px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;margin-bottom:4px;"></select>
            <div id="trajEndVals" style="display:flex;gap:3px;flex-wrap:wrap;"></div>
          </div>
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-top:8px;">
          <label style="font-size:.75rem;font-weight:500;">Duración:</label>
          <input type="range" id="trajDuration" min="1" max="5" step="0.5" value="3" style="width:120px;">
          <span class="time-val" id="trajDurationVal" style="font-size:.75rem;">3.0s</span>
          <label style="font-size:.75rem;font-weight:500;margin-left:8px;">Método:</label>
          <select id="trajMethod" style="padding:4px 6px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="both">Ambos</option>
            <option value="linear">Solo lineal</option>
            <option value="cubic">Solo cúbica</option>
          </select>
          <button class="btn btn-play btn-sm" id="runTrajBtn">Calcular y ejecutar</button>
          <button class="btn btn-sm btn-home" id="homeAct9Btn">Home</button>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div class="card" style="flex:1;min-width:300px;">
          <div class="card-title">Posición</div>
          <canvas id="trajPosCanvas" style="width:100%;height:180px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
        </div>
        <div class="card" style="flex:1;min-width:300px;">
          <div class="card-title">Velocidad</div>
          <canvas id="trajVelCanvas" style="width:100%;height:180px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
        </div>
        <div class="card" style="flex:1;min-width:300px;">
          <div class="card-title">Aceleración</div>
          <canvas id="trajAccCanvas" style="width:100%;height:180px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Métricas</div>
        <div id="trajMetrics" style="font-size:.75rem;font-family:'SF Mono','Fira Code',monospace;display:flex;gap:20px;flex-wrap:wrap;">
          <div><strong>Lineal:</strong> Vel máx: <span id="linVelMax">—</span> | Acel máx: <span id="linAccMax">—</span> | Jerk máx: <span id="linJerkMax">—</span></div>
          <div><strong>Cúbica:</strong> Vel máx: <span id="cubVelMax">—</span> | Acel máx: <span id="cubAccMax">—</span> | Jerk máx: <span id="cubJerkMax">—</span></div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="card-title">Estado</div>
        <div class="entries" id="act9Log"></div>
      </div>
    </div>
  </div>

  <div id="act13" class="tab-content">
    <div class="tr-body">
      <div class="tr-col">
        <div class="card">
          <div class="card-title">Robot</div>
          <div id="jointControlsTR"></div>
        </div>
        <div class="card">
          <div class="card-title">Guardar pose</div>
          <div class="save-row">
            <input type="text" id="poseName" placeholder="Nombre (ej. reposo, alcanzar...)">
            <button class="btn btn-success btn-sm" id="saveBtn">Guardar</button>
          </div>
          <button class="btn" id="clearAllBtn" style="width:100%;margin-top:4px;">Limpiar todas</button>
        </div>
      </div>
      <div class="tr-col">
        <div class="card">
          <div class="card-title">Poses guardadas <span class="count" id="poseCount">(0)</span></div>
          <div class="pose-list" id="poseList"><div class="empty">Aún no hay poses guardadas.</div></div>
        </div>
        <div class="card">
          <div class="card-title">Reproducción</div>
          <div class="play-row">
            <label>Tiempo transición:</label>
            <input type="range" id="transTime" min="0.5" max="5" step="0.1" value="2.0">
            <span class="time-val" id="transTimeVal">2.0s</span>
            <button class="btn btn-play btn-sm" id="playBtn">Reproducir</button>
            <button class="btn btn-stop btn-sm" id="stopBtn" disabled>Detener</button>
          </div>
          <div style="margin-top:8px;font-size:.7rem;color:var(--text-muted);">
            <span>Progreso: </span><span id="progressText">—</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div id="dance" class="tab-content">
    <div class="body">
      <div class="card">
        <div class="card-title">Baile &mdash; Coreografía</div>
        <p style="font-size:.75rem;color:var(--text-muted);margin-bottom:10px;">
          El robot baila al ritmo de la canción. Las poses se generan a partir de
          las configuraciones de la Actividad 7 (poses seguras).
          El audio se reproduce en el navegador.
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
          <button class="btn btn-play" id="danceStartBtn">▶ Iniciar Baile</button>
          <button class="btn btn-stop" id="danceStopBtn" disabled>■ Detener</button>
          <span style="font-size:.75rem;color:var(--text-muted);" id="danceStatus">Listo</span>
        </div>
        <div style="margin-top:10px;font-size:.75rem;font-family:monospace;color:var(--text-muted);">
          <div>Canción: <span id="danceSongName">—</span></div>
          <div>Tempo: <span id="danceTempo">—</span></div>
          <div>Beats: <span id="danceBeats">—</span></div>
          <div>Progreso: <span id="danceProgress">—</span></div>
          <div>Pose actual: <span id="dancePoseName">—</span></div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="entries" id="danceLog"></div>
      </div>
    </div>
  </div>
  <div id="sinusoidal" class="tab-content">
    <div class="body">
      <div class="card">
        <div class="card-title">Configuraci&oacute;n</div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
          <label style="font-size:.75rem;font-weight:500;">Articulaci&oacute;n:</label>
          <select id="sinJointSelect" style="padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;"></select>
          <label style="font-size:.75rem;font-weight:500;">Amplitud A:</label>
          <select id="sinAmpSelect" style="padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="30">30&deg;</option>
            <option value="60" selected>60&deg;</option>
          </select>
          <label style="font-size:.75rem;font-weight:500;">Frecuencia f:</label>
          <select id="sinFreqSelect" style="padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="0.25">0.25 Hz</option>
            <option value="0.50" selected>0.50 Hz</option>
          </select>
          <button class="btn btn-play btn-sm" id="sinStartBtn">▶ Iniciar prueba &uacute;nica</button>
          <button class="btn btn-play btn-sm" id="sinStartAllBtn">▶ Ejecutar 4 pruebas</button>
          <button class="btn btn-stop btn-sm" id="sinStopBtn" disabled>■ Detener</button>
          <button class="btn btn-sm btn-home" id="sinHomeBtn">Home</button>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div class="card" style="flex:1;min-width:300px;">
          <div class="card-title">Posici&oacute;n</div>
          <canvas id="sinPosCanvas" style="width:100%;height:200px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
        </div>
        <div class="card" style="flex:1;min-width:250px;">
          <div class="card-title">Resultados</div>
          <div id="sinResults" style="font-size:.75rem;font-family:'SF Mono','Fira Code',monospace;">
            <div>Prueba: <span id="sinTestName">—</span></div>
            <div>Error m&aacute;x: <span id="sinMaxErr">—</span></div>
            <div>RMSE: <span id="sinRmse">—</span></div>
            <div>Progreso: <span id="sinProgress">—</span></div>
          </div>
        </div>
      </div>
      <div class="card" style="margin-top:6px;">
        <div class="card-title" style="margin-bottom:6px;">Resumen de pruebas</div>
        <div id="sinSummaryTable" style="font-size:.75rem;font-family:'SF Mono','Fira Code',monospace;">
          <div style="display:grid;grid-template-columns:1fr 100px 100px 100px 100px;gap:4px;padding:4px 0;border-bottom:1px solid var(--border);font-weight:600;">
            <div>Prueba</div><div>Amplitud</div><div>Frecuencia</div><div>Error m&aacute;x</div><div>RMSE</div>
          </div>
          <div id="sinSummaryRows"></div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="card-title">Estado</div>
        <div class="entries" id="sinLog"></div>
      </div>
    </div>
  </div>
  <div id="act11" class="tab-content">
    <div class="body">
      <div class="card">
        <div class="card-title">FK &mdash; Cinem&aacute;tica Directa</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px;">
          <label style="font-size:.75rem;">q<sub>1</sub> (Base):</label>
          <input type="number" id="fkQ1" value="0" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">&deg;
          <label style="font-size:.75rem;margin-left:8px;">q<sub>2</sub> (Hombro):</label>
          <input type="number" id="fkQ2" value="0" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">&deg;
          <label style="font-size:.75rem;margin-left:8px;">q<sub>3</sub> (Codo):</label>
          <input type="number" id="fkQ3" value="0" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">&deg;
          <label style="font-size:.75rem;margin-left:8px;">q<sub>4</sub> (Mu&ntilde;eca):</label>
          <input type="number" id="fkQ4" value="0" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">&deg;
          <button class="btn btn-play btn-sm" id="fkCalcBtn">Calcular</button>
          <button class="btn btn-success btn-sm" id="fkSendBtn">Enviar al robot</button>
          <button class="btn btn-sm btn-home" id="fkHomeBtn">Home</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Resultados</div>
        <div id="fkResults" style="font-size:.85rem;font-family:'SF Mono','Fira Code',monospace;">
          <div>TCP: x = <span id="fkX">—</span> mm, y = <span id="fkY">—</span> mm, z = <span id="fkZ">—</span> mm</div>
          <div>Orientaci&oacute;n: roll = <span id="fkRoll">—</span>&deg;, pitch = <span id="fkPitch">—</span>&deg;, yaw = <span id="fkYaw">—</span>&deg;</div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="card-title">Estado</div>
        <div class="entries" id="fkLog"></div>
      </div>
    </div>
  </div>
  <div id="act12" class="tab-content">
    <div class="body">
      <div class="card">
        <div class="card-title">IK &mdash; Cinem&aacute;tica Inversa</div>
        <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;margin-bottom:10px;">
          <label style="font-size:.75rem;">x (mm):</label>
          <input type="number" id="ikX" value="130" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
          <label style="font-size:.75rem;margin-left:8px;">y (mm):</label>
          <input type="number" id="ikY" value="0" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
          <label style="font-size:.75rem;margin-left:8px;">z (mm):</label>
          <input type="number" id="ikZ" value="100" step="1" style="width:70px;padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
          <label style="font-size:.75rem;margin-left:8px;">Codo:</label>
          <select id="ikElbow" style="padding:4px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="up">Arriba</option>
            <option value="down">Abajo</option>
          </select>
          <button class="btn btn-play btn-sm" id="ikCalcBtn">Calcular</button>
          <button class="btn btn-success btn-sm" id="ikSendBtn">Enviar al robot</button>
          <button class="btn btn-sm btn-home" id="ikHomeBtn">Home</button>
        </div>
      </div>
      <div class="card">
        <div class="card-title">Resultados</div>
        <div id="ikResults" style="font-size:.85rem;font-family:'SF Mono','Fira Code',monospace;">
          <div>q<sub>1</sub> = <span id="ikQ1">—</span>&deg; | q<sub>2</sub> = <span id="ikQ2">—</span>&deg; | q<sub>3</sub> = <span id="ikQ3">—</span>&deg; | q<sub>4</sub> = <span id="ikQ4">—</span>&deg;</div>
          <div id="ikError" style="color:var(--accent);font-weight:600;"></div>
        <div style="font-size:.65rem;color:var(--text-muted);margin-top:4px;">Puntos de referencia: x=130 mm, z≈50–350 mm, y libre (l&iacute;mite radial ≈ 320 mm)</div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="card-title">Estado</div>
        <div class="entries" id="ikLog"></div>
      </div>
    </div>
  </div>
  <div id="tracing" class="tab-content">
    <div class="body">
      <div class="card">
        <div class="card-title">Configuraci&oacute;n</div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;margin-bottom:8px;">
          <label style="font-size:.75rem;font-weight:500;">Figura:</label>
          <select id="trFigSelect" style="padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="triangle">Tri&aacute;ngulo</option>
            <option value="square">Cuadrado</option>
          </select>
          <label style="font-size:.75rem;font-weight:500;">Tama&ntilde;o:</label>
          <select id="trSizeSelect" style="padding:4px 8px;border:1px solid var(--border);border-radius:4px;font-size:.75rem;">
            <option value="0.04">4 cm</option>
            <option value="0.06" selected>6 cm</option>
          </select>
          <button class="btn btn-play btn-sm" id="trStartBtn">&#9654; Trazar</button>
          <button class="btn btn-stop btn-sm" id="trStopBtn" disabled>&#9632; Detener</button>
          <button class="btn btn-sm btn-home" id="trHomeBtn">Home</button>
        </div>
      </div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;">
        <div class="card" style="flex:1;min-width:300px;">
          <div class="card-title">Trayectoria (vista Y&ndash;Z)</div>
          <canvas id="trCanvas" style="width:100%;height:350px;border:1px solid var(--border-light);border-radius:4px;"></canvas>
        </div>
        <div class="card" style="flex:1;min-width:250px;">
          <div class="card-title">Estado</div>
          <div id="trStatus" style="font-size:.75rem;font-family:'SF Mono','Fira Code',monospace;">
            <div>Figura: <span id="trFigName">—</span></div>
            <div>Punto: <span id="trPoint">0 / 0</span></div>
            <div>Progreso: <span id="trProgress">—</span></div>
          </div>
        </div>
      </div>
      <div class="log" style="margin-top:6px;">
        <div class="card-title">Estado</div>
        <div class="entries" id="trLog"></div>
      </div>
    </div>
  </div>
</div>

<script>
var JOINTS = ['waist','shoulder','elbow','wrist','gripper'];
var LIMITS = { waist:[-150,150], shoulder:[-150,150], elbow:[-150,150], wrist:[-150,150], gripper:[-90,90] };
var LABELS = { waist:'Base', shoulder:'Hombro', elbow:'Codo', wrist:'Muneca', gripper:'Pinza' };
var MAX_HIST = 120;
var state = {};
var history = {};
JOINTS.forEach(function(j) { history[j] = []; });

var poses = [];

function deg(v) { return (v * 180 / Math.PI).toFixed(1); }
function rad(v) { return v * Math.PI / 180; }
function clamp(v, lo, hi) { return Math.max(lo, Math.min(hi, v)); }

/* Tabs */
document.querySelectorAll('.tab').forEach(function(tab) {
  tab.addEventListener('click', function() {
    document.querySelectorAll('.tab').forEach(function(t) { t.classList.remove('active'); });
    document.querySelectorAll('.tab-content').forEach(function(c) { c.classList.remove('active'); });
    tab.classList.add('active');
    document.getElementById(tab.dataset.tab).classList.add('active');
  });
});

/* Act 4 — Sparklines */
function drawSpark(joint, canvas) {
  var data = history[joint];
  if (!data || data.length < 2) return;
  var ctx = canvas.getContext('2d');
  var w = canvas.width, h = canvas.height;
  var dpr = window.devicePixelRatio || 1;
  var lim = LIMITS[joint];
  var rng = lim[1] - lim[0] || 1;
  ctx.clearRect(0, 0, w, h);

  var grad = ctx.createLinearGradient(0, 0, 0, h);
  grad.addColorStop(0, 'rgba(26,54,93,0.04)');
  grad.addColorStop(1, 'rgba(26,54,93,0.10)');

  var n = data.length;
  ctx.beginPath();
  for (var i = 0; i < n; i++) {
    var x = (i / (MAX_HIST - 1)) * w;
    var y = h - ((data[i] - lim[0]) / rng) * h;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.lineTo(((n-1)/(MAX_HIST-1))*w, h);
  ctx.lineTo(0, h);
  ctx.closePath();
  ctx.fillStyle = grad;
  ctx.fill();

  ctx.strokeStyle = '#1a365d';
  ctx.lineWidth = 1.5 * dpr;
  ctx.beginPath();
  for (var i = 0; i < n; i++) {
    var x = (i / (MAX_HIST - 1)) * w;
    var y = h - ((data[i] - lim[0]) / rng) * h;
    if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
  }
  ctx.stroke();

  ctx.strokeStyle = 'rgba(26,54,93,0.15)';
  ctx.lineWidth = 0.5 * dpr;
  ctx.setLineDash([4, 4]);
  var mid = h - ((0 - lim[0]) / rng) * h;
  ctx.beginPath();
  ctx.moveTo(0, mid); ctx.lineTo(w, mid);
  ctx.stroke();
  ctx.setLineDash([]);
}

function resizeCanvas(canvas) {
  var parent = canvas.parentElement;
  var availW = parent.getBoundingClientRect().width - 74 - 14;
  var cw = Math.max(120, Math.min(availW, 1000));
  var ch = 40;
  var dpr = window.devicePixelRatio || 1;
  canvas.width = cw * dpr;
  canvas.height = ch * dpr;
  canvas.style.width = cw + 'px';
  canvas.style.height = ch + 'px';
}

function buildAct4() {
  var container = document.getElementById('jointList');
  JOINTS.forEach(function(j) {
    var lim = LIMITS[j];
    var card = document.createElement('div');
    card.className = 'joint-card';
    card.innerHTML =
      '<div class="joint-top">' +
        '<div class="joint-label">' + LABELS[j] + '<span class="en">' + j + '</span></div>' +
        '<input type="range" class="slider-el" min="' + lim[0] + '" max="' + lim[1] + '" step="0.1" value="0">' +
        '<input type="number" class="joint-input" min="' + lim[0] + '" max="' + lim[1] + '" step="0.1" value="0">' +
        '<span class="joint-cur" id="cur-' + j + '">0.0\u00b0</span>' +
      '</div>' +
      '<div class="joint-bottom">' +
        '<div class="range-labels"><span>' + lim[0] + '\u00b0</span><span>0\u00b0</span><span>' + lim[1] + '\u00b0</span></div>' +
        '<canvas class="spark" id="spark-' + j + '"></canvas>' +
      '</div>';
    container.appendChild(card);

    var slider = card.querySelector('.slider-el');
    var inp = card.querySelector('.joint-input');
    var cur = card.querySelector('.joint-cur');
    var canvas = card.querySelector('.spark');

    resizeCanvas(canvas);
    drawSpark(j, canvas);

    function sendNow() {
      var v = parseFloat(slider.value);
      if (isNaN(v)) return;
      v = clamp(v, lim[0], lim[1]);
      slider.value = v;
      inp.value = v.toFixed(1);
      fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: [j], position: [rad(v)] })
      }).then(function(r) { return r.json(); }).then(function(d) {
        if (d.status === 'ok') addLog(j, v);
      });
    }

    slider.addEventListener('input', function() {
      var v = parseFloat(slider.value);
      inp.value = v.toFixed(1);
      cur.textContent = v.toFixed(1) + '\u00b0';
    });
    slider.addEventListener('change', sendNow);

    inp.addEventListener('change', function() {
      var v = parseFloat(inp.value);
      if (isNaN(v)) { inp.value = slider.value; return; }
      v = clamp(v, lim[0], lim[1]);
      slider.value = v; inp.value = v.toFixed(1);
      cur.textContent = v.toFixed(1) + '\u00b0';
      sendNow();
    });
  });
  window.addEventListener('resize', function() {
    JOINTS.forEach(function(j) {
      var canvas = document.getElementById('spark-' + j);
      resizeCanvas(canvas);
      drawSpark(j, canvas);
    });
  });

  // TCP trajectory canvas
  var trajCanvas = document.getElementById('act4Traj');
  var trajCtx = trajCanvas.getContext('2d');
  var trajPoints = [];
  var MAX_TRAJ = 200;
  resizeCanvas(trajCanvas);

  setInterval(function() {
    var q = JOINTS.map(function(j) { return (state[j] || 0) * 180 / Math.PI; });
    var tcp = trFk(q);
    trajPoints.push({x: tcp.x, z: tcp.z});
    if (trajPoints.length > MAX_TRAJ) trajPoints.shift();
    drawTraj();
  }, 200);

  function drawTraj() {
    var ctx = trajCtx, w = trajCanvas.width, h = trajCanvas.height;
    ctx.clearRect(0, 0, w, h);
    if (trajPoints.length < 2) return;
    var margin = 20, pw = w - 2*margin, ph = h - 2*margin;
    var xs = trajPoints.map(function(p) { return p.x; });
    var zs = trajPoints.map(function(p) { return p.z; });
    var xMin = Math.min.apply(null, xs) - 0.01, xMax = Math.max.apply(null, xs) + 0.01;
    var zMin = Math.min.apply(null, zs) - 0.01, zMax = Math.max.apply(null, zs) + 0.01;
    if (xMax - xMin < 0.01) { xMin -= 0.005; xMax += 0.005; }
    if (zMax - zMin < 0.01) { zMin -= 0.005; zMax += 0.005; }
    function sx(v) { return margin + (v - xMin) / (xMax - xMin) * pw; }
    function sy(v) { return h - margin - (v - zMin) / (zMax - zMin) * ph; }
    ctx.strokeStyle = '#2b6cb0'; ctx.lineWidth = 1.5; ctx.beginPath();
    for (var i = 0; i < trajPoints.length; i++) {
      var px = sx(trajPoints[i].x), py = sy(trajPoints[i].z);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }
    ctx.stroke();
    var last = trajPoints[trajPoints.length-1];
    ctx.fillStyle = '#c53030'; ctx.beginPath();
    ctx.arc(sx(last.x), sy(last.z), 3, 0, Math.PI*2); ctx.fill();
    ctx.fillStyle = '#1a202c'; ctx.font = '10px monospace';
    ctx.fillText('XZ: (' + (last.x*1000).toFixed(0) + ', ' + (last.z*1000).toFixed(0) + ') mm', margin+2, margin+12);
  }
}

document.getElementById('homeBtn').onclick = function() {
  JOINTS.forEach(function(j) {
    history[j].push(0);
    if (history[j].length > MAX_HIST) history[j].shift();
    drawSpark(j, document.getElementById('spark-' + j));
  });
  fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
  }).then(function(r) { return r.json(); }).then(function() {
    addLog('Todas', 0);
    document.querySelectorAll('#act4 .joint-input').forEach(function(i) { i.value = '0'; });
    document.querySelectorAll('#act4 .slider-el').forEach(function(s) { s.value = '0'; });
    document.querySelectorAll('#act4 .joint-cur').forEach(function(c) { c.textContent = '0.0\u00b0'; });
  });
};

function addLog(joint, degVal) {
  var el = document.getElementById('logEntries');
  var d = new Date();
  var ts = d.toTimeString().slice(0,8);
  var sign = degVal >= 0 ? '+' : '';
  var text = (LABELS[joint]||joint) + ' ' + sign + degVal.toFixed(1) + '\u00b0';
  el.innerHTML = '<div><span class="time">' + ts + '</span>' + text + '</div>' + el.innerHTML;
  if (el.children.length > 40) el.removeChild(el.lastChild);
}

/* Act 13 */
function buildAct13() {
  var c = document.getElementById('jointControlsTR');
  JOINTS.forEach(function(j) {
    var lim = LIMITS[j];
    var label = j.charAt(0).toUpperCase() + j.slice(1);
    var r = document.createElement('div');
    r.className = 'joint-row';
    r.innerHTML =
      '<label>' + label + ' <span class="en">' + j + '</span></label>' +
      '<input type="range" min="' + lim[0] + '" max="' + lim[1] + '" step="0.5" value="0" id="tr-sl-' + j + '">' +
      '<input type="number" class="joint-input" min="' + lim[0] + '" max="' + lim[1] + '" step="0.5" value="0" id="tr-num-' + j + '">' +
      '<span class="val" id="tr-val-' + j + '">0.0\u00b0</span>' +
      '<span class="actual" id="tr-act-' + j + '">(0.0)</span>';
    c.appendChild(r);
    var slider = r.querySelector('input[type=range]');
    var numInput = r.querySelector('.joint-input');
    var valEl = r.querySelector('.val');

    function sendJoint(v) {
      v = clamp(v, lim[0], lim[1]);
      slider.value = v;
      numInput.value = v.toFixed(1);
      valEl.textContent = v.toFixed(1) + '\u00b0';
      fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: [j], position: [rad(v)] })
      });
    }

    slider.addEventListener('input', function() {
      var v = parseFloat(this.value);
      numInput.value = v.toFixed(1);
      valEl.textContent = v.toFixed(1) + '\u00b0';
    });
    slider.addEventListener('change', function() {
      sendJoint(parseFloat(this.value));
    });
    numInput.addEventListener('change', function() {
      var v = parseFloat(this.value);
      if (isNaN(v)) { this.value = slider.value; return; }
      sendJoint(v);
    });
  });
  // Home button below the joints
  var homeRow = document.createElement('div');
  homeRow.style.marginTop = '10px';
  homeRow.innerHTML = '<button class="btn-home" id="trHomeBtn">Home (todas a 0\u00b0)</button>';
  c.parentElement.appendChild(homeRow);
  document.getElementById('trHomeBtn').onclick = function() {
    JOINTS.forEach(function(j) {
      var sl = document.getElementById('tr-sl-' + j);
      var num = document.getElementById('tr-num-' + j);
      var val = document.getElementById('tr-val-' + j);
      if (sl) sl.value = '0';
      if (num) num.value = '0';
      if (val) val.textContent = '0.0\u00b0';
    });
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}

function updatePoseList() {
  var el = document.getElementById('poseList');
  if (poses.length === 0) {
    el.innerHTML = '<div class="empty">Aún no hay poses guardadas.</div>';
    document.getElementById('poseCount').textContent = '(0)';
    return;
  }
  document.getElementById('poseCount').textContent = '(' + poses.length + ')';
  var html = '';
  poses.forEach(function(p, i) {
    var vals = JOINTS.map(function(j) { return p.positions[j].toFixed(1) + '\u00b0'; }).join(' | ');
    html +=
      '<div class="pose-item">' +
        '<div><div class="name">' + (i + 1) + '. ' + p.name + '</div>' +
        '<div class="joints">' + vals + '</div></div>' +
        '<div class="actions">' +
          '<button class="btn btn-sm" onclick="moveToPose(' + i + ')">Ir</button>' +
          '<button class="btn btn-sm btn-danger" onclick="deletePose(' + i + ')">X</button>' +
        '</div>' +
      '</div>';
  });
  el.innerHTML = html;
}

function moveToPose(idx) {
  var p = poses[idx];
  var pos = JOINTS.map(function(j) { return rad(p.positions[j]); });
  fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name: JOINTS, position: pos })
  });
  JOINTS.forEach(function(j) {
    var sl = document.getElementById('tr-sl-' + j);
    if (sl) { sl.value = p.positions[j]; }
    var v = document.getElementById('tr-val-' + j);
    if (v) { v.textContent = p.positions[j].toFixed(1) + '\u00b0'; }
  });
}

function deletePose(idx) {
  fetch('/api/poses/' + idx, { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (d.status === 'ok') { poses = d.poses; updatePoseList(); }
    });
}

document.getElementById('saveBtn').onclick = function() {
  var name = document.getElementById('poseName').value.trim();
  if (!name) { alert('Ingresa un nombre para la pose.'); return; }
  var positions = {};
  JOINTS.forEach(function(j) {
    var sl = document.getElementById('tr-sl-' + j);
    positions[j] = parseFloat(sl ? sl.value : 0);
  });
  fetch('/api/poses', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name: name, positions: positions })
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.status === 'ok') { poses = d.poses; updatePoseList(); document.getElementById('poseName').value = ''; }
  });
};

document.getElementById('clearAllBtn').onclick = function() {
  if (!confirm('¿Borrar todas las poses?')) return;
  fetch('/api/poses', { method: 'DELETE' })
    .then(function(r) { return r.json(); })
    .then(function(d) { if (d.status === 'ok') { poses = d.poses; updatePoseList(); } });
};

document.getElementById('transTime').addEventListener('input', function() {
  document.getElementById('transTimeVal').textContent = parseFloat(this.value).toFixed(1) + 's';
});

document.getElementById('playBtn').onclick = function() {
  var trans = parseFloat(document.getElementById('transTime').value);
  fetch('/api/play', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ transition_time: trans })
  }).then(function(r) { return r.json(); });
};

document.getElementById('stopBtn').onclick = function() {
  fetch('/api/stop', { method: 'POST' });
};

/* Shared poll — errors silently ignored */
function poll() {
  fetch('/api/state')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      state = d;
      var parts = JOINTS.map(function(j) {
        var v = (d[j] || 0) * 180 / Math.PI;
        var actEl = document.getElementById('tr-act-' + j);
        if (actEl) actEl.textContent = '(' + v.toFixed(1) + ')';
        history[j].push(v);
        if (history[j].length > MAX_HIST) history[j].shift();
        var cv = document.getElementById('spark-' + j);
        if (cv) drawSpark(j, cv);
        return j + ': ' + v.toFixed(1) + '\u00b0';
      });
      document.getElementById('stateDisplay').textContent = parts.join(' | ');
    }).catch(function() {});

  fetch('/api/status')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      var ps = document.getElementById('playStatus');
      var statusText = document.getElementById('statusText');
      var dot = document.getElementById('statusDot');
      if (ps) {
        if (d.playing) {
          dot.className = 'dot amber';
          ps.innerHTML = 'Reproduciendo... ' + d.current + '/' + d.total;
        } else {
          dot.className = 'dot green';
          ps.innerHTML = 'OK';
        }
      } else {
        dot.className = d.playing ? 'dot amber' : 'dot green';
        statusText.textContent = d.playing ? 'Reproduciendo' : 'OK';
      }
      document.getElementById('progressText').textContent = d.playing ? (d.current + ' / ' + d.total + '  (' + d.pose_name + ')') : '—';
      document.getElementById('playBtn').disabled = d.playing;
      document.getElementById('stopBtn').disabled = !d.playing;
    }).catch(function() {});

  fetch('/api/poses')
    .then(function(r) { return r.json(); })
    .then(function(d) {
      if (JSON.stringify(d.poses) !== JSON.stringify(poses)) {
        poses = d.poses;
        updatePoseList();
      }
    }).catch(function() {});

  setTimeout(poll, 300);
}

/* Act 7 — Movimiento Simultáneo */
var ACT7_PRESETS = [
  { name: 'Config 1 — Home',    vals: [0, 0, 0, 0, 0] },
  { name: 'Config 2',           vals: [25, 25, 20, -20, 0] },
  { name: 'Config 3',           vals: [-35, 35, -30, 30, 0] },
  { name: 'Config 4',           vals: [85, -20, 55, 25, 0] },
  { name: 'Config 5',           vals: [80, -35, 55, -45, 0] },
];

function buildAct7() {
  var container = document.getElementById('presetList');
  ACT7_PRESETS.forEach(function(p, idx) {
    var row = document.createElement('div');
    row.className = 'joint-card';
    row.style.padding = '10px 14px';
    row.style.marginBottom = '6px';

    var header = document.createElement('div');
    header.style.cssText = 'display:flex;align-items:center;gap:10px;flex-wrap:wrap;';
    header.innerHTML = '<span style="font-weight:600;font-size:.8rem;min-width:150px;">' + p.name + '</span>';

    var inputs = [];
    JOINTS.forEach(function(j, ji) {
      var inp = document.createElement('input');
      inp.type = 'number';
      inp.className = 'joint-input';
      inp.style.width = '60px';
      inp.step = '1';
      inp.value = p.vals[ji];
      inp.title = LABELS[j];
      inp.dataset.idx = ji;
      header.appendChild(inp);
      inputs.push(inp);
    });

    var runBtn = document.createElement('button');
    runBtn.className = 'btn btn-sm btn-success';
    runBtn.textContent = 'Ejecutar';
    runBtn.onclick = function() {
      var vals = inputs.map(function(i) { return parseFloat(i.value) || 0; });
      sendAct7(vals, p.name);
    };
    header.appendChild(runBtn);

    row.appendChild(header);
    container.appendChild(row);
  });

  // Custom config inputs
  var customRow = document.getElementById('customRow');
  JOINTS.forEach(function(j, ji) {
    var inp = document.createElement('input');
    inp.type = 'number';
    inp.className = 'joint-input';
    inp.style.width = '60px';
    inp.step = '1';
    inp.value = '0';
    inp.title = LABELS[j];
    customRow.appendChild(inp);
  });

  document.getElementById('sendCustomBtn').onclick = function() {
    var inputs = customRow.querySelectorAll('input');
    var vals = Array.from(inputs).map(function(i) { return parseFloat(i.value) || 0; });
    sendAct7(vals, 'Personalizada');
  };

  var homeBtn = document.createElement('button');
  homeBtn.className = 'btn btn-sm btn-home';
  homeBtn.textContent = 'Home';
  homeBtn.style.marginLeft = '6px';
  homeBtn.onclick = function() { sendAct7([0, 0, 0, 0, 0], 'Home'); };
  document.getElementById('sendCustomBtn').parentElement.appendChild(homeBtn);
}

function sendAct7(vals, label) {
  var pos = vals.map(function(v) { return rad(v); });
  fetch('/api/command', {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify({ name: JOINTS, position: pos })
  }).then(function(r) { return r.json(); }).then(function(d) {
    if (d.status === 'ok') {
      var el = document.getElementById('act7Log');
      var ts = new Date().toTimeString().slice(0,8);
      var txt = JOINTS.map(function(j, i) { return vals[i].toFixed(0) + '\u00b0'; }).join(' | ');
      el.innerHTML = '<div><span class="time">' + ts + '</span> ' + label + ': ' + txt + '</div>' + el.innerHTML;
    }
  });
}

/* Act 8 — Movimiento Secuencial */
var ACT8_CONFIGS = [
  { name: 'Config 1 — Home',    vals: [0, 0, 0, 0, 0] },
  { name: 'Config 2',           vals: [25, 25, 20, -20, 0] },
  { name: 'Config 3',           vals: [-35, 35, -30, 30, 0] },
  { name: 'Config 4',           vals: [85, -20, 55, 25, 0] },
  { name: 'Config 5',           vals: [80, -35, 55, -45, 0] },
];
var act8Running = false;
var act8Stop = false;

function buildAct8() {
  var sel = document.getElementById('configSelect');
  ACT8_CONFIGS.forEach(function(c, i) {
    var opt = document.createElement('option');
    opt.value = i;
    opt.textContent = c.name;
    sel.appendChild(opt);
  });

  document.getElementById('seqDelay').addEventListener('input', function() {
    document.getElementById('seqDelayVal').textContent = parseFloat(this.value).toFixed(1) + 's';
  });

  function showConfigVals(idx) {
    var container = document.getElementById('configValues');
    container.innerHTML = '';
    var vals = ACT8_CONFIGS[idx].vals;
    JOINTS.forEach(function(j, i) {
      var span = document.createElement('span');
      span.style.cssText = 'padding:4px 8px;border:1px solid var(--border-light);border-radius:4px;font-size:.75rem;font-family:SF Mono,Fira Code,monospace;';
      span.textContent = LABELS[j] + ': ' + vals[i] + '\u00b0';
      container.appendChild(span);
    });
  }
  sel.onchange = function() { showConfigVals(parseInt(this.value)); };
  showConfigVals(0);

  async function runSequential() {
    var idx = parseInt(document.getElementById('configSelect').value);
    var vals = ACT8_CONFIGS[idx].vals;
    var delay = parseFloat(document.getElementById('seqDelay').value);
    var startTime = Date.now();

    act8Running = true;
    act8Stop = false;
    document.getElementById('runSeqBtn').disabled = true;
    document.getElementById('runSimBtn8').disabled = true;
    document.getElementById('currentJoint').textContent = '...';
    document.getElementById('elapsedTime').textContent = '0.0 s';
    document.getElementById('seqProgress').textContent = '0 / 5';
    document.getElementById('seqTimeResult').textContent = '—';

    for (var i = 0; i < JOINTS.length; i++) {
      if (act8Stop) break;
      document.getElementById('currentJoint').textContent = LABELS[JOINTS[i]];
      document.getElementById('seqProgress').textContent = (i + 1) + ' / 5';

      var joint = JOINTS[i];
      var pos = [rad(vals[i])];
      await fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: [joint], position: pos })
      }).then(function(r) { return r.json(); });

      if (i < JOINTS.length - 1) {
        await new Promise(function(resolve) {
          var waited = 0;
          var step = 100;
          var check = setInterval(function() {
            waited += step;
            document.getElementById('elapsedTime').textContent = ((Date.now() - startTime) / 1000).toFixed(1) + ' s';
            if (waited >= delay * 1000 || act8Stop) {
              clearInterval(check);
              resolve();
            }
          }, step);
        });
      }
    }

    var elapsed = (Date.now() - startTime) / 1000;
    document.getElementById('elapsedTime').textContent = elapsed.toFixed(1) + ' s';
    document.getElementById('seqTimeResult').textContent = elapsed.toFixed(2) + ' s';
    document.getElementById('currentJoint').textContent = act8Stop ? 'Detenido' : 'Completado';
    act8Running = false;
    document.getElementById('runSeqBtn').disabled = false;
    document.getElementById('runSimBtn8').disabled = false;

    var el = document.getElementById('act8Log');
    var ts = new Date().toTimeString().slice(0,8);
    var txt = vals.map(function(v) { return v.toFixed(0) + '\u00b0'; }).join(' | ');
    el.innerHTML = '<div><span class="time">' + ts + '</span> Secuencial (' + elapsed.toFixed(1) + 's): ' + txt + '</div>' + el.innerHTML;
  }

  document.getElementById('runSeqBtn').onclick = function() {
    if (act8Running) return;
    runSequential();
  };

  document.getElementById('runSimBtn8').onclick = function() {
    if (act8Running) return;
    var idx = parseInt(document.getElementById('configSelect').value);
    var vals = ACT8_CONFIGS[idx].vals;
    var startTime = Date.now();
    var pos = vals.map(function(v) { return rad(v); });

    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: pos })
    }).then(function(r) { return r.json(); }).then(function() {
      var elapsed = (Date.now() - startTime) / 1000;
      document.getElementById('simTimeResult8').textContent = elapsed.toFixed(2) + ' s';
      var el = document.getElementById('act8Log');
      var ts = new Date().toTimeString().slice(0,8);
      var txt = vals.map(function(v) { return v.toFixed(0) + '\u00b0'; }).join(' | ');
      el.innerHTML = '<div><span class="time">' + ts + '</span> Simult\u00e1neo (' + elapsed.toFixed(1) + 's): ' + txt + '</div>' + el.innerHTML;
    });
  };

  document.getElementById('homeAct8Btn').onclick = function() {
    if (act8Running) { act8Stop = true; return; }
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}

/* Sinusoidal generator for Act 10 */
function sinTraj(q0, ampDeg, freqHz, periods, fs) {
  var dur = periods / freqHz;
  var n = Math.round(fs * dur);
  var t = [], q = [];
  for (var i = 0; i < n; i++) {
    var ti = i / fs;
    t.push(ti);
    q.push(q0 + ampDeg * Math.sin(2 * Math.PI * freqHz * ti));
  }
  return { t: t, q: q };
}

/* Act 9 — Interpolación */
var TRAJ_CONFIGS = [
  { name: 'Config 1 — Home',  vals: [0, 0, 0, 0, 0] },
  { name: 'Config 2',         vals: [25, 25, 20, -20, 0] },
  { name: 'Config 3',         vals: [-35, 35, -30, 30, 0] },
  { name: 'Config 4',         vals: [85, -20, 55, 25, 0] },
  { name: 'Config 5',         vals: [80, -35, 55, -45, 0] },
];
var trajRunning = false;

function buildAct9() {
  var startSel = document.getElementById('trajStartSelect');
  var endSel = document.getElementById('trajEndSelect');
  TRAJ_CONFIGS.forEach(function(c, i) {
    var o1 = document.createElement('option'); o1.value = i; o1.textContent = c.name; startSel.appendChild(o1);
    var o2 = document.createElement('option'); o2.value = i; o2.textContent = c.name; endSel.appendChild(o2);
  });
  endSel.value = 3;  // Config 4 por defecto como destino

  function showVals(selId, containerId) {
    var idx = parseInt(document.getElementById(selId).value);
    var container = document.getElementById(containerId);
    container.innerHTML = '';
    TRAJ_CONFIGS[idx].vals.forEach(function(v, i) {
      var s = document.createElement('span');
      s.style.cssText = 'padding:2px 6px;border:1px solid var(--border-light);border-radius:3px;font-size:.7rem;font-family:SF Mono,Fira Code,monospace;';
      s.textContent = LABELS[JOINTS[i]] + ': ' + v + '\u00b0';
      container.appendChild(s);
    });
  }
  startSel.onchange = function() { showVals('trajStartSelect', 'trajStartVals'); };
  endSel.onchange = function() { showVals('trajEndSelect', 'trajEndVals'); };
  showVals('trajStartSelect', 'trajStartVals');
  showVals('trajEndSelect', 'trajEndVals');

  document.getElementById('trajDuration').addEventListener('input', function() {
    document.getElementById('trajDurationVal').textContent = parseFloat(this.value).toFixed(1) + 's';
  });

  function linTraj(q0, qf, n) {
    var q = [];
    for (var i = 0; i < n; i++) {
      var t = i / (n - 1);
      q.push(q0.map(function(v, j) { return v + (qf[j] - v) * t; }));
    }
    return q;
  }

  function cubTraj(q0, qf, n) {
    var q = [];
    for (var i = 0; i < n; i++) {
      var t = i / (n - 1);
      var s = 3 * t * t - 2 * t * t * t;
      q.push(q0.map(function(v, j) { return v + (qf[j] - v) * s; }));
    }
    return q;
  }

  function deriv(arr, dt) {
    var d = [];
    for (var i = 0; i < arr.length; i++) {
      if (i === 0) d.push(arr.map(function() { return 0; }));
      else if (i === arr.length - 1) d.push(arr.map(function() { return 0; }));
      else d.push(arr[i].map(function(v, j) { return (arr[i+1][j] - arr[i-1][j]) / (2 * dt); }));
    }
    return d;
  }

  function drawChart(canvasId, t, linData, cubData, label, linColor, cubColor, showBoth) {
    var canvas = document.getElementById(canvasId);
    var rect = canvas.parentElement.getBoundingClientRect();
    var dpr = window.devicePixelRatio || 1;
    var w = Math.max(200, rect.width - 4);
    var h = 180;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    var pad = { top: 15, right: 10, bottom: 22, left: 40 };
    var pw = w - pad.left - pad.right;
    var ph = h - pad.top - pad.bottom;

    function getRange(data) {
      var min = Infinity, max = -Infinity;
      data.forEach(function(row) { row.forEach(function(v) {
        if (v < min) min = v; if (v > max) max = v;
      }); });
      var margin = (max - min) * 0.1 || 1;
      return { min: min - margin, max: max + margin };
    }

    var allData = [];
    if (showBoth !== 'cubic' && linData) allData = allData.concat(linData);
    if (showBoth !== 'linear' && cubData) allData = allData.concat(cubData);
    var rng = getRange(allData);

    function toPixel(val) {
      var x = pad.left + ((val - t[0]) / (t[t.length-1] - t[0])) * pw;
      var y = pad.top + ((rng.max - val) / (rng.max - rng.min)) * ph;
      return { x: x, y: y };
    }

    // Grid
    ctx.strokeStyle = '#e9ecf0';
    ctx.lineWidth = 1;
    for (var i = 0; i <= 4; i++) {
      var y = pad.top + (i / 4) * ph;
      ctx.beginPath(); ctx.moveTo(pad.left, y); ctx.lineTo(w - pad.right, y); ctx.stroke();
      var val = rng.max - (i / 4) * (rng.max - rng.min);
      ctx.fillStyle = '#88909c';
      ctx.font = '9px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(val.toFixed(1), pad.left - 3, y + 3);
    }
    for (var i = 0; i <= 4; i++) {
      var x = pad.left + (i / 4) * pw;
      ctx.beginPath(); ctx.moveTo(x, pad.top); ctx.lineTo(x, pad.top + ph); ctx.stroke();
      var val = t[0] + (i / 4) * (t[t.length-1] - t[0]);
      ctx.fillStyle = '#88909c';
      ctx.font = '9px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(val.toFixed(1), x, pad.top + ph + 14);
    }

    function drawLine(data, color) {
      if (!data || data.length < 2) return;
      JOINTS.forEach(function(j, ji) {
        ctx.strokeStyle = color;
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = 0.4 + 0.15 * ji;
        ctx.beginPath();
        data.forEach(function(row, i) {
          var p = toPixel(t[i], row[ji]);
          // Override - we use the index for x, value for y
          var px = pad.left + (i / (data.length - 1)) * pw;
          var py = pad.top + ((rng.max - row[ji]) / (rng.max - rng.min)) * ph;
          if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
        });
        ctx.stroke();
      });
      ctx.globalAlpha = 1;
    }

    if (showBoth !== 'cubic') drawLine(linData, '#2b6cb0');
    if (showBoth !== 'linear') drawLine(cubData, '#e53e3e');

    // Legend
    ctx.font = '9px sans-serif';
    if (linData && showBoth !== 'cubic') {
      ctx.fillStyle = '#2b6cb0';
      ctx.fillRect(pad.left + 4, pad.top + 2, 10, 2);
      ctx.fillText('Lineal', pad.left + 17, pad.top + 6);
    }
    if (cubData && showBoth !== 'linear') {
      ctx.fillStyle = '#e53e3e';
      ctx.fillRect(pad.left + 60, pad.top + 2, 10, 2);
      ctx.fillText('Cúbica', pad.left + 73, pad.top + 6);
    }

    // Axis labels
    ctx.fillStyle = '#88909c';
    ctx.font = '8px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Tiempo (s)', pad.left + pw / 2, h - 2);
  }

  document.getElementById('runTrajBtn').onclick = function() {
    if (trajRunning) return;
    var startIdx = parseInt(document.getElementById('trajStartSelect').value);
    var endIdx = parseInt(document.getElementById('trajEndSelect').value);
    var duration = parseFloat(document.getElementById('trajDuration').value);
    var method = document.getElementById('trajMethod').value;

    var q0 = TRAJ_CONFIGS[startIdx].vals;
    var qf = TRAJ_CONFIGS[endIdx].vals;
    var freq = 50;
    var n = Math.round(freq * duration);
    var dt = 1 / freq;
    var t = [];
    for (var i = 0; i < n; i++) t.push(i * dt);

    var q_lin = method !== 'cubic' ? linTraj(q0, qf, n) : null;
    var q_cub = method !== 'linear' ? cubTraj(q0, qf, n) : null;

    var vel_lin = q_lin ? deriv(q_lin, dt) : null;
    var vel_cub = q_cub ? deriv(q_cub, dt) : null;
    var acc_lin = vel_lin ? deriv(vel_lin, dt) : null;
    var acc_cub = vel_cub ? deriv(vel_cub, dt) : null;

    // Compute metrics
    function maxAbs(arr) {
      if (!arr || arr.length === 0) return 0;
      var m = 0;
      arr.forEach(function(row) { row.forEach(function(v) { if (Math.abs(v) > m) m = Math.abs(v); }); });
      return m;
    }
    if (q_lin) {
      document.getElementById('linVelMax').textContent = maxAbs(vel_lin).toFixed(1) + ' \u00b0/s';
      document.getElementById('linAccMax').textContent = maxAbs(acc_lin).toFixed(1) + ' \u00b0/s\u00b2';
      document.getElementById('linJerkMax').textContent = maxAbs(deriv(acc_lin, dt)).toFixed(1) + ' \u00b0/s\u00b3';
    }
    if (q_cub) {
      document.getElementById('cubVelMax').textContent = maxAbs(vel_cub).toFixed(1) + ' \u00b0/s';
      document.getElementById('cubAccMax').textContent = maxAbs(acc_cub).toFixed(1) + ' \u00b0/s\u00b2';
      document.getElementById('cubJerkMax').textContent = maxAbs(deriv(acc_cub, dt)).toFixed(1) + ' \u00b0/s\u00b3';
    }

    // Draw charts
    drawChart('trajPosCanvas', t, q_lin, q_cub, 'Posición', '#2b6cb0', '#e53e3e', method);
    drawChart('trajVelCanvas', t, vel_lin, vel_cub, 'Velocidad', '#2b6cb0', '#e53e3e', method);
    drawChart('trajAccCanvas', t, acc_lin, acc_cub, 'Aceleración', '#2b6cb0', '#e53e3e', method);

    // Log
    var el = document.getElementById('act9Log');
    var ts = new Date().toTimeString().slice(0,8);
    var txt = q0.map(function(v) { return v.toFixed(0); }).join(',') + ' \u2192 ' + qf.map(function(v) { return v.toFixed(0); }).join(',');
    el.innerHTML = '<div><span class="time">' + ts + '</span> Trayectoria calculada: ' + txt + ' (' + duration + 's, ' + method + ')</div>' + el.innerHTML;

    // Execute
    var doExec = confirm('\u00bfEjecutar trayectoria en el robot?');
    if (doExec) {
      trajRunning = true;
      document.getElementById('runTrajBtn').disabled = true;

      function sendTraj(data, label, callback) {
        var i = 0;
        function step() {
          if (i >= data.length || !trajRunning) { callback(); return; }
          var pos = JOINTS.map(function(j, ji) { return rad(data[i][ji]); });
          fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ name: JOINTS, position: pos })
          });
          i++;
          setTimeout(step, 20);
        }
        step();
      }

      var completeCount = 0;
      function onDone() {
        completeCount++;
        if ((method === 'both' && completeCount >= 2) || (method !== 'both' && completeCount >= 1)) {
          trajRunning = false;
          document.getElementById('runTrajBtn').disabled = false;
          el.innerHTML = '<div><span class="time">' + new Date().toTimeString().slice(0,8) + '</span> Trayectoria ejecutada</div>' + el.innerHTML;
        }
      }

      if (q_lin) sendTraj(q_lin, 'Lineal', onDone);
      if (q_cub) setTimeout(function() { sendTraj(q_cub, 'Cúbica', onDone); }, q_lin ? (duration * 1000 + 500) : 0);
    }
  };

  document.getElementById('homeAct9Btn').onclick = function() {
    trajRunning = false;
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}

/* Error logger visible */
var errorLog = document.createElement('div');
errorLog.id = 'jsErrorLog';
errorLog.style.cssText = 'position:fixed;bottom:0;left:0;right:0;background:#c53030;color:#fff;padding:8px;font-size:12px;font-family:monospace;z-index:9999;max-height:200px;overflow:auto;display:none;';
document.body.appendChild(errorLog);

function logJSError(msg, source) {
  var el = document.getElementById('jsErrorLog');
  el.style.display = 'block';
  var d = new Date();
  el.innerHTML = '<div>[' + d.toTimeString().slice(0,8) + '] <strong>'+source+':</strong> ' + msg + '</div>' + el.innerHTML;
}

window.onerror = function(msg, url, line, col, err) {
  logJSError(msg + ' (line ' + line + ')', 'GLOBAL');
  return true;
};

// Catch unhandled promise rejections
window.addEventListener('unhandledrejection', function(e) {
  logJSError(e.reason ? (e.reason.message || e.reason) : 'Promise rejected', 'PROMISE');
});

/* Dance tab — browser audio + Act 7 presets */
var danceData = null;
var danceTimer = null;

function buildDance() {
  var startBtn = document.getElementById('danceStartBtn');
  var stopBtn = document.getElementById('danceStopBtn');
  var statusEl = document.getElementById('danceStatus');

  function setButtons(dancing) {
    startBtn.disabled = dancing;
    stopBtn.disabled = !dancing;
  }

  function addDanceLog(msg) {
    var el = document.getElementById('danceLog');
    var d = new Date();
    el.innerHTML = '<div><span class="time">' + d.toTimeString().slice(0,8) + '</span>' + msg + '</div>' + el.innerHTML;
  }

  function lerp(a, b, t) { return a + (b - a) * t; }

  function getDancePose(beatIdx, totalBeats) {
    var cycleLen = 5;
    var rawIdx = beatIdx % cycleLen;
    var nextIdx = (rawIdx + 1) % cycleLen;
    var phase = (beatIdx / cycleLen) * 2 * Math.PI;
    var blend = 0.5 + 0.5 * Math.sin(phase);
    var presets = ACT7_PRESETS;
    var vals = [];
    for (var i = 0; i < 5; i++) {
      vals.push(lerp(presets[rawIdx].vals[i], presets[nextIdx].vals[i], blend));
    }
    return { vals: vals, name: presets[rawIdx].name + ' → ' + presets[nextIdx].name };
  }

  function sendPose(vals) {
    var pos = vals.map(function(v) { return rad(v); });
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: pos })
    }).catch(function() {});
  }

  function startDanceCycle(beatTimes, duration) {
    var audio = new Audio('/api/dance/audio?' + Date.now());
    var total = beatTimes.length;
    var stopped = false;
    var lastPoseIdx = -1;

    function onStop() {
      if (!stopped) {
        stopped = true;
        audio.pause();
        audio = null;
        setButtons(false);
        statusEl.textContent = 'Detenido';
        addDanceLog('Baile detenido');
        if (danceTimer) { clearInterval(danceTimer); danceTimer = null; }
      }
    }

    stopBtn.onclick = onStop;
    statusEl.textContent = 'Bailando...';
    addDanceLog('Iniciando (' + total + ' beats, ' + duration.toFixed(1) + 's)');

    audio.play().then(function() {
      if (danceTimer) clearInterval(danceTimer);
      danceTimer = setInterval(function() {
        if (stopped || !audio) { clearInterval(danceTimer); danceTimer = null; return; }
        var ct = audio.currentTime;
        for (var i = lastPoseIdx + 1; i < beatTimes.length; i++) {
          if (ct >= beatTimes[i] - 0.04) {
            var pose = getDancePose(i, total);
            sendPose(pose.vals);
            lastPoseIdx = i;
            document.getElementById('dancePoseName').textContent = pose.name;
            document.getElementById('danceProgress').textContent = (i + 1) + ' / ' + total;
          }
        }
        if (audio.ended || lastPoseIdx >= total - 2) {
          clearInterval(danceTimer); danceTimer = null;
          setButtons(false);
          statusEl.textContent = 'Baile terminado';
          document.getElementById('danceProgress').textContent = 'Completado';
          addDanceLog('Baile finalizado');
          stopBtn.onclick = function() {};
        }
      }, 40);
    }).catch(function(e) {
      statusEl.textContent = 'Error al reproducir audio';
      addDanceLog('Error audio: ' + e.message);
      setButtons(false);
    });
  }

  startBtn.onclick = function() {
    setButtons(true);
    statusEl.textContent = 'Analizando canción...';
    addDanceLog('Analizando (puede tomar varios segundos)...');
    fetch('/api/dance/start', { method: 'POST' })
      .then(function(r) { return r.json(); })
      .then(function(d) {
        if (d.status === 'error') {
          statusEl.textContent = 'Error: ' + d.msg;
          addDanceLog('Error: ' + d.msg);
          setButtons(false);
          return;
        }
        var r = d.result;
        document.getElementById('danceSongName').textContent = r.song;
        document.getElementById('danceTempo').textContent = r.tempo + ' BPM';
        document.getElementById('danceBeats').textContent = r.total_beats;
        statusEl.textContent = 'Reproduciendo...';
        addDanceLog('Tempo: ' + r.tempo + ' BPM | ' + r.total_beats + ' beats');
        // Home first
        fetch('/api/command', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
        }).catch(function() {});
        setTimeout(function() { startDanceCycle(r.beat_times, r.duration); }, 500);
      })
      .catch(function(e) {
        statusEl.textContent = 'Error de conexión';
        addDanceLog('Error red: ' + e.message);
        setButtons(false);
      });
  };
}

function buildSinusoidal() {
  var jointSel = document.getElementById('sinJointSelect');
  JOINTS.forEach(function(j) {
    var o = document.createElement('option');
    o.value = j;
    o.textContent = LABELS[j] + ' (' + j + ')';
    jointSel.appendChild(o);
  });
  jointSel.value = 'shoulder';

  var sinRunning = false;
  var sinStopFlag = false;
  var sinAllResults = [];

  function sinLog(msg) {
    var el = document.getElementById('sinLog');
    var ts = new Date().toTimeString().slice(0,8);
    el.innerHTML = '<div><span class="time">' + ts + '</span> ' + msg + '</div>' + el.innerHTML;
  }

  function sinDrawChart(t, qDesired, qMeasured, maxErr, rmse, testName) {
    var canvas = document.getElementById('sinPosCanvas');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    var w = Math.max(200, rect.width - 4);
    var h = 200;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.clearRect(0, 0, w, h);

    var pad = { top: 15, right: 10, bottom: 22, left: 42 };
    var pw = w - pad.left - pad.right;
    var ph = h - pad.top - pad.bottom;

    // Determine range
    var allVals = qDesired.concat(qMeasured);
    var minV = Math.min.apply(null, allVals);
    var maxV = Math.max.apply(null, allVals);
    var margin = (maxV - minV) * 0.1 || 5;
    minV -= margin;
    maxV += margin;

    function toY(v) { return pad.top + ((maxV - v) / (maxV - minV)) * ph; }
    function toX(i) { return pad.left + (i / (t.length - 1)) * pw; }

    // Grid
    ctx.strokeStyle = '#e9ecf0';
    ctx.lineWidth = 1;
    for (var g = 0; g <= 4; g++) {
      var gy = pad.top + (g / 4) * ph;
      ctx.beginPath(); ctx.moveTo(pad.left, gy); ctx.lineTo(w - pad.right, gy); ctx.stroke();
      var gv = maxV - (g / 4) * (maxV - minV);
      ctx.fillStyle = '#88909c';
      ctx.font = '9px sans-serif';
      ctx.textAlign = 'right';
      ctx.fillText(gv.toFixed(1), pad.left - 3, gy + 3);
    }
    for (var g = 0; g <= 4; g++) {
      var gx = pad.left + (g / 4) * pw;
      ctx.beginPath(); ctx.moveTo(gx, pad.top); ctx.lineTo(gx, pad.top + ph); ctx.stroke();
      var gtv = t[0] + (g / 4) * (t[t.length-1] - t[0]);
      ctx.fillStyle = '#88909c';
      ctx.font = '9px sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(gtv.toFixed(1), gx, pad.top + ph + 14);
    }

    // Desired (solid line)
    ctx.strokeStyle = '#2b6cb0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (var i = 0; i < qDesired.length; i++) {
      var x = toX(i);
      var y = toY(qDesired[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    // Measured (dashed)
    ctx.strokeStyle = '#e53e3e';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([4, 3]);
    ctx.beginPath();
    for (var i = 0; i < qMeasured.length; i++) {
      var x = toX(i);
      var y = toY(qMeasured[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);

    // Shade error area
    ctx.fillStyle = 'rgba(229,62,62,0.08)';
    ctx.beginPath();
    for (var i = 0; i < qDesired.length; i++) {
      var x = toX(i);
      var y = toY(qDesired[i]);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    for (var i = qMeasured.length - 1; i >= 0; i--) {
      var x = toX(i);
      var y = toY(qMeasured[i]);
      ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.fill();

    // Legend
    ctx.font = '9px sans-serif';
    ctx.fillStyle = '#2b6cb0';
    ctx.fillRect(pad.left + 4, pad.top + 2, 12, 2);
    ctx.fillText('Deseada', pad.left + 19, pad.top + 6);
    ctx.fillStyle = '#e53e3e';
    ctx.fillRect(pad.left + 64, pad.top + 2, 12, 2);
    ctx.fillText('Medida', pad.left + 79, pad.top + 6);
    ctx.fillStyle = '#88909c';
    ctx.textAlign = 'center';
    ctx.fillText('Tiempo (s)', pad.left + pw / 2, h - 2);

    // Title
    ctx.fillStyle = '#1a365d';
    ctx.font = 'bold 10px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(testName, pad.left, pad.top - 2);
  }

  function sinSingleTest(joint, ampDeg, freqHz, periods, fs, callback) {
    var q0 = 0;
    var traj = sinTraj(q0, ampDeg, freqHz, periods, fs);
    var qt = traj.t;
    var qd = traj.q;
    var qm = [];
    var n = qd.length;
    var dt = 1 / fs;
    var i = 0;
    var errInfo = null;

    document.getElementById('sinTestName').textContent = 'A=' + ampDeg + '\u00b0 f=' + freqHz + 'Hz';

    function step() {
      if (sinStopFlag || i >= n) {
        if (!sinStopFlag && i >= n) {
          errInfo = computeErrors(qd, qm);
          sinDrawChart(qt, qd, qm, errInfo.maxErr, errInfo.rmse, 'A=' + ampDeg + '\u00b0 f=' + freqHz + 'Hz');
          document.getElementById('sinMaxErr').textContent = errInfo.maxErr.toFixed(2) + '\u00b0';
          document.getElementById('sinRmse').textContent = errInfo.rmse.toFixed(2) + '\u00b0';
          document.getElementById('sinProgress').textContent = 'Completado';
          sinLog('Prueba A=' + ampDeg + '\u00b0 f=' + freqHz + 'Hz: error m\u00e1x=' + errInfo.maxErr.toFixed(2) + '\u00b0 RMSE=' + errInfo.rmse.toFixed(2) + '\u00b0');
        }
        if (callback) callback(errInfo);
        return;
      }
      document.getElementById('sinProgress').textContent = (i + 1) + ' / ' + n;

      var qd_deg = qd[i];
      var qd_rad = rad(qd_deg);
      fetch('/api/command', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({ name: [joint], position: [qd_rad] })
      });

      // Record desired and poll actual
      setTimeout(function() {
        if (sinStopFlag) { if (callback) callback(null); return; }
        fetch('/api/state')
          .then(function(r) { return r.json(); })
          .then(function(state) {
            var posRad = state[joint] || 0;
            var posDeg = posRad / Math.PI * 180;
            qd.push(qd[i]); // maintain alignment
            qm.push(posDeg);
            i++;
            setTimeout(step, dt * 1000 - 10);
          })
          .catch(function() { qd.push(qd[i]); qm.push(0); i++; setTimeout(step, dt * 1000 - 10); });
      }, 5);
    }

    step();
  }

  function computeErrors(qd, qm) {
    var n = Math.min(qd.length, qm.length);
    if (n === 0) return { maxErr: 0, rmse: 0 };
    var maxErr = 0;
    var sumSq = 0;
    for (var i = 0; i < n; i++) {
      var e = Math.abs(qd[i] - qm[i]);
      if (e > maxErr) maxErr = e;
      sumSq += e * e;
    }
    return { maxErr: maxErr, rmse: Math.sqrt(sumSq / n) };
  }

  function sinRunAll() {
    if (sinRunning) return;
    sinRunning = true;
    sinStopFlag = false;
    sinAllResults = [];
    document.getElementById('sinStartAllBtn').disabled = true;
    document.getElementById('sinStartBtn').disabled = true;
    document.getElementById('sinStopBtn').disabled = false;
    document.getElementById('sinSummaryRows').innerHTML = '';

    var joint = jointSel.value;
    var tests = [
      { amp: 30, freq: 0.25, periods: 2 },
      { amp: 30, freq: 0.50, periods: 2 },
      { amp: 60, freq: 0.25, periods: 2 },
      { amp: 60, freq: 0.50, periods: 2 }
    ];
    var idx = 0;

    function nextTest() {
      if (idx >= tests.length || sinStopFlag) {
        sinRunning = false;
        document.getElementById('sinStartAllBtn').disabled = false;
        document.getElementById('sinStartBtn').disabled = false;
        document.getElementById('sinStopBtn').disabled = true;
        if (sinStopFlag) sinLog('Pruebas detenidas por el usuario.');
        else sinLog('4 pruebas completadas.');
        return;
      }
      var test = tests[idx];
      document.getElementById('sinProgress').textContent = 'Prueba ' + (idx+1) + ' / 4';
      sinSingleTest(joint, test.amp, test.freq, test.periods, 50, function(errInfo) {
        if (errInfo) {
          sinAllResults.push({
            name: 'A=' + test.amp + '\u00b0 f=' + test.freq + 'Hz',
            amp: test.amp,
            freq: test.freq,
            maxErr: errInfo.maxErr,
            rmse: errInfo.rmse
          });
          updateSummaryTable();
        }
        idx++;
        setTimeout(nextTest, 500);
      });
    }

    nextTest();
  }

  function sinRunSingle() {
    if (sinRunning) return;
    sinRunning = true;
    sinStopFlag = false;
    document.getElementById('sinStartAllBtn').disabled = true;
    document.getElementById('sinStartBtn').disabled = true;
    document.getElementById('sinStopBtn').disabled = false;

    var joint = jointSel.value;
    var amp = parseFloat(document.getElementById('sinAmpSelect').value);
    var freq = parseFloat(document.getElementById('sinFreqSelect').value);

    sinSingleTest(joint, amp, freq, 2, 50, function(errInfo) {
      sinRunning = false;
      document.getElementById('sinStartAllBtn').disabled = false;
      document.getElementById('sinStartBtn').disabled = false;
      document.getElementById('sinStopBtn').disabled = true;
      if (errInfo) sinLog('Prueba individual completada.');
    });
  }

  function updateSummaryTable() {
    var container = document.getElementById('sinSummaryRows');
    container.innerHTML = '';
    sinAllResults.forEach(function(r) {
      var row = document.createElement('div');
      row.style.cssText = 'display:grid;grid-template-columns:1fr 100px 100px 100px 100px;gap:4px;padding:3px 0;border-bottom:1px solid var(--border-light);';
      row.innerHTML = '<div>' + r.name + '</div><div>' + r.amp + '\u00b0</div><div>' + r.freq + ' Hz</div><div style="color:var(--accent);">' + r.maxErr.toFixed(2) + '\u00b0</div><div style="color:var(--accent);">' + r.rmse.toFixed(2) + '\u00b0</div>';
      container.appendChild(row);
    });
  }

  document.getElementById('sinStartBtn').onclick = sinRunSingle;
  document.getElementById('sinStartAllBtn').onclick = sinRunAll;
  document.getElementById('sinStopBtn').onclick = function() {
    sinStopFlag = true;
    document.getElementById('sinStopBtn').disabled = true;
    sinLog('Deteniendo...');
  };
  document.getElementById('sinHomeBtn').onclick = function() {
    sinStopFlag = true;
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}

/* Act 14 — Trazado */
var trRunning = false;
var trStopFlag = false;

/* IK for Phantom X Pincher — grid search over FK */
var L0 = 0.089, L1 = 0.101, L2 = 0.101, L3 = 0.119;
var MAX_REACH = L1 + L2 + L3;

function trIk(x, y, z) {
  var q1 = Math.atan2(y, x) * 180 / Math.PI;
  var r = Math.sqrt(x*x + y*y);
  var zRel = z - L0;
  var dTcp = Math.sqrt(r*r + zRel*zRel);
  if (dTcp > MAX_REACH + 0.005) return null;

  var limits = [[-150,150],[-120,120],[-139,139],[-98,103],[-90,90]];
  var best = null, bestErr = 1e9;
  var step = 5;
  for (var q2d = limits[1][0]; q2d <= limits[1][1]; q2d += step) {
    for (var q3d = limits[2][0]; q3d <= limits[2][1]; q3d += step) {
      for (var q4d = limits[3][0]; q4d <= limits[3][1]; q4d += step) {
        var tcp = trFk([q1, q2d, q3d, q4d]);
        var err = (tcp.x-x)*(tcp.x-x) + (tcp.y-y)*(tcp.y-y) + (tcp.z-z)*(tcp.z-z);
        if (err < bestErr) { bestErr = err; best = [q1, q2d, q3d, q4d, 0]; }
      }
    }
  }
  return best;
}

/* FK for Phantom X Pincher — Bioloid matrix chain */
var PI = Math.PI;
var aw = 0.038, ah = 0.032, fh = 0.0525, f10h = 0.004, f2h = 0.0265, fo = 0.001, fx = 0.019, fy = 0.0115;

function trFk(qDeg) {
  var q = qDeg.map(function(v) { return v * PI / 180; });
  var M = [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]];

  function Rx(a) { var ca=Math.cos(a), sa=Math.sin(a); return [[1,0,0],[0,ca,-sa],[0,sa,ca]]; }
  function Ry(a) { var ca=Math.cos(a), sa=Math.sin(a); return [[ca,0,sa],[0,1,0],[-sa,0,ca]]; }
  function Rz(a) { var ca=Math.cos(a), sa=Math.sin(a); return [[ca,-sa,0],[sa,ca,0],[0,0,1]]; }
  function rpy(r,p,y) { return mul33(Rz(y), mul33(Ry(p), Rx(r))); }
  function mul33(A,B) { return [[A[0][0]*B[0][0]+A[0][1]*B[1][0]+A[0][2]*B[2][0], A[0][0]*B[0][1]+A[0][1]*B[1][1]+A[0][2]*B[2][1], A[0][0]*B[0][2]+A[0][1]*B[1][2]+A[0][2]*B[2][2]], [A[1][0]*B[0][0]+A[1][1]*B[1][0]+A[1][2]*B[2][0], A[1][0]*B[0][1]+A[1][1]*B[1][1]+A[1][2]*B[2][1], A[1][0]*B[0][2]+A[1][1]*B[1][2]+A[1][2]*B[2][2]], [A[2][0]*B[0][0]+A[2][1]*B[1][0]+A[2][2]*B[2][0], A[2][0]*B[0][1]+A[2][1]*B[1][1]+A[2][2]*B[2][1], A[2][0]*B[0][2]+A[2][1]*B[1][2]+A[2][2]*B[2][2]]] }
  function mul4(A,B) { var R=[[],[],[],[]]; for(var i=0;i<4;i++) for(var j=0;j<4;j++) { var s=0; for(var k=0;k<4;k++) s+=A[i][k]*B[k][j]; R[i][j]=s; } return R; }
  function add(R,t) { var T=[[R[0][0],R[0][1],R[0][2],t[0]],[R[1][0],R[1][1],R[1][2],t[1]],[R[2][0],R[2][1],R[2][2],t[2]],[0,0,0,1]]; M = mul4(M,T); }

  add(rpy(PI/2,0,PI/2), [0,0,0]);
  add(rpy(-PI/2,PI/2,PI), [0,aw/2,0]);
  add(Rz(-q[0]), [0,0,0]);
  add(rpy(0,PI,0), [0,0,-ah-f10h+fo]);
  add(Ry(q[1]), [0,0,0]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,fh+f10h/2]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,f10h]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,f10h]);
  add(rpy(0,PI,0), [0,0,f10h/2]);
  add(rpy(0,PI,0), [0,0,-ah-f10h+fo]);
  add(Ry(q[2]), [0,0,0]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,fh+f10h/2]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,f10h]);
  add([[1,0,0],[0,1,0],[0,0,1]], [0,0,f10h]);
  add(rpy(0,PI,0), [0,0,f10h/2]);
  add(rpy(0,PI,0), [0,0,-ah-f10h+fo]);
  add(Ry(q[3]), [0,0,0]);
  add(rpy(0,PI,-PI), [0,0,f2h]);
  add(rpy(PI/2,PI,PI/2), [0,0,-aw/2]);
  add(rpy(PI,0,PI/2), [0,aw/2,0]);
  add(rpy(PI/2,-PI/2,PI/2), [fx,0,0]);

  var x = M[0][3], y = M[1][3], z = M[2][3];
  var R = [[M[0][0],M[0][1],M[0][2]],[M[1][0],M[1][1],M[1][2]],[M[2][0],M[2][1],M[2][2]]];
  var roll = Math.atan2(R[2][1], R[2][2]) * 180 / PI;
  var pitch = Math.atan2(-R[2][0], Math.sqrt(R[2][1]*R[2][1] + R[2][2]*R[2][2])) * 180 / PI;
  var yaw = Math.atan2(R[1][0], R[0][0]) * 180 / PI;
  return { x: x, y: y, z: z, roll: roll, pitch: pitch, yaw: yaw };
}

function buildTracing() {
  function trGenFig(shape, size, nEdge) {
    var pts = [];
    var verts;
    if (shape === 'triangle') {
      var h = size * Math.sqrt(3) / 2;
      // Vértices centrados en (0,0): apex arriba, base abajo
      verts = [[0, 2*h/3], [-size/2, -h/3], [size/2, -h/3]];
    } else {
      verts = [[-size/2, -size/2], [size/2, -size/2], [size/2, size/2], [-size/2, size/2]];
    }
    for (var i = 0; i < verts.length; i++) {
      var y0 = verts[i][0], z0 = verts[i][1];
      var y1 = verts[(i+1) % verts.length][0], z1 = verts[(i+1) % verts.length][1];
      var last = (i === verts.length - 1);
      var limit = last ? nEdge : nEdge - 1;
      for (var j = 0; j <= limit; j++) {
        var f = j / nEdge;
        pts.push({ wx: 0.13, wy: y0 + (y1-y0)*f, wz: 0.10 + z0 + (z1-z0)*f });
      }
    }
    return pts;
  }

  function trDraw(pts, actuals) {
    var canvas = document.getElementById('trCanvas');
    if (!canvas) return;
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.parentElement.getBoundingClientRect();
    var w = Math.max(300, rect.width - 4);
    var h = 350;
    canvas.width = w * dpr;
    canvas.height = h * dpr;
    canvas.style.width = w + 'px';
    canvas.style.height = h + 'px';
    var ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);
    ctx.fillStyle = '#fafafa';
    ctx.fillRect(0, 0, w, h);

    var allY = pts.map(function(p) { return p.wy; });
    var allZ = pts.map(function(p) { return p.wz; });
    if (actuals.length) {
      allY = allY.concat(actuals.map(function(p) { return p[0]; }));
      allZ = allZ.concat(actuals.map(function(p) { return p[1]; }));
    }
    var minY = Math.min.apply(null, allY), maxY = Math.max.apply(null, allY);
    var minZ = Math.min.apply(null, allZ), maxZ = Math.max.apply(null, allZ);
    var pad = 30;
    var rangeY = maxY - minY || 0.01;
    var rangeZ = maxZ - minZ || 0.01;
    rangeY *= 1.2; rangeZ *= 1.2;
    var cy = (minY + maxY) / 2;
    var cz = (minZ + maxZ) / 2;

    function toX(y) { return pad + ((y - cy + rangeY/2) / rangeY) * (w - 2*pad); }
    function toY(z) { return h - pad - ((z - cz + rangeZ/2) / rangeZ) * (h - 2*pad); }

    /* Grid */
    ctx.strokeStyle = '#e9ecf0';
    ctx.lineWidth = 1;
    for (var g = 0; g <= 4; g++) {
      var gy = pad + (g/4)*(h-2*pad);
      ctx.beginPath(); ctx.moveTo(pad, gy); ctx.lineTo(w-pad, gy); ctx.stroke();
    }
    for (var g = 0; g <= 4; g++) {
      var gx = pad + (g/4)*(w-2*pad);
      ctx.beginPath(); ctx.moveTo(gx, pad); ctx.lineTo(gx, h-pad); ctx.stroke();
    }

    /* Desired path */
    ctx.strokeStyle = '#2b6cb0';
    ctx.lineWidth = 2;
    ctx.beginPath();
    for (var i = 0; i < pts.length; i++) {
      var x = toX(pts[i].wy), y = toY(pts[i].wz);
      if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
    }
    ctx.stroke();

    /* Actual path */
    if (actuals.length > 1) {
      ctx.strokeStyle = '#e53e3e';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4,3]);
      ctx.beginPath();
      for (var i = 0; i < actuals.length; i++) {
        var x = toX(actuals[i][0]), y = toY(actuals[i][1]);
        if (i === 0) ctx.moveTo(x, y); else ctx.lineTo(x, y);
      }
      ctx.stroke();
      ctx.setLineDash([]);
    }

    /* Labels */
    ctx.fillStyle = '#88909c';
    ctx.font = '9px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Y (m)', w/2, h - 3);
    ctx.save();
    ctx.translate(8, h/2);
    ctx.rotate(-Math.PI/2);
    ctx.fillText('Z (m)', 0, 0);
    ctx.restore();

    /* Legend */
    ctx.fillStyle = '#2b6cb0';
    ctx.fillRect(pad+4, pad+2, 12, 2);
    ctx.fillStyle = '#1a365d';
    ctx.font = '9px sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Deseada', pad+19, pad+6);
    ctx.fillStyle = '#e53e3e';
    ctx.fillRect(pad+64, pad+2, 12, 2);
    ctx.fillText('Real', pad+79, pad+6);
  }

  document.getElementById('trStartBtn').onclick = function() {
    if (trRunning) return;
    trRunning = true;
    trStopFlag = false;
    document.getElementById('trStartBtn').disabled = true;
    document.getElementById('trStopBtn').disabled = false;

    var shape = document.getElementById('trFigSelect').value;
    var size = parseFloat(document.getElementById('trSizeSelect').value);
    var figName = shape === 'triangle' ? 'Tri\u00e1ngulo' : 'Cuadrado';
    document.getElementById('trFigName').textContent = figName + ' ' + (size*100) + ' cm';

    var pts = trGenFig(shape, size, 30);
    var total = pts.length;
    if (total === 0) { trRunning = false; return; }
    var i = 0;
    var actuals = [];
    trDraw(pts, []);
    document.getElementById('trProgress').textContent = 'Moviendo al inicio...';

    // Clear old RViz trajectory
    fetch('/api/trajectory', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ points: [] })
    });
    var logEl = document.getElementById('trLog');
    var ts = new Date().toTimeString().slice(0,8);
    logEl.innerHTML = '<div><span class="time">' + ts + '</span> Iniciando trazado de ' + figName + ' ' + (size*100) + ' cm</div>' + logEl.innerHTML;

    /* Mover al primer punto antes de empezar a registrar la trayectoria */
    function moveToStart() {
      var first = pts[0];
      var qFirst = trIk(first.wx, first.wy, first.wz);
      console.log('moveToStart IK:', first.wx.toFixed(3), first.wy.toFixed(3), first.wz.toFixed(3), '→', qFirst ? qFirst.map(function(v){return v.toFixed(1)}) : 'NULL');
      if (qFirst) {
        var pos = JOINTS.map(function(j, idx) { return qFirst[idx] * Math.PI / 180; });
        fetch('/api/command', {
          method: 'POST',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ name: JOINTS, position: pos })
        });
      }
      setTimeout(startLoop, 600);
    }

    function pollActual() {
      fetch('/api/track_tcp', {method:'POST'}).catch(function(){});
      fetch('/api/state').then(function(r) { return r.json(); }).then(function(s) {
        var qDeg = JOINTS.map(function(j) { return (s[j]||0) * 180 / Math.PI; });
        var tcp = trFk(qDeg);
        actuals.push([tcp.y, tcp.z, tcp.x]);
      }).catch(function() {});
    }

    function startLoop() {
      pollActual();
      i = 1;
      trDraw(pts, []);
      /* Muestrear posición cada 100ms mientras se envían comandos */
      var sampleTimer = setInterval(pollActual, 100);
      /* Enviar comandos rápido */
      function sendCmd() {
        if (trStopFlag || i >= total) {
          /* No detener el timer aún: la cola sigue procesando */
          setTimeout(function() {
            pollActual();
            setTimeout(function() {
              clearInterval(sampleTimer);
              pollActual();
              setTimeout(function() {
                trRunning = false;
                document.getElementById('trStartBtn').disabled = false;
                document.getElementById('trStopBtn').disabled = true;
                document.getElementById('trProgress').textContent = 'Completado';
                trDraw(pts, actuals);
                var ts2 = new Date().toTimeString().slice(0,8);
                logEl.innerHTML = '<div><span class="time">' + ts2 + '</span> Trazado completado (' + total + ' puntos)</div>' + logEl.innerHTML;
                // Publish trajectory from TF points stored on server
                fetch('/api/trajectory', {
                  method: 'POST',
                  headers: {'Content-Type':'application/json'},
                  body: JSON.stringify({ points: [] })
                });
              }, 200);
            }, 100);
          }, 3000);
          return;
        }
        var pt = pts[i];
        var q = trIk(pt.wx, pt.wy, pt.wz);
        if (q) {
          var pos = JOINTS.map(function(j, idx) { return q[idx] * Math.PI / 180; });
          fetch('/api/command', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({ name: JOINTS, position: pos })
          });
        }
        i++;
        document.getElementById('trPoint').textContent = i + ' / ' + total;
        document.getElementById('trProgress').textContent = Math.round(((i-1)/total)*100) + '%';
        setTimeout(sendCmd, 20);
      }
      sendCmd();
    }

    moveToStart();
  };

  document.getElementById('trStopBtn').onclick = function() {
    trStopFlag = true;
    document.getElementById('trStopBtn').disabled = true;
  };

  document.getElementById('trHomeBtn').onclick = function() {
    trStopFlag = true;
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}

/* Act 11 — FK */
function buildAct11() {
  document.getElementById('fkCalcBtn').onclick = function() {
    var q1 = parseFloat(document.getElementById('fkQ1').value) || 0;
    var q2 = parseFloat(document.getElementById('fkQ2').value) || 0;
    var q3 = parseFloat(document.getElementById('fkQ3').value) || 0;
    var q4 = parseFloat(document.getElementById('fkQ4').value) || 0;
    var qDeg = [q1, q2, q3, q4];
    var tcp = trFk(qDeg);
    if (!tcp) { document.getElementById('fkX').textContent = '—'; return; }
    document.getElementById('fkX').textContent = (tcp.x * 1000).toFixed(1);
    document.getElementById('fkY').textContent = (tcp.y * 1000).toFixed(1);
    document.getElementById('fkZ').textContent = (tcp.z * 1000).toFixed(1);
    var roll = Math.atan2(tcp.ry || 0, tcp.rz || 0);
    document.getElementById('fkRoll').textContent = tcp.roll.toFixed(1);
    document.getElementById('fkPitch').textContent = tcp.pitch.toFixed(1);
    document.getElementById('fkYaw').textContent = tcp.yaw.toFixed(1);
    var el = document.getElementById('fkLog');
    var ts = new Date().toTimeString().slice(0,8);
    el.innerHTML = '<div><span class="time">' + ts + '</span> FK: q=[' + q1.toFixed(1) + ',' + q2.toFixed(1) + ',' + q3.toFixed(1) + ',' + q4.toFixed(1) + '] &rarr; TCP (' + (tcp.x*1000).toFixed(1) + ', ' + (tcp.y*1000).toFixed(1) + ', ' + (tcp.z*1000).toFixed(1) + ') mm</div>' + el.innerHTML;
  };
  document.getElementById('fkSendBtn').onclick = function() {
    var q1 = parseFloat(document.getElementById('fkQ1').value) || 0;
    var q2 = parseFloat(document.getElementById('fkQ2').value) || 0;
    var q3 = parseFloat(document.getElementById('fkQ3').value) || 0;
    var q4 = parseFloat(document.getElementById('fkQ4').value) || 0;
    var pos = [rad(q1), rad(q2), rad(q3), rad(q4), 0];
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: pos })
    }).then(function(r) { return r.json(); }).then(function(d) {
      var el = document.getElementById('fkLog');
      var ts = new Date().toTimeString().slice(0,8);
      el.innerHTML = '<div><span class="time">' + ts + '</span> FK enviado al robot</div>' + el.innerHTML;
    });
  };
  document.getElementById('fkHomeBtn').onclick = function() {
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}
/* Act 12 — IK */
function buildAct12() {
  document.getElementById('ikX').value = 130;
  document.getElementById('ikY').value = 0;
  document.getElementById('ikZ').value = 100;
  document.getElementById('ikCalcBtn').onclick = function() {
    var x_mm = parseFloat(document.getElementById('ikX').value) || 0;
    var y_mm = parseFloat(document.getElementById('ikY').value) || 0;
    var z_mm = parseFloat(document.getElementById('ikZ').value) || 0;
    console.log('IK input mm:', x_mm, y_mm, z_mm);
    var x_m = x_mm/1000, y_m = y_mm/1000, z_m = z_mm/1000;
    console.log('IK input m:', x_m, y_m, z_m);
    console.log('L0,L1,L2,L3:', L0, L1, L2, L3);
    var q = trIk(x_m, y_m, z_m);
    console.log('trIk result:', q);
    var errEl = document.getElementById('ikError');
    if (!q) {
      errEl.textContent = 'Sin soluci&oacute;n v&aacute;lida (fuera del espacio de trabajo o l&iacute;mites)';
      return;
    }
    errEl.textContent = 'Soluci&oacute;n v&aacute;lida';
    document.getElementById('ikQ1').textContent = q[0].toFixed(1);
    document.getElementById('ikQ2').textContent = q[1].toFixed(1);
    document.getElementById('ikQ3').textContent = q[2].toFixed(1);
    document.getElementById('ikQ4').textContent = q[3].toFixed(1);
    var el = document.getElementById('ikLog');
    var ts = new Date().toTimeString().slice(0,8);
    el.innerHTML = '<div><span class="time">' + ts + '</span> IK: (' + x_mm + ', ' + y_mm + ', ' + z_mm + ') mm &rarr; q=[' + q.map(function(v){return v.toFixed(1);}).join(',') + ']&deg;</div>' + el.innerHTML;
  };
  document.getElementById('ikSendBtn').onclick = function() {
    var x_mm = parseFloat(document.getElementById('ikX').value) || 0;
    var y_mm = parseFloat(document.getElementById('ikY').value) || 0;
    var z_mm = parseFloat(document.getElementById('ikZ').value) || 0;
    var q = trIk(x_mm/1000, y_mm/1000, z_mm/1000);
    if (!q) return;
    var pos = q.map(function(v) { return rad(v); });
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: pos })
    }).then(function(r) { return r.json(); }).then(function(d) {
      var el = document.getElementById('ikLog');
      var ts = new Date().toTimeString().slice(0,8);
      el.innerHTML = '<div><span class="time">' + ts + '</span> IK enviado al robot</div>' + el.innerHTML;
    });
  };
  document.getElementById('ikHomeBtn').onclick = function() {
    fetch('/api/command', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({ name: JOINTS, position: [0,0,0,0,0] })
    });
  };
}
/* Init */
try { buildAct4(); } catch(e) { logJSError(e.message, 'buildAct4'); }
try { buildAct7(); } catch(e) { logJSError(e.message, 'buildAct7'); }
try { buildAct8(); } catch(e) { logJSError(e.message, 'buildAct8'); }
try { buildAct9(); } catch(e) { logJSError(e.message, 'buildAct9'); }
try { buildAct13(); } catch(e) { logJSError(e.message, 'buildAct13'); }
try { buildDance(); } catch(e) { logJSError(e.message, 'buildDance'); }
try { buildSinusoidal(); } catch(e) { logJSError(e.message, 'buildSinusoidal'); }
try { buildTracing(); } catch(e) { logJSError(e.message, 'buildTracing'); }
try { buildAct11(); } catch(e) { logJSError(e.message, 'buildAct11'); }
try { buildAct12(); } catch(e) { logJSError(e.message, 'buildAct12'); }
try { poll(); } catch(e) { logJSError(e.message, 'poll'); }
</script>
</body>
</html>'''

def load_poses():
    global poses
    if yaml is None:
        return
    if not os.path.exists(POSES_FILE):
        return
    try:
        with open(POSES_FILE) as f:
            data = yaml.safe_load(f)
        if data and isinstance(data, list):
            with poses_lock:
                poses = data
    except Exception:
        pass

def save_poses():
    if yaml is None:
        return
    try:
        os.makedirs(os.path.dirname(POSES_FILE), exist_ok=True)
        with open(POSES_FILE, 'w') as f:
            yaml.dump(poses, f, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        print(f'[YAML] Error guardando poses: {e}')

class APIHandler(BaseHTTPRequestHandler):
    def __init__(self, node_ref, *args, **kwargs):
        self.node_ref = node_ref
        super().__init__(*args, **kwargs)

    def _set_headers(self, code=200, content_type='application/json'):
        self.send_response(code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed_path = urlparse(self.path).path
        if parsed_path == '/api/state':
            with state_lock:
                data = {name: current_state.get(name, 0.0) for name in JOINT_NAMES}
            self._set_headers()
            self.wfile.write(json.dumps(data).encode())
        elif parsed_path == '/api/poses':
            with poses_lock:
                data = {'poses': poses}
            self._set_headers()
            self.wfile.write(json.dumps(data).encode())
        elif parsed_path == '/api/dance/audio':
            if not os.path.exists(DANCE_MP3):
                self._set_headers(404)
                self.wfile.write(b'{"error":"mp3 not found"}')
                return
            self.send_response(200)
            self.send_header('Content-Type', 'audio/mpeg')
            self.send_header('Accept-Ranges', 'bytes')
            self.send_header('Content-Length', str(os.path.getsize(DANCE_MP3)))
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            with open(DANCE_MP3, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
        elif parsed_path == '/api/dance/status':
            result = get_dance_analysis()
            if 'error' in result:
                info = {'status': 'error', 'msg': result['error']}
            else:
                info = {'status': 'ready', 'result': result}
            self._set_headers()
            self.wfile.write(json.dumps(info).encode())
        elif parsed_path == '/api/status':
            with poses_lock:
                p = playback_running
                pt = playback_target
            self._set_headers()
            self.wfile.write(json.dumps(pt if p else
                {'playing': False, 'current': 0, 'total': 0, 'pose_name': '—'}).encode())
        elif parsed_path == '/' or parsed_path == '/index.html':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(HTML.encode('utf-8'))
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path == '/api/command':
            length = int(self.headers.get('Content-Length', 0))
            body = self.wfile if length == 0 else self.rfile.read(length)
            data = json.loads(body)
            names = data.get('name', [])
            positions = data.get('position', [])
            if not names or len(names) != len(positions):
                self._set_headers(400)
                self.wfile.write(b'{"status":"error","msg":"name/position mismatch"}')
                return
            for n, p in zip(names, positions):
                if n in JOINT_NAMES:
                    lim = JOINT_LIMITS_DEG[n]
                    deg_val = p / DEG
                    if deg_val < lim[0] or deg_val > lim[1]:
                        self._set_headers(400)
                        self.wfile.write(json.dumps(
                            {'status':'error','msg':f'{n}: {deg_val:.1f}° fuera de límites [{lim[0]},{lim[1]}]'}).encode())
                        return
            command_queue.put({'type': 'move', 'name': names, 'position': positions})
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')
        elif self.path == '/api/home':
            command_queue.put({'type': 'home'})
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/track_tcp':
            try:
                now = rclpy.time.Time()
                t = self.node_ref.tf_buffer.lookup_transform('base_link', 'end_effector', now,
                    timeout=rclpy.duration.Duration(seconds=0.3))
                p = [t.transform.translation.x, t.transform.translation.y, t.transform.translation.z]
                self.node_ref.traj_points.append(p)
            except Exception:
                pass
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/trajectory':
            length = int(self.headers.get('Content-Length', 0))
            body = self.wfile if length == 0 else self.rfile.read(length)
            data = json.loads(body)
            pts = data.get('points', [])
            if pts:
                command_queue.put({'type': 'trajectory', 'points': pts})
            else:
                # Publish from stored TF points
                command_queue.put({'type': 'trajectory', 'points': list(self.node_ref.traj_points)})
                self.node_ref.traj_points = []
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/poses':
            length = int(self.headers.get('Content-Length', 0))
            body = self.wfile if length == 0 else self.rfile.read(length)
            data = json.loads(body)
            name = data.get('name', '').strip()
            positions = data.get('positions', {})
            if not name:
                self._set_headers(400)
                self.wfile.write(b'{"status":"error","msg":"name required"}')
                return
            with poses_lock:
                poses.append({'name': name, 'positions': positions})
                save_poses()
                result = {'status': 'ok', 'poses': poses}
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())

        elif self.path == '/api/play':
            length = int(self.headers.get('Content-Length', 0))
            body = self.wfile if length == 0 else self.rfile.read(length)
            data = json.loads(body)
            trans = float(data.get('transition_time', 2.0))
            with poses_lock:
                if not poses:
                    self._set_headers(400)
                    self.wfile.write(b'{"status":"error","msg":"No hay poses guardadas"}')
                    return
                if playback_running:
                    self._set_headers(400)
                    self.wfile.write('{"status":"error","msg":"Ya está reproduciendo"}'.encode())
                    return
            playback_stop.clear()
            t = threading.Thread(target=playback_worker, args=(trans,), daemon=True)
            t.start()
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/stop':
            playback_stop.set()
            self._set_headers()
            self.wfile.write(b'{"status":"ok"}')

        elif self.path == '/api/dance/start':
            result = get_dance_analysis()
            if 'error' in result:
                self._set_headers(400)
                self.wfile.write(json.dumps({'status':'error','msg':result['error']}).encode())
            else:
                self._set_headers()
                self.wfile.write(json.dumps({'status':'ok', 'result': result}).encode())

        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_DELETE(self):
        if self.path == '/api/poses':
            with poses_lock:
                poses.clear()
                save_poses()
                result = {'status': 'ok', 'poses': poses}
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        elif self.path.startswith('/api/poses/'):
            try:
                idx = int(self.path.split('/')[-1])
            except (ValueError, IndexError):
                self._set_headers(400)
                self.wfile.write(b'{"error":"invalid index"}')
                return
            with poses_lock:
                if 0 <= idx < len(poses):
                    poses.pop(idx)
                    save_poses()
                    result = {'status': 'ok', 'poses': poses}
                else:
                    result = {'status': 'error', 'msg': 'index out of range'}
            self._set_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self._set_headers(404)
            self.wfile.write(b'{"error":"not found"}')

    def do_OPTIONS(self):
        self._set_headers(204)

def playback_worker(transition_time):
    global playback_running
    with poses_lock:
        local_poses = list(poses)
    if not local_poses:
        playback_running = False
        return
    playback_running = True
    node = getattr(playback_worker, 'node', None)
    if node is None:
        playback_running = False
        return

    total = len(local_poses)
    for i, pose in enumerate(local_poses):
        if playback_stop.is_set():
            break
        with poses_lock:
            playback_target['playing'] = True
            playback_target['current'] = i + 1
            playback_target['total'] = total
            playback_target['pose_name'] = pose['name']

        pos_list = []
        for j in JOINT_NAMES:
            deg_val = pose['positions'].get(j, 0.0)
            pos_list.append(deg_val * DEG)
        msg = JointState()
        msg.header.stamp = node.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = pos_list
        node.cmd_pub.publish(msg)
        node.get_logger().info(f'[Playback] Pose {i+1}/{total}: {pose["name"]}')

        if i < total - 1:
            for _ in range(int(transition_time / 0.1)):
                if playback_stop.is_set():
                    break
                time.sleep(0.1)
            else:
                time.sleep(transition_time % 0.1)

    playback_running = False
    with poses_lock:
        playback_target['playing'] = False
        playback_target['current'] = 0
        playback_target['total'] = 0
        playback_target['pose_name'] = '—'
    node.get_logger().info('[Playback] Reproducción finalizada')

def get_dance_analysis():
    global _dance_cache
    if _dance_cache is not None:
        return _dance_cache
    try:
        import librosa
        import numpy as np
    except ImportError as e:
        return {'error': f'Faltan dependencias: {e}'}
    if not os.path.exists(DANCE_MP3):
        return {'error': f'MP3 no encontrado: {DANCE_MP3}'}
    try:
        y, sr = librosa.load(DANCE_MP3, sr=None)
        duration = float(len(y) / sr)
        tempo_arr, beats = librosa.beat.beat_track(y=y, sr=sr)
        if isinstance(tempo_arr, (np.ndarray, list)):
            tempo_val = float(tempo_arr[0])
        else:
            tempo_val = float(tempo_arr)
        beat_times = librosa.frames_to_time(beats, sr=sr).tolist()
        _dance_cache = {
            'tempo': round(tempo_val, 1),
            'total_beats': len(beat_times),
            'beat_times': beat_times,
            'duration': round(duration, 2),
            'song': os.path.basename(DANCE_MP3),
        }
        return _dance_cache
    except Exception as e:
        return {'error': str(e)}

def http_server(node_ref, port=5050):
    handler = partial(APIHandler, node_ref)
    server = HTTPServer(('0.0.0.0', port), handler)
    server.allow_reuse_address = True
    print(f'[Web] Servidor en http://0.0.0.0:{port}')
    server.serve_forever()

class MovementNode(Node):
    def __init__(self):
        super().__init__('individual_movement')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)
        self.traj_pub = self.create_publisher(Marker, '/tcp_trajectory',
            qos_profile=QoSProfile(
                depth=10,
                durability=DurabilityPolicy.TRANSIENT_LOCAL,
                reliability=ReliabilityPolicy.RELIABLE,
                history=HistoryPolicy.KEEP_LAST,
            ))
        self.traj_points = []
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        self.state_sub = self.create_subscription(
            JointState, '/joint_states', self.state_cb, 10)
        self.home_cli = self.create_client(Trigger, '/pincher/home')
        self._service_available = False
        for i in range(15):
            if not rclpy.ok():
                break
            if self.home_cli.wait_for_service(timeout_sec=1.0):
                self._service_available = True
                break
            self.get_logger().warn('Esperando servicio /pincher/home...')
        if self._service_available:
            self.get_logger().info('Servicio /pincher/home disponible')
        else:
            self.get_logger().warn('Servicio /pincher/home no disponible (continuando sin home)')

        playback_worker.node = self
        load_poses()
        with poses_lock:
            n = len(poses)
        self.get_logger().info(f'Poses cargadas: {n}')
        self.get_logger().info('Nodo individual_movement iniciado')

    def state_cb(self, msg):
        with state_lock:
            for n, p in zip(msg.name, msg.position):
                current_state[n] = p

    def process_queue(self):
        try:
            cmd = command_queue.get_nowait()
        except queue.Empty:
            return
        if cmd['type'] == 'move':
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = cmd['name']
            msg.position = cmd['position']
            self.cmd_pub.publish(msg)
            self.get_logger().info(
                f"Comando: {dict(zip(cmd['name'], [f'{v/DEG:.1f}°' for v in cmd['position']]))}")
        elif cmd['type'] == 'home':
            msg = JointState()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.name = list(JOINT_NAMES)
            msg.position = [0.0] * len(JOINT_NAMES)
            self.cmd_pub.publish(msg)
            self.get_logger().info('Home enviado (todas a 0°)')
        elif cmd['type'] == 'trajectory':
            self.publish_trajectory_marker(cmd['points'])

    def publish_trajectory_marker(self, points):
        marker = Marker()
        marker.header.frame_id = 'base_link'
        marker.header.stamp = self.get_clock().now().to_msg()
        marker.ns = 'tcp_traj'
        marker.id = 0
        if not points:
            marker.action = Marker.DELETEALL
            self.traj_pub.publish(marker)
            return

        marker.type = Marker.LINE_STRIP
        marker.action = Marker.ADD
        marker.pose.orientation.w = 1.0
        marker.scale.x = 0.008
        marker.color.r = 1.0
        marker.color.g = 0.1
        marker.color.b = 0.1
        marker.color.a = 1.0
        for p in points:
            pt = Point()
            pt.x = float(p[0]) if isinstance(p, list) else float(p.get('x', 0))
            pt.y = float(p[1]) if isinstance(p, list) else float(p.get('y', 0))
            pt.z = float(p[2]) if isinstance(p, list) else float(p.get('z', 0))
            marker.points.append(pt)
        self.traj_pub.publish(marker)
        self.get_logger().info(f'Trajectory: {len(marker.points)} pts')

def main():
    rclpy.init()
    node = MovementNode()
    running = True

    def shutdown(sig, frame):
        nonlocal running
        running = False
        playback_stop.set()
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    t = threading.Thread(target=http_server, args=(node, 5050), daemon=True)
    t.start()
    print(f'\n  [Lab05] Interfaz disponible en http://localhost:5050\n')

    try:
        while rclpy.ok() and running:
            rclpy.spin_once(node, timeout_sec=0.05)
            node.process_queue()
    except KeyboardInterrupt:
        pass
    finally:
        playback_stop.set()
        time.sleep(0.2)
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
