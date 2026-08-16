#!/usr/bin/env python3

from __future__ import annotations

import math
import os
import shutil
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List, Optional

import numpy as np
import yaml
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger


JOINT_LIMITS_DEG = {
    'waist': (-150.0, 150.0),
    'shoulder': (-150.0, 150.0),
    'elbow': (-150.0, 150.0),
    'wrist': (-150.0, 150.0),
    'gripper': (-90.0, 90.0),
}

SEQUENTIAL_ORDER = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

JOINT_LABELS = {
    'waist': 'Base', 
    'shoulder': 'Hombro',
    'elbow': 'Codo',
    'wrist': 'Muñeca', 
    'gripper': 'Pinza',
}

SEQUENTIAL_DELAY_MS = 1000


PRESETS: Dict[int, Dict[str, Optional[float]]] = {
    1: {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 0, 'gripper': 0},  
    2: {'waist': 25, 'shoulder': 25, 'elbow': 20, 'wrist': -20, 'gripper': 0},  
    3: {'waist': -35, 'shoulder': 35, 'elbow': -30, 'wrist': 30, 'gripper': 0},  
    4: {'waist': 85, 'shoulder': -20, 'elbow': 55, 'wrist': 25, 'gripper': 0},  
    5: {'waist': 80, 'shoulder': -35, 'elbow': 55, 'wrist': -45, 'gripper': 0},  
}

PRESET_LABELS = {
    1: 'Posición 1',
    2: 'Posición  2',
    3: 'Posición  3',
    4: 'Posición  4',
    5: 'Posición  5',
}


def trajectory_linear(theta0: float, theta1: float, t: np.ndarray, duration: float) -> np.ndarray:
    return theta0 + (theta1 - theta0) * (t / duration)


def trajectory_cubic(theta0: float, theta1: float, t: np.ndarray, duration: float) -> np.ndarray:
    delta = theta1 - theta0
    a2 = 3.0 * delta / duration ** 2
    a3 = -2.0 * delta / duration ** 3
    return theta0 + a2 * t ** 2 + a3 * t ** 3


def trajectory_quintic(theta0: float, theta1: float, t: np.ndarray, duration: float) -> np.ndarray:
    delta = theta1 - theta0
    a3 = 10.0 * delta / duration ** 3
    a4 = -15.0 * delta / duration ** 4
    a5 = 6.0 * delta / duration ** 5
    return theta0 + a3 * t ** 3 + a4 * t ** 4 + a5 * t ** 5


TRAJECTORY_FUNCTIONS = {
    'lineal': trajectory_linear,
    'cubica': trajectory_cubic,
    'quintica': trajectory_quintic,
}

TRAJECTORY_LABELS = {
    'lineal': 'Lineal',
    'cubica': 'Cúbica',
    'quintica': 'Quíntica',
}

TRAJECTORY_CONFIG_SOURCES = {0: 'Actual (GUI)', 1: 1, 2: 2, 3: 3, 4: 4, 5: 5}


POSES_YAML_PATH = os.path.expanduser('~/pincher_taught_poses.yaml')





TRIANGLE_POSES: List[Dict[str, float]] = [
    {'waist': 0, 'shoulder': 0.00, 'elbow': 0.00, 'wrist': 0.00, 'gripper': -90},
    {'waist': 0, 'shoulder': -4.02, 'elbow': 8.04, 'wrist': -4.02, 'gripper': -90},
    {'waist': 0, 'shoulder': -8.04, 'elbow': 16.08, 'wrist': -8.04, 'gripper': -90},
    {'waist': 0, 'shoulder': -12.06, 'elbow': 24.12, 'wrist': -12.06, 'gripper': -90},
    {'waist': 0, 'shoulder': -16.08, 'elbow': 32.16, 'wrist': -16.08, 'gripper': -90},
    {'waist': 0, 'shoulder': -20.10, 'elbow': 40.20, 'wrist': -20.10, 'gripper': -90},
    {'waist': 0, 'shoulder': -24.12, 'elbow': 48.24, 'wrist': -24.12, 'gripper': -90},
    {'waist': 0, 'shoulder': -28.14, 'elbow': 56.28, 'wrist': -28.14, 'gripper': -90},
    {'waist': 0, 'shoulder': -32.16, 'elbow': 64.32, 'wrist': -32.16, 'gripper': -90},
    {'waist': 0, 'shoulder': -36.18, 'elbow': 72.37, 'wrist': -36.18, 'gripper': -90},
    {'waist': 0, 'shoulder': -40.20, 'elbow': 80.41, 'wrist': -40.20, 'gripper': -90},  
    {'waist': 0, 'shoulder': -44.22, 'elbow': 88.45, 'wrist': -44.22, 'gripper': -90},
    {'waist': 0, 'shoulder': -48.24, 'elbow': 96.49, 'wrist': -48.24, 'gripper': -90},
    {'waist': 0, 'shoulder': -52.26, 'elbow': 104.53, 'wrist': -52.26, 'gripper': -90},
    {'waist': 0, 'shoulder': -56.28, 'elbow': 112.57, 'wrist': -56.28, 'gripper': -90},
    {'waist': 0, 'shoulder': -60.30, 'elbow': 120.61, 'wrist': -60.30, 'gripper': -90},
    {'waist': 0, 'shoulder': -64.32, 'elbow': 128.65, 'wrist': -64.32, 'gripper': -90},
    {'waist': 0, 'shoulder': -68.35, 'elbow': 136.69, 'wrist': -68.35, 'gripper': -90},
    {'waist': 0, 'shoulder': -72.37, 'elbow': 144.73, 'wrist': -72.37, 'gripper': -90},
    {'waist': 0, 'shoulder': -76.39, 'elbow': 152.77, 'wrist': -76.39, 'gripper': -90},
    {'waist': 0, 'shoulder': -80.41, 'elbow': 160.81, 'wrist': -80.41, 'gripper': -90},  

    {'waist': 0, 'shoulder': -74.93, 'elbow': 154.96, 'wrist': -80.03, 'gripper': -90},
    {'waist': 0, 'shoulder': -69.45, 'elbow': 149.11, 'wrist': -79.66, 'gripper': -90},
    {'waist': 0, 'shoulder': -63.97, 'elbow': 143.25, 'wrist': -79.28, 'gripper': -90},
    {'waist': 0, 'shoulder': -58.49, 'elbow': 137.40, 'wrist': -78.91, 'gripper': -90},
    {'waist': 0, 'shoulder': -53.01, 'elbow': 131.55, 'wrist': -78.54, 'gripper': -90},
    {'waist': 0, 'shoulder': -47.53, 'elbow': 125.70, 'wrist': -78.16, 'gripper': -90},
    {'waist': 0, 'shoulder': -42.05, 'elbow': 119.84, 'wrist': -77.79, 'gripper': -90},
    {'waist': 0, 'shoulder': -36.58, 'elbow': 113.99, 'wrist': -77.42, 'gripper': -90},
    {'waist': 0, 'shoulder': -31.10, 'elbow': 108.14, 'wrist': -77.04, 'gripper': -90},
    {'waist': 0, 'shoulder': -25.62, 'elbow': 102.29, 'wrist': -76.67, 'gripper': -90},  
    {'waist': 0, 'shoulder': -20.14, 'elbow': 96.43, 'wrist': -76.30, 'gripper': -90},
    {'waist': 0, 'shoulder': -14.66, 'elbow': 90.58, 'wrist': -75.92, 'gripper': -90},
    {'waist': 0, 'shoulder': -9.18, 'elbow': 84.73, 'wrist': -75.55, 'gripper': -90},
    {'waist': 0, 'shoulder': -3.70, 'elbow': 78.88, 'wrist': -75.17, 'gripper': -90},
    {'waist': 0, 'shoulder': 1.78, 'elbow': 73.02, 'wrist': -74.80, 'gripper': -90},
    {'waist': 0, 'shoulder': 7.26, 'elbow': 67.17, 'wrist': -74.43, 'gripper': -90},
    {'waist': 0, 'shoulder': 12.73, 'elbow': 61.32, 'wrist': -74.05, 'gripper': -90},
    {'waist': 0, 'shoulder': 18.21, 'elbow': 55.47, 'wrist': -73.68, 'gripper': -90},
    {'waist': 0, 'shoulder': 23.69, 'elbow': 49.61, 'wrist': -73.31, 'gripper': -90},
    {'waist': 0, 'shoulder': 29.17, 'elbow': 43.76, 'wrist': -72.93, 'gripper': -90},  

    {'waist': 0, 'shoulder': 27.71, 'elbow': 41.57, 'wrist': -69.29, 'gripper': -90},
    {'waist': 0, 'shoulder': 26.25, 'elbow': 39.39, 'wrist': -65.64, 'gripper': -90},
    {'waist': 0, 'shoulder': 24.80, 'elbow': 37.20, 'wrist': -61.99, 'gripper': -90},
    {'waist': 0, 'shoulder': 23.34, 'elbow': 35.01, 'wrist': -58.35, 'gripper': -90},
    {'waist': 0, 'shoulder': 21.88, 'elbow': 32.82, 'wrist': -54.70, 'gripper': -90},
    {'waist': 0, 'shoulder': 20.42, 'elbow': 30.63, 'wrist': -51.05, 'gripper': -90},
    {'waist': 0, 'shoulder': 18.96, 'elbow': 28.45, 'wrist': -47.41, 'gripper': -90},
    {'waist': 0, 'shoulder': 17.50, 'elbow': 26.26, 'wrist': -43.76, 'gripper': -90},
    {'waist': 0, 'shoulder': 16.04, 'elbow': 24.07, 'wrist': -40.11, 'gripper': -90},
    {'waist': 0, 'shoulder': 14.59, 'elbow': 21.88, 'wrist': -36.47, 'gripper': -90},  
    {'waist': 0, 'shoulder': 13.13, 'elbow': 19.69, 'wrist': -32.82, 'gripper': -90},
    {'waist': 0, 'shoulder': 11.67, 'elbow': 17.50, 'wrist': -29.17, 'gripper': -90},
    {'waist': 0, 'shoulder': 10.21, 'elbow': 15.32, 'wrist': -25.53, 'gripper': -90},
    {'waist': 0, 'shoulder': 8.75, 'elbow': 13.13, 'wrist': -21.88, 'gripper': -90},
    {'waist': 0, 'shoulder': 7.29, 'elbow': 10.94, 'wrist': -18.23, 'gripper': -90},
    {'waist': 0, 'shoulder': 5.83, 'elbow': 8.75, 'wrist': -14.59, 'gripper': -90},
    {'waist': 0, 'shoulder': 4.38, 'elbow': 6.56, 'wrist': -10.94, 'gripper': -90},
    {'waist': 0, 'shoulder': 2.92, 'elbow': 4.38, 'wrist': -7.29, 'gripper': -90},
    {'waist': 0, 'shoulder': 1.46, 'elbow': 2.19, 'wrist': -3.65, 'gripper': -90},
    {'waist': 0, 'shoulder': 0.00, 'elbow': 0.00, 'wrist': 0.00, 'gripper': -90},  
]
TRIANGLE_DELAY_MS = 500


