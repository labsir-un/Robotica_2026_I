from robodk.robolink import *
from robodk.robomath import *
import math
from matplotlib.textpath import TextPath

# Inicialización de la API de RoboDK
RDK = Robolink()

# Elegir un robot (si hay varios, aparece un popup)
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")

# Conectar al robot físico
if not robot.Connect():
    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")

# Confirmar conexión
if not robot.ConnectedState():
    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

print("Robot conectado correctamente.")
frame = RDK.Item("Frame_from_Target1", ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception("No se encontró el Frame de referencia.")

robot.setPoseFrame(frame)
robot.setSpeed(300)
robot.setRounding(5)

# Parámetros de la figura (Concoide de Nicomedes)
# r(theta) = A * (2/cos(theta) + 3)  =>  r = 60*sec(theta) + 90  (con A=30)
A = 30
z_surface, z_safe = 0, 50
margen = 0.2
puntos_curva = 360

# Posicionamiento inicial
target_home = RDK.Item("Target_Home", ITEM_TYPE_TARGET)
if target_home.Valid():
    robot.MoveJ(target_home)


def dibujar_rama(theta_i, theta_f):
    r_ini = A * ((2 / math.cos(theta_i)) + 3)
    x_i, y_i = r_ini * math.cos(theta_i), r_ini * math.sin(theta_i)

    robot.MoveJ(transl(x_i, y_i, z_surface - z_safe))
    robot.MoveL(transl(x_i, y_i, z_surface))

    for i in range(puntos_curva + 1):
        theta = theta_i + (i / puntos_curva) * (theta_f - theta_i)
        r = A * ((2 / math.cos(theta)) + 3)
        robot.MoveL(transl(r * math.cos(theta), r * math.sin(theta), z_surface))

    robot.MoveL(transl(r * math.cos(theta), r * math.sin(theta), z_surface - z_safe))


def dibujar_texto_transformado(texto, cx, cy, longitud):
    path = TextPath((0, 0), texto, size=1)
    bbox = path.get_extents()
    tw, th = bbox.x1 - bbox.x0, bbox.y1 - bbox.y0
    escala = longitud / tw

    def transformar(px, py):
        # Centrado local y aplicación de transformaciones (90° + espejos)
        lx, ly = px - (bbox.x0 + tw / 2), py - (bbox.y0 + th / 2)
        rx, ry = ly, lx
        return rx * escala + cx, ry * escala + cy

    for trazo in path.to_polygons():
        x0, y0 = transformar(trazo[0][0], trazo[0][1])
        robot.MoveJ(transl(x0, y0, z_surface - z_safe))
        robot.MoveL(transl(x0, y0, z_surface))

        for pt in trazo[1:]:
            x, y = transformar(pt[0], pt[1])
            robot.MoveL(transl(x, y, z_surface))

        robot.MoveL(transl(x, y, z_surface - z_safe))


# --- Ejecución de la rutina ---

# 1. Dibujar Concoide de Nicomedes (dos ramas)
dibujar_rama(-math.pi / 2 + margen, math.pi / 2 - margen)
dibujar_rama(math.pi / 2 + margen, 3 * math.pi / 2 - margen)

# 2. Dibujar texto con los nombres de los integrantes
dibujar_texto_transformado("Libardo, Andres, Cristian", -120, 0, 650)

# Retorno a Home
if target_home.Valid():
    robot.MoveJ(target_home)

print("Trayectoria completada con texto ampliado.")
