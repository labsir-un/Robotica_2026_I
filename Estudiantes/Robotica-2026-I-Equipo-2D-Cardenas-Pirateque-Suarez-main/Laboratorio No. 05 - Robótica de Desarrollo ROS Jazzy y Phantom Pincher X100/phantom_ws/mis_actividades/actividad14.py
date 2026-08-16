#!/usr/bin/env python3
"""
Actividad 14 - Trazado Cartesiano en RViz.
"""

import time
import math
import threading
import tkinter as tk
from tkinter import ttk

import rclpy
from geometry_msgs.msg import Point
from visualization_msgs.msg import Marker
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy

# Import local de la arquitectura del robot
from joint_selector import JointSelector, JOINTS

# Medidas Físicas Exactas del PhantomX
L1, L2, L3, L4 = 0.0450, 0.1070, 0.1070, 0.1088

# EL ARREGLO MAESTRO PARA RVIZ
FRAME_ROBOT = "phantomx_pincher_base_link"

class InterfazDibujo:
    def __init__(self, master, node_robot):
        self.master = master
        self.node = node_robot
        self.master.title("Actividad 14 - Trazado Cartesiano")
        self.master.geometry("650x700")
        
        self.parada_emergencia = False
        self.detener_rutina = False
        
        qos = QoSProfile(
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            reliability=QoSReliabilityPolicy.RELIABLE,
            durability=QoSDurabilityPolicy.VOLATILE
        )
        self.marker_pub = self.node.create_publisher(Marker, '/visualization_marker', qos)
        self.marker_id = 0
        
        # --- CONFIGURACIÓN DEL LIENZO GEOMÉTRICO ---
        self.lienzo_cx_figuras = 140.0
        self.lienzo_cz_figuras = 50.0  
        self.size_figuras = 50.0
        
        # --- CONFIGURACIÓN DEL LIENZO DE LETRAS ---
        self.lienzo_cx_letras = 100.0
        self.lienzo_cz_letras = 75.0   
        self.size_letras = 36.0        # Ajustado para compensar el espacio
        self.espacio_letras = 10.0     # ¡Aumentado de 5mm a 15mm!
        
        self.lienzo_cy = 0.0 
        
        # --- ABECEDARIO COMPLETO (A-Z) ---
        self.letras_soportadas = {
            'A': [(0,0), (0.5,1), (1,0), (0.75,0.5), (0.25,0.5)],
            'B': [(0,0), (0,1), (0.75,1), (1,0.75), (0.75,0.5), (0,0.5), (0.75,0.5), (1,0.25), (0.75,0), (0,0)],
            'C': [(1,0.8), (0.8,1), (0.2,1), (0,0.8), (0,0.2), (0.2,0), (0.8,0), (1,0.2)],
            'D': [(0,0), (0,1), (0.5,1), (0.8,0.8), (0.8,0.2), (0.5,0), (0,0)],
            'E': [(1,1), (0,1), (0,0), (1,0), (0,0), (0,0.5), (0.8,0.5)],
            'F': [(0,0), (0,1), (1,1), (0,1), (0,0.5), (0.8,0.5)],
            'G': [(1,0.8), (0.5,1), (0,0.8), (0,0.2), (0.5,0), (1,0.2), (1,0.5), (0.5,0.5)],
            'H': [(0,1), (0,0), (0,0.5), (1,0.5), (1,1), (1,0)],
            'I': [(0.2,1), (0.8,1), (0.5,1), (0.5,0), (0.2,0), (0.8,0)],
            'J': [(0.2,1), (0.8,1), (0.5,1), (0.5,0.2), (0.3,0), (0,0.2)],
            'K': [(0,1), (0,0), (0,0.5), (1,1), (0,0.5), (1,0)],
            'L': [(0,1), (0,0), (1,0)],
            'M': [(0,0), (0,1), (0.5,0.5), (1,1), (1,0)],
            'N': [(0,0), (0,1), (1,0), (1,1)],
            'O': [(0.5,1), (0.2,1), (0,0.8), (0,0.2), (0.2,0), (0.8,0), (1,0.2), (1,0.8), (0.8,1), (0.5,1)],
            'P': [(0,0), (0,1), (0.8,1), (1,0.8), (1,0.6), (0.8,0.4), (0,0.4)],
            'Q': [(0.5,1), (0.2,1), (0,0.8), (0,0.2), (0.2,0), (0.8,0), (1,0.2), (1,0.8), (0.8,1), (0.5,1), (0.7,0.3), (1,0)],
            'R': [(0,0), (0,1), (0.8,1), (1,0.8), (1,0.6), (0.8,0.4), (0,0.4), (0.5,0.4), (1,0)],
            'S': [(1,0.8), (0.5,1), (0,0.8), (0,0.6), (1,0.4), (1,0.2), (0.5,0), (0,0.2)],
            'T': [(0,1), (1,1), (0.5,1), (0.5,0)],
            'U': [(0,1), (0,0.2), (0.2,0), (0.8,0), (1,0.2), (1,1)],
            'V': [(0,1), (0.5,0), (1,1)],
            'W': [(0,1), (0.2,0), (0.5,0.5), (0.8,0), (1,1)],
            'X': [(0,1), (1,0), (0.5,0.5), (0,0), (1,1)],
            'Y': [(0,1), (0.5,0.5), (1,1), (0.5,0.5), (0.5,0)],
            'Z': [(0,1), (1,1), (0,0), (1,0)]
        }
        
        self._crear_widgets()

    def _crear_widgets(self):
        # --- BOTONES DE SEGURIDAD ---
        frame_seguridad = tk.Frame(self.master)
        frame_seguridad.pack(padx=20, pady=15, fill="x")
        tk.Button(frame_seguridad, text="🚨 EMERGENCIA", bg="#dc3545", fg="white", font=("Arial", 10, "bold"), command=self._emergencia).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_seguridad, text="🛑 DETENER", bg="#fd7e14", fg="white", font=("Arial", 10, "bold"), command=self._detener).pack(side="left", expand=True, fill="x", padx=2)
        tk.Button(frame_seguridad, text="🏠 IR A HOME", bg="#17a2b8", fg="white", font=("Arial", 10, "bold"), command=self._ir_home).pack(side="left", expand=True, fill="x", padx=2)

        # --- TIEMPO DE ESPERA ---
        marco_vel = ttk.LabelFrame(self.master, text="Configuración de Trazado", padding=10)
        marco_vel.pack(padx=20, pady=5, fill="x")
        ttk.Label(marco_vel, text="Tiempo de espera (dt) [s]:").pack(side="left", padx=5)
        self.var_dt = tk.DoubleVar(value=0.1) 
        ttk.Spinbox(marco_vel, from_=0.01, to=0.5, increment=0.01, textvariable=self.var_dt, width=6).pack(side="left", padx=5)

        # --- FIGURAS ---
        marco_figuras = ttk.LabelFrame(self.master, text="Dibujo Geométrico", padding=10)
        marco_figuras.pack(padx=20, pady=5, fill="x")
        tk.Button(marco_figuras, text="🔺 Triángulo", bg="#6610f2", fg="white", font=("Arial", 10, "bold"), command=lambda: self._iniciar_dibujo("triangulo")).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(marco_figuras, text="🟦 Cuadrado", bg="#6610f2", fg="white", font=("Arial", 10, "bold"), command=lambda: self._iniciar_dibujo("cuadrado")).pack(side="left", expand=True, fill="x", padx=5)
        tk.Button(marco_figuras, text="⭕ Círculo", bg="#6610f2", fg="white", font=("Arial", 10, "bold"), command=lambda: self._iniciar_dibujo("circulo")).pack(side="left", expand=True, fill="x", padx=5)

        # --- LETRAS ---
        marco_letras = ttk.LabelFrame(self.master, text="Trazado de Iniciales", padding=10)
        marco_letras.pack(padx=20, pady=10, fill="x")
        ttk.Label(marco_letras, text="Iniciales (Max 5):").pack(side="left", padx=5)
        self.var_iniciales = tk.StringVar(value="DFSCP") 
        ttk.Entry(marco_letras, textvariable=self.var_iniciales, width=10, font=("Arial", 12, "bold")).pack(side="left", padx=5)
        tk.Button(marco_letras, text="✏️ TRAZAR INICIALES", bg="#198754", fg="white", font=("Arial", 10, "bold"), command=lambda: self._iniciar_dibujo("letras")).pack(side="right", padx=10, fill="x", expand=True)

        # --- CONSOLA ---
        marco_consola = ttk.LabelFrame(self.master, text="Consola de Trazado", padding=10)
        marco_consola.pack(padx=20, pady=5, fill="both", expand=True)
        self.txt_consola = tk.Text(marco_consola, height=8, bg="#1e1e1e", fg="#00ff00", font=("Consolas", 10))
        self.txt_consola.pack(fill="both", expand=True)
        
        tk.Button(self.master, text="🧹 LIMPIAR LIENZO RVIZ", bg="#ffc107", font=("Arial", 10, "bold"), command=self._borrar_tinta).pack(pady=10)

    # ================= LOG Y BOTONES =================
    def _log(self, msg, color="#00ff00"):
        self.txt_consola.tag_config(color, foreground=color)
        self.txt_consola.insert(tk.END, msg + "\n", color)
        self.txt_consola.see(tk.END)

    def _emergencia(self):
        self.parada_emergencia = True
        self.node.apagar_torque_solamente()
        self._log("\n🚨 EMERGENCIA: Motores detenidos bruscamente.", "red")

    def _detener(self):
        self.detener_rutina = True
        self._log("\n🛑 DIBUJO DETENIDO (Control manual activo).", "orange")

    def _ir_home(self):
        self._log("Moviendo a HOME...", "cyan")
        self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.0)

    # ================= RVIZ: SPHERES (FUERZA BRUTA) =================
    def _agregar_punto_rviz(self, x, y, z):
        m = Marker()
        m.header.frame_id = FRAME_ROBOT
        m.header.stamp.sec = 0
        m.header.stamp.nanosec = 0
        
        m.ns = "trazado_robot"
        m.id = self.marker_id
        self.marker_id += 1 
        
        m.type = Marker.SPHERE
        m.action = Marker.ADD
        
        m.pose.position.x = x / 1000.0
        m.pose.position.y = y / 1000.0
        m.pose.position.z = z / 1000.0
        m.pose.orientation.w = 1.0
        
        m.scale.x = 0.010 # ¡Afinado a 10 mm para no empastar las letras!
        m.scale.y = 0.010
        m.scale.z = 0.010
        
        m.color.a = 1.0
        m.color.r = 0.0
        m.color.g = 1.0
        m.color.b = 1.0 # Cian
        
        self.marker_pub.publish(m)

    def _borrar_tinta(self):
        m = Marker()
        m.header.frame_id = FRAME_ROBOT
        m.action = 3 # DELETEALL
        self.marker_pub.publish(m)
        self.marker_id = 0
        self._log("Lienzo borrado.", "yellow")

    # ================= CINEMÁTICA E INTERPOLACIÓN =================
    def _cinematica_inversa(self, x, y, z):
        theta_deg = -90.0 
        X, Y, Z = x/1000.0, y/1000.0, z/1000.0
        
        q1 = math.degrees(math.atan2(Y, X))
        R = math.sqrt(X**2 + Y**2)
        sigma_q_rad = math.radians(90.0 - theta_deg)
        
        R_wc = R - L4 * math.sin(sigma_q_rad)
        Z_wc = Z - L4 * math.cos(sigma_q_rad)
        
        dR = R_wc
        dZ = Z_wc - L1
        D = math.sqrt(dR**2 + dZ**2)
        
        if D > (L2 + L3 + 0.0001) or D < (abs(L2 - L3) - 0.0001):
            return None 
            
        cos_beta = max(-1.0, min(1.0, (L2**2 + L3**2 - D**2) / (2 * L2 * L3)))
        beta = math.acos(cos_beta)
        cos_alpha = max(-1.0, min(1.0, (L2**2 + D**2 - L3**2) / (2 * L2 * D)))
        alpha = math.acos(cos_alpha)
        gamma = math.atan2(dR, dZ)
        
        q2 = math.degrees(gamma - alpha)
        q3 = math.degrees(math.pi - beta)
        q4 = (90.0 - theta_deg) - q2 - q3
        
        return {"base": q1, "hombro": q2, "codo": q3, "muneca": q4, "pinza": 0.0}

    def _interpolar_segmento(self, p1, p2, resolucion_mm=2.0):
        dx, dy, dz = p2[0]-p1[0], p2[1]-p1[1], p2[2]-p1[2]
        distancia = math.sqrt(dx**2 + dy**2 + dz**2)
        if distancia == 0: return [p2]
        pasos = max(2, int(distancia / resolucion_mm))
        return [(p1[0] + dx*(i/pasos), p1[1] + dy*(i/pasos), p1[2] + dz*(i/pasos)) for i in range(1, pasos+1)]

    def _generar_puntos_clave(self, tipo):
        puntos = []
        cy = self.lienzo_cy
        
        if tipo == "letras":
            cx = self.lienzo_cx_letras
            cz = self.lienzo_cz_letras
            s = self.size_letras
            espacio = self.espacio_letras
            texto = self.var_iniciales.get().upper().strip()[:5]
            
            offset_y = ((len(texto) * s) + (len(texto) - 1) * espacio) / 2
            
            for i, char in enumerate(texto):
                if char in self.letras_soportadas:
                    centro_y = cy + offset_y - (s / 2) - (i * (s + espacio))
                    for u, v in self.letras_soportadas[char]:
                        puntos.append((cx + (v - 0.5) * s, centro_y - (u - 0.5) * s, cz))
                    if i < len(texto)-1: puntos.append("SALTO")
                else:
                    self._log(f"⚠️ Letra '{char}' no soportada.", "orange")
        else:
            cx = self.lienzo_cx_figuras
            cz = self.lienzo_cz_figuras
            s = self.size_figuras
            if tipo == "cuadrado":
                puntos = [(cx-s/2, cy+s/2, cz), (cx+s/2, cy+s/2, cz), (cx+s/2, cy-s/2, cz), (cx-s/2, cy-s/2, cz), (cx-s/2, cy+s/2, cz)]
            elif tipo == "triangulo":
                puntos = [(cx-s/2, cy+s/2, cz), (cx-s/2, cy-s/2, cz), (cx+s/2, cy, cz), (cx-s/2, cy+s/2, cz)]
            elif tipo == "circulo":
                for ang in range(0, 365, 10):
                    puntos.append((cx + (s/2)*math.sin(math.radians(ang)), cy + (s/2)*math.cos(math.radians(ang)), cz))
                    
        return puntos

    # ================= HILO DE TRAZADO =================
    def _iniciar_dibujo(self, tipo):
        self.txt_consola.delete('1.0', tk.END)
        self.parada_emergencia = False
        self.detener_rutina = False
        threading.Thread(target=self._rutina_trazado, args=(tipo,), daemon=True).start()

    def _rutina_trazado(self, tipo):
        self._borrar_tinta()
        
        cz_actual = self.lienzo_cz_letras if tipo == "letras" else self.lienzo_cz_figuras
        salto_offset_z = 15.0 # Un salto modesto para evitar que el brazo rompa el límite
        
        self._log(f"Iniciando trazado: {tipo.upper()}", "cyan")
        
        puntos_clave = self._generar_puntos_clave(tipo)
        if not puntos_clave: return

        self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.0)
        time.sleep(2.0)
        
        punto_actual = None
        
        for pt in puntos_clave:
            if self.parada_emergencia or self.detener_rutina: break
            dt = self.var_dt.get()
            
            if pt == "SALTO":
                self._log("--- LEVANTANDO LÁPIZ ---", "yellow")
                if punto_actual:
                    q_up = self._cinematica_inversa(punto_actual[0], punto_actual[1], cz_actual + salto_offset_z)
                    if q_up:
                        self.node.mover_simultaneo(q_up, espera_s=0.5)
                        time.sleep(0.5)
                punto_actual = None
                continue
                
            if punto_actual is None:
                q_hover = self._cinematica_inversa(pt[0], pt[1], cz_actual + salto_offset_z)
                if q_hover: self.node.mover_simultaneo(q_hover, espera_s=0.5); time.sleep(0.5)
                
                q_down = self._cinematica_inversa(pt[0], pt[1], pt[2])
                if q_down: self.node.mover_simultaneo(q_down, espera_s=0.5); time.sleep(0.5)
                
                self._agregar_punto_rviz(pt[0], pt[1], pt[2])
                punto_actual = pt
                continue

            segmento = self._interpolar_segmento(punto_actual, pt, resolucion_mm=2.0)
            
            for sub_pt in segmento:
                if self.parada_emergencia or self.detener_rutina: break
                
                q_objs = self._cinematica_inversa(sub_pt[0], sub_pt[1], sub_pt[2])
                if q_objs:
                    self.node.mover_simultaneo(q_objs, espera_s=0.0) 
                    self._agregar_punto_rviz(sub_pt[0], sub_pt[1], sub_pt[2])
                    self._log(f"🎨 Trazando -> X:{sub_pt[0]:.0f}, Y:{sub_pt[1]:.0f}", "white")
                    time.sleep(dt) 
                    
            punto_actual = pt

        if not self.parada_emergencia and not self.detener_rutina:
            self._log("\n✅ Trazado finalizado con éxito.", "green")
            
        if punto_actual:
            q_up_final = self._cinematica_inversa(punto_actual[0], punto_actual[1], cz_actual + salto_offset_z)
            if q_up_final:
                self.node.mover_simultaneo(q_up_final, espera_s=1.0)
                time.sleep(1.0)
                
        self.node.mover_simultaneo({name: 0.0 for name in JOINTS}, espera_s=2.0)

def main(args=None):
    rclpy.init(args=args)
    node_robot = JointSelector()
    threading.Thread(target=rclpy.spin, args=(node_robot,), daemon=True).start()
    time.sleep(1.0) 
    
    root = tk.Tk()
    app = InterfazDibujo(root, node_robot)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        rclpy.shutdown()

if __name__ == '__main__':
    main()