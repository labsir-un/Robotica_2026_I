from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
import math
from matplotlib.textpath import TextPath
 
#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

# Elegir un robot (si hay varios, aparece un popup)
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")

# Conectar al robot físico
#if not robot.Connect():
#    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")

# Confirmar conexión
#if not robot.ConnectedState():
#    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

#print("Robot conectado correctamente.")

#------------------------------------------------
# 2) Cargar el Frame (ya existente) donde quieres dibujar
#    Ajusta el nombre si tu Frame se llama diferente
#------------------------------------------------
frame_name = "Frame_from_Target1"
frame = RDK.Item(frame_name, ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception(f'No se encontró el Frame "{frame_name}" en la estación.')

# Asignamos este frame al robot
robot.setPoseFrame(frame)
# Usamos la herramienta activa
robot.setPoseTool(robot.PoseTool())

# Ajustes de velocidad y blending
robot.setSpeed(300)   # mm/s - Ajusta según necesites
robot.setRounding(5)  # blending (radio de curvatura)

#------------------------------------------------
# 3) Parámetros de la espiral
#------------------------------------------------
num_points = 1000
theta_max = 4 * math.pi   # controla cuántas vueltas (3 vueltas)
A = 10                    # factor de escala (mm por radian)

z_surface = 0
z_safe = 50

#------------------------------------------------
# 4) Ir al centro en altura segura
#------------------------------------------------
target = RDK.Item("Target Home", ITEM_TYPE_TARGET)
robot.MoveJ(target)

robot.MoveJ(transl(0, 0, z_surface + z_safe))
robot.MoveL(transl(0, 0, z_surface))

#------------------------------------------------
# 5) Dibujar espiral r = A * theta
#------------------------------------------------
for i in range(num_points + 1):
    t = i / num_points
    theta = theta_max * t

    r = A * theta

    x = r * math.sin(theta)
    y = -r * math.cos(theta)

    robot.MoveL(transl(x, y, z_surface))

# Salida segura
robot.MoveL(transl(x, y, z_surface + z_safe))
robot.MoveJ(target)

#------------------------------------------------
# 4) Ir al centro en altura segura
#------------------------------------------------
target = RDK.Item("Target Home", ITEM_TYPE_TARGET)
robot.MoveJ(target)

robot.MoveJ(transl(0, 0, z_surface + z_safe))
robot.MoveL(transl(0, 0, z_surface))

#------------------------------------------------
# 5) Dibujar espiral r = A * theta
#------------------------------------------------
for i in range(num_points + 1):
    t = i / num_points
    theta = -theta_max * t

    r = A * theta

    x = r * math.sin(theta)
    y = -r * math.cos(theta)
    robot.MoveL(transl(x, y, z_surface))


# Salida segura
robot.MoveL(transl(x, y, z_surface + z_safe))
robot.MoveJ(target)


# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(x, y, z_surface - z_safe))

robot.MoveJ(target)

print(f"¡Figura (rosa polar) completada en el frame '{frame_name}'!")
