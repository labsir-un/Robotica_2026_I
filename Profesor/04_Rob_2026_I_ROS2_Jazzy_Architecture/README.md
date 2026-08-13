<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>Arquitectura y Funcionamiento de ROS 2 Graph</h1>

<h2>Guía 04 - Arquitectura y Funcionamiento de ROS 2 Graph (ROS 2 Jazzy)</h2>

<h4>Pedro Fabián Cárdenas Herrera<br>
    Manuel Felipe Carranza Montenegro</h4>

<p>
  <img alt="Ubuntu 24.04 LTS" src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420?logo=ubuntu&logoColor=white">
  <img alt="ROS 2 Jazzy" src="https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros&logoColor=white">
  <img alt="Nivel" src="https://img.shields.io/badge/Nivel-Introductorio-2ea44f">
</p>

</div>

<div align="justify"> 

## Tabla de contenidos
- [1. ¿Qué es la ROS 2 Graph?](#1-qué-es-la-ros-2-graph)
- [2. Nodos en ROS 2](#2-nodos-en-ros-2)
- [3. Tópicos en ROS 2](#3-tópicos-en-ros-2)
- [4. Servicios en ROS 2](#4-servicios-en-ros-2)
- [5. Parámetros en ROS 2](#5-parámetros-en-ros-2)
- [6. Acciones en ROS 2](#6-acciones-en-ros-2)
- [7. Diferencias (tabla resumen)](#7-diferencias-tabla-resumen)
- [8. Pruebas de funcionamiento (ROS 2 Jazzy)](#8-pruebas-de-funcionamiento-ros-2-jazzy)
  - [8.1 Preparación (workspace + paquetes)](#81-preparación-workspace--paquetes)
  - [8.2 Interfaces (srv/action)](#82-interfaces-srvaction)
  - [8.3 Tópico: Publisher + Subscriber (Python)](#83-tópico-publisher--subscriber-python)
  - [8.4 Servicio: Server + Client (Python)](#84-servicio-server--client-python)
  - [8.5 Acción: Action Server + Action Client (Python)](#85-acción-action-server--action-client-python)
  - [8.6 Parámetros: set/get desde CLI y desde código](#86-parámetros-setget-desde-cli-y-desde-código)
  - [8.7 Cómo probar todo (comandos)](#87-cómo-probar-todo-comandos)
- [9. Herramientas para “ver” la Graph (CLI + GUI)](#9-herramientas-para-ver-la-graph-cli--gui)
- [10. Bibliografía](#10-bibliografía)

---

## 1. ¿Qué es la ROS 2 Graph?

La **ROS 2 Graph** es una representación abstracta de cómo los elementos dentro de un sistema ROS 2 se conectan entre sí. Es una red dinámica de **nodos**, **tópicos**, **servicios**, **parámetros** y **acciones** que interactúan para procesar y compartir datos en tiempo real.

Si la visualizáramos, veríamos nodos conectados por tópicos, servicios y acciones, mostrando el flujo de información del sistema.

---

## 2. Nodos en ROS 2

Un **nodo** es la unidad básica de ejecución. Cada nodo cumple una tarea específica (leer un sensor, controlar un motor, calcular navegación) y se comunica con otros nodos.

> Importante: en ROS 2, un ejecutable puede contener **uno o varios nodos** (composición), pero en el curso normalmente empezaremos con **1 nodo por script** para claridad.

<div align="center">
  <img src="https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZ2p1N3lrMmJieW5hMXdtMTEwcXBmbTZuajZqYTlmdDJ6dWZ4MGQ0eCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/qquDouwBrGsBnWaAmY/giphy.gif" alt="Nodos ROS 2">
</div>

---

## 3. Tópicos en ROS 2

Los **tópicos** son canales de comunicación basados en **publish/subscribe**. Un nodo publica mensajes y otros se suscriben.

- Ideal para flujos continuos: sensores, odometría, estado, etc.
- No hay “respuesta”; es streaming.

<div align="center">
  <img src="https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExd3F3dGUwMnJlbjZqd3ZhdTJidW9sNWs1NW9uZjI4ZzAzeTI4cmxvMiZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/p42BrUzXTiFzu26CSz/giphy.gif" alt="Topics ROS 2">
</div>

---

## 4. Servicios en ROS 2

Los **servicios** siguen un modelo **request/response**:

- Un nodo cliente hace una solicitud.
- Un nodo servidor responde una vez.

Útil para consultas puntuales: “dame el estado”, “resetea”, “cambia modo”, etc.

<div align="center">
  <img src="https://media0.giphy.com/media/v1.Y2lkPTc5MGI3NjExYWVmeTRvMmltOWlsdTFxOXc1YjNvNWk1em16dnlobW80OHUyYW0zNSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/ZwtP7OMlnkGiovXZMP/giphy.gif" alt="Services ROS 2">
</div>

---

## 5. Parámetros en ROS 2

Un **parámetro** es una configuración que vive en un nodo y modifica su comportamiento (velocidad, umbral, nombre, etc.). Se puede leer y cambiar en tiempo de ejecución.

> Nota (avanzado): por defecto, ROS 2 es estricto con el tipo. Se puede permitir tipado dinámico con `ParameterDescriptor(dynamic_typing=True)` cuando sea necesario.

---

## 6. Acciones en ROS 2

Las **acciones** sirven para tareas de duración “larga” con:

- **Goal** (objetivo)
- **Feedback** (progreso)
- **Result** (resultado final)
- posibilidad de **cancelación**

Son similares a servicios, pero con feedback continuo y cancelación.

<div align="center">
  <img src="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExenp4Nm9vYnRneXowZm95cTJ4eDY3dGl0cmRobjlpaW56aDFwdjQ2ayZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/pvXuyzRoWrUwDlaQUw/giphy.gif" alt="Actions ROS 2">
</div>

---

## 7. Diferencias (tabla resumen)

| Elemento | Descripción | Modelo | Propósito | Ejemplo |
|---|---|---|---|---|
| **Nodos** | Ejecutables que hacen tareas | Autónomo | Ejecutan funciones y se comunican | Nodo de sensor, nodo de motor |
| **Tópicos** | Canal de mensajes | Pub/Sub | Flujo continuo de datos | `/scan`, `/odom`, `/cmd_vel` |
| **Servicios** | Solicitud/respuesta | Cliente/Servidor | Respuesta puntual | `/reset`, `/get_state` |
| **Parámetros** | Configuración del nodo | — | Ajustar comportamiento | `speed_limit`, `rate_hz` |
| **Acciones** | Tarea larga con feedback | Cliente/Servidor + feedback | Planificación/ejecución prolongada | Navegar a un punto, countdown |

---

## 8. Pruebas de funcionamiento (ROS 2 Jazzy)

En esta sección crearás **tres mini-proyectos** separados dentro de una carpeta común llamada `tests_ws`, para probar por separado:

✅ Tópico (publisher/subscriber)  
✅ Servicio (server/client)  
✅ Acción (action server/client con feedback)  
✅ Parámetros (en el caso del tópico)

> En ROS 2 **no existe `roscore`**. Solo necesitas `source` y ejecutar nodos.

---

### Estructura que vamos a crear

Dentro de tu HOME (`~`) quedará así:

```
~/tests_ws/
  topic_ws/
    src/
      demo_topic/
  services_ws/
    src/
      demo_services_interfaces/
      demo_services_py/
  actions_ws/
    src/
      demo_actions_interfaces/
      demo_actions_py/
```

> Importante: Cada workspace es independiente. Compilas y “source” el workspace que vas a usar en ese momento.

---

### 8.1 Preparación: carpeta raíz `tests_ws`

```bash
# 1) Cargar ROS 2 Jazzy
source /opt/ros/jazzy/setup.bash

# 2) Crear carpeta raíz
mkdir -p ~/tests_ws
cd ~/tests_ws
```

---

## 8.2 ✅ TÓPICO: Publisher + Subscriber (topic_ws)

### 8.2.1 Crear workspace y paquete

```bash
source /opt/ros/jazzy/setup.bash

mkdir -p ~/tests_ws/topic_ws/src
cd ~/tests_ws/topic_ws/src

# Paquete Python con rclpy
ros2 pkg create demo_topic --build-type ament_python --dependencies rclpy std_msgs

# Carpeta del módulo (por si no quedó creada)
mkdir -p demo_topic/demo_topic
```

### 8.2.2 Crear nodos Python

#### A) Publisher: `demo_topic/demo_topic/talker.py`

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class TalkerDemo(Node):
    def __init__(self):
        super().__init__("talker_demo")

        # Parámetros (ejemplo)
        self.declare_parameter("rate_hz", 2.0)
        self.declare_parameter("greeting", "Hola desde ROS 2 Topic")

        self.rate_hz = float(self.get_parameter("rate_hz").value)
        self.greeting = str(self.get_parameter("greeting").value)

        self.pub = self.create_publisher(String, "/demo/chatter", 10)

        period = 1.0 / max(self.rate_hz, 0.1)
        self.i = 0
        self.timer = self.create_timer(period, self.on_timer)

        self.get_logger().info(f"Talker listo. rate_hz={self.rate_hz}, greeting='{self.greeting}'")

    def on_timer(self):
        msg = String()
        msg.data = f"{self.greeting} #{self.i}"
        self.pub.publish(msg)
        self.get_logger().info(f"Publicado: {msg.data}")
        self.i += 1

def main():
    rclpy.init()
    node = TalkerDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
```

#### B) Subscriber: `demo_topic/demo_topic/listener.py`

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class ListenerDemo(Node):
    def __init__(self):
        super().__init__("listener_demo")
        self.sub = self.create_subscription(String, "/demo/chatter", self.cb, 10)
        self.get_logger().info("Listener listo.")

    def cb(self, msg: String):
        self.get_logger().info(f"Recibido: {msg.data}")

def main():
    rclpy.init()
    node = ListenerDemo()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()
```

### 8.2.3 Registrar entry points (para `ros2 run`)

Edita `demo_topic/setup.py` y en `entry_points` agrega:

```python
entry_points={
    'console_scripts': [
        'talker = demo_topic.talker:main',
        'listener = demo_topic.listener:main',
    ],
},
```

### 8.2.4 (Recomendado) Permisos

```bash
chmod +x ~/tests_ws/topic_ws/src/demo_topic/demo_topic/*.py
```

### 8.2.5 Compilar y source

```bash
cd ~/tests_ws/topic_ws
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions
colcon build --symlink-install
source install/setup.bash
```

### 8.2.6 Ejecutar y verificar

Terminal A (Publisher):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/topic_ws/install/setup.bash
ros2 run demo_topic talker --ros-args -p rate_hz:=2.0 -p greeting:="Hola estudiantes"
```

Terminal B (Subscriber):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/topic_ws/install/setup.bash
ros2 run demo_topic listener
```

Comandos útiles:
```bash
ros2 topic list
ros2 topic echo /demo/chatter
ros2 topic hz /demo/chatter
```

Parámetros (con el talker corriendo):
```bash
ros2 param list /talker_demo
ros2 param get /talker_demo greeting
ros2 param set /talker_demo greeting "Hola con params (CLI)"
```

---

## 8.3 ✅ SERVICIO: Server + Client (services_ws)

### 8.3.1 Crear workspace y paquetes (interfaces + python)

```bash
source /opt/ros/jazzy/setup.bash

mkdir -p ~/tests_ws/services_ws/src
cd ~/tests_ws/services_ws/src

# Paquete de interfaces (srv) - ament_cmake
ros2 pkg create demo_services_interfaces --build-type ament_cmake

# Paquete python (server/client) - ament_python
ros2 pkg create demo_services_py --build-type ament_python --dependencies rclpy
mkdir -p demo_services_interfaces/srv
mkdir -p demo_services_py/demo_services_py
```

### 8.3.2 Definir servicio

Crea `demo_services_interfaces/srv/AddTwoInts.srv`:

```srv
int64 a
int64 b
---
int64 sum
```

### 8.3.3 Configurar CMakeLists y package.xml (interfaces)

Edita `demo_services_interfaces/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(demo_services_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/AddTwoInts.srv"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

Edita `demo_services_interfaces/package.xml` (añade):

```xml
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 8.3.4 Crear server y client (Python)

#### A) Server: `demo_services_py/demo_services_py/add_server.py`

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from demo_services_interfaces.srv import AddTwoInts


class AddServer(Node):
    def __init__(self):
        super().__init__("add_server_demo")

        self.srv = self.create_service(
            AddTwoInts,
            "/demo/add_two_ints",
            self.handle_add
        )

        self.get_logger().info("Servicio /demo/add_two_ints listo.")

    def handle_add(self, req: AddTwoInts.Request, resp: AddTwoInts.Response) -> AddTwoInts.Response:
        self.get_logger().info(f"Servicio llamado: a={req.a}, b={req.b}")
        resp.sum = req.a + req.b
        return resp


def main():
    rclpy.init()
    node = AddServer()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
```

#### B) Client: `demo_services_py/demo_services_py/add_client.py`

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from demo_services_interfaces.srv import AddTwoInts

class AddClient(Node):
    def __init__(self):
        super().__init__("add_client_demo")

        self.declare_parameter("a", 2)
        self.declare_parameter("b", 3)
        a = int(self.get_parameter("a").value)
        b = int(self.get_parameter("b").value)

        self.cli = self.create_client(AddTwoInts, "/demo/add_two_ints")
        self.get_logger().info("Esperando servicio /demo/add_two_ints ...")
        self.cli.wait_for_service()

        req = AddTwoInts.Request()
        req.a = a
        req.b = b

        future = self.cli.call_async(req)
        future.add_done_callback(lambda f: self.on_done(f, a, b))

    def on_done(self, future, a, b):
        try:
            resp = future.result()
            self.get_logger().info(f"Resultado: {a} + {b} = {resp.sum}")
        except Exception as e:
            self.get_logger().error(f"Error llamando servicio: {e}")
        finally:
            rclpy.shutdown()

def main():
    rclpy.init()
    node = AddClient()
    rclpy.spin(node)

if __name__ == "__main__":
    main()
```

### 8.3.5 Dependencias y entry points

1) En `demo_services_py/package.xml` agrega:

```xml
<exec_depend>demo_services_interfaces</exec_depend>
```

2) En `demo_services_py/setup.py` agrega:

```python
entry_points={
    'console_scripts': [
        'add_server = demo_services_py.add_server:main',
        'add_client = demo_services_py.add_client:main',
    ],
},
```

3) Permisos:

```bash
chmod +x ~/tests_ws/services_ws/src/demo_services_py/demo_services_py/*.py
```

### 8.3.6 Compilar y source

```bash
cd ~/tests_ws/services_ws
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions
colcon build --symlink-install
source install/setup.bash
```

### 8.3.7 Ejecutar y verificar

Terminal A (Server):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/services_ws/install/setup.bash
ros2 run demo_services_py add_server
```

Terminal B (Client):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/services_ws/install/setup.bash
ros2 run demo_services_py add_client --ros-args -p a:=10 -p b:=25
```

CLI útil:
```bash
ros2 service list
ros2 service type /demo/add_two_ints
ros2 interface show demo_services_interfaces/srv/AddTwoInts
ros2 service call /demo/add_two_ints demo_services_interfaces/srv/AddTwoInts "{a: 7, b: 8}"
```

---

## 8.4 ✅ ACCIÓN: Action Server + Action Client (actions_ws)

### 8.4.1 Crear workspace y paquetes (interfaces + python)

```bash
source /opt/ros/jazzy/setup.bash

mkdir -p ~/tests_ws/actions_ws/src
cd ~/tests_ws/actions_ws/src

# Paquete de interfaces (action) - ament_cmake
ros2 pkg create demo_actions_interfaces --build-type ament_cmake

# Paquete python (server/client) - ament_python
ros2 pkg create demo_actions_py --build-type ament_python --dependencies rclpy
mkdir -p demo_actions_interfaces/action
mkdir -p demo_actions_py/demo_actions_py
```

### 8.4.2 Definir acción

Crea `demo_actions_interfaces/action/Countdown.action`:

```action
# Goal
int32 seconds
---
# Result
bool success
---
# Feedback
int32 remaining
```

### 8.4.3 Configurar CMakeLists y package.xml (interfaces)

Edita `demo_actions_interfaces/CMakeLists.txt`:

```cmake
cmake_minimum_required(VERSION 3.8)
project(demo_actions_interfaces)

find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "action/Countdown.action"
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
```

Edita `demo_actions_interfaces/package.xml` (añade):

```xml
<build_depend>rosidl_default_generators</build_depend>
<exec_depend>rosidl_default_runtime</exec_depend>
<member_of_group>rosidl_interface_packages</member_of_group>
```

### 8.4.4 Crear action server y client (Python)

#### A) Server: `demo_actions_py/demo_actions_py/countdown_server.py`

```python
#!/usr/bin/env python3
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.executors import MultiThreadedExecutor
from demo_actions_interfaces.action import Countdown

class CountdownServer(Node):
    def __init__(self):
        super().__init__("countdown_server_demo")
        self._server = ActionServer(
            self,
            Countdown,
            "/demo/countdown",
            execute_callback=self.execute,
            goal_callback=self.goal_cb,
            cancel_callback=self.cancel_cb
        )
        self.get_logger().info("Action server /demo/countdown listo.")

    def goal_cb(self, goal_request):
        self.get_logger().info(f"Goal recibido: seconds={goal_request.seconds}")
        return GoalResponse.ACCEPT

    def cancel_cb(self, goal_handle):
        self.get_logger().warn("Solicitud de cancelación recibida.")
        return CancelResponse.ACCEPT

    def execute(self, goal_handle):
        secs = max(0, int(goal_handle.request.seconds))
        feedback = Countdown.Feedback()

        for remaining in range(secs, -1, -1):
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()
                result = Countdown.Result()
                result.success = False
                self.get_logger().warn("Acción cancelada.")
                return result

            feedback.remaining = remaining
            goal_handle.publish_feedback(feedback)
            self.get_logger().info(f"Quedan: {remaining} s")
            time.sleep(1.0)

        goal_handle.succeed()
        result = Countdown.Result()
        result.success = True
        self.get_logger().info("Cuenta regresiva terminada.")
        return result

def main():
    rclpy.init()
    node = CountdownServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()

if __name__ == "__main__":
    main()
```

#### B) Client: `demo_actions_py/demo_actions_py/countdown_client.py`

```python
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from demo_actions_interfaces.action import Countdown

class CountdownClient(Node):
    def __init__(self):
        super().__init__("countdown_client_demo")

        self.declare_parameter("seconds", 5)
        seconds = int(self.get_parameter("seconds").value)

        self.client = ActionClient(self, Countdown, "/demo/countdown")
        self.get_logger().info("Esperando action server...")
        self.client.wait_for_server()

        goal = Countdown.Goal()
        goal.seconds = seconds

        self.get_logger().info(f"Enviando goal: {seconds} segundos")
        self._send_goal_future = self.client.send_goal_async(
            goal,
            feedback_callback=self.feedback_cb
        )
        self._send_goal_future.add_done_callback(self.goal_response_cb)

    def feedback_cb(self, fb_msg):
        self.get_logger().info(f"Feedback: remaining={fb_msg.feedback.remaining}")

    def goal_response_cb(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal rechazado.")
            rclpy.shutdown()
            return

        self.get_logger().info("Goal aceptado.")
        self._result_future = goal_handle.get_result_async()
        self._result_future.add_done_callback(self.result_cb)

    def result_cb(self, future):
        result = future.result().result
        self.get_logger().info(f"Resultado: success={result.success}")
        rclpy.shutdown()

def main():
    rclpy.init()
    node = CountdownClient()
    rclpy.spin(node)

if __name__ == "__main__":
    main()
```

### 8.4.5 Dependencias y entry points

1) En `demo_actions_py/package.xml` agrega:

```xml
<exec_depend>demo_actions_interfaces</exec_depend>
```

2) En `demo_actions_py/setup.py` agrega:

```python
entry_points={
    'console_scripts': [
        'countdown_server = demo_actions_py.countdown_server:main',
        'countdown_client = demo_actions_py.countdown_client:main',
    ],
},
```

3) Permisos:

```bash
chmod +x ~/tests_ws/actions_ws/src/demo_actions_py/demo_actions_py/*.py
```

### 8.4.6 Compilar y source

```bash
cd ~/tests_ws/actions_ws
source /opt/ros/jazzy/setup.bash
sudo apt update
sudo apt install -y python3-colcon-common-extensions
colcon build --symlink-install
source install/setup.bash
```

### 8.4.7 Ejecutar y verificar

Terminal A (Server):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/actions_ws/install/setup.bash
ros2 run demo_actions_py countdown_server
```

Terminal B (Client):
```bash
source /opt/ros/jazzy/setup.bash
source ~/tests_ws/actions_ws/install/setup.bash
ros2 run demo_actions_py countdown_client --ros-args -p seconds:=6
```

CLI útil:
```bash
ros2 action list
ros2 action info /demo/countdown
ros2 interface show demo_actions_interfaces/action/Countdown
ros2 action send_goal /demo/countdown demo_actions_interfaces/action/Countdown "{seconds: 5}" --feedback
```

---

### Nota final de esta sección

- Si te equivocas y algo “no aparece”, lo más común es:
  - No hiciste `source install/setup.bash`
  - No configuraste bien `entry_points` en `setup.py`
  - No recompilaste después de editar `setup.py`


## 9. Herramientas para “ver” la Graph (CLI + GUI)

### 9.1 CLI

```bash
ros2 node list
ros2 node info /talker_demo

ros2 topic list
ros2 topic info /demo/chatter

ros2 service list
ros2 action list

ros2 param list /talker_demo
ros2 daemon status
```

Si algo “se queda pegado”:
```bash
ros2 daemon stop
ros2 daemon start
```

### 9.2 GUI: rqt_graph

```bash
sudo apt update
sudo apt install -y ros-jazzy-rqt ros-jazzy-rqt-graph
ros2 run rqt_graph rqt_graph
```

---

## 10. Bibliografía

[1] Open Robotics, “Introspection with command line tools (ROS 2 Jazzy),” ROS 2 Documentation, consultado en 2026. Disponible: https://docs.ros.org/en/jazzy/Concepts/Basic/About-Command-Line-Tools.html citeturn0search7

[2] Open Robotics, “Understanding ROS 2 Actions (ROS 2 Jazzy),” ROS 2 Documentation, consultado en 2026. Disponible: https://docs.ros.org/en/jazzy/Tutorials/Beginner-CLI-Tools/Understanding-ROS2-Actions/Understanding-ROS2-Actions.html citeturn0search4

[3] Open Robotics, “Writing an action server and client (Python) — Jazzy,” ROS 2 Documentation, consultado en 2026. Disponible: https://docs.ros.org/en/jazzy/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html citeturn0search9

[4] Open Robotics, “Using the ros2 param command-line tool,” ROS 2 Documentation, consultado en 2026. Disponible: https://docs.ros.org/en/rolling/How-To-Guides/Using-ros2-param.html citeturn0search1

[5] ROS Wiki, “rqt_graph,” consultado en 2026. Disponible: https://wiki.ros.org/rqt_graph citeturn0search2

[6] Open Robotics, “Custom ROS 2 Interfaces (msg/srv) tutorial (concepto de rosidl),” ROS 2 Documentation, consultado en 2026. Disponible: https://docs.ros.org/en/foxy/Tutorials/Beginner-Client-Libraries/Custom-ROS2-Interfaces.html citeturn0search0

</div>
