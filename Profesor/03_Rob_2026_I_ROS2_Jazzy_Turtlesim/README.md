<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>Introducción a Turtlesim</h1>

<h2>Uso de Turtlesim en ROS 2 Jazzy (Ubuntu 24.04)</h2>

<h4>Pedro Fabián Cárdenas Herrera<br>
    Manuel Felipe Carranza Montenegro</h4>

<p>
  <img alt="Ubuntu 24.04 LTS" src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420?logo=ubuntu&logoColor=white">
  <img alt="ROS 2 Jazzy" src="https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros&logoColor=white">
  <img alt="Package" src="https://img.shields.io/badge/Package-turtlesim-2ea44f">
</p>

</div>

<div align="justify"> 

## Tabla de contenidos
- [Introducción](#introducción)
- [Objetivos](#objetivos)
- [Prerrequisitos](#prerrequisitos)
- [1. Instalar turtlesim](#1-instalar-turtlesim)
- [2. Iniciar turtlesim](#2-iniciar-turtlesim)
- [3. Controlar la tortuga (teleop)](#3-controlar-la-tortuga-teleop)
- [4. Explorar nodos, tópicos, servicios y acciones](#4-explorar-nodos-tópicos-servicios-y-acciones)
- [5. Instalar y usar rqt](#5-instalar-y-usar-rqt)
- [6. Servicios clave en turtlesim](#6-servicios-clave-en-turtlesim)
- [7. Controlar múltiples tortugas (remapeo)](#7-controlar-múltiples-tortugas-remapeo)
- [8. Workspace + VS Code (mínimo recomendado)](#8-workspace--vs-code-mínimo-recomendado)
- [9. Crear un nodo en Python para controlar la tortuga](#9-crear-un-nodo-en-python-para-controlar-la-tortuga)
- [Checklist de verificación](#checklist-de-verificación)
- [Errores comunes y solución rápida](#errores-comunes-y-solución-rápida)
- [Recursos útiles](#recursos-útiles)
- [Bibliografía](#bibliografía)

---

## Introducción

El paquete `turtlesim` es un simulador ligero incluido en ROS 2 que permite comprender de forma **visual y práctica** conceptos fundamentales como **nodos**, **tópicos**, **servicios**, **parámetros** y **remapeo**. A través de una tortuga animada, es posible interactuar con estos elementos usando comandos de terminal o interfaces gráficas como `rqt`.

Este entorno es ideal para comenzar en ROS 2 porque ofrece un “laboratorio” rápido: todo ocurre en tu computador, sin hardware físico, y con retroalimentación inmediata.

> Nota del curso: esta guía asume **Ubuntu 24.04 LTS** y **ROS 2 Jazzy** (la combinación recomendada en el curso).  
> Si estás en Ubuntu 22.04, normalmente se usa **ROS 2 Humble**.

---

## Objetivos

- Instalar y ejecutar el simulador `turtlesim`.
- Controlar una tortuga mediante el teclado usando ROS 2.
- Visualizar y manipular nodos, tópicos y servicios mediante comandos y la herramienta gráfica `rqt`.
- Utilizar servicios para crear nuevas tortugas y cambiar propiedades como el color del trazo.
- Aplicar remapeo de tópicos para controlar múltiples tortugas simultáneamente.
- Crear un primer nodo en Python que publique comandos de velocidad (`Twist`) para controlar a la tortuga.

---

## Prerrequisitos

- Tener ROS 2 correctamente instalado y configurado (en el curso: **ROS 2 Jazzy**).
- Haber ejecutado `source /opt/ros/jazzy/setup.bash` (o tenerlo en `~/.bashrc`).
- Conocer comandos básicos de terminal.

Verifica rápidamente tu distro activa:

```bash
printenv | grep ROS_DISTRO
# Debe mostrar: ROS_DISTRO=jazzy
```

---

## 1. Instalar turtlesim

```bash
sudo apt update
sudo apt install -y ros-jazzy-turtlesim
```

Verifica que existan ejecutables:

```bash
ros2 pkg executables turtlesim
```

---

## 2. Iniciar turtlesim

Abre una terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtlesim_node
```

Deberías ver una ventana con la tortuga y un fondo azul.

> Si estás en WSL2 o en una VM sin GUI, la ventana puede no abrir. En ese caso, usa instalación nativa/dual boot o configura GUI (WSLg/X11).

---

## 3. Controlar la tortuga (teleop)

En otra terminal:

```bash
source /opt/ros/jazzy/setup.bash
ros2 run turtlesim turtle_teleop_key
```

> Usa las flechas del teclado para mover la tortuga y dibujar.

---

## 4. Explorar nodos, tópicos, servicios y acciones

Con `turtlesim_node` y `turtle_teleop_key` corriendo, ejecuta:

```bash
ros2 node list
ros2 topic list
ros2 service list
ros2 action list
```

### Inspección rápida (muy útil para depurar)

```bash
ros2 topic info /turtle1/cmd_vel
ros2 topic echo /turtle1/pose
ros2 interface show geometry_msgs/msg/Twist
ros2 interface show turtlesim/msg/Pose
```

---

## 5. Instalar y usar rqt

`rqt` agrupa herramientas gráficas útiles (por ejemplo: visualización de tópicos, llamadas a servicios, etc.).

### Instalar rqt
```bash
sudo apt update
sudo apt install -y '~nros-jazzy-rqt*'
```

### Ejecutar rqt
```bash
rqt
```

Si no aparecen plugins:

```bash
rqt --force-discover
```

---

## 6. Servicios clave en turtlesim

En `rqt`: **Plugins > Services > Service Caller**

### 6.1 Usar el servicio `/spawn` (crear otra tortuga)

- Selecciona `/spawn`
- Ingresa:
  - `x=1.0`, `y=1.0`, `theta=0.0`
  - `name=turtle2`
- Click en **Call**  
✅ Aparecerá una nueva tortuga.

### 6.2 Usar el servicio `/turtle1/set_pen` (cambiar color y grosor)

- Selecciona `/turtle1/set_pen`
- Ejemplo:
  - `r=255`, `g=0`, `b=0`, `width=5`, `off=0`
- Click en **Call**  
✅ La tortuga dibuja con línea roja y gruesa.

### 6.3 Otros servicios útiles (por terminal)

Listar servicios y tipos:

```bash
ros2 service list
ros2 service type /spawn
ros2 interface show $(ros2 service type /spawn)
```

Llamar `/clear` (borra el dibujo):

```bash
ros2 service call /clear std_srvs/srv/Empty {}
```

Cambiar fondo (parámetros del nodo):

```bash
ros2 param list /turtlesim
ros2 param set /turtlesim background_r 200
ros2 param set /turtlesim background_g 200
ros2 param set /turtlesim background_b 255
```

> Nota: en turtlesim, los cambios de parámetros pueden requerir refresco. Si no ves el cambio, reinicia `turtlesim_node`.

---

## 7. Controlar múltiples tortugas (remapeo)

La teleoperación por defecto publica en:

- `/turtle1/cmd_vel`

Para controlar `turtle2`, remapea el tópico de salida de la teleop:

```bash
ros2 run turtlesim turtle_teleop_key --ros-args --remap /turtle1/cmd_vel:=/turtle2/cmd_vel
```

✅ Ahora esa terminal controla `turtle2`, mientras otra puede seguir controlando `turtle1`.

> Consejo: usa **nombres absolutos** (con `/`) al remapear para evitar confusiones de namespaces.

---

## 8. Workspace + VS Code (mínimo recomendado)

### 8.1 Instalar herramientas de build (colcon)

```bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions
```

### 8.2 Crear workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws
colcon build
```

Cargar ROS + workspace:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
```

(Opcional) Automático en cada terminal:

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
echo "source ~/ros2_ws/install/setup.bash" >> ~/.bashrc
source ~/.bashrc
```

---

## 9. Crear un nodo en Python para controlar la tortuga

### 9.1 Crear un paquete

```bash
cd ~/ros2_ws/src
ros2 pkg create --build-type ament_python my_turtle_controller
```

### 9.2 Configurar `setup.py`

Edita `my_turtle_controller/setup.py` y asegúrate de incluir:

```python
entry_points={
    'console_scripts': [
        'move_turtle = my_turtle_controller.move_turtle:main',
    ],
},
```

### 9.3 Crear el nodo `move_turtle.py`

Crea `my_turtle_controller/my_turtle_controller/move_turtle.py`:

```python
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleController(Node):
    def __init__(self):
        super().__init__('turtle_controller')
        self.publisher_ = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.timer = self.create_timer(0.5, self.move_turtle)

    def move_turtle(self):
        msg = Twist()
        msg.linear.x = 2.0   # Velocidad hacia adelante
        msg.angular.z = 1.0  # Rotación
        self.publisher_.publish(msg)
        self.get_logger().info('Moviendo la tortuga')

def main(args=None):
    rclpy.init(args=args)
    node = TurtleController()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()
```

> Tip: si quieres controlar `turtle2`, cambia el tópico a `/turtle2/cmd_vel` o usa remapeo al ejecutar.

---

## Compilar y ejecutar el nodo

1) Asegúrate de que `turtlesim_node` esté corriendo.  
2) Compila y ejecuta:

```bash
cd ~/ros2_ws
colcon build
source /opt/ros/jazzy/setup.bash
source install/setup.bash
ros2 run my_turtle_controller move_turtle
```

✅ La tortuga debería moverse automáticamente.

---

## Checklist de verificación

```bash
# 1) ¿Estoy en la distro correcta?
printenv | grep ROS_DISTRO

# 2) ¿turtlesim está instalado?
ros2 pkg list | grep turtlesim

# 3) ¿Se ven los ejecutables?
ros2 pkg executables turtlesim

# 4) ¿Se ven tópicos y nodos con turtlesim corriendo?
ros2 node list
ros2 topic list
```

---

## Errores comunes y solución rápida

### 1) `ros2: command not found`
No está instalado ROS 2 o no está en el PATH. Revisa la instalación de la guía anterior y/o ejecuta:
```bash
source /opt/ros/jazzy/setup.bash
```

### 2) `Package 'turtlesim' not found`
Falta instalar o no estás en la distro correcta:
```bash
sudo apt install -y ros-jazzy-turtlesim
printenv | grep ROS_DISTRO
```

### 3) `rqt` abre pero no tiene plugins
Forzar descubrimiento:
```bash
rqt --force-discover
```
o reinstalar:
```bash
sudo apt install -y '~nros-jazzy-rqt*'
```

### 4) La ventana de turtlesim no aparece
- Estás en WSL2/VM sin GUI configurada.
- Solución: usa instalación nativa/dual boot o configura GUI (WSLg/X11).

---

## Recursos útiles

- Documentación oficial (Jazzy) — “Using turtlesim, ros2, and rqt”:  
  https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html

- RQt (concepto y uso):  
  https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-RQt.html

- ROS Index — paquete `turtlesim`:  
  https://index.ros.org/p/turtlesim/

- Extensión ROS para Visual Studio Code:  
  https://marketplace.visualstudio.com/items?itemName=ms-iot.vscode-ros

- Código fuente (tutorials):  
  https://github.com/ros/ros_tutorials

### Videos recomendados (opcionales)
- Búsqueda: “ROS2 Jazzy turtlesim rqt”  
  https://www.youtube.com/results?search_query=ros2+jazzy+turtlesim+rqt
- Búsqueda: “ROS2 turtlesim topics services”  
  https://www.youtube.com/results?search_query=ros2+turtlesim+topics+services

---

## Bibliografía

[1] Open Robotics, “Using turtlesim, ros2, and rqt (Jazzy),” ROS 2 Documentation, 2024–2026. Disponible: https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Introducing-Turtlesim/Introducing-Turtlesim.html

[2] Open Robotics, “Overview and usage of RQt (Jazzy),” ROS 2 Documentation, 2024–2026. Disponible: https://docs.ros.org/en/jazzy/Concepts/Intermediate/About-RQt.html

[3] Open Robotics, “Ubuntu (deb packages) — Jazzy,” ROS 2 Documentation, 2024–2026. Disponible: https://docs.ros.org/en/jazzy/Installation/Ubuntu-Install-Debs.html

[4] Open Robotics, “turtlesim — ROS Index,” 2024–2026. Disponible: https://index.ros.org/p/turtlesim/

[5] Microsoft, “ROS Extension for Visual Studio Code,” Visual Studio Marketplace, 2024–2026. Disponible: https://marketplace.visualstudio.com/items?itemName=ms-iot.vscode-ros

</div>
