from robodk.robolink import *
from robodk.robomath import *
import math

# ------------------------------------------------
# 1) Conexión e inicialización
# ------------------------------------------------
RDK = Robolink()
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)

if not robot.Valid():
    raise Exception("No se ha seleccionado un robot válido.")
if not robot.Connect():
    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")
if not robot.ConnectedState():
    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

# -----------------------------------------------
# Frame
# -----------------------------------------------
frame_name = "Frame_from_Target1"
frame = RDK.Item(frame_name, ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception(f'No se encontró el Frame "{frame_name}"')

robot.setPoseFrame(frame)
robot.setSpeed(300)
robot.setRounding(10)

# ------------------------------------------------
# 2) Parámetros de la Rosa Polar
# ------------------------------------------------
# Ecuación: r = A * theta * sin(10 * theta)
num_points = 30
A = 30
z_surface = 0
z_safe = -50

# ------------------------------------------------
# 3) Movimiento a Home y Rosa Polar
# ------------------------------------------------
target = RDK.Item("Target home", ITEM_TYPE_TARGET)
robot.MoveJ(target)
robot.MoveJ(transl(0, 0, z_surface + z_safe))
robot.MoveL(transl(0, 0, z_surface))

full_turn = 2 * math.pi
for i in range(num_points + 1):
    theta = full_turn * (i / num_points)
    r = A * theta * math.sin(10 * theta)
    # Convertimos a cartesianas: x = r*cos(theta), y = r*sin(theta)
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    robot.MoveL(transl(x, y, z_surface))

robot.MoveL(transl(0, 0, z_surface + z_safe))

# ------------------------------------------------
# 4) Funciones de dibujo en MODO ESPEJO
# ------------------------------------------------
# Para el espejo, multiplicamos el desplazamiento en X por -1

def dibujar_linea_espejo(inicio_x, inicio_y, fin_x, fin_y, z_height):
    robot.MoveJ(transl(inicio_x, inicio_y, z_height + z_safe))
    robot.MoveL(transl(inicio_x, inicio_y, z_height))
    robot.MoveL(transl(fin_x, fin_y, z_height))
    robot.MoveL(transl(fin_x, fin_y, z_height + z_safe))

def letra_L_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy + t, cx + t, cy - t, z)
    dibujar_linea_espejo(cx + t, cy - t, cx - t, cy - t, z)

def letra_U_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy + t, cx + t, cy - t, z)
    dibujar_linea_espejo(cx + t, cy - t, cx - t, cy - t, z)
    dibujar_linea_espejo(cx - t, cy - t, cx - t, cy + t, z)

def letra_I_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx, cy + t, cx, cy - t, z)
    dibujar_linea_espejo(cx - t*0.4, cy + t, cx + t*0.4, cy + t, z)
    dibujar_linea_espejo(cx - t*0.4, cy - t, cx + t*0.4, cy - t, z)

def letra_S_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx - t, cy + t, cx + t, cy + t, z)
    dibujar_linea_espejo(cx + t, cy + t, cx + t, cy, z)
    dibujar_linea_espejo(cx + t, cy, cx - t, cy, z)
    dibujar_linea_espejo(cx - t, cy, cx - t, cy - t, z)
    dibujar_linea_espejo(cx - t, cy - t, cx + t, cy - t, z)

def letra_D_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy + t, cx + t, cy - t, z)
    dibujar_linea_espejo(cx + t, cy + t, cx - t, cy, z)
    dibujar_linea_espejo(cx - t, cy, cx + t, cy - t, z)

def letra_V_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy + t, cx, cy - t, z)
    dibujar_linea_espejo(cx, cy - t, cx - t, cy + t, z)

def letra_A_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy - t, cx, cy + t, z)
    dibujar_linea_espejo(cx, cy + t, cx - t, cy - t, z)
    dibujar_linea_espejo(cx + t*0.5, cy, cx - t*0.5, cy, z)

def letra_N_esp(cx, cy, z, t):
    dibujar_linea_espejo(cx + t, cy - t, cx + t, cy + t, z)
    dibujar_linea_espejo(cx + t, cy + t, cx - t, cy - t, z)
    dibujar_linea_espejo(cx - t, cy - t, cx - t, cy + t, z)

# ------------------------------------------------
# 5) Ejecución del nombre ESPEJADO
# ------------------------------------------------
y_pos = -180
t_letra = 12
esp = 35

print("Dibujando nombres en modo espejo...")

# LUIS en espejo
letra_L_esp(100,          y_pos, z_surface, t_letra)
letra_U_esp(100 - esp,    y_pos, z_surface, t_letra)
letra_I_esp(100 - esp*2,  y_pos, z_surface, t_letra)
letra_S_esp(100 - esp*3,  y_pos, z_surface, t_letra)

# DUVAN en espejo
letra_D_esp(-50,          y_pos, z_surface, t_letra)
letra_U_esp(-50 - esp,    y_pos, z_surface, t_letra)
letra_V_esp(-50 - esp*2,  y_pos, z_surface, t_letra)
letra_A_esp(-50 - esp*3,  y_pos, z_surface, t_letra)
letra_N_esp(-50 - esp*4,  y_pos, z_surface, t_letra)

robot.MoveJ(target)
print("¡Escritura en modo espejo finalizada!")
