#!/usr/bin/env python3
import math
import os
import sys
import threading
import time
from typing import Dict, List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import UInt32

# Safe software limits
JOINT_LIMITS_DEG = {
    'waist': (-140.0, 139.0),
    'shoulder': (-106.0, 64.0),
    'elbow': (-131.0, 137.0),
    'wrist': (-93.0, 93.0),
    'gripper': (-110.0, 110.0),
}

JOINT_NAMES = ['waist', 'shoulder', 'elbow', 'wrist', 'gripper']

def get_choreography_pose(t: float) -> List[float]:
    """Calculates the target joint angles in degrees for time t (seconds)."""
    # 1. Intro (0.0s to 5.0s): transition from Home to starting pose
    if t < 5.0:
        tau = t / 5.0
        s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
        q1 = 0.0
        q2 = 0.0 + s * (-30.0 - 0.0)
        q3 = 0.0 + s * (30.0 - 0.0)
        q4 = 0.0 + s * (20.0 - 0.0)
        q5 = 0.0
        return [q1, q2, q3, q4, q5]
        
    # 2. Verse 1 (5.0s to 15.0s): playful slow movements
    elif t < 15.0:
        t_rel = t - 5.0
        q1 = 30.0 * math.sin(2.0 * math.pi * 0.1 * t_rel)
        q2 = -30.0 + 10.0 * math.sin(2.0 * math.pi * 0.2 * t_rel)
        q3 = 30.0 + 15.0 * math.cos(2.0 * math.pi * 0.2 * t_rel)
        q4 = 20.0 + 20.0 * math.sin(2.0 * math.pi * 0.15 * t_rel)
        q5 = 45.0 * math.sin(2.0 * math.pi * 0.25 * t_rel)
        return [q1, q2, q3, q4, q5]
        
    # 3. Chorus 1 (15.0s to 25.0s): fast chipi-chipi and dubi-dubi beats
    elif t < 25.0:
        t_rel = t - 15.0
        
        # 15s to 19s: "Chipi Chipi Chapa Chapa"
        if t_rel < 4.0:
            q1 = 25.0 * math.sin(2.0 * math.pi * 2.0 * t_rel)
            q2 = -20.0
            q3 = 40.0
            q4 = 0.0
            q5 = 45.0 + 45.0 * math.copysign(1.0, math.sin(2.0 * math.pi * 2.0 * t_rel))
            
        # 19s to 22.5s: "Dubi Dubi Daba Daba"
        elif t_rel < 7.5:
            t_sub = t_rel - 4.0
            q1 = 0.0
            q2 = -20.0 + 20.0 * math.sin(2.0 * math.pi * 1.5 * t_sub)
            q3 = 40.0 - 20.0 * math.sin(2.0 * math.pi * 1.5 * t_sub)
            q4 = 15.0 * math.cos(2.0 * math.pi * 1.5 * t_sub)
            q5 = 0.0
            
        # 22.5s to 24.0s: "Mágico mi dubi dubi"
        elif t_rel < 9.0:
            t_sub = t_rel - 7.5
            q1 = 0.0
            q2 = -30.0
            q3 = 30.0
            q4 = 45.0 * math.sin(2.0 * math.pi * 3.0 * t_sub)
            q5 = 0.0
            
        # 24.0s to 25.0s: "Boom boom boom boom!"
        else:
            t_sub = t_rel - 9.0
            q1 = 0.0
            q2 = -30.0 - 25.0 * max(0.0, math.sin(2.0 * math.pi * 4.0 * t_sub))
            q3 = 30.0 + 25.0 * max(0.0, math.sin(2.0 * math.pi * 4.0 * t_sub))
            q4 = 0.0
            q5 = -30.0 if math.sin(2.0 * math.pi * 4.0 * t_sub) > 0 else 30.0
            
        return [q1, q2, q3, q4, q5]
        
    # 4. Verse 2 (25.0s to 35.0s): circular dance
    elif t < 35.0:
        t_rel = t - 25.0
        q1 = 60.0 * math.sin(2.0 * math.pi * 0.1 * t_rel)
        q2 = -25.0 + 5.0 * math.sin(2.0 * math.pi * 0.2 * t_rel)
        q3 = 45.0 + 20.0 * math.sin(2.0 * math.pi * 0.2 * t_rel)
        q4 = 10.0 + 30.0 * math.cos(2.0 * math.pi * 0.2 * t_rel)
        q5 = 0.0
        return [q1, q2, q3, q4, q5]
        
    # 5. Chorus 2 (35.0s to 45.0s): peak energy and grand finale bow
    elif t < 45.0:
        t_rel = t - 35.0
        
        # 35s to 39s: "Chipi Chipi Chapa Chapa" (larger amplitude)
        if t_rel < 4.0:
            q1 = 40.0 * math.sin(2.0 * math.pi * 2.5 * t_rel)
            q2 = -15.0
            q3 = 50.0
            q4 = 0.0
            q5 = 50.0 + 50.0 * math.copysign(1.0, math.sin(2.0 * math.pi * 2.5 * t_rel))
            
        # 39s to 42.5s: "Dubi Dubi Daba Daba" (larger amplitude)
        elif t_rel < 7.5:
            t_sub = t_rel - 4.0
            q1 = 0.0
            q2 = -15.0 + 30.0 * math.sin(2.0 * math.pi * 2.0 * t_sub)
            q3 = 50.0 - 30.0 * math.sin(2.0 * math.pi * 2.0 * t_sub)
            q4 = 20.0 * math.cos(2.0 * math.pi * 2.0 * t_sub)
            q5 = 0.0
            
        # 42.5s to 44.0s: "Mágico mi dubi dubi"
        elif t_rel < 9.0:
            t_sub = t_rel - 7.5
            q1 = 0.0
            q2 = -25.0
            q3 = 35.0
            q4 = 60.0 * math.sin(2.0 * math.pi * 3.5 * t_sub)
            q5 = 0.0
            
        # 44.0s to 45.0s: "Boom boom boom boom!" and final bow
        else:
            t_sub = t_rel - 9.0
            q1 = 0.0
            tau = t_sub / 1.0
            s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
            q2 = -25.0 + s * (-60.0 - (-25.0))
            q3 = 35.0 + s * (80.0 - 35.0)
            q4 = 0.0
            q5 = 45.0 * s
            
        return [q1, q2, q3, q4, q5]
        
    # 6. Outro (45.0s to 50.0s): return to home position
    else:
        t_rel = t - 45.0
        tau = t_rel / 5.0
        s = 3.0 * (tau ** 2) - 2.0 * (tau ** 3)
        q1 = 0.0
        q2 = -60.0 + s * (0.0 - (-60.0))
        q3 = 80.0 + s * (0.0 - 80.0)
        q4 = 0.0
        q5 = 45.0 + s * (0.0 - 45.0)
        return [q1, q2, q3, q4, q5]

