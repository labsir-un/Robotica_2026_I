# Actividad 4: Interfaz de Control Cinético (GUI)

En esta actividad se implementa una interfaz gráfica mediante `tkinter` destinada al control manual y simultáneo de las articulaciones del manipulador Phantom X.

## 🛠️ Requisitos
* Se requiere disponer de Python 3 y la librería `tkinter` (usualmente incluida por defecto en la mayoría de las distribuciones de Linux).
* El entorno de simulación principal de ROS 2 (o el controlador del hardware físico) debe encontrarse en ejecución de manera previa.

## ▶️ Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz gráfica
python3 mis_actividades/actividad4.py
```

## 🧠 Principio de Funcionamiento
El script `joint_selector.py` opera como nodo backend, estableciendo una suscripción al tópico `/joint_states` y publicando trayectorias hacia los controladores del brazo (`/joint_trajectory_controller/...`) y de la pinza (`/gripper_trajectory_controller/...`). Por su parte, la interfaz gráfica desarrollada en `actividad4.py` establece comunicación con dicho nodo para la transmisión de los comandos de posición generados a través de los controles deslizantes (sliders).
