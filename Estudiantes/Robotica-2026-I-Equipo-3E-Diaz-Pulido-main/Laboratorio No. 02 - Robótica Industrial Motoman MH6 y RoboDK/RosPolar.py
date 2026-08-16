from robodk.robolink import * # API para comunicarte con RoboDK
from robodk.robomath import * # Funciones matemáticas
import math
import time


time.sleep(2)  # espera 2 segundos

def obtener_trazos_letra(letra):
    l = letra.upper()
    if l == 'J': return [[(30, 50), (30, 10), (15, 0), (0, 10), (0, 20)]]
    elif l == 'O': return [[(0, 0), (0, 50), (30, 50), (30, 0), (0, 0)]]
    elif l == 'S': return [[(30, 50), (0, 50), (0, 25), (30, 25), (30, 0), (0, 0)]]
    elif l == 'E': return [[(30, 50), (0, 50), (0, 0), (30, 0)], [(0, 25), (20, 25)]]
    elif l == 'L': return [[(0, 50), (0, 0), (30, 0)]]
    elif l == 'U': return [[(0, 50), (0, 0), (30, 0), (30, 50)]]
    elif l == 'I': return [[(15, 0), (15, 50)]]
    elif l == 'A': return [[(0, 0), (15, 50), (30, 0)], [(5, 20), (25, 20)]]
    elif l == 'R': return [[(0, 0), (0, 50), (30, 50), (30, 25), (0, 25)], [(15, 25), (30, 0)]]
    elif l == 'D': return [[(0, 0), (0, 50), (20, 50), (30, 35), (30, 15), (20, 0), (0, 0)]]
    elif l == 'V': return [[(0, 50), (15, 0), (30, 50)]]
    else: return []

def generar_posiciones_texto(texto, x_start, y_start, escala=1.2):
    puntos = []
    w_letra = 30 * escala
    espacio = 15 * escala
    x_act = x_start
    
    for letra in texto:
        if letra == ' ':
            x_act += w_letra
            continue
        trazos = obtener_trazos_letra(letra)
        for trazo in trazos:
            x0, y0 = trazo[0]
            puntos.append([x_act + x0, y_start + y0, 5.000])
            puntos.append([x_act + x0, y_start + y0, 0.000])
            for pt in trazo[1:]:
                xi, yi = pt
                puntos.append([x_act + xi, y_start + yi, 0.000])
            puntos.append([x_act + xi, y_start + yi, 5.000])
        x_act += w_letra + espacio
    return puntos

posiciones = []
posiciones += generar_posiciones_texto("JOSE LUIS", x_start=60, y_start=-260, escala=1.4)
posiciones += generar_posiciones_texto("JAIRO DAVID", x_start=40, y_start=-100, escala=1.4)

#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")

# Conectar al robot físico
#if not robot.Connect():
#    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")

# Confirmar conexión
#if not robot.ConnectedState():
#    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

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
#robot.setPoseTool(robot.PoseTool())

# Ajustes de velocidad y blending
robot.setSpeed(300)   # mm/s - Ajusta según necesites
robot.setRounding(1)  # blending (radio de curvatura)

#------------------------------------------------
# 3) Parámetros de la figura figura polar
#------------------------------------------------
ver = False #True # ver las lineas (truco solo para el programa, dejar en true)

z_surface = 0          # Z=0 en el plano del frame
z_safe = -50            # Altura segura para aproximarse y salir

x_dibujo = 150
y_dibujo = 0

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------

# Ir a posición home
robot.MoveJ([0, 0, 0, 0, 0, 0])

# Luego moverte en cartesiano para dibujar
robot.MoveL(transl(x_dibujo, y_dibujo, z_surface + z_safe))

# El centro de la figura polar (r=0) corresponds a x=0, y=0
robot.MoveJ(transl(x_dibujo, y_dibujo, z_surface + z_safe))

# Bajamos a la "superficie" (Z=0)
robot.MoveL(transl(x_dibujo, y_dibujo, z_surface + z_safe))

b = 50
a = 100
num_points = 360

for i in range(num_points+1):

    t = (i / num_points) * 2 * math.pi

    r = b + a * math.cos(t)
    x = r * math.cos(t)
    y = r * math.sin(t)

    x_rot = -y + x_dibujo
    y_rot = x + y_dibujo

    if i == 0:
        robot.MoveL(transl(x_rot, y_rot, z_surface + z_safe))
    robot.MoveL(transl(x_rot, y_rot, z_surface))

# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(x_rot, y_rot, z_surface + z_safe))

z_surface = 0
z_safe_ficticio = 5

if ver:
    z_safe = -50
else:
    z_safe = 50
# Punto inicial
#x0, y0, z0 = posiciones[0]

# Ir al inicio en altura segura
#robot.MoveJ(transl(x0, y0, z_safe))

# Estado anterior
pen_down = False

x_letras = 600 - 20
y_letras = -800/2  - 20

x, y, z = posiciones[1]
x_rot = y + x_letras
y_rot = x + y_letras
robot.MoveL(transl(x_rot, y_rot, -50))

for x, y, z in posiciones:

    # ROTACIÓN + OFFSET
    x_rot = y + x_letras
    y_rot = x + y_letras

    if z == z_safe_ficticio:
        robot.MoveL(transl(x_rot, y_rot, z_safe))
        pen_down = False

    else:
        if not pen_down:
            robot.MoveL(transl(x_rot, y_rot, z_surface))
            pen_down = True

        robot.MoveL(transl(x_rot, y_rot, z_surface))

x, y, z = posiciones[-1]
x_rot = y + x_letras 
y_rot = x + y_letras
robot.MoveL(transl(x_rot, y_rot, -50))

# Al terminar, subir
robot.MoveL(transl(x_dibujo, y_dibujo, -50))

robot.MoveJ([0, 0, 0, 0, 0, 0])

print("¡Texto dibujado correctamente!")

print(f"¡Figura completada en el frame '{frame_name}'!")