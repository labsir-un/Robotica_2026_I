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

"""# Conectar al robot físico
if not robot.Connect():
    raise Exception("No se pudo conectar al robot. Verifica que esté en modo remoto y que la configuración sea correcta.")

# Confirmar conexión
if not robot.ConnectedState():
    raise Exception("El robot no está conectado correctamente. Revisa la conexión.")

print("Robot conectado correctamente.")"""

frame = RDK.Item("Frame_from_Target1", ITEM_TYPE_FRAME)
if not frame.Valid():
    raise Exception("No se encontró el Frame de referencia.")

robot.setPoseFrame(frame)
# robot.setPoseTool(robot.PoseTool())
robot.setSpeed(300)
robot.setRounding(5)

# Parámetros de la figura
A = 150             # Radio máximo del lóbulo (Ajustado para mantener el tamaño original)
z_surface, z_safe = 0, 50            
puntos_curva = 180  # 180 puntos por lóbulo es suficiente para un trazo suave

# --- Posicionamiento inicial OBLIGATORIO ---
target_home = RDK.Item("Target_Home", ITEM_TYPE_TARGET) 
if not target_home.Valid():
    raise Exception("CRÍTICO: No se encontró 'Target_Home' en la estación. Es obligatorio para iniciar y terminar.")

robot.MoveJ(target_home)

def dibujar_lobulo(angulo_central):
    """
    Dibuja un lóbulo basado en la ecuación polar r = A * cos(2 * theta).
    El lóbulo apuntará en la dirección del 'angulo_central'.
    """
    # Un lóbulo completo se traza en un rango de pi/2 (-pi/4 a pi/4 respecto al centro)
    theta_i = angulo_central - math.pi / 4
    theta_f = angulo_central + math.pi / 4

    # Los lóbulos de esta ecuación siempre nacen en el origen (0,0)
    x_i, y_i = 0, 0
    
    robot.MoveJ(transl(x_i, y_i, z_surface - z_safe))
    robot.MoveL(transl(x_i, y_i, z_surface))
    
    for i in range(puntos_curva + 1):
        theta = theta_i + (i / puntos_curva) * (theta_f - theta_i)
        
        # Ecuación polar para el lóbulo
        r = A * math.cos(2 * (theta - angulo_central))
        
        # Filtro de seguridad: evita r negativo por precisión de decimales en los extremos
        r = max(0, r) 
        
        x = r * math.cos(theta)
        y = r * math.sin(theta)
        robot.MoveL(transl(x, y, z_surface))
        
    # Elevar la herramienta al terminar el lóbulo (de vuelta en el origen)
    robot.MoveL(transl(0, 0, z_surface - z_safe))

def dibujar_texto_transformado(texto, cx, cy, longitud):
    path = TextPath((0, 0), texto, size=1)
    bbox = path.get_extents()
    tw, th = bbox.x1 - bbox.x0, bbox.y1 - bbox.y0
    escala = longitud / tw
    
    def transformar(px, py):
        # Centrado local y aplicación de transformaciones (90° + Espejos)
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

# 1. Dibujar Figura Polar (Dos lóbulos independientes)
dibujar_lobulo(0)            # Dibuja el lóbulo hacia la derecha (0 radianes)
dibujar_lobulo(math.pi / 2)  # Dibuja el lóbulo hacia arriba (pi/2 radianes)

# 2. Dibujar Texto (Letras extra grandes: longitud=400, Ubicado más abajo: CX=-120)
dibujar_texto_transformado("David.P, Daniel, David.C", -120, 0, 650)

# --- Retorno a Home OBLIGATORIO ---
robot.MoveJ(target_home)

print("Trayectoria completada. El robot inició y regresó a Home exitosamente.")
