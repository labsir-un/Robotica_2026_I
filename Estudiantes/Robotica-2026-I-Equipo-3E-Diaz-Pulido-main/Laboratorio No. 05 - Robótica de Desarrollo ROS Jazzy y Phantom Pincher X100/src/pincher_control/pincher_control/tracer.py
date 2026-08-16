import numpy as np
from pincher_control.Kin import Kinematic
from pincher_control.limits_pincher import Limits

class Tracer:
    def __init__(self, robot_kinematic: Kinematic, limits_analyzer: Limits):
        """
        Clase principal para trazar movimientos, validación de colisiones y 
        generación de trayectorias (interpolación).
        """
        self.robot = robot_kinematic
        self.limits = limits_analyzer
        self.intervalos_cacheados = {}

    def mapear_obstaculos(self, obstaculos):
        """Pre-calcula los micro-rangos prohibidos y guarda la geometría original."""
        print("Mapeando obstáculos en el C-Space...")
        self.obstaculos_geom = obstaculos  # <-- NUEVO: Guardar geometría
        for obs in obstaculos:
            nombre = obs.get('name', 'Obstáculo')
            lista_intervalos = self.limits.analyze_obstacle(obs, step=12.0)
            self.intervalos_cacheados[nombre] = lista_intervalos
            print(f" -> {nombre}: Mapeado con {len(lista_intervalos)} sub-regiones articulares prohibidas")
        print("Mapeo completo.\n")

    def _punto_en_obstaculo(self, x, y, z, obs, margen=2):
        """Matemática rápida para ver si un eslabón atraviesa un obstáculo."""
        if obs['type'] == 'box':
            cx, cy, cz = obs['center']
            dx, dy, dz = obs['dims'][0]/2, obs['dims'][1]/2, obs['dims'][2]/2
            R = self.robot.get_rotation_matrix(*np.radians(obs['rpy']))
            p_local = R.T @ np.array([x - cx, y - cy, z - cz])
            
            return (-dx - margen <= p_local[0] <= dx + margen) and \
                   (-dy - margen <= p_local[1] <= dy + margen) and \
                   (-dz - margen <= p_local[2] <= dz + margen)
                   
        elif obs['type'] == 'cylinder':
            cx, cy, cz = obs['center']
            r = obs['radius'] + margen
            h = obs['height'] + margen
            return ((x - cx)**2 + (y - cy)**2 <= r**2) and (cz - margen <= z <= cz + h + margen)
        return False

    def _esta_colisionando(self, q_sol):
        """Devuelve (True/False, Nombre_Obstaculo, Intervalo_Especifico)"""
        # 0. Revisar Límites Físicos de los Motores
        dentro_limites, msg = self.limits.check_physical_limits(q_sol)
        if not dentro_limites:
            # Reportamos la violación del límite para que la trayectoria lo descarte
            return True, msg, "Fuera de Rango Mecánico"
        
        # 1. Colisiones de la punta (TCP) según los conjuntos pequeños precalculados
        for nombre, lista_intervalos in self.intervalos_cacheados.items():
            if not lista_intervalos: continue
            
            for sub_intervalo in lista_intervalos:
                en_colision = True
                for i, art in enumerate(['θ1', 'θ2', 'θ3', 'θ4']):
                    if art in sub_intervalo:
                        vmin, vmax = sub_intervalo[art]
                        if not (vmin <= q_sol[i] <= vmax):
                            en_colision = False
                            break 
                
                # Si coincide con este pequeño conjunto, RETORNAMOS EL INTERVALO EXACTO
                if en_colision:
                    intervalo_limpio = {
                        art: [round(float(val_min), 2), round(float(val_max), 2)] 
                        for art, (val_min, val_max) in sub_intervalo.items()
                    }
                
                    return True, f"{nombre} (Choque en TCP/Efector Final)", intervalo_limpio
        # 2. Colisiones de las Juntas/Eslabones al vuelo (Soluciona el cilindro a 70°)
        if hasattr(self.robot, 'get_joint_positions') and hasattr(self, 'obstaculos_geom'):
            q4 = q_sol[3] if len(q_sol) > 3 else self.robot.theta4_internal
            puntos = self.robot.get_joint_positions(q_sol[0], q_sol[1], q_sol[2], q4)
            
            # Revisamos las "líneas" o tubos que conectan cada articulación
            for i in range(1, len(puntos) - 1):
                p_A, p_B = np.array(puntos[i]), np.array(puntos[i+1])
                distancia = np.linalg.norm(p_B - p_A)
                if distancia < 1.0: continue
                
                # Muestreamos el eslabón cada 20 milímetros
                num_muestras = max(3, int(distancia / 20.0))
                for t in np.linspace(0, 1, num_muestras):
                    pt = p_A + t * (p_B - p_A)
                    for obs in self.obstaculos_geom:
                        if self._punto_en_obstaculo(pt[0], pt[1], pt[2], obs):
                            # Creamos un intervalo representativo al vuelo y lo retornamos
                            margen = 3.0
                            interv_junta = {
                                'θ1': [q_sol[0]-margen, q_sol[0]+margen],
                                'θ2': [q_sol[1]-margen, q_sol[1]+margen],
                                'θ3': [q_sol[2]-margen, q_sol[2]+margen]
                            }
                            if len(q_sol)>3: interv_junta['θ4'] = [q_sol[3]-margen, q_sol[3]+margen]
                            
                            return True, f"{obs.get('name', 'Obs')} (Choque en Junta/Eslabón {i+1})", interv_junta

        return False, None, None
    
    def trace_forward(self, q1, q2, q3, q4=None):
        """Pasa de Ángulos -> Posición Cartesiana y Orientación (RPY)"""
        x, y, z, roll, pitch, yaw = self.robot.get_pose(q1, q2, q3, q4)
        return {
            'Coordenadas': (x, y, z),
            'Rotacion_RPY': (roll, pitch, yaw+90)
        }

    def trace_inverse(self, x, y, z, phi=None, theta4=None):
        """Pasa de Posición Cartesiana -> Posibles Ángulos (Codo Arriba/Abajo y Colisiones)"""
        exito, soluciones = self.robot.InvKin(x, y, z, phi_val=phi,theta4_in=theta4)
        
        if not exito:
            return {"Estado": "Error", "Mensaje": "Coordenadas fuera del alcance geométrico del robot."}

        resultados = []
        etiquetas = ["Codo Arriba", "Codo Abajo"]

        for idx, sol in enumerate(soluciones):
            etiqueta = etiquetas[idx] if idx < len(etiquetas) else f"Solución {idx+1}"
            
            # Validar colisiones usando la caché de obstáculos
            colision, obstaculo_nombre, intervalo_causante = self._esta_colisionando(sol)
            estado_seguridad = "ALCANZABLE (Seguro)" if not colision else f"¡COLISIÓN! ({obstaculo_nombre})"
            
            resultados.append({
                'Tipo': etiqueta,
                'Configuracion': sol,
                'Estado': estado_seguridad,
                'Colision': colision,
                'Intervalo Causante': intervalo_causante
            })
            
        return {"Estado": "Éxito", "Soluciones": resultados}

    def interpolar_trayectoria(self, q_start, q_end, steps, method='lineal', validar_colisiones=False):
        """
        Genera una trayectoria angular suave entre q_start y q_end.
        Opciones de 'method': 'lineal', 'cuadratica', 'cubica', 'cuartica', 'quintica', 'sinusoidal'
        """
        q_start = np.array(q_start)
        q_end = np.array(q_end)
        trayectoria = []
        reporte_colisiones = []

        # Vector de tiempo normalizado de 0 a 1
        t_norm = np.linspace(0, 1, steps)

        for t in t_norm:
            # Calcular factor de escala 's' según la matemática seleccionada
            if method == 'lineal':
                s = t
            elif method == 'cuadratica':
                s = 2 * (t**2) if t < 0.5 else 1 - ((-2 * t + 2)**2) / 2
            elif method == 'cubica':
                s = 3*(t**2) - 2*(t**3)
            elif method == 'cuartica':
                s = 8 * (t**4) if t < 0.5 else 1 - ((-2 * t + 2)**4) / 2
            elif method == 'quintica':
                s = 10*(t**3) - 15*(t**4) + 6*(t**5)
            elif method == 'sinusoidal':
                s = 0.5 - 0.5 * np.cos(np.pi * t)
            else:
                s = t # Lineal por defecto

            # Aplicar la escala al delta de posiciones
            q_actual = q_start + s * (q_end - q_start)
            trayectoria.append(q_actual.tolist())

            if validar_colisiones:
                colision, obstaculo_nombre, intervalo_causante = self._esta_colisionando(q_actual)
                if colision:
                    # Caso 1: Los motores intentan ir más allá de su límite físico
                    if intervalo_causante == "Fuera de Rango Mecánico":
                        reporte_colisiones.append(f"⚠️ LÍMITE MECÁNICO -> {obstaculo_nombre}")
                    
                    # Caso 2: Colisión física real en el espacio de trabajo
                    else:
                        # Extraemos "Qué chocó" y "Con qué" separando el string
                        if "(Choque en" in obstaculo_nombre:
                            partes = obstaculo_nombre.split(" (Choque en ")
                            con_que = partes[0].strip()
                            que_colisiono = partes[1].replace(")", "").strip()
                        else:
                            con_que = obstaculo_nombre
                            que_colisiono = "Desconocido"
                            
                        # Calculamos DÓNDE estaba el TCP en ese instante (X, Y, Z)
                        q4_val = q_actual[3] if len(q_actual) > 3 else None
                        x, y, z, _, _, _ = self.robot.get_pose(q_actual[0], q_actual[1], q_actual[2], q4_val)
                        
                        reporte_colisiones.append(
                            f"🛑 COLISIÓN | ¿Qué chocó?: {que_colisiono} | "
                            f"¿Con qué?: {con_que} | "
                            f"¿Dónde (XYZ del TCP)?: [X:{x:.1f}, Y:{y:.1f}, Z:{z:.1f}] | "
                            f"Intervalo: {intervalo_causante}"
                        )
                else:
                    reporte_colisiones.append("✅ Seguro")
        return trayectoria, reporte_colisiones
                    
            

    def interpolar_trayectoria_cartesiana(self, pose_start, pose_end, steps, method='lineal'):
        """
        Genera una trayectoria a partir de poses Cartesianas: 
        pose_start/end en formato (x, y, z, phi). Retorna la interpolación en ángulos.
        """
        # Calcular inversa para el punto inicial
        inv_start = self.trace_inverse(*pose_start)
        if inv_start['Estado'] != "Éxito": return None, ["Punto de inicio inalcanzable"]
        
        # Calcular inversa para el punto final
        inv_end = self.trace_inverse(*pose_end)
        if inv_end['Estado'] != "Éxito": return None, ["Punto final inalcanzable"]

        # Se toma la primera configuración segura disponible
        q_start = next((sol['Configuracion'] for sol in inv_start['Soluciones'] if not sol['Colision']), None)
        q_end = next((sol['Configuracion'] for sol in inv_end['Soluciones'] if not sol['Colision']), None)

        if not q_start or not q_end:
            return None, ["Colisión en los puntos extremos elegidos"]

        # Interpolar en el espacio articular
        return self.interpolar_trayectoria(q_start, q_end, steps, method=method, validar_colisiones=True)

    def graficar_trayectoria(self, theta1=0.0, theta2=0.0, theta3=0.0, theta4=0.0, obstacles=None):
        """Delega la llamada de graficación a la clase cinemática subyacente con sus parámetros."""
        self.robot.plot(theta1, theta2, theta3, theta4=theta4, obstacles=obstacles)