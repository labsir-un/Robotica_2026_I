from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
import math
from matplotlib.textpath import TextPath
from matplotlib.path import Path

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
# 3) Parámetros de la figura (rosa polar)
#------------------------------------------------
num_points = 720       # Cuántos puntos muestreamos (mayor = más suave)
A = 150               # Amplitud (300 mm = radio máximo)
k = 5                  # Parámetro de la rosa (pétalos). Si es impar, habrá k pétalos; si es par, 2k
z_surface = 0          # Z=0 en el plano del frame
z_safe = -50            # Altura segura para aproximarse y salir

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------
#Movimiento a home
target_name= "Target_HOME" #nombre target en la estación
target= RDK.Item(target_name, ITEM_TYPE_TARGET) #Buscar target
robot.MoveJ(target)


# El centro de la rosa (r=0) corresponde a x=0, y=0

robot.MoveJ(transl(0, 0, z_surface + z_safe))

# Bajamos a la "superficie" (Z=0)


#------------------------------------------------
# 5) Dibujar mariposa
#    r = A * sin(k*theta)
#    x = r*cos(theta), y = r*sin(theta)
#------------------------------------------------
# Recorremos theta de 0 a 2*pi (una vuelta completa)
full_turn = 2*math.pi

for i in range(num_points+1):
    # Fracción entre 0 y 1
    t = i / num_points
    # Ángulo actual
    theta = full_turn * t

    # Calculamos r
    r=A*(math.sin(2*theta)**2) + (math.cos(1*theta)**2) + A*0.5


    # Convertimos a coordenadas Cartesianas X, Y
    x = r * math.cos(theta)
    y = r * math.sin(theta)

    # Movemos linealmente (MoveL) en el plano del Frame
    robot.MoveL(transl(x+200, y, z_surface))## añado el offset en x para que queden mejor centrados los nombres

# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(x+200, y, z_surface+z_safe))
## dibujamos nombres(50 de altura de cada letra)


text = "YESID"
scale = 1.5             # escalado (para probar tamaños)
letter_spacing = 50       # separación entre letras en X (en el frame del objeto es y positivo)
text_offset_x = -150        # donde empieza el texto en X (en el frame del objeto es y positivo)
text_offset_y = -60 # debajo de la rosa en Y (en el frame del objeto es x positivo)

x_cursor = text_offset_x  # cursor que avanza en X por cada letra

for char in text:
    tp = TextPath((0, 0), char, size=50)
    verts = tp.vertices * scale
    codes = tp.codes

    last_x, last_y = None, None

    for (vx, vy), code in zip(verts, codes):
        x_pos = x_cursor + vx
        y_pos = text_offset_y + vy

        if code == Path.MOVETO:
            robot.MoveL(transl(y_pos, x_pos, z_safe))
            robot.MoveL(transl(y_pos, x_pos, z_surface))
        elif code in (Path.LINETO, Path.CURVE3, Path.CURVE4):
            robot.MoveL(transl(y_pos, x_pos, z_surface))

        # Actualiza última posición
        last_x, last_y = x_pos, y_pos

    # Al terminar la letra, solo levanta en el mismo sitio
    if last_x is not None and last_y is not None:
        robot.MoveL(transl(last_y, last_x, z_safe))

    # Avanza cursor para la siguiente letra
    x_cursor += letter_spacing

# segundo nombre
text2 = "VALE"
x_cursor = text_offset_x       # reinicia el cursor horizontal
text_offset_y -= 80  # baja el texto

for char in text2:
    tp = TextPath((0, 0), char, size=50)
    verts = tp.vertices * scale
    codes = tp.codes

    last_x, last_y = None, None

    for (vx, vy), code in zip(verts, codes):
        x_pos = x_cursor + vx
        y_pos = text_offset_y + vy

        if code == Path.MOVETO:
            robot.MoveL(transl(y_pos, x_pos, z_safe))
            robot.MoveL(transl(y_pos, x_pos, z_surface))
        elif code in (Path.LINETO, Path.CURVE3, Path.CURVE4):
            robot.MoveL(transl(y_pos, x_pos, z_surface))

        last_x, last_y = x_pos, y_pos

    # Levantar pluma al terminar la letra
    if last_x is not None and last_y is not None:
        robot.MoveL(transl(last_y, last_x, z_safe))

    # Avanzar cursor para la siguiente letra
    x_cursor += letter_spacing
#------------------------------------------------
# 7) Volver a Home
#------------------------------------------------
robot.MoveJ(target)
print(f"¡Figura (rosa polar) completada en el frame '{frame_name}'!")
