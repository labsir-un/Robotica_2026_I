import rclpy
from pincher_lab_utils import PincherLab, JOINTS, LIMITS
from actividad12_ik import ik_best

def main():
    rclpy.init(); node = PincherLab()
    puntos = [(0.15,0.05,0.15,0.3),(0.20,0.0,0.10,0.5),(0.05,0.15,0.20,-0.2)]
    for x,y,z,th in puntos:
        q_act = tuple(node.current[j] for j in JOINTS[:4])
        lims = [LIMITS[j] for j in JOINTS[:4]]
        sol = ik_best(x,y,z,th,lims,q_act)
        if sol is None:
            print('inalcanzable o fuera de limites'); continue
        node.send(dict(zip(JOINTS[:4], sol))); node.spin_for(2.0)
    node.destroy_node(); rclpy.shutdown()

if __name__=='__main__': main()
