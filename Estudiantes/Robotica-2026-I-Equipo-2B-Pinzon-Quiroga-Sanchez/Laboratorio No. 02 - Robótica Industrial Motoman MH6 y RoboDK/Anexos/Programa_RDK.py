from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
from matplotlib.textpath import TextPath
import matplotlib.pyplot as plt
import math

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
if not robot.ConnectedState():
    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

print("Robot conectado correctamente.")

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
robot.setSpeed(100)   # mm/s - Ajusta según necesites
robot.setRounding(5)  # blending (radio de curvatura)

#------------------------------------------------
# 3) Parámetros de la figura (rosa polar)
#------------------------------------------------
num_points = 720       # Cuántos puntos muestreamos (mayor = más suave)
A = 150               # Amplitud (300 mm = radio máximo)
k = 5                  # Parámetro de la rosa (pétalos). Si es impar, habrá k pétalos; si es par, 2k
z_surface = 0          # Z=0 en el plano del frame
z_safe = 50            # Altura segura para aproximarse y salir

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------

#4.1 Mov a home
target_name="Target_home"
target = RDK.Item(target_name, ITEM_TYPE_TARGET) #Buscar target de la estación
robot.MoveJ(target)
#4.2 Mov al centro de la rosa
# El centro de la rosa (r=0) corresponde a x=0, y=0
robot.MoveJ(transl(500, 0, z_surface - z_safe))

# Bajamos a la "superficie" (Z=0)
robot.MoveL(transl(500, 0, z_surface))

#------------------------------------------------
# 5) Dibujar la rosa polar
#    r = A * sin(k*theta)
#    x = r*cos(theta), y = r*sin(theta)
#------------------------------------------------
# Recorremos theta de 0 a 2*pi (una vuelta completa)
full_turn = 8*math.pi

for i in range(num_points+1):
    # Fracción entre 0 y 1
    t = i / num_points
    # Ángulo actual
    theta = full_turn * t

    # Calculamos r
    r = 200*math.cos((5/4)*theta)*math.sin(2*theta)

    # Convertimos a coordenadas Cartesianas X, Y
    x = r * math.cos(theta)+500
    y = r * math.sin(theta)

    # Movemos linealmente (MoveL) en el plano del Frame
    robot.MoveL(transl(x, y, z_surface))

tp = TextPath((-150,0), "JESÚS", size=100)
tp1 = TextPath((-150,120), "PAULA", size=100)
tp2 = TextPath((-150,240), "DAVID", size=100)

verts = tp.vertices
codes = tp.codes
verts1 = tp1.vertices
codes1 = tp1.codes
verts2 = tp2.vertices
codes2 = tp2.codes

for i in range(len(verts)):
    if codes[i] == 1 or codes[i] == 79:
        robot.MoveJ(transl(verts[i,1], verts[i,0], z_surface - z_safe))
        robot.MoveL(transl(verts[i,1], verts[i,0], z_surface))
    else:
        robot.MoveL(transl(verts[i,1], verts[i,0], z_surface))

for i in range(len(verts1)):
    if codes1[i] == 1 or codes1[i] == 79:
        robot.MoveJ(transl(verts1[i,1], verts1[i,0], z_surface - z_safe))
        robot.MoveL(transl(verts1[i,1], verts1[i,0], z_surface))
    else:
        robot.MoveL(transl(verts1[i,1], verts1[i,0], z_surface))

for i in range(len(verts2)):
    if codes2[i] == 1 or codes2[i] == 79:
        robot.MoveJ(transl(verts2[i,1], verts2[i,0], z_surface - z_safe))
        robot.MoveL(transl(verts2[i,1], verts2[i,0], z_surface))
    else:
        robot.MoveL(transl(verts2[i,1], verts2[i,0], z_surface))

# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(0, 0, z_surface - z_safe))
robot.MoveJ(target)

print(f"¡Figura (rosa polar) completada en el frame '{frame_name}'!")