DANCE_AUDIO_PATH = os.path.expanduser('~/Descargas/chipi chipi chapa chapa dubi dubi daba daba tiktok cat  Christell - Dubidubidu (LETRA).mp3')

DANCE_POSES: List[Dict[str, object]] = [
    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 550},
    {'joints': {'waist': 45, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -45, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 45, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -45, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': -75, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': -60, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': -45, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': -30, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': -15, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750}, 
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 75, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 60, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 45, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 30, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 15, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 90, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 75, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 60, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 45, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 60, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 120, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 60, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 120, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 0, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},

    {'joints': {'waist': -0, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},

    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': -30, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 30, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': -30, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 30, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': -30, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 30, 'wrist': 30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': -30, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 30, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},

    {'joints': {'waist': -0, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},

    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': -15, 'wrist': 30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 15, 'wrist': 30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -30, 'shoulder': 0, 'elbow': -15, 'wrist': -30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 30, 'shoulder': 0, 'elbow': 15, 'wrist': -30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': -15, 'wrist': 30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 15, 'wrist': 30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -60, 'shoulder': 0, 'elbow': -15, 'wrist': -30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': 15, 'wrist': -30, 'gripper': -45}, 'delay_ms': 750},

    {'joints': {'waist': -0, 'shoulder': 0, 'elbow': 0, 'wrist': -30, 'gripper': 90}, 'delay_ms': 750},

    {'joints': {'waist': -90, 'shoulder': 0, 'elbow': -15, 'wrist': 30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': 0, 'elbow': 15, 'wrist': 30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 0, 'elbow': -15, 'wrist': -30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': 0, 'elbow': 15, 'wrist': -30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -120, 'shoulder': 0, 'elbow': -15, 'wrist': 30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 15, 'wrist': 30, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': 120, 'shoulder': 0, 'elbow': -15, 'wrist': -30, 'gripper': 45}, 'delay_ms': 750},
    {'joints': {'waist': 0, 'shoulder': 0, 'elbow': 15, 'wrist': -30, 'gripper': -45}, 'delay_ms': 750},

    {'joints': {'waist': 90, 'shoulder': -45, 'elbow': 45, 'wrist': 90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 45, 'elbow': -45, 'wrist': -90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': -45, 'elbow': 45, 'wrist': 90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 45, 'elbow': -45, 'wrist': -90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': -45, 'elbow': 45, 'wrist': 90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 45, 'elbow': -45, 'wrist': -90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': -45, 'elbow': 45, 'wrist': 90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 45, 'elbow': -45, 'wrist': -90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': 90, 'shoulder': -45, 'elbow': 45, 'wrist': 90, 'gripper': -45}, 'delay_ms': 750},
    {'joints': {'waist': -90, 'shoulder': 45, 'elbow': -45, 'wrist': -90, 'gripper': -45}, 'delay_ms': 750},

    {'joints': {'waist': 0, 'shoulder': -90, 'elbow': 90, 'wrist': 90, 'gripper': 90}, 'delay_ms': 550},
]

class PincherGuiNode(Node):

    def __init__(self) -> None:
        super().__init__('pincher_gui')
        self.command_publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10,
        )
        self.home_client = self.create_client(Trigger, '/pincher/home')
        self.stop_client = self.create_client(Trigger, '/pincher/software_stop')
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')
        self.latest_status = 'Esperando al controlador...'
        self.status_subscription = self.create_subscription(
            String,
            '/pincher/status',
            self._status_callback,
            10,
        )
        self.latest_measured_deg: Dict[str, float] = {}
        self.joint_state_subscription = self.create_subscription(
            JointState,
            '/joint_states',
            self._joint_state_callback,
            10,
        )

    def _joint_state_callback(self, msg: JointState) -> None:
        for name, position in zip(msg.name, msg.position):
            self.latest_measured_deg[name] = math.degrees(position)

    def _status_callback(self, msg: String) -> None:
        self.latest_status = msg.data

    def publish_joint_command(self, names: List[str], degrees: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = [math.radians(value) for value in degrees]
        self.command_publisher.publish(msg)

    def publish_speed(self, speed: int) -> None:
        msg = UInt32()
        msg.data = max(0, int(speed))
        self.speed_publisher.publish(msg)


class PincherGui:

    def __init__(self, node: PincherGuiNode) -> None:
        self.node = node
        self.root = tk.Tk()
        self.root.title('PhantomX Pincher X100 - ROS 2 Jazzy')
        self.root.minsize(900, 750)
        try:
            self.root.geometry('1100x750')
        except tk.TclError:
            pass
        self.root.protocol('WM_DELETE_WINDOW', self.close)

        self.joint_names = list(JOINT_LIMITS_DEG)

        self.variables: Dict[str, tk.DoubleVar] = {
            name: tk.DoubleVar(value=0.0) for name in self.joint_names
        }
        self.entries: Dict[str, ttk.Entry] = {}
        self.status_var = tk.StringVar(value=self.node.latest_status)
        self.speed_var = tk.IntVar(value=100)
        self.mode_var = tk.StringVar(value='simultaneo')  

        self.traj_start_var = tk.StringVar(value='Actual (GUI)')
        self.traj_end_var = tk.StringVar(value='Posición 1')
        self.traj_joint_var = tk.StringVar(value=self.joint_names[0])
        self.traj_duration_var = tk.DoubleVar(value=5.0)
        self.traj_samples_var = tk.IntVar(value=60)
        self.traj_interp_var = tk.StringVar(value='cubica')  
        self.traj_figure: Optional[Figure] = None
        self.traj_canvas: Optional[FigureCanvasTkAgg] = None
        self.traj_send_job = None

        self.sin_joint_var = tk.StringVar(value=self.joint_names[0])
        self.sin_q0_var = tk.DoubleVar(value=0.0)
        self.sin_amp1_var = tk.DoubleVar(value=10.0)
        self.sin_amp2_var = tk.DoubleVar(value=20.0)
        self.sin_freq1_var = tk.DoubleVar(value=0.1)
        self.sin_freq2_var = tk.DoubleVar(value=0.2)
        self.sin_duration_var = tk.DoubleVar(value=10.0)
        self.sin_rate_var = tk.DoubleVar(value=20.0)  
        self.sin_test_select_var = tk.StringVar(value='Prueba 1 (A1, f1)')
        self.sin_results: Dict[int, Dict[str, np.ndarray]] = {}
        self.sin_metrics_var = tk.StringVar(value='Sin resultados todavía.')
        self.sin_figure: Optional[Figure] = None
        self.sin_canvas: Optional[FigureCanvasTkAgg] = None
        self.sin_running = False
        self.sin_job = None

        self.teach_pose_name_var = tk.StringVar(value='')
        self.teach_transition_var = tk.DoubleVar(value=1.5)  
        self.teach_poses: List[Dict[str, object]] = []  
        self.teach_listbox: Optional[tk.Listbox] = None
        self.teach_playing = False
        self.teach_job = None
        self._load_poses_from_yaml()

        self.triangle_running = False
        self.triangle_job = None
        self.dance_running = False
        self.dance_job = None
        self.dance_audio_process = None

        self._configure_styles()
        self._build_layout()
        self.root.after(20, self._spin_ros)
        self.root.after(200, self._refresh_status)

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use('clam')
        except tk.TclError:
            pass

        bg = '#f4f6f8'
        accent = '#2b6cb0'
        danger = '#c53030'

        self.root.configure(bg=bg)

        style.configure('.', background=bg, font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 18, 'bold'), background=bg, foreground='#1a202c')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 10), background=bg, foreground='#4a5568')
        style.configure('Section.TLabelframe', background=bg, borderwidth=1, relief='groove')
        style.configure('Section.TLabelframe.Label', font=('Segoe UI', 11, 'bold'), background=bg, foreground='#2d3748')
        style.configure('TFrame', background=bg)
        style.configure('TLabel', background=bg)
        style.configure('TCheckbutton', background=bg)
        style.configure('TRadiobutton', background=bg, font=('Segoe UI', 10, 'bold'))

        style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.map('Accent.TButton', background=[('active', accent)])

        style.configure('Danger.TButton', font=('Segoe UI', 11, 'bold'), padding=10, foreground=danger)
        style.map('Danger.TButton', foreground=[('active', 'white')], background=[('active', danger)])

        style.configure('Preset.TButton', font=('Segoe UI', 11, 'bold'), padding=16)

    def _build_layout(self) -> None:
        header = ttk.Frame(self.root, padding=(16, 14))
        header.pack(fill='x')
        ttk.Label(
            header,
            text='Control del PhantomX Pincher X100',
            style='Title.TLabel',
        ).pack(anchor='w')
        ttk.Label(
            header,
            text='Comandos articulares en grados; ROS 2 transmite radianes.',
            style='Subtitle.TLabel',
        ).pack(anchor='w', pady=(2, 0))

        mode_frame = ttk.LabelFrame(self.root, text='Modo de envío', padding=12, style='Section.TLabelframe')
        mode_frame.pack(fill='x', padx=16, pady=(0, 10))

        ttk.Radiobutton(
            mode_frame,
            text='Simultáneo',
            value='simultaneo',
            variable=self.mode_var,
        ).pack(side='left', padx=(4, 20))
        ttk.Radiobutton(
            mode_frame,
            text='Secuencial (1.Base → 2.Hombro → 3.Codo → 4.Muñeca → 5.Pinza)',
            value='secuencial',
            variable=self.mode_var,
        ).pack(side='left')

        controls = ttk.LabelFrame(self.root, text='Control general', padding=12, style='Section.TLabelframe')
        controls.pack(fill='x', padx=16, pady=(0, 10))

        ttk.Label(controls, text='Velocidad / Profile Velocity:').grid(row=0, column=0, sticky='w')
        speed_spin = ttk.Spinbox(
            controls,
            from_=0,
            to=1023,
            textvariable=self.speed_var,
            width=9,
        )
        speed_spin.grid(row=0, column=1, padx=(6, 12))
        ttk.Button(controls, text='Aplicar velocidad', style='Accent.TButton', command=self.apply_speed).grid(
            row=0, column=2, padx=4,
        )
        ttk.Button(controls, text='HOME', style='Accent.TButton', command=self.call_home).grid(
            row=0, column=3, padx=4,
        )
        ttk.Button(controls, text='Torque ON', style='Accent.TButton', command=lambda: self.call_torque(True)).grid(
            row=0, column=4, padx=4,
        )
        ttk.Button(controls, text='Torque OFF', style='Accent.TButton', command=lambda: self.call_torque(False)).grid(
            row=0, column=5, padx=4,
        )
        ttk.Button(
            controls,
            text='PARADA DE SOFTWARE',
            command=self.call_stop,
            style='Danger.TButton',
        ).grid(row=1, column=0, columnspan=6, sticky='ew', padx=4, pady=(10, 0))

        for col in range(6):
            controls.columnconfigure(col, weight=1)

        status_frame = ttk.LabelFrame(self.root, text='Estado', padding=10, style='Section.TLabelframe')
        status_frame.pack(fill='x', padx=16, pady=(0, 10))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            wraplength=760,
        ).pack(anchor='w')
        ttk.Label(
            status_frame,
            text=(
                'La parada de la GUI no sustituye un circuito físico de emergencia. '
                'Mantén disponible el corte de alimentación.'
            ),
            style='Subtitle.TLabel',
        ).pack(anchor='w', pady=(6, 0))

        notebook_outer = ttk.Frame(self.root)
        notebook_outer.pack(fill='both', expand=True, padx=16, pady=(0, 16))

        notebook_canvas = tk.Canvas(notebook_outer, highlightthickness=0, bg='#f4f6f8')
        notebook_scrollbar = ttk.Scrollbar(notebook_outer, orient='vertical', command=notebook_canvas.yview)
        notebook_canvas.configure(yscrollcommand=notebook_scrollbar.set)
        notebook_canvas.pack(side='left', fill='both', expand=True)
        notebook_scrollbar.pack(side='right', fill='y')

        notebook_holder = ttk.Frame(notebook_canvas)
        notebook_holder_id = notebook_canvas.create_window((0, 0), window=notebook_holder, anchor='nw')

        def _on_holder_configure(_event=None) -> None:
            notebook_canvas.configure(scrollregion=notebook_canvas.bbox('all'))

        def _on_canvas_configure(event) -> None:
            notebook_canvas.itemconfigure(notebook_holder_id, width=event.width)

        notebook_holder.bind('<Configure>', _on_holder_configure)
        notebook_canvas.bind('<Configure>', _on_canvas_configure)

        def _on_mousewheel(event) -> None:
            delta = -1 * (event.delta // 120) if event.delta else (-1 if event.num == 4 else 1)
            notebook_canvas.yview_scroll(int(delta), 'units')

        notebook_canvas.bind_all('<MouseWheel>', _on_mousewheel)
        notebook_canvas.bind_all('<Button-4>', _on_mousewheel)
        notebook_canvas.bind_all('<Button-5>', _on_mousewheel)

        notebook = ttk.Notebook(notebook_holder)
        notebook.pack(fill='both', expand=True)

        manual_tab = ttk.Frame(notebook, padding=12)
        presets_tab = ttk.Frame(notebook, padding=12)
        trajectory_tab = ttk.Frame(notebook, padding=12)
        sinusoidal_tab = ttk.Frame(notebook, padding=12)
        teaching_tab = ttk.Frame(notebook, padding=12)
        triangle_tab = ttk.Frame(notebook, padding=12)
        dance_tab = ttk.Frame(notebook, padding=12)
        notebook.add(manual_tab, text='Manual')
        notebook.add(presets_tab, text='Presets')
        notebook.add(trajectory_tab, text='Trayectorias')
        notebook.add(sinusoidal_tab, text='Senoidal')
        notebook.add(teaching_tab, text='Modo enseñanza')
        notebook.add(triangle_tab, text='Triángulo')
        notebook.add(dance_tab, text='Baile')

        self._build_manual_tab(manual_tab)
        self._build_presets_tab(presets_tab)
        self._build_trajectory_tab(trajectory_tab)
        self._build_sinusoidal_tab(sinusoidal_tab)
        self._build_teaching_tab(teaching_tab)
        self._build_triangle_tab(triangle_tab)
        self._build_dance_tab(dance_tab)

    def _build_manual_tab(self, parent: ttk.Frame) -> None:
        joints_frame = ttk.LabelFrame(parent, text='Articulaciones', padding=14, style='Section.TLabelframe')
        joints_frame.pack(fill='both', expand=True)
        joints_frame.columnconfigure(1, weight=1)

        for row, name in enumerate(self.joint_names):
            lower, upper = JOINT_LIMITS_DEG[name]

            ttk.Label(joints_frame, text=JOINT_LABELS[name], width=12, font=('Segoe UI', 10, 'bold')).grid(
                row=row, column=0, sticky='w', padx=(4, 10), pady=10,
            )

            entry = ttk.Entry(joints_frame, width=12, justify='center', font=('Segoe UI', 11))
            entry.insert(0, '0.0')
            entry.grid(row=row, column=1, sticky='w', pady=10)
            entry.bind('<Return>', lambda event, joint=name: self._entry_committed(joint))
            entry.bind('<FocusOut>', lambda event, joint=name: self._entry_committed(joint))
            self.entries[name] = entry

            ttk.Label(joints_frame, text='°').grid(row=row, column=2, sticky='w', padx=(2, 10))
            ttk.Label(
                joints_frame,
                text=f'Rango: {lower:.0f}° a {upper:.0f}°',
                style='Subtitle.TLabel',
            ).grid(row=row, column=3, sticky='w')

        button_row = ttk.Frame(joints_frame)
        button_row.grid(row=len(self.joint_names), column=0, columnspan=4, sticky='ew', pady=(16, 4))
        ttk.Button(
            button_row,
            text='Enviar posiciones',
            style='Accent.TButton',
            command=self.send_all,
        ).pack(side='right')

    def _build_presets_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                'Configuraciones de las 5 articulaciones \n'
            ),
            style='Subtitle.TLabel',
            justify='left',
        )
        info.pack(anchor='w', pady=(0, 14))

        grid = ttk.Frame(parent)
        grid.pack(fill='both', expand=True)
        for col in range(5):
            grid.columnconfigure(col, weight=1)

        for idx, preset_id in enumerate(sorted(PRESETS.keys())):
            btn = ttk.Button(
                grid,
                text=PRESET_LABELS.get(preset_id, f'Preset {preset_id}'),
                style='Preset.TButton',
                command=lambda pid=preset_id: self.send_preset(pid),
            )
            btn.grid(row=0, column=idx, padx=8, pady=8, sticky='nsew')
            grid.rowconfigure(0, weight=1, minsize=90)

    def _build_trajectory_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                'Genera una trayectoria entre dos configuraciones alejadas y compara '
                'la suavidad de la interpolación lineal frente a la cúbica/quíntica.'
            ),
            style='Subtitle.TLabel',
            justify='left',
        )
        info.pack(anchor='w', pady=(0, 12))

        config_frame = ttk.LabelFrame(parent, text='Configuración de la trayectoria', padding=12,
                                       style='Section.TLabelframe')
        config_frame.pack(fill='x', pady=(0, 10))

        config_options = ['Actual (GUI)'] + [PRESET_LABELS[p] for p in sorted(PRESETS.keys())]

        ttk.Label(config_frame, text='Config. inicial:').grid(row=0, column=0, sticky='w', padx=(0, 6), pady=4)
        ttk.OptionMenu(config_frame, self.traj_start_var, self.traj_start_var.get(), *config_options).grid(
            row=0, column=1, sticky='w', padx=(0, 18), pady=4,
        )

        ttk.Label(config_frame, text='Config. final:').grid(row=0, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.OptionMenu(config_frame, self.traj_end_var, self.traj_end_var.get(), *config_options).grid(
            row=0, column=3, sticky='w', pady=4,
        )

        ttk.Label(config_frame, text='Articulación a graficar:').grid(row=1, column=0, sticky='w', padx=(0, 6), pady=4)
        joint_options = [JOINT_LABELS[name] for name in self.joint_names]
        self.traj_joint_var.set(JOINT_LABELS[self.joint_names[0]])
        ttk.OptionMenu(config_frame, self.traj_joint_var, self.traj_joint_var.get(), *joint_options).grid(
            row=1, column=1, sticky='w', padx=(0, 18), pady=4,
        )

        ttk.Label(config_frame, text='Duración (s):').grid(row=1, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(config_frame, from_=0.5, to=60.0, increment=0.5, textvariable=self.traj_duration_var,
                    width=8).grid(row=1, column=3, sticky='w', pady=4)

        ttk.Label(config_frame, text='Muestras:').grid(row=2, column=0, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(config_frame, from_=10, to=500, increment=10, textvariable=self.traj_samples_var,
                    width=8).grid(row=2, column=1, sticky='w', pady=4)

        ttk.Label(config_frame, text='Interpolación a enviar:').grid(row=2, column=2, sticky='w', padx=(0, 6), pady=4)
        interp_frame = ttk.Frame(config_frame)
        interp_frame.grid(row=2, column=3, sticky='w', pady=4)
        ttk.Radiobutton(interp_frame, text='Lineal', value='lineal', variable=self.traj_interp_var).pack(side='left')
        ttk.Radiobutton(interp_frame, text='Cúbica', value='cubica', variable=self.traj_interp_var).pack(
            side='left', padx=(10, 0))
        ttk.Radiobutton(interp_frame, text='Quíntica', value='quintica', variable=self.traj_interp_var).pack(
            side='left', padx=(10, 0))

        button_row = ttk.Frame(config_frame)
        button_row.grid(row=3, column=0, columnspan=4, sticky='ew', pady=(10, 0))
        ttk.Button(
            button_row,
            text='Graficar comparación (Lineal vs Cúbica/Quíntica)',
            style='Accent.TButton',
            command=self.plot_trajectory_comparison,
        ).pack(side='left')
        ttk.Button(
            button_row,
            text='Enviar trayectoria al robot',
            style='Accent.TButton',
            command=self.send_trajectory,
        ).pack(side='left', padx=(10, 0))

        plot_frame = ttk.LabelFrame(parent, text='Posición angular vs. tiempo', padding=8,
                                     style='Section.TLabelframe')
        plot_frame.pack(fill='both', expand=True)

        self.traj_figure = Figure(figsize=(6.5, 3.6), dpi=100)
        self.traj_axes = self.traj_figure.add_subplot(111)
        self.traj_axes.set_xlabel('Tiempo (s)')
        self.traj_axes.set_ylabel('Posición angular (°)')
        self.traj_axes.set_title('Genera una trayectoria para visualizarla aquí')
        self.traj_axes.grid(True, linestyle='--', alpha=0.4)
        self.traj_figure.tight_layout()

        self.traj_canvas = FigureCanvasTkAgg(self.traj_figure, master=plot_frame)
        self.traj_canvas.draw()
        self.traj_canvas.get_tk_widget().pack(fill='both', expand=True)

    def _resolve_trajectory_config(self, label: str) -> Dict[str, float]:
        if label == 'Actual (GUI)':
            for name in self.joint_names:
                self._entry_committed(name)
            return {name: self.variables[name].get() for name in self.joint_names}

        for preset_id, preset_label in PRESET_LABELS.items():
            if preset_label == label:
                preset = PRESETS[preset_id]
                return {name: (deg if deg is not None else 0.0) for name, deg in preset.items()}

        return {name: self.variables[name].get() for name in self.joint_names}

    def _joint_name_from_label(self, label: str) -> str:
        for name, lab in JOINT_LABELS.items():
            if lab == label:
                return name
        return self.joint_names[0]

    def _compute_full_trajectory(self, method: str):
        start_cfg = self._resolve_trajectory_config(self.traj_start_var.get())
        end_cfg = self._resolve_trajectory_config(self.traj_end_var.get())

        try:
            duration = max(0.1, float(self.traj_duration_var.get()))
            samples = max(2, int(self.traj_samples_var.get()))
        except (ValueError, tk.TclError):
            messagebox.showwarning('Valor inválido', 'Duración y muestras deben ser numéricas.')
            return None

        t = np.linspace(0.0, duration, samples)
        func = TRAJECTORY_FUNCTIONS[method]

        joint_trajectories: Dict[str, np.ndarray] = {}
        for name in self.joint_names:
            theta0 = start_cfg.get(name, 0.0)
            theta1 = end_cfg.get(name, 0.0)
            lower, upper = JOINT_LIMITS_DEG[name]
            angles = func(theta0, theta1, t, duration)
            angles = np.clip(angles, lower, upper)
            joint_trajectories[name] = angles

        return t, duration, joint_trajectories

    def plot_trajectory_comparison(self) -> None:
        start_cfg = self._resolve_trajectory_config(self.traj_start_var.get())
        end_cfg = self._resolve_trajectory_config(self.traj_end_var.get())
        joint_name = self._joint_name_from_label(self.traj_joint_var.get())

        try:
            duration = max(0.1, float(self.traj_duration_var.get()))
            samples = max(2, int(self.traj_samples_var.get()))
        except (ValueError, tk.TclError):
            messagebox.showwarning('Valor inválido', 'Duración y muestras deben ser numéricas.')
            return

        theta0 = start_cfg.get(joint_name, 0.0)
        theta1 = end_cfg.get(joint_name, 0.0)
        t = np.linspace(0.0, duration, samples)

        linear_curve = trajectory_linear(theta0, theta1, t, duration)
        second_method = self.traj_interp_var.get() if self.traj_interp_var.get() != 'lineal' else 'cubica'
        second_curve = TRAJECTORY_FUNCTIONS[second_method](theta0, theta1, t, duration)

        self.traj_axes.clear()
        self.traj_axes.plot(t, linear_curve, label='Lineal', color='#2b6cb0', linewidth=2)
        self.traj_axes.plot(t, second_curve, label=TRAJECTORY_LABELS[second_method],
                             color='#c53030', linewidth=2, linestyle='--')
        self.traj_axes.set_xlabel('Tiempo (s)')
        self.traj_axes.set_ylabel('Posición angular (°)')
        self.traj_axes.set_title(f'{JOINT_LABELS[joint_name]}: {theta0:.1f}° → {theta1:.1f}° en {duration:.1f} s')
        self.traj_axes.legend(loc='best')
        self.traj_axes.grid(True, linestyle='--', alpha=0.4)
        self.traj_figure.tight_layout()
        self.traj_canvas.draw()

        self.status_var.set(
            f'Comparación graficada: Lineal vs {TRAJECTORY_LABELS[second_method]} '
            f'para {JOINT_LABELS[joint_name]}.'
        )

    def send_trajectory(self) -> None:
        if self.traj_send_job is not None:
            self.root.after_cancel(self.traj_send_job)
            self.traj_send_job = None

        result = self._compute_full_trajectory(self.traj_interp_var.get())
        if result is None:
            return
        t, duration, joint_trajectories = result
        samples = len(t)
        interval_ms = max(1, int(1000 * duration / (samples - 1))) if samples > 1 else 0

        self.status_var.set(
            f'Enviando trayectoria {TRAJECTORY_LABELS[self.traj_interp_var.get()]} '
            f'({samples} muestras, {duration:.1f} s)...'
        )
        self._send_trajectory_step(joint_trajectories, samples, interval_ms, 0)

    def _send_trajectory_step(self, joint_trajectories: Dict[str, np.ndarray], samples: int,
                               interval_ms: int, index: int) -> None:
        if index >= samples:
            self.traj_send_job = None
            self.status_var.set('Trayectoria completada.')
            return

        names = self.joint_names
        degrees = [float(joint_trajectories[name][index]) for name in names]
        self.node.publish_joint_command(names, degrees)

        for name, deg in zip(names, degrees):
            self._set_entry_value(name, deg)

        self.traj_send_job = self.root.after(
            interval_ms,
            lambda: self._send_trajectory_step(joint_trajectories, samples, interval_ms, index + 1),
        )

    def _build_sinusoidal_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                'Selecciona una articulación y programa q(t) = q0 + A·sin(2πf·t).\n'
                'Se ejecutan 4 pruebas combinando 2 amplitudes y 2 frecuencias. '
                'Todas las pruebas se recortan automáticamente a los límites seguros.'
            ),
            style='Subtitle.TLabel',
            justify='left',
        )
        info.pack(anchor='w', pady=(0, 12))

        cfg = ttk.LabelFrame(parent, text='Parámetros', padding=12, style='Section.TLabelframe')
        cfg.pack(fill='x', pady=(0, 10))

        ttk.Label(cfg, text='Articulación:').grid(row=0, column=0, sticky='w', padx=(0, 6), pady=4)
        joint_options = [JOINT_LABELS[name] for name in self.joint_names]
        self.sin_joint_var.set(JOINT_LABELS[self.joint_names[0]])
        ttk.OptionMenu(cfg, self.sin_joint_var, self.sin_joint_var.get(), *joint_options).grid(
            row=0, column=1, sticky='w', padx=(0, 18), pady=4,
        )

        ttk.Label(cfg, text='q0 (centro, °):').grid(row=0, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=-150, to=150, increment=1, textvariable=self.sin_q0_var, width=8).grid(
            row=0, column=3, sticky='w', pady=4,
        )

        ttk.Label(cfg, text='Amplitud A1 (°):').grid(row=1, column=0, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=0, to=90, increment=1, textvariable=self.sin_amp1_var, width=8).grid(
            row=1, column=1, sticky='w', padx=(0, 18), pady=4,
        )
        ttk.Label(cfg, text='Amplitud A2 (°):').grid(row=1, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=0, to=90, increment=1, textvariable=self.sin_amp2_var, width=8).grid(
            row=1, column=3, sticky='w', pady=4,
        )

        ttk.Label(cfg, text='Frecuencia f1 (Hz):').grid(row=2, column=0, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=0.01, to=2.0, increment=0.01, textvariable=self.sin_freq1_var, width=8).grid(
            row=2, column=1, sticky='w', padx=(0, 18), pady=4,
        )
        ttk.Label(cfg, text='Frecuencia f2 (Hz):').grid(row=2, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=0.01, to=2.0, increment=0.01, textvariable=self.sin_freq2_var, width=8).grid(
            row=2, column=3, sticky='w', pady=4,
        )

        ttk.Label(cfg, text='Duración (s):').grid(row=3, column=0, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=2, to=120, increment=1, textvariable=self.sin_duration_var, width=8).grid(
            row=3, column=1, sticky='w', padx=(0, 18), pady=4,
        )
        ttk.Label(cfg, text='Frecuencia de envío (Hz):').grid(row=3, column=2, sticky='w', padx=(0, 6), pady=4)
        ttk.Spinbox(cfg, from_=2, to=50, increment=1, textvariable=self.sin_rate_var, width=8).grid(
            row=3, column=3, sticky='w', pady=4,
        )

        button_row = ttk.Frame(cfg)
        button_row.grid(row=4, column=0, columnspan=4, sticky='ew', pady=(10, 0))
        ttk.Button(
            button_row,
            text='Ejecutar las 4 pruebas (A1f1, A1f2, A2f1, A2f2)',
            style='Accent.TButton',
            command=self.run_sinusoidal_tests,
        ).pack(side='left')
        ttk.Button(
            button_row,
            text='Detener',
            style='Danger.TButton',
            command=self.stop_sinusoidal_tests,
        ).pack(side='left', padx=(10, 0))

        ttk.Label(cfg, text='Ver prueba:').grid(row=5, column=0, sticky='w', padx=(0, 6), pady=(10, 4))
        test_options = [
            'Prueba 1 (A1, f1)', 'Prueba 2 (A1, f2)', 'Prueba 3 (A2, f1)', 'Prueba 4 (A2, f2)',
        ]
        ttk.OptionMenu(
            cfg, self.sin_test_select_var, test_options[0], *test_options,
            command=lambda _evt: self._plot_sinusoidal_result(),
        ).grid(row=5, column=1, sticky='w', pady=(10, 4))

        metrics_frame = ttk.LabelFrame(parent, text='Error de la prueba seleccionada', padding=10,
                                        style='Section.TLabelframe')
        metrics_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(metrics_frame, textvariable=self.sin_metrics_var, justify='left').pack(anchor='w')

        plot_frame = ttk.LabelFrame(parent, text='Posición deseada vs. medida', padding=8,
                                     style='Section.TLabelframe')
        plot_frame.pack(fill='both', expand=True)

        self.sin_figure = Figure(figsize=(6.5, 3.4), dpi=100)
        self.sin_axes = self.sin_figure.add_subplot(111)
        self.sin_axes.set_xlabel('Tiempo (s)')
        self.sin_axes.set_ylabel('Posición angular (°)')
        self.sin_axes.set_title('Ejecuta las pruebas para visualizar aquí')
        self.sin_axes.grid(True, linestyle='--', alpha=0.4)
        self.sin_figure.tight_layout()
        self.sin_canvas = FigureCanvasTkAgg(self.sin_figure, master=plot_frame)
        self.sin_canvas.draw()
        self.sin_canvas.get_tk_widget().pack(fill='both', expand=True)

    def run_sinusoidal_tests(self) -> None:
        if self.sin_running:
            messagebox.showinfo('En curso', 'Ya hay una prueba senoidal en ejecución.')
            return

        joint_name = self._joint_name_from_label(self.sin_joint_var.get())
        lower, upper = JOINT_LIMITS_DEG[joint_name]
        q0 = float(self.sin_q0_var.get())
        amps = [float(self.sin_amp1_var.get()), float(self.sin_amp2_var.get())]
        freqs = [float(self.sin_freq1_var.get()), float(self.sin_freq2_var.get())]
        duration = max(1.0, float(self.sin_duration_var.get()))
        rate = max(1.0, float(self.sin_rate_var.get()))

        combos = [(amps[0], freqs[0]), (amps[0], freqs[1]), (amps[1], freqs[0]), (amps[1], freqs[1])]

        safe_combos = []
        for amp, freq in combos:
            max_amp_allowed = min(upper - q0, q0 - lower)
            amp_safe = max(0.0, min(amp, max_amp_allowed))
            safe_combos.append((amp_safe, freq))

        self.sin_results = {}
        self.sin_running = True
        self.status_var.set(f'Iniciando pruebas senoidales en {JOINT_LABELS[joint_name]}...')
        self._run_sinusoidal_test(joint_name, q0, safe_combos, duration, rate, 0)

    def _run_sinusoidal_test(self, joint_name: str, q0: float, combos: List, duration: float,
                              rate: float, test_index: int) -> None:
        if test_index >= len(combos) or not self.sin_running:
            self.sin_running = False
            self.status_var.set('Pruebas senoidales completadas.')
            self.sin_test_select_var.set('Prueba 1 (A1, f1)')
            self._plot_sinusoidal_result()
            return

        amp, freq = combos[test_index]
        n_samples = max(2, int(duration * rate))
        t = np.linspace(0.0, duration, n_samples)
        desired = q0 + amp * np.sin(2 * math.pi * freq * t)
        lower, upper = JOINT_LIMITS_DEG[joint_name]
        desired = np.clip(desired, lower, upper)

        measured = np.full(n_samples, np.nan)
        interval_ms = max(1, int(1000.0 / rate))

        self.status_var.set(
            f'Prueba {test_index + 1}/4: A={amp:.1f}°, f={freq:.2f} Hz, q0={q0:.1f}°.'
        )

        self._send_sinusoidal_sample(joint_name, t, desired, measured, interval_ms, 0,
                                      lambda: self._finish_sinusoidal_test(
                                          joint_name, q0, combos, duration, rate, test_index, t, desired, measured))

    def _send_sinusoidal_sample(self, joint_name: str, t: np.ndarray, desired: np.ndarray,
                                 measured: np.ndarray, interval_ms: int, index: int, on_done) -> None:
        if index >= len(t) or not self.sin_running:
            on_done()
            return

        target_deg = float(desired[index])
        self.node.publish_joint_command([joint_name], [target_deg])
        self._set_entry_value(joint_name, target_deg)

        measured_val = self.node.latest_measured_deg.get(joint_name)
        measured[index] = measured_val if measured_val is not None else target_deg

        self.sin_job = self.root.after(
            interval_ms,
            lambda: self._send_sinusoidal_sample(joint_name, t, desired, measured, interval_ms, index + 1, on_done),
        )

    def _finish_sinusoidal_test(self, joint_name: str, q0: float, combos: List, duration: float,
                                 rate: float, test_index: int, t: np.ndarray, desired: np.ndarray,
                                 measured: np.ndarray) -> None:
        error = measured - desired
        max_error = float(np.nanmax(np.abs(error))) if len(error) else 0.0
        rmse = float(np.sqrt(np.nanmean(error ** 2))) if len(error) else 0.0
        self.sin_results[test_index] = {
            't': t, 'desired': desired, 'measured': measured,
            'max_error': max_error, 'rmse': rmse,
            'amp': combos[test_index][0], 'freq': combos[test_index][1], 'q0': q0,
            'joint_name': joint_name,
        }
        self._run_sinusoidal_test(joint_name, q0, combos, duration, rate, test_index + 1)

    def stop_sinusoidal_tests(self) -> None:
        self.sin_running = False
        if self.sin_job is not None:
            self.root.after_cancel(self.sin_job)
            self.sin_job = None
        self.status_var.set('Pruebas senoidales detenidas por el usuario.')

    def _plot_sinusoidal_result(self) -> None:
        label = self.sin_test_select_var.get()
        index_map = {
            'Prueba 1 (A1, f1)': 0, 'Prueba 2 (A1, f2)': 1,
            'Prueba 3 (A2, f1)': 2, 'Prueba 4 (A2, f2)': 3,
        }
        idx = index_map.get(label, 0)
        data = self.sin_results.get(idx)
        if data is None:
            self.sin_metrics_var.set('Esta prueba todavía no se ha ejecutado.')
            return

        self.sin_axes.clear()
        self.sin_axes.plot(data['t'], data['desired'], label='Deseada', color='#2b6cb0', linewidth=2)
        self.sin_axes.plot(data['t'], data['measured'], label='Medida', color='#c53030',
                            linewidth=2, linestyle='--')
        self.sin_axes.set_xlabel('Tiempo (s)')
        self.sin_axes.set_ylabel('Posición angular (°)')
        self.sin_axes.set_title(
            f"{JOINT_LABELS[data['joint_name']]}: q0={data['q0']:.1f}°, "
            f"A={data['amp']:.1f}°, f={data['freq']:.2f} Hz"
        )
        self.sin_axes.legend(loc='best')
        self.sin_axes.grid(True, linestyle='--', alpha=0.4)
        self.sin_figure.tight_layout()
        self.sin_canvas.draw()

        self.sin_metrics_var.set(
            f"Error máximo: {data['max_error']:.3f}°    |    Error cuadrático medio (RMSE): {data['rmse']:.3f}°"
        )

    def _build_teaching_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                '1) Mueve el robot en la pestaña Manual o con los presets. '
                '2) Vuelve aquí y pulsa "Guardar pose actual" con un nombre. '
                '3) Registra al menos 8 poses. 4) Reprodúcelas en orden, ajusta el '
                'tiempo de transición o detén la reproducción en cualquier momento.\n'
                f'Las poses se guardan en: {POSES_YAML_PATH}'
            ),
            style='Subtitle.TLabel', justify='left', wraplength=760,
        )
        info.pack(anchor='w', pady=(0, 10))

        save_frame = ttk.LabelFrame(parent, text='Guardar configuración actual', padding=12,
                                     style='Section.TLabelframe')
        save_frame.pack(fill='x', pady=(0, 10))
        ttk.Label(save_frame, text='Nombre de la pose:').pack(side='left', padx=(0, 6))
        ttk.Entry(save_frame, textvariable=self.teach_pose_name_var, width=24).pack(side='left', padx=(0, 12))
        ttk.Button(
            save_frame, text='Guardar pose actual', style='Accent.TButton',
            command=self.teach_save_current_pose,
        ).pack(side='left')

        list_frame = ttk.LabelFrame(parent, text='Poses registradas (orden de reproducción)', padding=10,
                                     style='Section.TLabelframe')
        list_frame.pack(fill='both', expand=True, pady=(0, 10))

        list_inner = ttk.Frame(list_frame)
        list_inner.pack(fill='both', expand=True)
        self.teach_listbox = tk.Listbox(list_inner, height=8, exportselection=False)
        self.teach_listbox.pack(side='left', fill='both', expand=True)
        scrollbar = ttk.Scrollbar(list_inner, orient='vertical', command=self.teach_listbox.yview)
        scrollbar.pack(side='left', fill='y')
        self.teach_listbox.configure(yscrollcommand=scrollbar.set)

        list_buttons = ttk.Frame(list_frame)
        list_buttons.pack(fill='x', pady=(8, 0))
        ttk.Button(list_buttons, text='Ir a la pose seleccionada', command=self.teach_goto_selected).pack(
            side='left', padx=(0, 6))
        ttk.Button(list_buttons, text='Eliminar pose seleccionada', command=self.teach_delete_selected).pack(
            side='left', padx=(0, 6))
        ttk.Button(list_buttons, text='Guardar en YAML', command=self._save_poses_to_yaml).pack(
            side='left', padx=(0, 6))
        ttk.Button(list_buttons, text='Recargar desde YAML', command=self._reload_poses_from_yaml).pack(
            side='left')

        play_frame = ttk.LabelFrame(parent, text='Reproducción', padding=12, style='Section.TLabelframe')
        play_frame.pack(fill='x')
        ttk.Label(play_frame, text='Tiempo de transición entre poses (s):').grid(
            row=0, column=0, sticky='w', padx=(0, 6))
        ttk.Spinbox(play_frame, from_=0.2, to=20.0, increment=0.1, textvariable=self.teach_transition_var,
                    width=8).grid(row=0, column=1, sticky='w', padx=(0, 18))
        ttk.Button(play_frame, text='Reproducir todas', style='Accent.TButton',
                   command=self.teach_play_all).grid(row=0, column=2, padx=4)
        ttk.Button(play_frame, text='Detener reproducción', style='Danger.TButton',
                   command=self.teach_stop_playback).grid(row=0, column=3, padx=4)

        self._refresh_teach_listbox()

    def teach_save_current_pose(self) -> None:
        name = self.teach_pose_name_var.get().strip()
        if not name:
            name = f'Pose {len(self.teach_poses) + 1}'
        for name_ in self.joint_names:
            self._entry_committed(name_)
        joints = {name_: self.variables[name_].get() for name_ in self.joint_names}
        self.teach_poses.append({'name': name, 'joints': joints})
        self.teach_pose_name_var.set('')
        self._refresh_teach_listbox()
        self._save_poses_to_yaml()
        self.status_var.set(f'Pose "{name}" guardada ({len(self.teach_poses)} en total).')

    def _refresh_teach_listbox(self) -> None:
        if self.teach_listbox is None:
            return
        self.teach_listbox.delete(0, tk.END)
        for i, pose in enumerate(self.teach_poses, start=1):
            joints_txt = ', '.join(f'{JOINT_LABELS[n]}={v:.1f}°' for n, v in pose['joints'].items())
            self.teach_listbox.insert(tk.END, f"{i}. {pose['name']}  —  {joints_txt}")

    def teach_goto_selected(self) -> None:
        sel = self.teach_listbox.curselection() if self.teach_listbox else ()
        if not sel:
            messagebox.showinfo('Sin selección', 'Selecciona una pose de la lista.')
            return
        pose = self.teach_poses[sel[0]]
        for name, deg in pose['joints'].items():
            self._set_entry_value(name, deg)
        self._dispatch(pose['joints'])
        self.status_var.set(f"Moviendo a la pose \"{pose['name']}\".")

    def teach_delete_selected(self) -> None:
        sel = self.teach_listbox.curselection() if self.teach_listbox else ()
        if not sel:
            return
        del self.teach_poses[sel[0]]
        self._refresh_teach_listbox()
        self._save_poses_to_yaml()

    def teach_play_all(self) -> None:
        if self.teach_playing:
            return
        if len(self.teach_poses) < 1:
            messagebox.showinfo('Sin poses', 'No hay poses guardadas todavía.')
            return
        self.teach_playing = True
        self._teach_play_step(0)

    def _teach_play_step(self, index: int) -> None:
        if not self.teach_playing or index >= len(self.teach_poses):
            self.teach_playing = False
            self.status_var.set('Reproducción de poses finalizada.')
            return
        pose = self.teach_poses[index]
        for name, deg in pose['joints'].items():
            self._set_entry_value(name, deg)
        self._dispatch(pose['joints'])
        self.status_var.set(f"Reproduciendo pose {index + 1}/{len(self.teach_poses)}: \"{pose['name']}\".")
        transition_ms = max(100, int(float(self.teach_transition_var.get()) * 1000))
        self.teach_job = self.root.after(transition_ms, lambda: self._teach_play_step(index + 1))

    def teach_stop_playback(self) -> None:
        self.teach_playing = False
        if self.teach_job is not None:
            self.root.after_cancel(self.teach_job)
            self.teach_job = None
        self.status_var.set('Reproducción de poses detenida por el usuario.')

    def _save_poses_to_yaml(self) -> None:
        try:
            with open(POSES_YAML_PATH, 'w', encoding='utf-8') as handle:
                yaml.safe_dump({'poses': self.teach_poses}, handle, allow_unicode=True, sort_keys=False)
            self.status_var.set(f'Poses guardadas en {POSES_YAML_PATH}.')
        except OSError as exc:
            messagebox.showwarning('Error al guardar', f'No se pudo escribir el YAML: {exc}')

    def _load_poses_from_yaml(self) -> None:
        if not os.path.exists(POSES_YAML_PATH):
            self.teach_poses = []
            return
        try:
            with open(POSES_YAML_PATH, 'r', encoding='utf-8') as handle:
                data = yaml.safe_load(handle) or {}
            self.teach_poses = data.get('poses', []) or []
        except (OSError, yaml.YAMLError):
            self.teach_poses = []

    def _reload_poses_from_yaml(self) -> None:
        self._load_poses_from_yaml()
        self._refresh_teach_listbox()
        self.status_var.set('Poses recargadas desde el archivo YAML.')

    def _build_triangle_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                'Ejecuta una secuencia de 5 poses predefinidas (editables en la constante '
                'TRIANGLE_POSES, al inicio del archivo) con un retardo fijo entre cada una.'
            ),
            style='Subtitle.TLabel', justify='left', wraplength=760,
        )
        info.pack(anchor='w', pady=(0, 14))

        list_frame = ttk.LabelFrame(parent, text='Secuencia programada', padding=10,
                                     style='Section.TLabelframe')
        list_frame.pack(fill='both', expand=True, pady=(0, 14))
        for i, pose in enumerate(TRIANGLE_POSES, start=1):
            txt = ', '.join(f'{JOINT_LABELS[n]}={v:.0f}°' for n, v in pose.items())
            ttk.Label(list_frame, text=f'{i}. {txt}').pack(anchor='w', pady=2)

        ttk.Button(
            parent, text='Ejecutar secuencia Triángulo', style='Accent.TButton',
            command=self.run_triangle_sequence,
        ).pack(side='left')
        ttk.Button(
            parent, text='Detener', style='Danger.TButton',
            command=self.stop_triangle_sequence,
        ).pack(side='left', padx=(10, 0))

    def run_triangle_sequence(self) -> None:
        if self.triangle_running:
            return
        self.triangle_running = True
        self._triangle_step(0)

    def _triangle_step(self, index: int) -> None:
        if not self.triangle_running or index >= len(TRIANGLE_POSES):
            self.triangle_running = False
            self.status_var.set('Secuencia Triángulo finalizada.')
            return
        pose = TRIANGLE_POSES[index]
        for name, deg in pose.items():
            self._set_entry_value(name, deg)
        self._dispatch(pose)
        self.status_var.set(f'Triángulo: pose {index + 1}/{len(TRIANGLE_POSES)}.')
        self.triangle_job = self.root.after(TRIANGLE_DELAY_MS, lambda: self._triangle_step(index + 1))

    def stop_triangle_sequence(self) -> None:
        self.triangle_running = False
        if self.triangle_job is not None:
            self.root.after_cancel(self.triangle_job)
            self.triangle_job = None
        self.status_var.set('Secuencia Triángulo detenida por el usuario.')

    def _build_dance_tab(self, parent: ttk.Frame) -> None:
        info = ttk.Label(
            parent,
            text=(
                ''
            ),
            style='Subtitle.TLabel', justify='left', wraplength=760,
        )
        info.pack(anchor='w', pady=(0, 14))

        list_frame = ttk.LabelFrame(parent, text='Coreografía programada', padding=10,
                                     style='Section.TLabelframe')
        list_frame.pack(fill='both', expand=True, pady=(0, 14))
        for i, pose in enumerate(DANCE_POSES, start=1):
            txt = ', '.join(f'{JOINT_LABELS[n]}={v:.0f}°' for n, v in pose['joints'].items())
            delay_s = pose['delay_ms'] / 1000.0
            ttk.Label(list_frame, text=f"{i}. {txt}   (retardo a la siguiente: {delay_s:.1f} s)").pack(
                anchor='w', pady=2)

        controls = ttk.Frame(parent)
        controls.pack(fill='x')
        ttk.Button(
            controls, text='Ejecutar Baile', style='Accent.TButton',
            command=self.run_dance_sequence,
        ).pack(side='left')
        ttk.Button(
            controls, text='Detener', style='Danger.TButton',
            command=self.stop_dance_sequence,
        ).pack(side='left', padx=(10, 0))

    def run_dance_sequence(self) -> None:
        if self.dance_running:
            return
        self.dance_running = True
        self._play_dance_audio()
        self._dance_step(0)

    def _play_dance_audio(self) -> None:
        self._stop_dance_audio()  

        if not os.path.exists(DANCE_AUDIO_PATH):
            self.status_var.set(
                f'Aviso: no se encontró el audio en {DANCE_AUDIO_PATH}; el baile sigue sin sonido.'
            )
            return

        candidates = [
            ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', DANCE_AUDIO_PATH],
            ['mpg123', '-q', DANCE_AUDIO_PATH],
            ['mpv', '--no-video', '--really-quiet', DANCE_AUDIO_PATH],
            ['paplay', DANCE_AUDIO_PATH],
            ['aplay', DANCE_AUDIO_PATH],
            ['afplay', DANCE_AUDIO_PATH],  
        ]
        for cmd in candidates:
            if shutil.which(cmd[0]) is not None:
                try:
                    self.dance_audio_process = subprocess.Popen(
                        cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                    )
                    return
                except OSError:
                    continue

        self.status_var.set(
            'Aviso: no se encontró ningún reproductor de audio (ffplay/mpg123/mpv/paplay/aplay). '
            'Instala uno para escuchar el audio del baile.'
        )

    def _stop_dance_audio(self) -> None:
        process = getattr(self, 'dance_audio_process', None)
        if process is not None and process.poll() is None:
            try:
                process.terminate()
            except OSError:
                pass
        self.dance_audio_process = None

    def _dance_step(self, index: int) -> None:
        if not self.dance_running or index >= len(DANCE_POSES):
            self.dance_running = False
            self._stop_dance_audio()
            self.status_var.set('Baile finalizado.')
            return
        pose = DANCE_POSES[index]
        for name, deg in pose['joints'].items():
            self._set_entry_value(name, deg)
        self._dispatch(pose['joints'])
        self.status_var.set(f'Baile: pose {index + 1}/{len(DANCE_POSES)}.')
        delay_ms = max(50, int(pose['delay_ms']))
        self.dance_job = self.root.after(delay_ms, lambda: self._dance_step(index + 1))

    def stop_dance_sequence(self) -> None:
        self.dance_running = False
        if self.dance_job is not None:
            self.root.after_cancel(self.dance_job)
            self.dance_job = None
        self._stop_dance_audio()
        self.status_var.set('Baile detenido por el usuario.')

    def _entry_committed(self, joint: str) -> None:
        entry = self.entries[joint]
        try:
            value = float(entry.get())
        except ValueError:
            value = self.variables[joint].get()
            messagebox.showwarning('Valor inválido', f'La entrada de {JOINT_LABELS[joint]} no es numérica.')
        lower, upper = JOINT_LIMITS_DEG[joint]
        value = max(lower, min(upper, value))
        self.variables[joint].set(value)
        entry.delete(0, tk.END)
        entry.insert(0, f'{value:.1f}')

    def _set_entry_value(self, joint: str, value: float) -> None:
        self.variables[joint].set(value)
        entry = self.entries.get(joint)
        if entry is not None:
            entry.delete(0, tk.END)
            entry.insert(0, f'{value:.1f}')

    def send_all(self) -> None:
        for name in self.joint_names:
            self._entry_committed(name)
        targets = {name: self.variables[name].get() for name in self.joint_names}
        self._dispatch(targets)
        self.status_var.set('Comando articular publicado en /pincher/command.')

    def send_preset(self, preset_id: int) -> None:
        preset = PRESETS.get(preset_id, {})
        targets = {name: deg for name, deg in preset.items() if deg is not None}
        
        for name, deg in targets.items():
            self._set_entry_value(name, deg)
        self._dispatch(targets)
        self.status_var.set(f'Preset {preset_id} enviado ({self.mode_var.get()}).')

    def _dispatch(self, targets: Dict[str, float]) -> None:
        if self.mode_var.get() == 'secuencial':
            ordered = [name for name in SEQUENTIAL_ORDER if name in targets]
            self._send_sequential(ordered, targets)
        else:
            names = list(targets.keys())
            self.node.publish_joint_command(names, [targets[n] for n in names])

    def _send_sequential(self, ordered_names: List[str], targets: Dict[str, float], index: int = 0) -> None:
        if index >= len(ordered_names):
            return
        name = ordered_names[index]
        self.node.publish_joint_command([name], [targets[name]])
        self.status_var.set(f'Secuencial: enviando {JOINT_LABELS[name]} ({index + 1}/{len(ordered_names)}).')
        self.root.after(SEQUENTIAL_DELAY_MS, lambda: self._send_sequential(ordered_names, targets, index + 1))

    def apply_speed(self) -> None:
        try:
            speed = int(self.speed_var.get())
        except (ValueError, tk.TclError):
            messagebox.showwarning('Valor inválido', 'La velocidad debe ser un número entero.')
            return
        speed = max(0, min(1023, speed))
        self.speed_var.set(speed)
        self.node.publish_speed(speed)
        self.status_var.set(f'Velocidad {speed} publicada.')

    def _service_available(self, client, name: str) -> bool:
        if client.service_is_ready():
            return True
        self.status_var.set(f'El servicio {name} todavía no está disponible.')
        return False

    def call_home(self) -> None:
        if not self._service_available(self.node.home_client, '/pincher/home'):
            return
        future = self.node.home_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)
        for name in self.joint_names:
            self._set_entry_value(name, 0.0)

    def call_stop(self) -> None:
        if not self._service_available(self.node.stop_client, '/pincher/software_stop'):
            return
        future = self.node.stop_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)

    def call_torque(self, enabled: bool) -> None:
        if not self._service_available(self.node.torque_client, '/pincher/torque_enable'):
            return
        request = SetBool.Request()
        request.data = enabled
        future = self.node.torque_client.call_async(request)
        future.add_done_callback(self._service_done)

    def _service_done(self, future) -> None:
        try:
            response = future.result()
            self.status_var.set(response.message)
        except Exception as exc:  
            self.status_var.set(f'Error llamando al servicio: {exc}')

    def _spin_ros(self) -> None:
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self._spin_ros)

    def _refresh_status(self) -> None:
        if self.node.latest_status:
            self.status_var.set(self.node.latest_status)
        if rclpy.ok():
            self.root.after(200, self._refresh_status)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self._stop_dance_audio()
        self.root.destroy()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PincherGuiNode()
    gui = PincherGui(node)
    try:
        gui.run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()