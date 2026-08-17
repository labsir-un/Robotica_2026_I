from robodk.robolink import * # API para comunicarte con RoboDK
from robodk.robomath import * # Funciones matemáticas
import math

# Importamos librerías necesarias para la generación de texto
from matplotlib.textpath import TextPath
import numpy as np

#------------------------------------------------
# 1) Conexión a RoboDK e inicialización
#------------------------------------------------
RDK = Robolink()

#Elegir un robot (si hay varios, aparece un popup)
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
# 3) Parámetros de la figura (Curva de la Mariposa)
#------------------------------------------------
num_points = 40      # Aumentado: la mariposa da varias vueltas y necesita más recorrido
A = 30                 # Escala: la fórmula original llega hasta ~5.7, 30*5.7 = ~170mm de radio máximo
z_surface = 0          # Z=0 en el plano del frame
z_safe = 50            # Altura segura para aproximarse y salir

#------------------------------------------------
# 4) Movimiento al centro en altura segura
#------------------------------------------------

#4.1) Movimiento a Home

target_name = "TargetHome" #Punto definido en la estacion
targetHome = RDK.Item(target_name, ITEM_TYPE_TARGET)
robot.MoveJ(targetHome)


#4.2) Movimiento al cento de la figura
# El centro (r=0) corresponde a x=0, y=0
robot.MoveJ(transl(0, 0, z_surface - z_safe))

# Bajamos a la "superficie" (Z=0)
robot.MoveL(transl(0, 0, z_surface))

#------------------------------------------------
# 5) Dibujar la curva de la mariposa
#    r = e^cos(theta) - 2*cos(4*theta) + sin^5(theta/12)
#    x = r*cos(theta), y = r*sin(theta)
#------------------------------------------------
# La mariposa necesita de 0 a 12*pi para completar los detalles de las alas
full_turn = 12 * math.pi

for i in range(num_points+1):
    # Fracción entre 0 y 1
    t = i / num_points
    # Ángulo actual
    theta = full_turn * t

    # Calculamos r con la ecuación de la mariposa
    r = A * (math.exp(math.cos(theta)) - 2 * math.cos(4 * theta) + math.pow(math.sin(theta / 12), 5))

    # Convertimos a coordenadas Cartesianas X, Y
    x = r * math.cos(theta)
    y = r * math.sin(theta)

    # Movemos linealmente (MoveL) en el plano del Frame
    robot.MoveL(transl(x, y, z_surface))

# Al terminar la figura, subimos de nuevo para no chocar
robot.MoveL(transl(x, y, z_surface - z_safe))


#------------------------------------------------
# 6) Dibujar los Nombres debajo de la flor (POSICIÓN Y ROTACIÓN CONTROLADA)
#------------------------------------------------
nombres = ["Duvan", "Mora", "Gustavo"]
font_size = 35 
espacio_entre_nombres = 50 

# ========================================================
# --- PANEL DE CONTROL DE ORIENTACIÓN DEL TEXTO ---
# ========================================================
# 1. Posición del bloque de texto:
# Según tu imagen, para que quede "abajo" visualmente, debemos moverlo 
# sobre el eje X positivo (la flecha roja).
x_inicio = A * 5.7 + 60   # Ajuste dinámico de distancia basado en la escala máxima de la mariposa
y_inicio = 0       # Centrado en el eje Y

# 2. Rotación del texto (en grados):
# Como el texto salía vertical, lo giramos 90 grados para que fluya 
# a lo largo del eje Y (flecha verde), que es la horizontal de tu pantalla.
# (Si queda de cabeza, prueba con -90 o 180)
rotacion_grados = 90 
angulo_rad = math.radians(rotacion_grados)

# 3. Corrección de Espejo:
# Mantenemos esto activo porque te funcionó para quitar el efecto espejo.
invertir_y = True 
invertir_x = False
# ========================================================

for indice, nombre in enumerate(nombres):
    # Generamos la trayectoria del texto
    tp = TextPath((0, 0), nombre, size=font_size)
    
    # Extraemos vértices para calcular el ancho y poder centrar cada palabra
    vertices = tp.vertices
    if len(vertices) > 0:
        min_x = np.min(vertices[:, 0])
        max_x = np.max(vertices[:, 0])
        ancho_texto = max_x - min_x
    else:
        ancho_texto = 0

    # Coordenadas locales de la palabra (antes de aplicar la rotación global)
    x_offset_local = -ancho_texto / 2 
    y_offset_local = -(indice * espacio_entre_nombres) # Si se apilan al revés, quita este signo menos (-)

    poligonos = tp.to_polygons()

    for poligono in poligonos:
        if len(poligono) == 0:
            continue
            
        # Función interna para rotar, trasladar y corregir espejos de cada punto
        def transformar_punto(punto_original):
            px_loc = x_offset_local + punto_original[0]
            py_loc = y_offset_local + punto_original[1]
            
            # 1. Corrección de espejos
            if invertir_x: px_loc = -px_loc
            if invertir_y: py_loc = -py_loc
            
            # 2. Rotación 2D y Traslación final al Frame Global
            x_glob = x_inicio + (px_loc * math.cos(angulo_rad) - py_loc * math.sin(angulo_rad))
            y_glob = y_inicio + (px_loc * math.sin(angulo_rad) + py_loc * math.cos(angulo_rad))
            return x_glob, y_glob

        # --- DIBUJO DE LA LETRA ---
        # 1. Moverse al inicio de la letra (CON LA MANO ALZADA)
        x_ini, y_ini = transformar_punto(poligono[0])
        robot.MoveL(transl(x_ini, y_ini, z_surface - z_safe))
        
        # 2. Bajar la herramienta a la superficie
        robot.MoveL(transl(x_ini, y_ini, z_surface))
        
        # 3. Trazar el resto de los puntos de la letra
        for punto in poligono[1:]:
            x_p, y_p = transformar_punto(punto)
            robot.MoveL(transl(x_p, y_p, z_surface))
            
        # 4. ALZAR LA MANO al terminar el trazo
        x_fin, y_fin = transformar_punto(poligono[-1])
        robot.MoveL(transl(x_fin, y_fin, z_surface - z_safe))

#------------------------------------------------
# 7) Retorno final a Home
#------------------------------------------------
robot.MoveJ(targetHome)
print(f"¡Figura y nombres completados en el frame '{frame_name}'!")

