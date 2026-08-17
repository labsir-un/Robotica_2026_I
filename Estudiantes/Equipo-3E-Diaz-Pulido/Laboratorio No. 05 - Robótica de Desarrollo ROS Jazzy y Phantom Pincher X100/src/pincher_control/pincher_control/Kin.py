import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


class Kinematic:
    def __init__(self, l1, l2, l3, w1, w2, w3, lTool, wTool, thetaTool, phi, 
                 offset_t1=0.0, offset_t2=0.0, offset_t3=0.0, offset_t4=0.0,
                 dir_t1=1.0, dir_t2=1.0, dir_t3=1.0, dir_t4=1.0):
        self.l1, self.l2, self.l3 = l1, l2, l3
        self.w1, self.w2, self.w3 = w1, w2, w3
        self.lTool, self.wTool = lTool, wTool
        self.theta4_internal = thetaTool
        self.phi = phi
        
        # Offsets articulares (Para calibrar el "Cero" mecánico del robot)
        self.off1 = offset_t1
        self.off2 = offset_t2
        self.off3 = offset_t3
        self.off4 = offset_t4

        # Direcciones articulares (1.0 = normal, -1.0 = invertido)
        self.dir1 = dir_t1
        self.dir2 = dir_t2
        self.dir3 = dir_t3
        self.dir4 = dir_t4

    def MTH(self, theta, alpha, d, a):
        ct, st = np.cos(theta), np.sin(theta)
        ca, sa = np.cos(alpha), np.sin(alpha)
        return np.array([
            [ct, -ca*st,  sa*st, a*ct],
            [st,  ca*ct, -sa*ct, a*st],
            [ 0,     sa,     ca,    d],
            [ 0,      0,      0,    1]
        ])

    def DirKin(self, theta1, theta2, theta3, theta4=None, use_tcp_norm=False):
        if theta4 is None: theta4 = self.theta4_internal
        
        # NUEVO: Aplicar el multiplicador de dirección y el offset
        t1 = np.radians((theta1 * self.dir1) + self.off1)
        t2 = np.radians((theta2 * self.dir2) + self.off2)
        t3 = np.radians((theta3 * self.dir3) + self.off3)
        t4 = np.radians((theta4 * self.dir4) + self.off4)
        
        m1 = self.MTH(t1, np.pi/2.0, self.l1, self.w1)
        m2 = self.MTH(t2, 0.0, self.w2, self.l2)
        m3 = self.MTH(t3, 0.0, self.w3, self.l3)
        m4 = self.MTH(t4, 0.0, self.wTool, self.lTool)
        resMatrix = m1 @ m2 @ m3 @ m4
        
        if use_tcp_norm:
            angle = np.radians(90.0)
            R_adj = np.eye(4)
            R_adj[:3, :3] = np.array([[np.cos(angle), 0, np.sin(angle)], [0, 1, 0], [-np.sin(angle), 0, np.cos(angle)]])
            resMatrix = resMatrix @ R_adj
        return resMatrix

    def get_pose(self, theta1, theta2, theta3, theta4=None, use_tcp_norm=False):
        """Retorna (X, Y, Z, Roll, Pitch, Yaw) a partir de los ángulos"""
        # Se pasa el argumento use_tcp_norm hacia DirKin
        T = self.DirKin(theta1, theta2, theta3, theta4, use_tcp_norm=use_tcp_norm)
        x, y, z = T[0, 3], T[1, 3], T[2, 3]
        
        sy = np.sqrt(T[0,0]**2 + T[1,0]**2)
        singular = sy < 1e-6
        if not singular:
            roll = np.arctan2(T[2,1], T[2,2])
            pitch = np.arctan2(-T[2,0], sy)
            yaw = np.arctan2(T[1,0], T[0,0])
        else:
            roll = np.arctan2(-T[1,2], T[1,1])
            pitch = np.arctan2(-T[2,0], sy)
            yaw = 0
    
        return x, y, z, np.degrees(roll), np.degrees(pitch), np.degrees(yaw)
    
    
    def get_joint_positions(self, theta1, theta2, theta3, theta4=None):
        """Retorna las coordenadas (X,Y,Z) de la base, juntas y el TCP."""
        if theta4 is None: theta4 = self.theta4_internal
        
        t1 = np.radians((theta1 * self.dir1) + self.off1)
        t2 = np.radians((theta2 * self.dir2) + self.off2)
        t3 = np.radians((theta3 * self.dir3) + self.off3)
        t4 = np.radians((theta4 * self.dir4) + self.off4)
        
        # Origen (Base)
        T0 = np.eye(4)
        
        # Multiplicación acumulativa de matrices para hallar cada codo
        m1 = self.MTH(t1, np.pi/2.0, self.l1, self.w1)
        T1 = m1
        
        m2 = self.MTH(t2, 0.0, self.w2, self.l2)
        T2 = T1 @ m2
        
        m3 = self.MTH(t3, 0.0, self.w3, self.l3)
        T3 = T2 @ m3
        
        m4 = self.MTH(t4, 0.0, self.wTool, self.lTool)
        T4 = T3 @ m4
        
        # Retorna: [Base, Junta 1, Junta 2, Junta 3, TCP]
        return [T0[:3,3], T1[:3,3], T2[:3,3], T3[:3,3], T4[:3,3]]
    
    
    def InvKin(self, x, y, z, phi_val=None, theta4_in=None):
        """Retorna: (Exito, [Soluciones])"""
        W = self.w2 + self.w3 + self.wTool
        r_xy_sq = (x * x) + (y * y)
        if r_xy_sq < (W * W): return False, []
        raiz_w = np.sqrt(r_xy_sq - (W * W))
        
        t1_rad = np.arctan2(y, x) + np.arctan2(W, raiz_w)
        zRel = z - self.l1
        R = (x * np.cos(t1_rad)) + (y * np.sin(t1_rad)) - self.w1
        
        soluciones = []
        
        # === Lógica 4-DOF ===
        if phi_val is not None:
            phi_rad = np.radians(phi_val)
            Rj = R - self.lTool * np.cos(phi_rad)
            zj = zRel - self.lTool * np.sin(phi_rad)
            D = ((Rj**2) + (zj**2) - (self.l2**2) - (self.l3**2)) / (2.0 * self.l2 * self.l3)
            
            if abs(D) > 1.0: return False, []
            
            t3_rad_opts = [
                np.arctan2(-np.sqrt(1.0 - (D**2)), D),
                np.arctan2(np.sqrt(1.0 - (D**2)), D)
            ]
            
            for t3_rad in t3_rad_opts:
                t2_rad = np.arctan2(zj, Rj) - np.arctan2(self.l3 * np.sin(t3_rad), self.l2 + self.l3 * np.cos(t3_rad))
                t4_rad = phi_rad - (t2_rad + t3_rad)
                
                # NUEVO: Invertir el proceso (Resta Offset y multiplica por Dirección)
                th1 = (np.degrees(t1_rad) - self.off1) * self.dir1
                th2 = (np.degrees(t2_rad) - self.off2) * self.dir2
                th3 = (np.degrees(t3_rad) - self.off3) * self.dir3
                th4 = (np.degrees(np.arctan2(np.sin(t4_rad), np.cos(t4_rad))) - self.off4) * self.dir4
                
                soluciones.append((th1, th2, th3, th4))
                
            return True, soluciones

        # === Lógica 3-DOF ===
        else:
            t4_in = theta4_in if theta4_in is not None else self.theta4_internal
            theta4_rad = np.radians((t4_in * self.dir4) + self.off4)
            L_virt = np.sqrt((self.l3**2) + (self.lTool**2) + (2.0 * self.l3 * self.lTool * np.cos(theta4_rad)))
            D = ((R**2) + (zRel**2) - (self.l2**2) - (L_virt**2)) / (2.0 * self.l2 * L_virt)
            
            if abs(D) > 1.0: return False, []
            
            gamma_opts = [
                np.arctan2(-np.sqrt(1.0 - (D**2)), D), 
                np.arctan2(np.sqrt(1.0 - (D**2)), D)
            ]
            beta = np.arctan2(self.lTool * np.sin(theta4_rad), self.l3 + self.lTool * np.cos(theta4_rad))
            
            for gamma in gamma_opts:
                t3_rad = gamma - beta
                t2_rad = np.arctan2(zRel, R) - np.arctan2(L_virt * np.sin(gamma), self.l2 + L_virt * np.cos(gamma))
                
                # NUEVO: Invertir el proceso (Resta Offset y multiplica por Dirección)
                th1 = (np.degrees(t1_rad) - self.off1) * self.dir1
                th2 = (np.degrees(t2_rad) - self.off2) * self.dir2
                th3 = (np.degrees(t3_rad) - self.off3) * self.dir3
                
                soluciones.append((th1, th2, th3))
                
            return True, soluciones

    # Funciones de dibujo _draw_frame, get_rotation_matrix, _draw_oriented_box, _draw_cylinder
    def _draw_frame(self, ax, T_matrix, axis_length=10.0, label=""):
        origen = T_matrix[:3, 3]
        ax.plot([origen[0], origen[0] + T_matrix[0,0]*axis_length], [origen[1], origen[1] + T_matrix[1,0]*axis_length], [origen[2], origen[2] + T_matrix[2,0]*axis_length], 'r-', linewidth=2)
        ax.plot([origen[0], origen[0] + T_matrix[0,1]*axis_length], [origen[1], origen[1] + T_matrix[1,1]*axis_length], [origen[2], origen[2] + T_matrix[2,1]*axis_length], 'g-', linewidth=2)
        ax.plot([origen[0], origen[0] + T_matrix[0,2]*axis_length], [origen[1], origen[1] + T_matrix[1,2]*axis_length], [origen[2], origen[2] + T_matrix[2,2]*axis_length], 'b-', linewidth=2)
        if label: ax.text(origen[0], origen[1], origen[2] + axis_length*0.2, label, color='black', weight='bold')

    def get_rotation_matrix(self, r, p, y):
        cr, sr = np.cos(r), np.sin(r)
        cp, sp = np.cos(p), np.sin(p)
        cy, sy = np.cos(y), np.sin(y)
        Rx = np.array([[1, 0, 0], [0, cr, -sr], [0, sr, cr]])
        Ry = np.array([[cp, 0, sp], [0, 1, 0], [-sp, 0, cp]])
        Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
        return Rz @ Ry @ Rx

    def _draw_oriented_box(self, ax, center, dims, rpy, color='orange', alpha=0.5):
        dx, dy, dz = dims[0]/2, dims[1]/2, dims[2]/2
        v_local = np.array([
            [-dx, -dy, -dz], [dx, -dy, -dz], [dx, dy, -dz], [-dx, dy, -dz],
            [-dx, -dy, dz],  [dx, -dy, dz],  [dx, dy, dz],  [-dx, dy, dz]
        ])
        R = self.get_rotation_matrix(*np.radians(rpy))
        v_world = (R @ v_local.T).T + center
        faces = [[v_world[0], v_world[1], v_world[2], v_world[3]], [v_world[4], v_world[5], v_world[6], v_world[7]], [v_world[0], v_world[1], v_world[5], v_world[4]], [v_world[2], v_world[3], v_world[7], v_world[6]], [v_world[1], v_world[2], v_world[6], v_world[5]], [v_world[0], v_world[3], v_world[7], v_world[4]]]
        ax.add_collection3d(Poly3DCollection(faces, facecolors=color, linewidths=1, edgecolors='darkred', alpha=alpha))
        return v_world 

    def _draw_cylinder(self, ax, center, radius, height, color='purple', alpha=0.5):
        cx, cy, cz = center
        z = np.linspace(cz, cz + height, 10)
        theta = np.linspace(0, 2*np.pi, 20)
        theta_grid, z_grid = np.meshgrid(theta, z)
        x_grid = cx + radius * np.cos(theta_grid)
        y_grid = cy + radius * np.sin(theta_grid)
        ax.plot_surface(x_grid, y_grid, z_grid, color=color, alpha=alpha, edgecolor='none')
        ax.plot_surface(x_grid, y_grid, np.full_like(z_grid, cz), color=color, alpha=alpha, edgecolor='none')
        ax.plot_surface(x_grid, y_grid, np.full_like(z_grid, cz + height), color=color, alpha=alpha, edgecolor='none')

    def plot(self, theta1, theta2, theta3, theta4=None, obstacles=None):
        if theta4 is None: theta4 = self.theta4_internal
        
        # NUEVO: Aplicar el multiplicador de dirección y el offset para que la gráfica respete el ajuste
        t1 = np.radians((theta1 * self.dir1) + self.off1)
        t2 = np.radians((theta2 * self.dir2) + self.off2)
        t3 = np.radians((theta3 * self.dir3) + self.off3)
        t4 = np.radians((theta4 * self.dir4) + self.off4)

        T0 = np.eye(4)
        T1 = T0 @ self.MTH(t1, np.pi/2.0, self.l1, self.w1)
        T2 = T1 @ self.MTH(t2, 0.0, self.w2, self.l2)
        T3 = T2 @ self.MTH(t3, 0.0, self.w3, self.l3)
        T4 = T3 @ self.MTH(t4, 0.0, self.wTool, self.lTool)

        x_coords = [T0[0,3], T1[0,3], T2[0,3], T3[0,3], T4[0,3]]
        y_coords = [T0[1,3], T1[1,3], T2[1,3], T3[1,3], T4[1,3]]
        z_coords = [T0[2,3], T1[2,3], T2[2,3], T3[2,3], T4[2,3]]

        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')

        all_x, all_y, all_z = x_coords.copy(), y_coords.copy(), z_coords.copy()

        R_max = np.sqrt(self.w1**2 + self.l1**2) + np.sqrt(self.w2**2 + self.l2**2) + np.sqrt(self.w3**2 + self.l3**2) + np.sqrt(self.wTool**2 + self.lTool**2)

        grid_size = R_max * 1.2
        xx, yy = np.meshgrid(np.linspace(-grid_size, grid_size, 10), np.linspace(-grid_size, grid_size, 10))
        zz = np.zeros_like(xx)
        ax.plot_surface(xx, yy, zz, color='gray', alpha=0.3, edgecolor='none')

        u = np.linspace(0, 2 * np.pi, 40)
        v = np.linspace(0, np.pi, 20)
        x_sphere = R_max * np.outer(np.cos(u), np.sin(v))
        y_sphere = R_max * np.outer(np.sin(u), np.sin(v))
        z_sphere = R_max * np.outer(np.ones_like(u), np.cos(v))
        
        ax.plot_surface(x_sphere, y_sphere, z_sphere, color='cyan', alpha=0.08, edgecolor='none')
        all_x.extend([-R_max, R_max]); all_y.extend([-R_max, R_max]); all_z.extend([-R_max, R_max])

        if obstacles is not None:
            for obs in obstacles:
                if obs['type'] == 'box':
                    verts = self._draw_oriented_box(ax, obs['center'], obs['dims'], obs['rpy'])
                    all_x.extend(verts[:,0]); all_y.extend(verts[:,1]); all_z.extend(verts[:,2])
                elif obs['type'] == 'cylinder':
                    self._draw_cylinder(ax, obs['center'], obs['radius'], obs['height'])
                    cx, cy, cz = obs['center']; r, h = obs['radius'], obs['height']
                    all_x.extend([cx-r, cx+r]); all_y.extend([cy-r, cy+r]); all_z.extend([cz, cz+h])

        ax.plot(x_coords, y_coords, z_coords, '-ko', linewidth=4, markersize=8, label='Robot')

        eje_len = (self.l1 + self.l2 + self.l3 + self.lTool) * 0.15
        if eje_len == 0: eje_len = 10.0
        self._draw_frame(ax, T0, axis_length=eje_len, label='Base')
        self._draw_frame(ax, T4, axis_length=eje_len, label='TCP')

        max_range = np.array([max(all_x)-min(all_x), max(all_y)-min(all_y), max(all_z)-min(all_z)]).max() / 2.0
        mid_x = (max(all_x) + min(all_x)) * 0.5
        mid_y = (max(all_y) + min(all_y)) * 0.5
        mid_z = (max(all_z) + min(all_z)) * 0.5

        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)

        ax.set_xlabel('Eje X'); ax.set_ylabel('Eje Y'); ax.set_zlabel('Eje Z')
        ax.set_title('Espacio de Trabajo: Robot, Alcance Máximo y Obstáculos')
        plt.show()