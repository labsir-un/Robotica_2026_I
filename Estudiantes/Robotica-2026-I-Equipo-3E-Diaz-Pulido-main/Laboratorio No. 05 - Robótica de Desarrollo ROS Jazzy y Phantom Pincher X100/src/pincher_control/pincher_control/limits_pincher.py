import numpy as np
from pincher_control.Kin import Kinematic

class Limits:
    def __init__(self, robot_kinematic: Kinematic):
        self.robot = robot_kinematic
    
    def analyze_points(self, points, phi_val=None, theta4_in=None, margin=3.0):
        """Calcula la cinemática inversa y crea una nube de micro-intervalos (vóxeles) en C-Space"""
        c_space_intervals = []

        for pt in points:
            x, y, z = pt
            exito, listas_angulos = self.robot.InvKin(x, y, z, phi_val=phi_val, theta4_in=theta4_in)
            if exito:
                # Iteramos sobre las múltiples soluciones (separa naturalmente codo arriba y abajo)
                for angles in listas_angulos: 
                    # Creamos un micro-intervalo exclusivo para este punto específico
                    
                    intervalo_punto = {
                        'θ1': [round(float(angles[0] - margin), 2), round(float(angles[0] + margin), 2)],
                        'θ2': [round(float(angles[1] - margin), 2), round(float(angles[1] + margin), 2)],
                        'θ3': [round(float(angles[2] - margin), 2), round(float(angles[2] + margin), 2)]
                    }
                    if len(angles) == 4: 
                        intervalo_punto['θ4'] = [round(float(angles[3] - margin), 2), round(float(angles[3] + margin), 2)]
                                        
                    c_space_intervals.append(intervalo_punto)

        return c_space_intervals

    def get_oriented_box_points(self, center, dims, rpy, step=5.0):
        """Genera la nube de puntos para una caja inclinada"""
        dx, dy, dz = dims[0]/2, dims[1]/2, dims[2]/2
        x_s = np.arange(-dx, dx + step, step)
        y_s = np.arange(-dy, dy + step, step)
        z_s = np.arange(-dz, dz + step, step)
        X, Y, Z = np.meshgrid(x_s, y_s, z_s)
        pts_local = np.vstack((X.ravel(), Y.ravel(), Z.ravel())).T
        
        R = self.robot.get_rotation_matrix(*np.radians(rpy))
        pts_world = (R @ pts_local.T).T + center
        return pts_world

    def get_cylinder_points(self, center, radius, height, step=5.0):
        """Genera la nube de puntos para un cilindro vertical"""
        cx, cy, cz = center
        x_s = np.arange(cx - radius, cx + radius + step, step)
        y_s = np.arange(cy - radius, cy + radius + step, step)
        z_s = np.arange(cz, cz + height + step, step)
        
        X, Y, Z = np.meshgrid(x_s, y_s, z_s)
        mask = (X - cx)**2 + (Y - cy)**2 <= radius**2
        pts = np.vstack((X[mask], Y[mask], Z[mask])).T
        return pts

    def analyze_obstacle(self, obs, step=10.0):
        """Enrutador que genera puntos y analiza según el tipo de obstáculo"""
        if obs['type'] == 'box':
            pts = self.get_oriented_box_points(obs['center'], obs['dims'], obs['rpy'], step)
        elif obs['type'] == 'cylinder':
            pts = self.get_cylinder_points(obs['center'], obs['radius'], obs['height'], step)
        return self.analyze_points(pts)
    
    def graficar_limites(self, theta1=0.0, theta2=0.0, theta3=0.0, theta4=0.0, obstacles=None):
        """Delega la graficación a la clase principal de cinemática con sus respectivos parámetros."""
        self.robot.plot(theta1, theta2, theta3, theta4=theta4, obstacles=obstacles)
        
    def check_physical_limits(self, angles):
        """
        Verifica que los ángulos estén dentro de los límites mecánicos de los servos.
        Retorna: (Booleano_es_valido, Mensaje_de_error)
        """
        # Array de límites mecánicos: (min, max) para cada articulación
        limites_motores = [
            (-150.0, 150.0), # θ1 (Base)
            (-95.0, 95.0),   # θ2 (Hombro)
            (-95.0, 95.0),   # θ3 (Codo)
            (-95.0, 95.0),   # θ4 (Muñeca)
            (-90.0, 90.0)    # θ5 (Gripper) -> Ajusta estos valores según tu hardware
        ]
        
        # Iteramos dinámicamente sobre los ángulos que reciba la función
        for i, ang in enumerate(angles):
            # Nos aseguramos de no salirnos del índice si pasas menos de 5 motores
            if i < len(limites_motores):
                lim_min, lim_max = limites_motores[i]
                
                if not (lim_min <= ang <= lim_max):
                    return False, f"Límite de motor excedido en θ{i+1}: {ang:.1f}° (Rango permitido: {lim_min}° a {lim_max}°)"
                    
        return True, "Dentro de límites"