class ChoreographyNode(Node):
    """ROS 2 Node for running the robotic choreography routine."""
    def __init__(self) -> None:
        super().__init__('choreography')
        self.publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(UInt32, '/pincher/profile_velocity', 10)
        
    def set_speed(self, speed_val: int) -> None:
        msg = UInt32()
        msg.data = int(speed_val)
        self.speed_publisher.publish(msg)

    def send_simultaneous_command(self, positions_deg: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = JOINT_NAMES
        
        # Clamp target positions to safe limits to prevent hardware damage
        clamped_deg = []
        for val, name in zip(positions_deg, JOINT_NAMES):
            low, high = JOINT_LIMITS_DEG[name]
            clamped_deg.append(max(low, min(high, val)))
            
        msg.position = [math.radians(val) for val in clamped_deg]
        self.publisher.publish(msg)

def main(args=None) -> None:
    rclpy.init(args=args)
    node = ChoreographyNode()
    
    # Wait for connections and set speed to a safe value (30% raw)
    print("Iniciando Coreografía...")
    time.sleep(1.0)
    node.set_speed(30)
    time.sleep(0.5)
    
    print("\n============================================================")
    # Visual ASCII Cat matching the TikTok cat!
    print(r"       /\_/\   ")
    print("      ( o.o )  ~ Chipi chipi chapa chapa ~")
    print("       > ^ <   ")
    print("============================================================")
    print("Coreografía iniciada: Christell - Dubidubidu")
    print("Duración: 50 segundos. Presiona Ctrl+C para abortar.")
    print("============================================================\n")
    
    duration = 50.0
    freq = 50.0
    dt = 1.0 / freq
    steps = int(duration * freq)
    
    start_time = time.time()
    try:
        for step in range(steps + 1):
            t = step * dt
            
            # Print periodic progress
            if step % int(freq) == 0:
                print(f"[Coreografía] Tiempo: {t:.1f}s / {duration:.1f}s")
                
            q_target = get_choreography_pose(t)
            node.send_simultaneous_command(q_target)
            
            # Accurate timing compensation
            elapsed = time.time() - start_time
            sleep_time = (step + 1) * dt - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
                
    except KeyboardInterrupt:
        print("\nCoreografía interrumpida por el usuario.")
    finally:
        # Gracefully transition back to home
        print("\nCoreografía terminada. Retornando a Home vertical...")
        time.sleep(0.2)
        node.send_simultaneous_command([0.0, 0.0, 0.0, 0.0, 0.0])
        time.sleep(1.0)
        
        # Shutdown ROS
        node.destroy_node()
        rclpy.shutdown()
        print("[OK] Sistema finalizado.")

if __name__ == '__main__':
    main()
