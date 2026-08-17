```python
from robodk.robolink import *    # API para comunicarte con RoboDK
from robodk.robomath import *    # Funciones matemáticas
from matplotlib.textpath import TextPath 
from matplotlib.font_manager import FontProperties
from matplotlib.path import Path
import math

#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

# Elegir un robot (si hay varios, aparece un popup)
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
#if not robot.Valid():
#    raise Exception("No se ha seleccionado un robot válido.")

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
robot.setRounding(5)  # blending (radio de curvatura)

#------------------------------------------------
# 3) Parámetros de la figura (rosa polar)
#------------------------------------------------
num_points = 30       # Cuántos puntos muestreamos (mayor = más suave)
A = 95             # Amplitud (300 mm = radio máximo)
k = 5                  # Parámetro de la rosa (pétalos). Si es impar, habrá k pétalos; si es par, 2k
z_surface = 0          # Z=0 en el plano del frame
z_safe = 50            # Altura segura para aproximarse y salir

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------
#4.1 Primero debe ir a home
target_name = "Target_home" #Defino target home en la estación
target = RDK.Item(target_name, ITEM_TYPE_TARGET) #Buscando Target de la estación
robot.MoveJ(target)

#4.2 El centro de la rosa (r=0) corresponde a x=0, y=0
robot.MoveJ(transl(0, 0, z_surface - z_safe))

# Bajamos a la "superficie" (Z=0)
robot.MoveL(transl(0, 0, z_surface))

#------------------------------------------------
# 5) Dibujar el trébol de 4 hojas
# Recorremos theta de 0 a 2*pi (una vuelta completa)
full_turn = 2*math.pi

for i in range(num_points+1):
    # Fracción entre 0 y 1
    t = i / num_points
    # Ángulo actual
    theta = full_turn * t

    # Calculamos r
    r = A * (1 + abs(math.cos(2*theta+math.pi/2)))

    # Convertimos a coordenadas Cartesianas X, Y
    x = r * math.cos(theta)
    y = r * math.sin(theta)

    # Movemos linealmente (MoveL) en el plano del Frame
    robot.MoveL(transl(x, y, z_surface))

#Ahora escribo los nombres
z_surface = 0     # altura dibujando
z_safe = 50       # altura segura

scale = 100     # escala del texto
offset_x = 200    # posición en X
offset_y = 100    # posición en Y

# =========================
# 4. Fuente y textos
# =========================
fp = FontProperties(family="DejaVu Sans", size=1)

text1 = TextPath((-2, 3), "ALEJANDRA", prop=fp)
text2 = TextPath((-1, 1), "JUANITO", prop=fp)  # debajo


# =========================
# 5. Función para dibujar texto
# =========================
def draw_text(textpath):

    vertices = textpath.vertices
    codes = textpath.codes

    # Escalar y trasladar
    vertices_scaled = []
    for x, y in vertices:
        x_new = -(scale * y  + offset_x)
        y_new = (-scale * x + offset_y)
        vertices_scaled.append((x_new, y_new))
        

        

    # Recorrer puntos
    for i in range(len(vertices_scaled)):

        x, y = vertices_scaled[i]
        code = codes[i]
        x=-x
        y=-y

        if code == Path.MOVETO:
            # Ir sin dibujar
            robot.MoveJ(transl(x, y, -z_safe))
            robot.MoveJ(transl(x, y, -z_surface))

        elif code == Path.LINETO:
            # Dibujar
            robot.MoveJ(transl(x, y, -z_surface))

        elif code == Path.CLOSEPOLY:
            # Cerrar contorno
            robot.MoveJ(transl(x, y, -z_surface))

        elif code == Path.CURVE3:
            #curvitas
            robot.MoveJ(transl(x, y, -z_surface))

    # Al final subir
    robot.MoveL(transl(x, y, z_safe))
draw_text(text1)
draw_text(text2)

# Al terminar, subimos de nuevo para no chocar
robot.MoveL(transl(x, y, z_surface - z_safe))

robot.MoveJ(target)
```
