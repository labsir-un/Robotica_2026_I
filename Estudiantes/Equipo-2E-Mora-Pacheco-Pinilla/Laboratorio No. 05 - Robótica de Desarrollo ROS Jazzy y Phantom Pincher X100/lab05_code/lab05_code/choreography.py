#!/usr/bin/env python3
import argparse
import math
import random
import sys
import threading
import time

import numpy as np
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState

DEG = math.pi / 180.0

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

HOME = [0.0, 0.0, 0.0, 0.0, 0.0]

def make_pose(beat_idx: int) -> list[float]:
    i = beat_idx % 8
    if i == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    if i == 1:
        return [30 * DEG, 20 * DEG, -10 * DEG, 10 * DEG, 0.0]
    if i == 2:
        return [-30 * DEG, -20 * DEG, 10 * DEG, -10 * DEG, 0.0]
    if i == 3:
        return [45 * DEG, 30 * DEG, -20 * DEG, 15 * DEG, 10 * DEG]
    if i == 4:
        return [-45 * DEG, -30 * DEG, 20 * DEG, -15 * DEG, -10 * DEG]
    if i == 5:
        return [60 * DEG, 40 * DEG, -30 * DEG, 20 * DEG, 20 * DEG]
    if i == 6:
        return [-60 * DEG, -40 * DEG, 30 * DEG, -20 * DEG, -20 * DEG]
    return [10 * DEG, -10 * DEG, 5 * DEG, -5 * DEG, 0.0]


class DanceNode(Node):
    def __init__(self):
        super().__init__('dance_choreography')
        self.cmd_pub = self.create_publisher(JointState, '/pincher/command', 10)

    def send(self, positions: list[float]):
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(JOINT_NAMES)
        msg.position = positions
        self.cmd_pub.publish(msg)

    def go_home(self):
        self.send(HOME)
        time.sleep(0.5)


def main():
    parser = argparse.ArgumentParser(description='Robot dance to music')
    parser.add_argument('mp3', help='Path to MP3 file')
    parser.add_argument('--start-offset', type=float, default=0.0,
                        help='Skip first N seconds')
    parser.add_argument('--duration', type=float, default=0.0,
                        help='Duration in seconds (0 = entire song)')
    args = parser.parse_args()

    print(f'Cargando {args.mp3}...')
    import librosa
    y, sr = librosa.load(args.mp3, sr=None, offset=args.start_offset,
                         duration=args.duration if args.duration > 0 else None)
    print(f'Audio cargado: {len(y)/sr:.1f}s, {sr} Hz')

    print('Detectando beats...')
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)
    print(f'Tempo: {float(tempo[0]):.0f} BPM | Beats: {len(beat_times)}')

    rclpy.init()
    node = DanceNode()

    print('Enviando a HOME...')
    node.go_home()

    print('Reproduciendo audio...')
    import simpleaudio as sa
    audio_data = (y * 32767).astype(np.int16)
    play_obj = sa.play_buffer(audio_data, 1, 2, sr)

    start_real = time.time()
    start_audio = time.time()

    poses = [make_pose(i) for i in range(len(beat_times))]

    try:
        for i, t in enumerate(beat_times):
            now = time.time() - start_real
            sleep_needed = t - now
            if sleep_needed > 0:
                time.sleep(sleep_needed)
            node.send(poses[i])
            elapsed = time.time() - start_real
            drift = elapsed - t
            if abs(drift) > 0.05:
                print(f'  Beat {i}: drift {drift*1000:.0f}ms')
    except KeyboardInterrupt:
        pass

    play_obj.wait_done()
    node.go_home()
    node.destroy_node()
    rclpy.shutdown()
    print('Baile terminado')


if __name__ == '__main__':
    main()
