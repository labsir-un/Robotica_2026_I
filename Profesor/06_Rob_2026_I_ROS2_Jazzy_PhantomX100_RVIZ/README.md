<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>PhantomX Pincher X100 con ROS 2 Jazzy</h1>

<h2>Guía 06 - Control del Robot Real, Interfaz Gráfica y Visualización en RViz</h2>

<h4>Pedro Fabián Cárdenas Herrera<br>
    Manuel Felipe Carranza Montenegro</h4>

<p>
  <img alt="Ubuntu 24.04 LTS" src="https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420?logo=ubuntu&logoColor=white">
  <img alt="ROS 2 Jazzy" src="https://img.shields.io/badge/ROS%202-Jazzy-22314E?logo=ros&logoColor=white">
  <img alt="Python" src="https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white">
  <img alt="Dynamixel" src="https://img.shields.io/badge/Dynamixel-AX--12A%20%7C%20XL430-00979D">
  <img alt="Nivel" src="https://img.shields.io/badge/Nivel-Intermedio-f39c12">
</p>

</div>

<div align="justify">

## Tabla de contenidos

- [1. Propósito de la guía](#1-propósito-de-la-guía)
- [2. Conceptos que se van a trabajar](#2-conceptos-que-se-van-a-trabajar)
- [3. Advertencias de seguridad](#3-advertencias-de-seguridad)
- [4. Requisitos](#4-requisitos)
- [5. Diferencias entre AX-12A y XL430](#5-diferencias-entre-ax-12a-y-xl430)
- [6. Instalación de ROS 2 Jazzy y dependencias](#6-instalación-de-ros-2-jazzy-y-dependencias)
- [7. Preparación del puerto serie](#7-preparación-del-puerto-serie)
- [8. Creación del workspace y de los paquetes](#8-creación-del-workspace-y-de-los-paquetes)
  - [8.1 Crear el workspace](#81-crear-el-workspace)
  - [8.2 Crear `pincher_control`](#82-crear-pincher_control)
  - [8.3 Crear `pincher_description`](#83-crear-pincher_description)
  - [8.4 Verificar la creación](#84-verificar-la-creación)
- [9. Estructura completa del repositorio](#9-estructura-completa-del-repositorio)
- [10. Código completo de `pincher_control`](#10-código-completo-de-pincher_control)
- [11. Código completo de `pincher_description`](#11-código-completo-de-pincher_description)
- [12. Descarga y ubicación de las mallas STL](#12-descarga-y-ubicación-de-las-mallas-stl)
- [13. Compilación del workspace](#13-compilación-del-workspace)
- [14. Práctica 1: modelo del robot sin controlador](#14-práctica-1-modelo-del-robot-sin-controlador)
- [15. Práctica 2: sistema completo sin hardware](#15-práctica-2-sistema-completo-sin-hardware)
- [16. Detección del puerto e IDs Dynamixel](#16-detección-del-puerto-e-ids-dynamixel)
- [17. Práctica 3: conexión con AX-12A](#17-práctica-3-conexión-con-ax-12a)
- [18. Práctica 4: conexión con XL430](#18-práctica-4-conexión-con-xl430)
- [19. Uso de la interfaz gráfica](#19-uso-de-la-interfaz-gráfica)
- [20. Verificación mediante ROS 2 CLI](#20-verificación-mediante-ros-2-cli)
- [21. Validación del Xacro y de las mallas](#21-validación-del-xacro-y-de-las-mallas)
- [22. Solución de problemas](#22-solución-de-problemas)
- [23. Actividad propuesta para estudiantes](#23-actividad-propuesta-para-estudiantes)
- [24. Publicación en GitHub](#24-publicación-en-github)
- [25. Cambios respecto a una implementación Humble](#25-cambios-respecto-a-una-implementación-humble)
- [26. Bibliografía](#26-bibliografía)

---

## 1. Propósito de la guía

Esta guía construye un proyecto completo para controlar y visualizar el **PhantomX Pincher X100** con **Ubuntu 24.04 LTS** y **ROS 2 Jazzy Jalisco**. El material integra comunicación directa con servomotores DYNAMIXEL, una interfaz gráfica con Tkinter, publicación estándar de estados articulares y visualización tridimensional en RViz2.

El repositorio trabaja con dos modos:

- `use_hardware:=false`: no abre el puerto serie. Las posiciones solicitadas se publican en `/joint_states` y permiten verificar la GUI, el Xacro, TF y RViz2.
- `use_hardware:=true`: escribe `Goal Position` y lee `Present Position` mediante DynamixelSDK.

> **Ruta recomendada:** la guía asume que los paquetes terminan en `~/ros2_jazzy/phantom_ws/src`. El repositorio también contiene un workspace listo dentro de `ros2_jazzy/phantom_ws` para compilarlo directamente desde la carpeta descargada.

> **Dato pendiente para publicación:** el correo de mantenimiento se dejó como `pendiente@ejemplo.invalid` porque no se proporcionó un correo institucional. Debe reemplazarse antes de publicar oficialmente el repositorio.

---

## 2. Conceptos que se van a trabajar

| Concepto | Aplicación en la práctica |
|---|---|
| **Nodo ROS 2** | `pincher_controller`, `pincher_gui`, `robot_state_publisher` y `dynamixel_scanner`. |
| **Tópico** | `/pincher/command`, `/pincher/profile_velocity`, `/joint_states`, `/tf` y `/tf_static`. |
| **Servicio** | HOME, activación de torque y parada de software. |
| **JointState** | Transporte de nombres y posiciones articulares en radianes. |
| **Xacro/URDF** | Definición del árbol cinemático, límites, ejes, articulaciones mimic y mallas. |
| **TF** | Transformaciones entre `world`, `link0`, `link1`, `link2`, `link3`, `link4` y la pinza. |
| **DynamixelSDK** | Apertura del puerto, ping, lectura y escritura de registros. |
| **Tkinter** | Sliders, entradas numéricas, HOME, velocidad, torque y parada de software. |
| **Modo sin hardware** | Validación segura del software antes de energizar el brazo. |

---

## 3. Advertencias de seguridad

> **La parada incluida en la GUI es una parada de software. No sustituye una parada de emergencia física, cableada y certificada.**

Antes de usar el robot real:

- fija la base del manipulador;
- mantén disponible el corte físico de alimentación;
- retira objetos y personas del volumen de trabajo;
- prueba primero con `use_hardware:=false`;
- verifica individualmente IDs, protocolo, baudrate y sentido de cada articulación;
- no conectes ni desconectes motores con el bus energizado;
- no mezcles AX-12A y XL430 en esta implementación básica;
- no actives `home_on_startup` hasta comprobar físicamente los valores HOME;
- empieza con una velocidad baja;
- comprueba que la fuente corresponde al modelo instalado.

Si la inicialización falla en uno o más motores, el nodo intenta deshabilitar el torque y cierra el puerto para evitar que el sistema quede parcialmente habilitado.

---

## 4. Requisitos

### 4.1 Software

- Ubuntu 24.04 LTS de 64 bits.
- ROS 2 Jazzy Desktop.
- Python 3.12 del sistema.
- `colcon`, `rosdep`, Xacro, RViz2 y `robot_state_publisher`.
- DynamixelSDK para Python.
- Tkinter.
- Git, cURL y `tree`.

### 4.2 Hardware

- PhantomX Pincher X100.
- Cinco servomotores del mismo perfil: AX-12A o XL430-W250.
- U2D2, USB2Dynamixel o interfaz compatible.
- Fuente de alimentación adecuada.
- Cableado DYNAMIXEL en buen estado.

---

## 5. Diferencias entre AX-12A y XL430

| Característica | AX-12A | XL430-W250 |
|---|---:|---:|
| Protocolo | 1.0 | 2.0 |
| Posición mínima | 0 | 0 |
| Centro usado | 512 | 2048 |
| Posición máxima | 1023 | 4095 |
| Rango representado | aproximadamente 300° | una vuelta en modo posición |
| Torque Enable | dirección 24, 1 byte | dirección 64, 1 byte |
| Goal Position | dirección 30, 2 bytes | dirección 116, 4 bytes |
| Velocidad | dirección 32, 2 bytes | Profile Velocity, dirección 112, 4 bytes |
| Present Position | dirección 36, 2 bytes | dirección 132, 4 bytes |
| Torque Limit equivalente | dirección 34, 2 bytes | no existe un equivalente directo |

El archivo `dynamixel_profiles.py` concentra estas diferencias. El controlador evita escribir la dirección 38 del XL430 como si fuera un `Torque Limit`, porque ese registro no tiene la misma función que el registro 34 del AX-12A.

---

## 6. Instalación de ROS 2 Jazzy y dependencias

Comprueba el sistema:

```bash
lsb_release -a
source /opt/ros/jazzy/setup.bash
ros2 --version
```

Instalación manual:

```bash
sudo apt update
sudo apt install -y \
  python3-colcon-common-extensions \
  python3-rosdep \
  python3-tk \
  python3-serial \
  git curl tree \
  ros-jazzy-dynamixel-sdk \
  ros-jazzy-xacro \
  ros-jazzy-robot-state-publisher \
  ros-jazzy-joint-state-publisher \
  ros-jazzy-joint-state-publisher-gui \
  ros-jazzy-rviz2
```


Comprobaciones:

```bash
python3 -c "import dynamixel_sdk; print('DynamixelSDK disponible')"
python3 -c "import tkinter; print('Tkinter disponible')"
```

Inicializa `rosdep` solamente una vez:

```bash
sudo rosdep init
rosdep update
```

Si ya estaba inicializado:

```bash
rosdep update
```

---

## 7. Preparación del puerto serie

Conecta el adaptador y revisa los dispositivos:

```bash
ls /dev/ttyUSB* 2>/dev/null
ls /dev/ttyACM* 2>/dev/null
dmesg | tail -n 30
```

Añade el usuario al grupo `dialout`:

```bash
sudo usermod -aG dialout $USER
```

Después, cierra sesión y vuelve a ingresar. Comprueba:

```bash
groups
ls -l /dev/ttyUSB0
```

No se recomienda ejecutar el nodo permanentemente con `sudo`.

---

## 8. Creación del workspace y de los paquetes

Esta sección muestra la creación completa del workspace y de los dos paquetes. Los comandos deben ejecutarse antes de reemplazar el contenido de los archivos con el código de las secciones 10 y 11.

> **Ruta usada en toda la guía:** `~/ros2_jazzy/phantom_ws`. La ruta `~/ros_humble/phantom_ws` no se usa porque este repositorio corresponde a ROS 2 Jazzy.

### 8.1 Crear el workspace

Carga ROS 2 Jazzy y crea la carpeta `src`:

```bash
source /opt/ros/jazzy/setup.bash

mkdir -p ~/ros2_jazzy/phantom_ws/src
cd ~/ros2_jazzy/phantom_ws/src
```

Comprueba la ruta actual:

```bash
pwd
```

La salida debe terminar en:

```text
/ros2_jazzy/phantom_ws/src
```

### 8.2 Crear `pincher_control`

Desde `phantom_ws/src`, genera el paquete de control en Python:

```bash
cd ~/ros2_jazzy/phantom_ws/src

ros2 pkg create --build-type ament_python pincher_control \
  --dependencies rclpy dynamixel_sdk
```

ROS 2 crea inicialmente:

```text
pincher_control/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── pincher_control
├── pincher_control/
│   └── __init__.py
└── test/
```

Crea las carpetas adicionales del paquete:

```bash
cd ~/ros2_jazzy/phantom_ws/src/pincher_control
mkdir -p config launch
```

Crea los archivos de código, configuración y lanzamiento que se completarán en la sección 10:

```bash
touch pincher_control/dynamixel_profiles.py
touch pincher_control/control_servo.py
touch pincher_control/pincher_gui.py
touch pincher_control/scan_dynamixel.py

touch config/ax12a.yaml
touch config/xl430.yaml
touch launch/pincher_system.launch.py
```

La carpeta `test` generada automáticamente no se utiliza en esta guía. Para que la estructura coincida con el repositorio final:

```bash
rm -rf test
```

> El comando de creación añade inicialmente `rclpy` y `dynamixel_sdk`. En la sección 10 se reemplaza `package.xml` por la versión completa, que declara también `sensor_msgs`, `std_msgs`, `std_srvs`, `launch`, `launch_ros` y `pincher_description`.

### 8.3 Crear `pincher_description`

Regresa a `phantom_ws/src` y crea el paquete de descripción:

```bash
cd ~/ros2_jazzy/phantom_ws/src

ros2 pkg create --build-type ament_python pincher_description
```

ROS 2 crea inicialmente:

```text
pincher_description/
├── package.xml
├── setup.py
├── setup.cfg
├── resource/
│   └── pincher_description
├── pincher_description/
│   └── __init__.py
└── test/
```

Crea las carpetas del modelo y de visualización:

```bash
cd ~/ros2_jazzy/phantom_ws/src/pincher_description
mkdir -p meshes urdf rviz launch
```

Crea los archivos que se completarán en la sección 11:

```bash
touch urdf/robot.xacro
touch rviz/pincher.rviz
touch launch/display.launch.py
touch launch/display_gui.launch.py
```

Este paquete usa `setup.py` solamente para instalar recursos; no contiene nodos Python. Por eso se eliminan el módulo Python vacío y la carpeta de pruebas que genera `ros2 pkg create`:

```bash
rm -rf pincher_description
rm -rf test
```

Descarga los ocho archivos de la carpeta `meshes` anexa al repositorio y cópialos en:

```text
~/ros2_jazzy/phantom_ws/src/pincher_description/meshes/
```

Los nombres deben conservarse exactamente como se muestran en la sección 12.

### 8.4 Verificar la creación

Comprueba la estructura antes de pegar el código:

```bash
cd ~/ros2_jazzy/phantom_ws/src
tree -L 3
```

La estructura mínima debe ser:

```text
~/ros2_jazzy/phantom_ws/src/
├── pincher_control/
│   ├── config/
│   │   ├── ax12a.yaml
│   │   └── xl430.yaml
│   ├── launch/
│   │   └── pincher_system.launch.py
│   ├── package.xml
│   ├── pincher_control/
│   │   ├── __init__.py
│   │   ├── control_servo.py
│   │   ├── dynamixel_profiles.py
│   │   ├── pincher_gui.py
│   │   └── scan_dynamixel.py
│   ├── resource/
│   │   └── pincher_control
│   ├── setup.cfg
│   └── setup.py
└── pincher_description/
    ├── launch/
    │   ├── display.launch.py
    │   └── display_gui.launch.py
    ├── meshes/
    ├── package.xml
    ├── resource/
    │   └── pincher_description
    ├── rviz/
    │   └── pincher.rviz
    ├── setup.cfg
    ├── setup.py
    └── urdf/
        └── robot.xacro
```

A partir de este punto, reemplaza cada archivo con el contenido completo de las secciones 10 y 11.

---

## 9. Estructura completa del repositorio

```text
PhantomX_Pincher_X100_ROS2_Jazzy/
├── README.md
├── LICENSE
├── .gitignore
└── ros2_jazzy/
    └── phantom_ws/
        └── src/
            ├── pincher_control/
            │   ├── package.xml
            │   ├── setup.py
            │   ├── setup.cfg
            │   ├── resource/pincher_control
            │   ├── config/
            │   │   ├── ax12a.yaml
            │   │   └── xl430.yaml
            │   ├── launch/pincher_system.launch.py
            │   └── pincher_control/
            │       ├── __init__.py
            │       ├── dynamixel_profiles.py
            │       ├── control_servo.py
            │       ├── pincher_gui.py
            │       └── scan_dynamixel.py
            └── pincher_description/
                ├── package.xml
                ├── setup.py
                ├── setup.cfg
                ├── resource/pincher_description
                ├── launch/
                │   ├── display.launch.py
                │   └── display_gui.launch.py
                ├── urdf/robot.xacro
                ├── rviz/pincher.rviz
                └── meshes/
                    ├── README.md
                    ├── px100_1_base.stl
                    ├── px100_2_shoulder.stl
                    ├── px100_3_upper_arm.stl
                    ├── px100_4_forearm.stl
                    ├── px100_5_gripper.stl
                    ├── px100_6_gripper_prop.stl
                    ├── px100_7_gripper_bar.stl
                    └── px100_8_gripper_finger.stl
```

Las ocho mallas STL se entregan en la carpeta `meshes` anexa al repositorio. Deben copiarse dentro de `pincher_description/meshes` conservando exactamente los nombres indicados.


---


## 10. Código completo de `pincher_control`

`pincher_control` es el paquete `ament_python` creado en la sección 8.2. Reemplaza ahora los archivos generados por ROS 2 y completa los archivos vacíos con el contenido presentado a continuación. El controlador publica `/joint_states`, recibe objetivos en `/pincher/command`, permite actualizar velocidad y expone servicios estándar sin crear interfaces personalizadas.

#### `ros2_jazzy/phantom_ws/src/pincher_control/package.xml`

```xml
<?xml version="1.0"?>
<package format="3">
  <name>pincher_control</name>
  <version>0.1.0</version>
  <description>Control directo del PhantomX Pincher X100 con DynamixelSDK, GUI y publicación de JointState para ROS 2 Jazzy.</description>
  <maintainer email="pendiente@ejemplo.invalid">Curso de Robótica 2026-I</maintainer>
  <license>BSD-3-Clause</license>

  <exec_depend>rclpy</exec_depend>
  <exec_depend>dynamixel_sdk</exec_depend>
  <exec_depend>sensor_msgs</exec_depend>
  <exec_depend>std_msgs</exec_depend>
  <exec_depend>std_srvs</exec_depend>
  <exec_depend>launch</exec_depend>
  <exec_depend>launch_ros</exec_depend>
  <exec_depend>pincher_description</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/setup.py`

```python
from glob import glob
import os

from setuptools import find_packages, setup

package_name = 'pincher_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Curso de Robótica 2026-I',
    maintainer_email='pendiente@ejemplo.invalid',
    description='Control directo, GUI y herramientas Dynamixel para PhantomX Pincher X100 en ROS 2 Jazzy.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'control_servo = pincher_control.control_servo:main',
            'pincher_gui = pincher_control.pincher_gui:main',
            'scan_dynamixel = pincher_control.scan_dynamixel:main',
        ],
    },
)
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/setup.cfg`

```ini
[develop]
script_dir=$base/lib/pincher_control
[install]
install_scripts=$base/lib/pincher_control
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/resource/pincher_control`

```text

```

#### `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/__init__.py`

```python
"""Herramientas de control para el PhantomX Pincher X100."""
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/dynamixel_profiles.py`

```python
"""Perfiles de registros y conversión para servomotores DYNAMIXEL compatibles."""

from dataclasses import dataclass
import math
from typing import Optional


@dataclass(frozen=True)
class MotorProfile:
    """Descripción mínima de un modelo para control de posición."""

    name: str
    protocol_version: float
    raw_min: int
    raw_center: int
    raw_max: int
    mechanical_range_rad: float
    torque_enable_addr: int
    goal_position_addr: int
    goal_position_size: int
    speed_addr: int
    speed_size: int
    present_position_addr: int
    present_position_size: int
    torque_limit_addr: Optional[int] = None
    torque_limit_size: int = 0

    def clamp_raw(self, value: int) -> int:
        return max(self.raw_min, min(self.raw_max, int(value)))

    def raw_to_radians(self, value: int) -> float:
        """Convierte una lectura absoluta a radianes alrededor del centro."""
        value = self.clamp_raw(value)
        units_per_rad = (self.raw_max - self.raw_min) / self.mechanical_range_rad
        return (value - self.raw_center) / units_per_rad

    def radians_to_raw(self, radians: float) -> int:
        """Convierte radianes alrededor del centro a unidades DYNAMIXEL."""
        units_per_rad = (self.raw_max - self.raw_min) / self.mechanical_range_rad
        return self.clamp_raw(round(self.raw_center + radians * units_per_rad))


MOTOR_PROFILES = {
    'ax12a': MotorProfile(
        name='AX-12A',
        protocol_version=1.0,
        raw_min=0,
        raw_center=512,
        raw_max=1023,
        mechanical_range_rad=math.radians(300.0),
        torque_enable_addr=24,
        goal_position_addr=30,
        goal_position_size=2,
        speed_addr=32,
        speed_size=2,
        present_position_addr=36,
        present_position_size=2,
        torque_limit_addr=34,
        torque_limit_size=2,
    ),
    'xl430': MotorProfile(
        name='XL430-W250',
        protocol_version=2.0,
        raw_min=0,
        raw_center=2048,
        raw_max=4095,
        mechanical_range_rad=2.0 * math.pi,
        torque_enable_addr=64,
        goal_position_addr=116,
        goal_position_size=4,
        speed_addr=112,
        speed_size=4,
        present_position_addr=132,
        present_position_size=4,
        # El XL430 no posee un registro equivalente al Torque Limit(34) del AX-12A.
        torque_limit_addr=None,
        torque_limit_size=0,
    ),
}


def get_motor_profile(model: str) -> MotorProfile:
    key = model.strip().lower().replace('-', '').replace('_', '')
    aliases = {
        'ax12': 'ax12a',
        'ax12a': 'ax12a',
        'xl430': 'xl430',
        'xl430w250': 'xl430',
    }
    canonical = aliases.get(key)
    if canonical is None:
        valid = ', '.join(sorted(MOTOR_PROFILES))
        raise ValueError(f'Modelo DYNAMIXEL no soportado: {model}. Opciones: {valid}')
    return MOTOR_PROFILES[canonical]
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/control_servo.py`

```python
#!/usr/bin/env python3
"""Nodo ROS 2 para controlar el PhantomX Pincher mediante DynamixelSDK.

El nodo acepta comandos articulares en radianes por ``/pincher/command`` y
publica el estado en ``/joint_states``. Con ``use_hardware:=false`` actúa como
controlador didáctico sin abrir el puerto serie.
"""

from __future__ import annotations

import math
from typing import Dict, Iterable, List, Optional, Tuple

import rclpy
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger

from pincher_control.dynamixel_profiles import MotorProfile, get_motor_profile


class PincherController(Node):
    """Controlador de posición para cinco articulaciones DYNAMIXEL."""

    def __init__(self) -> None:
        super().__init__('pincher_controller')

        self.declare_parameter('motor_model', 'xl430')
        self.declare_parameter('use_hardware', False)
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 1000000)
        self.declare_parameter('dxl_ids', [1, 2, 3, 4, 5])
        self.declare_parameter(
            'joint_names',
            ['waist', 'shoulder', 'elbow', 'wrist', 'gripper'],
        )
        self.declare_parameter('joint_signs', [1.0, -1.0, -1.0, -1.0, 1.0])
        self.declare_parameter('home_positions', [-1, -1, -1, -1, -1])
        self.declare_parameter('moving_speed', 100)
        self.declare_parameter('max_speed_value', 1023)
        self.declare_parameter('torque_limit', -1)
        self.declare_parameter('read_rate_hz', 20.0)
        self.declare_parameter('home_on_startup', False)
        self.declare_parameter('disable_torque_on_shutdown', True)

        self.profile: MotorProfile = get_motor_profile(
            str(self.get_parameter('motor_model').value)
        )
        self.use_hardware = bool(self.get_parameter('use_hardware').value)
        self.port_name = str(self.get_parameter('port').value)
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.dxl_ids = [int(value) for value in self.get_parameter('dxl_ids').value]
        self.joint_names = [str(value) for value in self.get_parameter('joint_names').value]
        self.joint_signs = [float(value) for value in self.get_parameter('joint_signs').value]
        raw_home = [int(value) for value in self.get_parameter('home_positions').value]
        self.moving_speed = int(self.get_parameter('moving_speed').value)
        self.max_speed_value = int(self.get_parameter('max_speed_value').value)
        self.torque_limit = int(self.get_parameter('torque_limit').value)
        self.read_rate_hz = float(self.get_parameter('read_rate_hz').value)
        self.home_on_startup = bool(self.get_parameter('home_on_startup').value)
        self.disable_torque_on_shutdown = bool(
            self.get_parameter('disable_torque_on_shutdown').value
        )

        self._validate_configuration(raw_home)
        self.home_positions = [
            self.profile.raw_center if value < 0 else self.profile.clamp_raw(value)
            for value in raw_home
        ]

        self.port_handler: Optional[PortHandler] = None
        self.packet_handler: Optional[PacketHandler] = None
        self.hardware_ready = False
        self.torque_enabled = not self.use_hardware
        self.software_stop_active = False
        self._closed = False
        self._last_read_error_ns: Dict[int, int] = {}

        self.current_joint_positions = [
            self._raw_to_joint_radians(raw, index)
            for index, raw in enumerate(self.home_positions)
        ]
        self.commanded_joint_positions = list(self.current_joint_positions)

        self.joint_state_publisher = self.create_publisher(JointState, '/joint_states', 10)
        self.status_publisher = self.create_publisher(String, '/pincher/status', 10)
        self.command_subscription = self.create_subscription(
            JointState,
            '/pincher/command',
            self.command_callback,
            10,
        )
        self.speed_subscription = self.create_subscription(
            UInt32,
            '/pincher/profile_velocity',
            self.speed_callback,
            10,
        )
        self.home_service = self.create_service(Trigger, '/pincher/home', self.home_callback)
        self.stop_service = self.create_service(
            Trigger,
            '/pincher/software_stop',
            self.stop_callback,
        )
        self.torque_service = self.create_service(
            SetBool,
            '/pincher/torque_enable',
            self.torque_callback,
        )

        timer_period = 1.0 / max(self.read_rate_hz, 1.0)
        self.state_timer = self.create_timer(timer_period, self.state_timer_callback)

        if self.use_hardware:
            self.hardware_ready = self._connect_hardware()
            if self.hardware_ready and self.home_on_startup:
                self._move_home()
        else:
            self._publish_status(
                f'Modo sin hardware activo. Perfil seleccionado: {self.profile.name}.'
            )

        self.get_logger().info(
            f'Controlador iniciado | modelo={self.profile.name} | '
            f'use_hardware={self.use_hardware} | articulaciones={self.joint_names}'
        )

    def _validate_configuration(self, raw_home: List[int]) -> None:
        expected = len(self.dxl_ids)
        fields = {
            'joint_names': self.joint_names,
            'joint_signs': self.joint_signs,
            'home_positions': raw_home,
        }
        if expected == 0:
            raise ValueError('dxl_ids no puede estar vacío.')
        if len(set(self.dxl_ids)) != expected:
            raise ValueError(f'Los IDs DYNAMIXEL deben ser únicos: {self.dxl_ids}')
        for name, values in fields.items():
            if len(values) != expected:
                raise ValueError(
                    f'{name} debe tener {expected} elementos; se recibieron {len(values)}.'
                )
        for sign in self.joint_signs:
            if not math.isclose(abs(sign), 1.0, abs_tol=1e-9):
                raise ValueError('Cada elemento de joint_signs debe ser 1.0 o -1.0.')

    def _publish_status(self, text: str) -> None:
        msg = String()
        msg.data = text
        self.status_publisher.publish(msg)
        self.get_logger().info(text)

    def _connect_hardware(self) -> bool:
        self.port_handler = PortHandler(self.port_name)
        self.packet_handler = PacketHandler(self.profile.protocol_version)

        if not self.port_handler.openPort():
            self.get_logger().error(f'No se pudo abrir el puerto {self.port_name}.')
            return False
        if not self.port_handler.setBaudRate(self.baudrate):
            self.get_logger().error(f'No se pudo configurar baudrate={self.baudrate}.')
            self.port_handler.closePort()
            return False

        self.get_logger().info(
            f'Puerto {self.port_name} abierto a {self.baudrate} baud, '
            f'protocolo {self.profile.protocol_version:.1f}.'
        )

        all_ok = True
        for dxl_id in self.dxl_ids:
            if not self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                1,
                'Torque Enable',
            ):
                all_ok = False
                continue
            if not self._write_speed(dxl_id, self.moving_speed):
                all_ok = False
            if (
                self.profile.torque_limit_addr is not None
                and self.torque_limit >= 0
                and not self._write_register(
                    dxl_id,
                    self.profile.torque_limit_addr,
                    self.profile.torque_limit_size,
                    max(0, min(1023, self.torque_limit)),
                    'Torque Limit',
                )
            ):
                all_ok = False

        if self.profile.torque_limit_addr is None and self.torque_limit >= 0:
            self.get_logger().warning(
                'El parámetro torque_limit se ignora para XL430: no existe un registro '
                'equivalente al Torque Limit(34) del AX-12A.'
            )

        self.torque_enabled = all_ok
        if all_ok:
            self._publish_status('Comunicación DYNAMIXEL inicializada correctamente.')
            return True

        self.get_logger().error(
            'La inicialización no fue correcta para todos los motores. '
            'Se deshabilitará el torque y se cerrará el puerto por seguridad.'
        )
        for dxl_id in self.dxl_ids:
            self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                0,
                'Torque Enable de recuperación',
            )
        self.torque_enabled = False
        self.port_handler.closePort()
        return False

    def _communication_error_text(self, comm_result: int, dxl_error: int) -> str:
        if self.packet_handler is None:
            return 'PacketHandler no inicializado.'
        parts: List[str] = []
        if comm_result != COMM_SUCCESS:
            parts.append(self.packet_handler.getTxRxResult(comm_result))
        if dxl_error != 0:
            parts.append(self.packet_handler.getRxPacketError(dxl_error))
        return ' | '.join(parts) if parts else 'sin detalle'

    def _write_register(
        self,
        dxl_id: int,
        address: int,
        size: int,
        value: int,
        label: str,
    ) -> bool:
        if self.packet_handler is None or self.port_handler is None:
            return False
        methods = {
            1: self.packet_handler.write1ByteTxRx,
            2: self.packet_handler.write2ByteTxRx,
            4: self.packet_handler.write4ByteTxRx,
        }
        method = methods.get(size)
        if method is None:
            raise ValueError(f'Tamaño de registro no soportado: {size}')
        comm_result, dxl_error = method(
            self.port_handler,
            int(dxl_id),
            int(address),
            int(value),
        )
        if comm_result != COMM_SUCCESS or dxl_error != 0:
            self.get_logger().error(
                f'ID {dxl_id}: error escribiendo {label}: '
                f'{self._communication_error_text(comm_result, dxl_error)}'
            )
            return False
        return True

    def _read_register(
        self,
        dxl_id: int,
        address: int,
        size: int,
        label: str,
    ) -> Tuple[Optional[int], bool]:
        if self.packet_handler is None or self.port_handler is None:
            return None, False
        methods = {
            1: self.packet_handler.read1ByteTxRx,
            2: self.packet_handler.read2ByteTxRx,
            4: self.packet_handler.read4ByteTxRx,
        }
        method = methods.get(size)
        if method is None:
            raise ValueError(f'Tamaño de registro no soportado: {size}')
        value, comm_result, dxl_error = method(
            self.port_handler,
            int(dxl_id),
            int(address),
        )
        if comm_result != COMM_SUCCESS or dxl_error != 0:
            now_ns = self.get_clock().now().nanoseconds
            previous_ns = self._last_read_error_ns.get(dxl_id, 0)
            if now_ns - previous_ns > 2_000_000_000:
                self.get_logger().error(
                    f'ID {dxl_id}: error leyendo {label}: '
                    f'{self._communication_error_text(comm_result, dxl_error)}'
                )
                self._last_read_error_ns[dxl_id] = now_ns
            return None, False
        return int(value), True

    def _write_speed(self, dxl_id: int, speed: int) -> bool:
        safe_speed = max(0, min(self.max_speed_value, int(speed)))
        return self._write_register(
            dxl_id,
            self.profile.speed_addr,
            self.profile.speed_size,
            safe_speed,
            'Moving Speed/Profile Velocity',
        )

    def _raw_to_joint_radians(self, raw: int, joint_index: int) -> float:
        return self.profile.raw_to_radians(raw) * self.joint_signs[joint_index]

    def _joint_radians_to_raw(self, radians: float, joint_index: int) -> int:
        motor_radians = float(radians) / self.joint_signs[joint_index]
        return self.profile.radians_to_raw(motor_radians)

    def _command_pairs(self, msg: JointState) -> Iterable[Tuple[int, float]]:
        if msg.name:
            name_to_position = dict(zip(msg.name, msg.position))
            for index, name in enumerate(self.joint_names):
                if name in name_to_position:
                    yield index, float(name_to_position[name])
        else:
            for index, position in enumerate(msg.position[: len(self.joint_names)]):
                yield index, float(position)

    def command_callback(self, msg: JointState) -> None:
        if self.software_stop_active:
            self.get_logger().warning(
                'Comando ignorado: la parada de software está activa. '
                'Reactiva el torque antes de mover.'
            )
            return

        command_received = False
        for joint_index, radians in self._command_pairs(msg):
            command_received = True
            raw_goal = self._joint_radians_to_raw(radians, joint_index)
            clamped_radians = self._raw_to_joint_radians(raw_goal, joint_index)
            self.commanded_joint_positions[joint_index] = clamped_radians

            if self.use_hardware:
                if not self.hardware_ready or not self.torque_enabled:
                    self.get_logger().warning(
                        f'Comando para {self.joint_names[joint_index]} ignorado: '
                        'hardware no disponible o torque deshabilitado.'
                    )
                    continue
                self._write_register(
                    self.dxl_ids[joint_index],
                    self.profile.goal_position_addr,
                    self.profile.goal_position_size,
                    raw_goal,
                    'Goal Position',
                )
            else:
                self.current_joint_positions[joint_index] = clamped_radians

        if not command_received:
            self.get_logger().warning(
                'El mensaje /pincher/command no contiene articulaciones reconocidas.'
            )

    def speed_callback(self, msg: UInt32) -> None:
        requested = max(0, min(self.max_speed_value, int(msg.data)))
        self.moving_speed = requested
        if not self.use_hardware:
            self._publish_status(f'Velocidad simulada actualizada a {requested}.')
            return
        if not self.hardware_ready:
            self.get_logger().warning('No se puede actualizar velocidad: hardware no disponible.')
            return
        successes = sum(self._write_speed(dxl_id, requested) for dxl_id in self.dxl_ids)
        self._publish_status(
            f'Velocidad actualizada a {requested} en {successes}/{len(self.dxl_ids)} motores.'
        )

    def _move_home(self) -> bool:
        if self.software_stop_active or not self.torque_enabled:
            return False
        success = True
        for index, raw_goal in enumerate(self.home_positions):
            self.commanded_joint_positions[index] = self._raw_to_joint_radians(
                raw_goal,
                index,
            )
            if self.use_hardware:
                success = self._write_register(
                    self.dxl_ids[index],
                    self.profile.goal_position_addr,
                    self.profile.goal_position_size,
                    raw_goal,
                    'Goal Position HOME',
                ) and success
            else:
                self.current_joint_positions[index] = self.commanded_joint_positions[index]
        return success

    def home_callback(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        del request
        if self.software_stop_active or not self.torque_enabled:
            response.success = False
            response.message = (
                'HOME bloqueado: activa el torque y libera la parada de software primero.'
            )
            return response
        response.success = self._move_home()
        response.message = (
            'Comando HOME enviado.' if response.success else 'No fue posible enviar HOME.'
        )
        self._publish_status(response.message)
        return response

    def _set_torque_all(self, enabled: bool) -> bool:
        if not self.use_hardware:
            self.torque_enabled = enabled
            return True
        if not self.hardware_ready and enabled:
            return False
        successes = 0
        for dxl_id in self.dxl_ids:
            if self._write_register(
                dxl_id,
                self.profile.torque_enable_addr,
                1,
                1 if enabled else 0,
                'Torque Enable',
            ):
                successes += 1
        all_ok = successes == len(self.dxl_ids)
        if all_ok:
            self.torque_enabled = enabled
        return all_ok

    def torque_callback(
        self,
        request: SetBool.Request,
        response: SetBool.Response,
    ) -> SetBool.Response:
        response.success = self._set_torque_all(bool(request.data))
        if response.success:
            self.software_stop_active = False if request.data else self.software_stop_active
            state = 'habilitado' if request.data else 'deshabilitado'
            response.message = f'Torque {state} en todos los motores.'
        else:
            response.message = 'No fue posible cambiar el torque en todos los motores.'
        self._publish_status(response.message)
        return response

    def stop_callback(self, request: Trigger.Request, response: Trigger.Response) -> Trigger.Response:
        del request
        self.software_stop_active = True
        response.success = self._set_torque_all(False)
        response.message = (
            'Parada de software activa: torque deshabilitado.'
            if response.success
            else 'Parada solicitada, pero no se confirmó el torque de todos los motores.'
        )
        self._publish_status(response.message)
        return response

    def _read_hardware_positions(self) -> None:
        for index, dxl_id in enumerate(self.dxl_ids):
            raw, ok = self._read_register(
                dxl_id,
                self.profile.present_position_addr,
                self.profile.present_position_size,
                'Present Position',
            )
            if ok and raw is not None:
                self.current_joint_positions[index] = self._raw_to_joint_radians(raw, index)

    def state_timer_callback(self) -> None:
        if self.use_hardware and self.hardware_ready:
            self._read_hardware_positions()

        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = list(self.joint_names)
        msg.position = list(self.current_joint_positions)
        self.joint_state_publisher.publish(msg)

    def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if self.use_hardware and self.port_handler is not None:
            if self.disable_torque_on_shutdown and self.packet_handler is not None:
                for dxl_id in self.dxl_ids:
                    self._write_register(
                        dxl_id,
                        self.profile.torque_enable_addr,
                        1,
                        0,
                        'Torque Enable al cerrar',
                    )
            self.port_handler.closePort()
            self.get_logger().info('Puerto DYNAMIXEL cerrado.')

    def destroy_node(self) -> bool:
        self.close()
        return super().destroy_node()


def main(args=None) -> None:
    rclpy.init(args=args)
    node: Optional[PincherController] = None
    try:
        node = PincherController()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as exc:  # noqa: BLE001 - mostrar configuración inválida al usuario
        if node is not None:
            node.get_logger().fatal(f'Error fatal: {exc}')
        else:
            print(f'Error fatal iniciando pincher_control: {exc}')
        raise
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/pincher_gui.py`

```python
#!/usr/bin/env python3
"""Interfaz Tkinter para enviar comandos articulares al PhantomX Pincher."""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import JointState
from std_msgs.msg import String, UInt32
from std_srvs.srv import SetBool, Trigger


JOINT_LIMITS_DEG = {
    'waist': (-150.0, 150.0),
    'shoulder': (-150.0, 150.0),
    'elbow': (-150.0, 150.0),
    'wrist': (-150.0, 150.0),
    'gripper': (-90.0, 90.0),
}


class PincherGuiNode(Node):
    """Nodo ligero usado por la ventana Tkinter."""

    def __init__(self) -> None:
        super().__init__('pincher_gui')
        self.command_publisher = self.create_publisher(JointState, '/pincher/command', 10)
        self.speed_publisher = self.create_publisher(
            UInt32,
            '/pincher/profile_velocity',
            10,
        )
        self.home_client = self.create_client(Trigger, '/pincher/home')
        self.stop_client = self.create_client(Trigger, '/pincher/software_stop')
        self.torque_client = self.create_client(SetBool, '/pincher/torque_enable')
        self.latest_status = 'Esperando al controlador...'
        self.status_subscription = self.create_subscription(
            String,
            '/pincher/status',
            self._status_callback,
            10,
        )

    def _status_callback(self, msg: String) -> None:
        self.latest_status = msg.data

    def publish_joint_command(self, names: List[str], degrees: List[float]) -> None:
        msg = JointState()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.name = names
        msg.position = [math.radians(value) for value in degrees]
        self.command_publisher.publish(msg)

    def publish_speed(self, speed: int) -> None:
        msg = UInt32()
        msg.data = max(0, int(speed))
        self.speed_publisher.publish(msg)


class PincherGui:
    """Ventana principal con sliders, entradas y controles de seguridad."""

    def __init__(self, node: PincherGuiNode) -> None:
        self.node = node
        self.root = tk.Tk()
        self.root.title('PhantomX Pincher X100 - ROS 2 Jazzy')
        self.root.minsize(760, 520)
        self.root.protocol('WM_DELETE_WINDOW', self.close)

        self.joint_names = list(JOINT_LIMITS_DEG)
        self.variables: Dict[str, tk.DoubleVar] = {
            name: tk.DoubleVar(value=0.0) for name in self.joint_names
        }
        self.entries: Dict[str, ttk.Entry] = {}
        self.status_var = tk.StringVar(value=self.node.latest_status)
        self.speed_var = tk.IntVar(value=100)

        self._build_layout()
        self.root.after(20, self._spin_ros)
        self.root.after(200, self._refresh_status)

    def _build_layout(self) -> None:
        style = ttk.Style(self.root)
        style.configure('Title.TLabel', font=('TkDefaultFont', 16, 'bold'))
        style.configure('Danger.TButton', font=('TkDefaultFont', 11, 'bold'))

        header = ttk.Frame(self.root, padding=12)
        header.pack(fill='x')
        ttk.Label(
            header,
            text='Control del PhantomX Pincher X100',
            style='Title.TLabel',
        ).pack(anchor='w')
        ttk.Label(
            header,
            text='Comandos articulares en grados; ROS 2 transmite radianes.',
        ).pack(anchor='w', pady=(4, 0))

        joints_frame = ttk.LabelFrame(self.root, text='Articulaciones', padding=12)
        joints_frame.pack(fill='both', expand=True, padx=12, pady=(0, 8))
        joints_frame.columnconfigure(1, weight=1)

        for row, name in enumerate(self.joint_names):
            lower, upper = JOINT_LIMITS_DEG[name]
            ttk.Label(joints_frame, text=name.capitalize(), width=12).grid(
                row=row,
                column=0,
                sticky='w',
                padx=(0, 8),
                pady=5,
            )
            scale = ttk.Scale(
                joints_frame,
                from_=lower,
                to=upper,
                variable=self.variables[name],
                orient='horizontal',
                command=lambda value, joint=name: self._scale_changed(joint, value),
            )
            scale.grid(row=row, column=1, sticky='ew', pady=5)
            scale.bind('<ButtonRelease-1>', lambda event: self.send_all())

            entry = ttk.Entry(joints_frame, width=10)
            entry.insert(0, '0.0')
            entry.grid(row=row, column=2, padx=(10, 4), pady=5)
            entry.bind('<Return>', lambda event, joint=name: self._entry_committed(joint))
            entry.bind('<FocusOut>', lambda event, joint=name: self._entry_committed(joint))
            self.entries[name] = entry
            ttk.Label(joints_frame, text='°').grid(row=row, column=3, sticky='w')

        controls = ttk.LabelFrame(self.root, text='Control general', padding=12)
        controls.pack(fill='x', padx=12, pady=(0, 8))

        ttk.Label(controls, text='Velocidad/Profile Velocity:').grid(
            row=0,
            column=0,
            sticky='w',
        )
        speed_spin = ttk.Spinbox(
            controls,
            from_=0,
            to=1023,
            textvariable=self.speed_var,
            width=9,
        )
        speed_spin.grid(row=0, column=1, padx=(6, 12))
        ttk.Button(controls, text='Aplicar velocidad', command=self.apply_speed).grid(
            row=0,
            column=2,
            padx=4,
        )
        ttk.Button(controls, text='Enviar posiciones', command=self.send_all).grid(
            row=0,
            column=3,
            padx=4,
        )
        ttk.Button(controls, text='HOME', command=self.call_home).grid(
            row=0,
            column=4,
            padx=4,
        )
        ttk.Button(controls, text='Torque ON', command=lambda: self.call_torque(True)).grid(
            row=1,
            column=0,
            padx=4,
            pady=(10, 0),
        )
        ttk.Button(controls, text='Torque OFF', command=lambda: self.call_torque(False)).grid(
            row=1,
            column=1,
            padx=4,
            pady=(10, 0),
        )
        ttk.Button(
            controls,
            text='PARADA DE SOFTWARE',
            command=self.call_stop,
            style='Danger.TButton',
        ).grid(row=1, column=2, columnspan=3, sticky='ew', padx=4, pady=(10, 0))

        status_frame = ttk.LabelFrame(self.root, text='Estado', padding=10)
        status_frame.pack(fill='x', padx=12, pady=(0, 12))
        ttk.Label(
            status_frame,
            textvariable=self.status_var,
            wraplength=700,
        ).pack(anchor='w')
        ttk.Label(
            status_frame,
            text=(
                'La parada de la GUI no sustituye un circuito físico de emergencia. '
                'Mantén disponible el corte de alimentación.'
            ),
        ).pack(anchor='w', pady=(6, 0))

    def _scale_changed(self, joint: str, value: str) -> None:
        numeric = float(value)
        entry = self.entries[joint]
        entry.delete(0, tk.END)
        entry.insert(0, f'{numeric:.1f}')

    def _entry_committed(self, joint: str) -> None:
        entry = self.entries[joint]
        try:
            value = float(entry.get())
        except ValueError:
            value = self.variables[joint].get()
            messagebox.showwarning('Valor inválido', f'La entrada de {joint} no es numérica.')
        lower, upper = JOINT_LIMITS_DEG[joint]
        value = max(lower, min(upper, value))
        self.variables[joint].set(value)
        entry.delete(0, tk.END)
        entry.insert(0, f'{value:.1f}')

    def send_all(self) -> None:
        for name in self.joint_names:
            self._entry_committed(name)
        values = [self.variables[name].get() for name in self.joint_names]
        self.node.publish_joint_command(self.joint_names, values)
        self.status_var.set('Comando articular publicado en /pincher/command.')

    def apply_speed(self) -> None:
        try:
            speed = int(self.speed_var.get())
        except (ValueError, tk.TclError):
            messagebox.showwarning('Valor inválido', 'La velocidad debe ser un número entero.')
            return
        speed = max(0, min(1023, speed))
        self.speed_var.set(speed)
        self.node.publish_speed(speed)
        self.status_var.set(f'Velocidad {speed} publicada.')

    def _service_available(self, client, name: str) -> bool:
        if client.service_is_ready():
            return True
        self.status_var.set(f'El servicio {name} todavía no está disponible.')
        return False

    def call_home(self) -> None:
        if not self._service_available(self.node.home_client, '/pincher/home'):
            return
        future = self.node.home_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)
        for name in self.joint_names:
            self.variables[name].set(0.0)
            self._scale_changed(name, '0.0')

    def call_stop(self) -> None:
        if not self._service_available(self.node.stop_client, '/pincher/software_stop'):
            return
        future = self.node.stop_client.call_async(Trigger.Request())
        future.add_done_callback(self._service_done)

    def call_torque(self, enabled: bool) -> None:
        if not self._service_available(self.node.torque_client, '/pincher/torque_enable'):
            return
        request = SetBool.Request()
        request.data = enabled
        future = self.node.torque_client.call_async(request)
        future.add_done_callback(self._service_done)

    def _service_done(self, future) -> None:
        try:
            response = future.result()
            self.status_var.set(response.message)
        except Exception as exc:  # noqa: BLE001
            self.status_var.set(f'Error llamando al servicio: {exc}')

    def _spin_ros(self) -> None:
        if rclpy.ok():
            rclpy.spin_once(self.node, timeout_sec=0.0)
            self.root.after(20, self._spin_ros)

    def _refresh_status(self) -> None:
        if self.node.latest_status:
            self.status_var.set(self.node.latest_status)
        if rclpy.ok():
            self.root.after(200, self._refresh_status)

    def run(self) -> None:
        self.root.mainloop()

    def close(self) -> None:
        self.root.destroy()


def main(args=None) -> None:
    rclpy.init(args=args)
    node = PincherGuiNode()
    gui = PincherGui(node)
    try:
        gui.run()
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/pincher_control/scan_dynamixel.py`

```python
#!/usr/bin/env python3
"""Escáner de IDs DYNAMIXEL para protocolo 1.0 o 2.0."""

from __future__ import annotations

from typing import List, Optional

import rclpy
from dynamixel_sdk import COMM_SUCCESS, PacketHandler, PortHandler
from rclpy.node import Node


class DynamixelScanner(Node):
    def __init__(self) -> None:
        super().__init__('dynamixel_scanner')
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 1000000)
        self.declare_parameter('protocol_version', 2.0)
        self.declare_parameter('min_id', 0)
        self.declare_parameter('max_id', 20)

        self.port_name = str(self.get_parameter('port').value)
        self.baudrate = int(self.get_parameter('baudrate').value)
        self.protocol_version = float(self.get_parameter('protocol_version').value)
        self.min_id = max(0, int(self.get_parameter('min_id').value))
        self.max_id = min(252, int(self.get_parameter('max_id').value))

        if self.min_id > self.max_id:
            raise ValueError('min_id no puede ser mayor que max_id.')
        if self.protocol_version not in (1.0, 2.0):
            raise ValueError('protocol_version debe ser 1.0 o 2.0.')

    def scan(self) -> List[int]:
        port = PortHandler(self.port_name)
        packet = PacketHandler(self.protocol_version)
        detected: List[int] = []

        if not port.openPort():
            raise RuntimeError(f'No se pudo abrir {self.port_name}.')
        try:
            if not port.setBaudRate(self.baudrate):
                raise RuntimeError(f'No se pudo configurar baudrate={self.baudrate}.')

            self.get_logger().info(
                f'Escaneando IDs {self.min_id}..{self.max_id} en {self.port_name}, '
                f'{self.baudrate} baud, protocolo {self.protocol_version:.1f}.'
            )
            for dxl_id in range(self.min_id, self.max_id + 1):
                model_number, comm_result, dxl_error = packet.ping(port, dxl_id)
                if comm_result == COMM_SUCCESS and dxl_error == 0:
                    detected.append(dxl_id)
                    self.get_logger().info(
                        f'ID detectado: {dxl_id} | model_number={model_number}'
                    )

            if detected:
                self.get_logger().info(f'IDs encontrados: {detected}')
            else:
                self.get_logger().warning(
                    'No se detectaron motores. Revisa alimentación, puerto, baudrate y protocolo.'
                )
            return detected
        finally:
            port.closePort()


def main(args=None) -> None:
    rclpy.init(args=args)
    node: Optional[DynamixelScanner] = None
    try:
        node = DynamixelScanner()
        node.scan()
    except Exception as exc:  # noqa: BLE001
        if node is not None:
            node.get_logger().error(str(exc))
        else:
            print(f'Error iniciando el escáner: {exc}')
    finally:
        if node is not None:
            node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/config/ax12a.yaml`

```yaml
pincher_controller:
  ros__parameters:
    motor_model: ax12a
    use_hardware: false
    port: /dev/ttyUSB0
    baudrate: 1000000
    dxl_ids: [1, 2, 3, 4, 5]
    joint_names: [waist, shoulder, elbow, wrist, gripper]
    joint_signs: [1.0, -1.0, -1.0, -1.0, 1.0]
    home_positions: [512, 512, 512, 512, 512]
    moving_speed: 100
    torque_limit: 800
    read_rate_hz: 20.0
    home_on_startup: false
    disable_torque_on_shutdown: true
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/config/xl430.yaml`

```yaml
pincher_controller:
  ros__parameters:
    motor_model: xl430
    use_hardware: false
    port: /dev/ttyUSB0
    baudrate: 1000000
    dxl_ids: [1, 2, 3, 4, 5]
    joint_names: [waist, shoulder, elbow, wrist, gripper]
    joint_signs: [1.0, -1.0, -1.0, -1.0, 1.0]
    home_positions: [2048, 2048, 2048, 2048, 2048]
    moving_speed: 100
    torque_limit: -1
    read_rate_hz: 20.0
    home_on_startup: false
    disable_torque_on_shutdown: true
```

#### `ros2_jazzy/phantom_ws/src/pincher_control/launch/pincher_system.launch.py`

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    description_share = get_package_share_directory('pincher_description')
    display_launch = PythonLaunchDescriptionSource(
        os.path.join(description_share, 'launch', 'display.launch.py')
    )

    return LaunchDescription([
        DeclareLaunchArgument('motor_model', default_value='xl430'),
        DeclareLaunchArgument('use_hardware', default_value='false'),
        DeclareLaunchArgument('port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('baudrate', default_value='1000000'),
        DeclareLaunchArgument('read_rate_hz', default_value='20.0'),
        DeclareLaunchArgument('home_on_startup', default_value='false'),
        DeclareLaunchArgument('start_gui', default_value='true'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('use_meshes', default_value='false'),
        IncludeLaunchDescription(
            display_launch,
            launch_arguments={
                'use_meshes': LaunchConfiguration('use_meshes'),
                'start_rviz': LaunchConfiguration('start_rviz'),
                'use_sim_time': 'false',
            }.items(),
        ),
        Node(
            package='pincher_control',
            executable='control_servo',
            name='pincher_controller',
            output='screen',
            parameters=[{
                'motor_model': LaunchConfiguration('motor_model'),
                'use_hardware': ParameterValue(
                    LaunchConfiguration('use_hardware'),
                    value_type=bool,
                ),
                'port': LaunchConfiguration('port'),
                'baudrate': ParameterValue(
                    LaunchConfiguration('baudrate'),
                    value_type=int,
                ),
                'read_rate_hz': ParameterValue(
                    LaunchConfiguration('read_rate_hz'),
                    value_type=float,
                ),
                'home_on_startup': ParameterValue(
                    LaunchConfiguration('home_on_startup'),
                    value_type=bool,
                ),
            }],
        ),
        Node(
            package='pincher_control',
            executable='pincher_gui',
            name='pincher_gui',
            output='screen',
            condition=IfCondition(LaunchConfiguration('start_gui')),
        ),
    ])
```


---

## 11. Código completo de `pincher_description`

`pincher_description` es el paquete `ament_python` creado en la sección 8.3. Reemplaza ahora `package.xml`, `setup.py` y `setup.cfg`, y completa los archivos de `urdf`, `launch` y `rviz` con el contenido presentado a continuación. Aunque un paquete de descripción suele implementarse con `ament_cmake`, esta versión usa `ament_python` porque instala los recursos mediante `setup.py`. No deben mezclarse instrucciones de `ament_cmake` con un `setup.py` de Python.

#### `ros2_jazzy/phantom_ws/src/pincher_description/package.xml`

```xml
<?xml version="1.0"?>
<package format="3">
  <name>pincher_description</name>
  <version>0.1.0</version>
  <description>Modelo Xacro, mallas, configuración de RViz y launch del PhantomX Pincher X100 para ROS 2 Jazzy.</description>
  <maintainer email="pendiente@ejemplo.invalid">Curso de Robótica 2026-I</maintainer>
  <license>BSD-3-Clause</license>

  <exec_depend>ament_index_python</exec_depend>
  <exec_depend>launch</exec_depend>
  <exec_depend>launch_ros</exec_depend>
  <exec_depend>joint_state_publisher</exec_depend>
  <exec_depend>joint_state_publisher_gui</exec_depend>
  <exec_depend>robot_state_publisher</exec_depend>
  <exec_depend>rviz2</exec_depend>
  <exec_depend>xacro</exec_depend>

  <test_depend>ament_copyright</test_depend>
  <test_depend>ament_flake8</test_depend>
  <test_depend>ament_pep257</test_depend>
  <test_depend>python3-pytest</test_depend>

  <export>
    <build_type>ament_python</build_type>
  </export>
</package>
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/setup.py`

```python
from glob import glob
import os

from setuptools import setup

package_name = 'pincher_description'

setup(
    name=package_name,
    version='0.1.0',
    packages=[],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'urdf'), glob('urdf/*')),
        (os.path.join('share', package_name, 'meshes'), glob('meshes/*')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*')),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Curso de Robótica 2026-I',
    maintainer_email='pendiente@ejemplo.invalid',
    description='URDF/Xacro, mallas y visualización RViz del PhantomX Pincher X100.',
    license='BSD-3-Clause',
    tests_require=['pytest'],
    entry_points={'console_scripts': []},
)
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/setup.cfg`

```ini
[develop]
script_dir=$base/lib/pincher_description
[install]
install_scripts=$base/lib/pincher_description
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/resource/pincher_description`

```text

```

#### `ros2_jazzy/phantom_ws/src/pincher_description/urdf/robot.xacro`

```xml
<?xml version="1.0"?>
<robot name="filoberta" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <xacro:arg name="use_meshes" default="true"/>

  <!-- Dimensiones cinemáticas suministradas para el modelo PX100. -->
  <xacro:property name="L1" value="0.0445"/>
  <xacro:property name="L2" value="0.1010"/>
  <xacro:property name="L3" value="0.1010"/>
  <xacro:property name="L4" value="0.1190"/>
  <xacro:property name="Lm" value="0.0315"/>

  <material name="pincher_black">
    <color rgba="0.15 0.15 0.15 1.0"/>
  </material>

  <!-- Cuando no están las mallas, el mismo árbol cinemático se visualiza con cajas. -->
  <xacro:macro name="visual_mesh_or_box" params="mesh mesh_xyz mesh_rpy box_size box_xyz box_rpy">
    <xacro:if value="$(arg use_meshes)">
      <visual>
        <origin xyz="${mesh_xyz}" rpy="${mesh_rpy}"/>
        <geometry>
          <mesh filename="package://pincher_description/meshes/${mesh}" scale="0.001 0.001 0.001"/>
        </geometry>
        <material name="pincher_black"/>
      </visual>
    </xacro:if>
    <xacro:unless value="$(arg use_meshes)">
      <visual>
        <origin xyz="${box_xyz}" rpy="${box_rpy}"/>
        <geometry>
          <box size="${box_size}"/>
        </geometry>
        <material name="pincher_black"/>
      </visual>
    </xacro:unless>
  </xacro:macro>

  <link name="world"/>

  <joint name="joint_world" type="fixed">
    <parent link="world"/>
    <child link="link0"/>
  </joint>

  <link name="link0">
    <xacro:visual_mesh_or_box
      mesh="px100_1_base.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 0.0 ${pi/2}"
      box_size="0.10 0.10 0.045"
      box_xyz="0.0 0.0 0.0225"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="waist" type="revolute">
    <origin xyz="0.0 0.0 ${0.08945-L1}" rpy="0.0 0.0 0.0"/>
    <parent link="link0"/>
    <child link="link1"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-150*pi/180}" upper="${150*pi/180}" effort="4.0" velocity="2.0"/>
  </joint>

  <link name="link1">
    <xacro:visual_mesh_or_box
      mesh="px100_2_shoulder.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 0.0 ${pi/2}"
      box_size="0.065 0.065 0.070"
      box_xyz="0.0 0.0 0.015"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="shoulder" type="revolute">
    <origin xyz="0.0 0.0 ${L1}" rpy="${-pi/2} 0.0 0.0"/>
    <parent link="link1"/>
    <child link="link2"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-150*pi/180}" upper="${150*pi/180}" effort="4.0" velocity="2.0"/>
  </joint>

  <link name="link2">
    <xacro:visual_mesh_or_box
      mesh="px100_3_upper_arm.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="${pi/2} ${-pi/2} 0.0"
      box_size="0.045 ${L2} 0.045"
      box_xyz="${Lm/2} ${-L2/2} 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="elbow" type="revolute">
    <origin xyz="${Lm} ${-L2} 0.0" rpy="0.0 0.0 ${-atan2(L2,Lm)}"/>
    <parent link="link2"/>
    <child link="link3"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-150*pi/180}" upper="${150*pi/180}" effort="4.0" velocity="2.0"/>
  </joint>

  <link name="link3">
    <xacro:visual_mesh_or_box
      mesh="px100_4_forearm.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 ${pi/2} ${pi/2+atan2(L2,Lm)}"
      box_size="${L3} 0.040 0.040"
      box_xyz="${L3/2} 0.0 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="wrist" type="revolute">
    <origin xyz="${L3*cos(atan2(L2,Lm))} ${L3*sin(atan2(L2,Lm))} 0.0" rpy="0.0 0.0 ${atan2(L2,Lm)}"/>
    <parent link="link3"/>
    <child link="link4"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-150*pi/180}" upper="${150*pi/180}" effort="4.0" velocity="2.0"/>
  </joint>

  <link name="link4">
    <xacro:visual_mesh_or_box
      mesh="px100_5_gripper.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 ${-pi/2} ${pi/2}"
      box_size="${L4} 0.055 0.050"
      box_xyz="${L4/2} 0.0 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="joint4" type="fixed">
    <origin xyz="${L4} 0.0 0.0" rpy="${-pi/2} 0.0 ${-pi/2}"/>
    <parent link="link4"/>
    <child link="gripper_bar"/>
  </joint>

  <link name="gripper_bar">
    <xacro:visual_mesh_or_box
      mesh="px100_7_gripper_bar.stl"
      mesh_xyz="0.0 0.0 ${-L4}"
      mesh_rpy="${-pi/2} 0.0 ${-pi/2}"
      box_size="0.075 0.020 0.018"
      box_xyz="0.035 0.0 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="gripper" type="revolute">
    <origin xyz="0.066 0.0 0.0" rpy="0.0 ${pi/2} 0.0"/>
    <parent link="link4"/>
    <child link="prop"/>
    <axis xyz="0.0 0.0 1.0"/>
    <limit lower="${-pi/2}" upper="${pi/2}" effort="2.0" velocity="1.0"/>
  </joint>

  <link name="prop">
    <xacro:visual_mesh_or_box
      mesh="px100_6_gripper_prop.stl"
      mesh_xyz="0.0 0.0 -0.066"
      mesh_rpy="${-pi/2} 0.0 0.0"
      box_size="0.025 0.025 0.050"
      box_xyz="0.0 0.0 -0.025"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="joint6" type="prismatic">
    <origin xyz="0.0 0.0 ${0.08605-L4}" rpy="0.0 ${pi/2} 0.0"/>
    <parent link="gripper_bar"/>
    <child link="finger_1"/>
    <axis xyz="0.0 1.0 0.0"/>
    <limit lower="-0.04" upper="-0.015" effort="2.0" velocity="0.05"/>
    <mimic joint="gripper" multiplier="-0.008" offset="-0.0265"/>
  </joint>

  <link name="finger_1">
    <xacro:visual_mesh_or_box
      mesh="px100_8_gripper_finger.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 0.0 0.0"
      box_size="0.070 0.012 0.015"
      box_xyz="0.035 0.0 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>

  <joint name="joint7" type="prismatic">
    <origin xyz="0.0 0.0 ${0.08605-L4}" rpy="0.0 ${pi/2} ${pi}"/>
    <parent link="gripper_bar"/>
    <child link="finger_2"/>
    <axis xyz="0.0 1.0 0.0"/>
    <limit lower="-0.04" upper="-0.015" effort="2.0" velocity="0.05"/>
    <mimic joint="joint6" multiplier="1.0" offset="0.0"/>
  </joint>

  <link name="finger_2">
    <xacro:visual_mesh_or_box
      mesh="px100_8_gripper_finger.stl"
      mesh_xyz="0.0 0.0 0.0"
      mesh_rpy="0.0 0.0 0.0"
      box_size="0.070 0.012 0.015"
      box_xyz="0.035 0.0 0.0"
      box_rpy="0.0 0.0 0.0"/>
  </link>
</robot>
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/launch/display.launch.py`

```python
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
import xacro


EXPECTED_MESHES = [
    'px100_1_base.stl',
    'px100_2_shoulder.stl',
    'px100_3_upper_arm.stl',
    'px100_4_forearm.stl',
    'px100_5_gripper.stl',
    'px100_6_gripper_prop.stl',
    'px100_7_gripper_bar.stl',
    'px100_8_gripper_finger.stl',
]


def _all_meshes_exist(package_share: str) -> bool:
    mesh_dir = os.path.join(package_share, 'meshes')
    return all(os.path.isfile(os.path.join(mesh_dir, name)) for name in EXPECTED_MESHES)


def _launch_setup(context):
    package_share = get_package_share_directory('pincher_description')
    xacro_file = os.path.join(package_share, 'urdf', 'robot.xacro')
    rviz_config = os.path.join(package_share, 'rviz', 'pincher.rviz')

    use_meshes = LaunchConfiguration('use_meshes').perform(context).lower()
    robot_description = xacro.process_file(
        xacro_file,
        mappings={'use_meshes': use_meshes},
    ).toxml()

    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': ParameterValue(
                    LaunchConfiguration('use_sim_time'),
                    value_type=bool,
                ),
            }],
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            output='screen',
            arguments=['-d', rviz_config],
            condition=IfCondition(LaunchConfiguration('start_rviz')),
        ),
    ]


def generate_launch_description():
    package_share = get_package_share_directory('pincher_description')
    default_meshes = 'true' if _all_meshes_exist(package_share) else 'false'

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value=default_meshes,
            description=(
                'Usa las ocho mallas STL. El valor predeterminado es true solo '
                'cuando todas están instaladas; de lo contrario usa cajas.'
            ),
        ),
        DeclareLaunchArgument(
            'start_rviz',
            default_value='true',
            description='Inicia RViz2.',
        ),
        DeclareLaunchArgument(
            'use_sim_time',
            default_value='false',
            description='Usa el reloj de simulación.',
        ),
        OpaqueFunction(function=_launch_setup),
    ])
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/launch/display_gui.launch.py`

```python
#!/usr/bin/env python3

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import (
    Command,
    FindExecutable,
    LaunchConfiguration,
    PathJoinSubstitution,
)
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ---------------------------------------------------------
    # Argumentos del launch
    # ---------------------------------------------------------
    use_meshes = LaunchConfiguration('use_meshes')

    # ---------------------------------------------------------
    # Rutas del paquete
    # ---------------------------------------------------------
    package_share = FindPackageShare('pincher_description')

    xacro_file = PathJoinSubstitution([
        package_share,
        'urdf',
        'robot.xacro',
    ])

    rviz_config_file = PathJoinSubstitution([
        package_share,
        'rviz',
        'pincher.rviz',
    ])

    # ---------------------------------------------------------
    # Procesar Xacro
    # ---------------------------------------------------------
    robot_description_content = Command([
        FindExecutable(name='xacro'),
        ' ',
        xacro_file,
        ' ',
        'use_meshes:=',
        use_meshes,
    ])

    robot_description = {
        'robot_description': robot_description_content
    }

    # ---------------------------------------------------------
    # robot_state_publisher
    # Recibe /joint_states y publica /tf y /tf_static
    # ---------------------------------------------------------
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[
            robot_description,
            {
                'publish_frequency': 30.0,
                'ignore_timestamp': False,
            },
        ],
    )

    # ---------------------------------------------------------
    # joint_state_publisher_gui
    # Publica /joint_states para las articulaciones móviles
    # ---------------------------------------------------------
    joint_state_publisher_gui_node = Node(
        package='joint_state_publisher_gui',
        executable='joint_state_publisher_gui',
        name='joint_state_publisher_gui',
        output='screen',
        parameters=[
            robot_description,
            {
                'rate': 30,
                'publish_default_positions': True,
                'publish_default_velocities': False,
                'publish_default_efforts': False,
                'use_mimic_tags': True,
            },
        ],
    )

    # ---------------------------------------------------------
    # RViz2
    # ---------------------------------------------------------
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d',
            rviz_config_file,
        ],
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_meshes',
            default_value='true',
            description='Mostrar las mallas STL del robot.',
        ),

        robot_state_publisher_node,
        joint_state_publisher_gui_node,
        rviz_node,
    ])
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/rviz/pincher.rviz`

```yaml
Panels:
  - Class: rviz_common/Displays
    Help Height: 78
    Name: Displays
    Property Tree Widget:
      Expanded:
        - /Global Options1
        - /RobotModel1
      Splitter Ratio: 0.5
    Tree Height: 480
  - Class: rviz_common/Views
    Expanded:
      - /Current View1
    Name: Views
    Splitter Ratio: 0.5
Visualization Manager:
  Class: ""
  Displays:
    - Alpha: 0.5
      Cell Size: 0.05
      Class: rviz_default_plugins/Grid
      Color: 160; 160; 164
      Enabled: true
      Line Style:
        Line Width: 0.03
        Value: Lines
      Name: Grid
      Normal Cell Count: 0
      Offset:
        X: 0
        Y: 0
        Z: 0
      Plane: XY
      Plane Cell Count: 20
      Reference Frame: world
      Value: true
    - Class: rviz_default_plugins/RobotModel
      Collision Enabled: false
      Description Source: Topic
      Description Topic:
        Depth: 5
        Durability Policy: Transient Local
        History Policy: Keep Last
        Reliability Policy: Reliable
        Value: /robot_description
      Enabled: true
      Links:
        All Links Enabled: true
        Expand Joint Details: false
        Expand Link Details: false
        Expand Tree: false
        Link Tree Style: Links in Alphabetic Order
      Mass Properties:
        Inertia: false
        Mass: false
      Name: RobotModel
      TF Prefix: ""
      Update Interval: 0
      Value: true
      Visual Enabled: true
    - Class: rviz_default_plugins/TF
      Enabled: true
      Frame Timeout: 15
      Frames:
        All Enabled: true
      Marker Scale: 0.08
      Name: TF
      Show Arrows: true
      Show Axes: true
      Show Names: false
      Tree:
        {}
      Update Interval: 0
      Value: true
  Enabled: true
  Global Options:
    Background Color: 48; 48; 48
    Fixed Frame: world
    Frame Rate: 30
  Name: root
  Tools:
    - Class: rviz_default_plugins/Interact
      Hide Inactive Objects: true
    - Class: rviz_default_plugins/MoveCamera
    - Class: rviz_default_plugins/Select
    - Class: rviz_default_plugins/FocusCamera
    - Class: rviz_default_plugins/Measure
      Line color: 128; 128; 0
  Transformation:
    Current:
      Class: rviz_default_plugins/TF
  Value: true
  Views:
    Current:
      Class: rviz_default_plugins/Orbit
      Distance: 0.65
      Enable Stereo Rendering:
        Stereo Eye Separation: 0.06
        Stereo Focal Distance: 1
        Swap Stereo Eyes: false
        Value: false
      Focal Point:
        X: 0.08
        Y: 0.0
        Z: 0.13
      Focal Shape Fixed Size: true
      Focal Shape Size: 0.05
      Invert Z Axis: false
      Name: Current View
      Near Clip Distance: 0.01
      Pitch: 0.55
      Target Frame: world
      Value: Orbit (rviz)
      Yaw: 0.78
    Saved: ~
Window Geometry:
  Displays:
    collapsed: false
  Height: 800
  Hide Left Dock: false
  Hide Right Dock: false
  QMainWindow State: 000000ff00000000fd000000010000000000000156000002c4fc0200000002fb000000100044006900730070006c006100790073010000003d000001d6000000c900fffffffb0000000a005600690065007700730100000219000000e8000000a400ffffff00000280000002c400000004000000040000000800000008fc00000000
  Views:
    collapsed: false
  Width: 1200
  X: 100
  Y: 100
```

#### `ros2_jazzy/phantom_ws/src/pincher_description/meshes/README.md`

```markdown
# Mallas del PhantomX Pincher X100

Descarga o copia los archivos de la carpeta `meshes` anexa al repositorio y ubícalos en esta carpeta. Deben conservar exactamente estos nombres:

- `px100_1_base.stl`
- `px100_2_shoulder.stl`
- `px100_3_upper_arm.stl`
- `px100_4_forearm.stl`
- `px100_5_gripper.stl`
- `px100_6_gripper_prop.stl`
- `px100_7_gripper_bar.stl`
- `px100_8_gripper_finger.stl`

Después de copiar las mallas, recompila el workspace para que los archivos también se instalen en el directorio `install/`.

El paquete puede iniciarse temporalmente con `use_meshes:=false` para validar TF, articulaciones y `/joint_states` mediante geometría simplificada.
```


---

## 12. Descarga y ubicación de las mallas STL

Descarga o copia los ocho archivos de la carpeta `meshes` anexa al repositorio y ubícalos en:

```text
~/ros2_jazzy/phantom_ws/src/pincher_description/meshes/
```

Los nombres deben ser exactamente:

```text
px100_1_base.stl
px100_2_shoulder.stl
px100_3_upper_arm.stl
px100_4_forearm.stl
px100_5_gripper.stl
px100_6_gripper_prop.stl
px100_7_gripper_bar.stl
px100_8_gripper_finger.stl
```

Verifica que los ocho archivos estén presentes:

```bash
find ~/ros2_jazzy/phantom_ws/src/pincher_description/meshes \
  -maxdepth 1 -type f -name '*.stl' -printf '%f
' | sort
```

Después de copiar las mallas, recompila el workspace. Para visualizar el modelo detallado utiliza:

```bash
use_meshes:=true
```

Mientras las mallas no estén disponibles, se puede validar el árbol cinemático con:

```bash
use_meshes:=false
```

---

## 13. Compilación del workspace


```bash
cd ~/ros2_jazzy/phantom_ws
source /opt/ros/jazzy/setup.bash
rosdep update
rosdep install -y -r -i \
  --from-paths src \
  --rosdistro jazzy
colcon build --symlink-install
source install/setup.bash
```

Añadir al `~/.bashrc` es opcional:

```bash
echo 'source /opt/ros/jazzy/setup.bash' >> ~/.bashrc
echo 'source ~/ros2_jazzy/phantom_ws/install/setup.bash' >> ~/.bashrc
source ~/.bashrc
```

Comprueba los paquetes:

```bash
ros2 pkg prefix pincher_control
ros2 pkg prefix pincher_description
```

---

## 14. Práctica 1: modelo del robot sin controlador

Esta práctica utiliza `joint_state_publisher_gui`; no ejecuta el controlador DYNAMIXEL.

Sin STL:

```bash
source ~/ros2_jazzy/phantom_ws/install/setup.bash
ros2 launch pincher_description display_gui.launch.py use_meshes:=false
```

Con STL:

```bash
ros2 launch pincher_description display_gui.launch.py use_meshes:=true
```

Mueve los sliders del `joint_state_publisher_gui` y comprueba que RViz actualiza las articulaciones.

> No ejecutes `joint_state_publisher_gui` al mismo tiempo que `pincher_controller`, porque ambos publicarían `/joint_states`.

---

## 15. Práctica 2: sistema completo sin hardware

Perfil XL430:

```bash
source ~/ros2_jazzy/phantom_ws/install/setup.bash
ros2 launch pincher_control pincher_system.launch.py \
  motor_model:=xl430 \
  use_hardware:=false \
  use_meshes:=false
```

Perfil AX-12A:

```bash
ros2 launch pincher_control pincher_system.launch.py \
  motor_model:=ax12a \
  use_hardware:=false \
  use_meshes:=false
```

Debe abrirse:

- `pincher_controller`;
- la GUI Tkinter;
- `robot_state_publisher`;
- RViz2.

Al mover un slider y soltarlo, la GUI publica el comando, el controlador actualiza `/joint_states` y RViz mueve el modelo.

---

## 16. Detección del puerto e IDs Dynamixel

### 16.1 AX-12A, protocolo 1.0

```bash
ros2 run pincher_control scan_dynamixel --ros-args \
  -p port:=/dev/ttyUSB0 \
  -p baudrate:=1000000 \
  -p protocol_version:=1.0 \
  -p min_id:=0 \
  -p max_id:=20
```

### 16.2 XL430, protocolo 2.0

```bash
ros2 run pincher_control scan_dynamixel --ros-args \
  -p port:=/dev/ttyUSB0 \
  -p baudrate:=1000000 \
  -p protocol_version:=2.0 \
  -p min_id:=0 \
  -p max_id:=20
```

El escáner solamente ejecuta `ping`; no habilita torque ni mueve los motores.

---

## 17. Práctica 3: conexión con AX-12A

Antes de energizar:

1. verifica cinco IDs únicos;
2. revisa `config/ax12a.yaml`;
3. valida `home_positions` y `joint_signs`;
4. deja `home_on_startup: false` durante las primeras pruebas.

Ejecución básica:

```bash
ros2 launch pincher_control pincher_system.launch.py \
  motor_model:=ax12a \
  use_hardware:=true \
  port:=/dev/ttyUSB0 \
  baudrate:=1000000 \
  use_meshes:=true
```

Para ejecutar solamente el controlador con el archivo YAML:

```bash
ros2 run pincher_control control_servo --ros-args \
  --params-file ~/ros2_jazzy/phantom_ws/src/pincher_control/config/ax12a.yaml \
  -p use_hardware:=true
```

En otra terminal se puede iniciar la descripción sin `joint_state_publisher_gui`:

```bash
ros2 launch pincher_description display.launch.py use_meshes:=true
```

---

## 18. Práctica 4: conexión con XL430

Revisa que los motores estén en modo posición y que todos utilicen protocolo 2.0.

```bash
ros2 launch pincher_control pincher_system.launch.py \
  motor_model:=xl430 \
  use_hardware:=true \
  port:=/dev/ttyUSB0 \
  baudrate:=1000000 \
  use_meshes:=true
```

Con YAML:

```bash
ros2 run pincher_control control_servo --ros-args \
  --params-file ~/ros2_jazzy/phantom_ws/src/pincher_control/config/xl430.yaml \
  -p use_hardware:=true
```

El parámetro `torque_limit` se deja en `-1` para XL430, porque la familia X no utiliza el registro 34 del AX-12A.

---

## 19. Uso de la interfaz gráfica

La GUI contiene:

- sliders para `waist`, `shoulder`, `elbow`, `wrist` y `gripper`;
- entradas numéricas en grados;
- botón **Enviar posiciones**;
- control de velocidad;
- botón **HOME**;
- botones **Torque ON** y **Torque OFF**;
- botón **PARADA DE SOFTWARE**;
- panel de estado.

La GUI publica:

```text
/pincher/command
/pincher/profile_velocity
```

Y utiliza:

```text
/pincher/home
/pincher/torque_enable
/pincher/software_stop
```

Después de una parada de software, utiliza **Torque ON** antes de enviar un nuevo movimiento. HOME no reactiva el torque automáticamente.

---

## 20. Verificación mediante ROS 2 CLI

### 20.1 Nodos

```bash
ros2 node list
```

### 20.2 Tópicos

```bash
ros2 topic list
ros2 topic info /joint_states -v
ros2 topic echo /joint_states --once
ros2 topic hz /joint_states
```

### 20.3 TF

```bash
ros2 topic hz /tf
ros2 run tf2_tools view_frames
```

### 20.4 Servicios

```bash
ros2 service list | grep pincher
```

Activar torque:

```bash
ros2 service call /pincher/torque_enable std_srvs/srv/SetBool "{data: true}"
```

Enviar HOME:

```bash
ros2 service call /pincher/home std_srvs/srv/Trigger "{}"
```

Parada de software:

```bash
ros2 service call /pincher/software_stop std_srvs/srv/Trigger "{}"
```

### 20.5 Publicar un comando sin GUI

```bash
ros2 topic pub --once /pincher/command sensor_msgs/msg/JointState "{
  name: ['waist', 'shoulder', 'elbow', 'wrist', 'gripper'],
  position: [0.0, 0.2, -0.3, 0.1, 0.0]
}"
```

---

## 21. Validación del Xacro y de las mallas

### 21.1 Generar URDF sin mallas

```bash
xacro ~/ros2_jazzy/phantom_ws/src/pincher_description/urdf/robot.xacro \
  use_meshes:=false > /tmp/pincher.urdf
```

### 21.2 Comprobar el árbol

```bash
check_urdf /tmp/pincher.urdf
```

### 21.3 Generar URDF con mallas

```bash
xacro ~/ros2_jazzy/phantom_ws/src/pincher_description/urdf/robot.xacro \
  use_meshes:=true > /tmp/pincher_meshes.urdf
```

### 21.4 Verificar archivos instalados

```bash
PKG_SHARE=$(ros2 pkg prefix pincher_description)/share/pincher_description
find "$PKG_SHARE/meshes" -maxdepth 1 -name '*.stl' -printf '%f\n' | sort
```

### 21.5 Revisar `/robot_description`

```bash
ros2 topic echo /robot_description --once
```

---

## 22. Solución de problemas

### 22.1 `No se pudo abrir el puerto`

```bash
ls -l /dev/ttyUSB0
groups
```

Añade el usuario a `dialout` y vuelve a iniciar sesión.

### 22.2 No se detectan IDs

Revisa:

- alimentación de los motores;
- puerto correcto;
- baudrate;
- protocolo 1.0 o 2.0;
- continuidad del bus;
- IDs dentro del rango escaneado.

### 22.3 RViz muestra el árbol, pero no las mallas

Comprueba que las ocho STL de la carpeta `meshes` anexa al repositorio hayan sido copiadas tanto en el paquete fuente como en el paquete instalado:

```bash
find ~/ros2_jazzy/phantom_ws/src/pincher_description/meshes \
  -maxdepth 1 -type f -name '*.stl' -printf '%f\n' | sort

cd ~/ros2_jazzy/phantom_ws
colcon build --symlink-install
source install/setup.bash
```

Después inicia con `use_meshes:=true`.

### 22.4 RViz muestra cajas en vez del robot detallado

Eso significa que se inició con `use_meshes:=false`. Es un modo válido para comprobar cinemática y TF.

### 22.5 El modelo no se mueve

```bash
ros2 topic hz /joint_states
ros2 topic echo /pincher/command --once
```

No ejecutes dos publicadores diferentes de `/joint_states` al mismo tiempo.

### 22.6 El robot físico se mueve en sentido contrario

Detén el sistema y corrige `joint_signs`. Cambia solamente una articulación por vez y prueba a baja velocidad.

### 22.7 HOME no funciona después de la parada

Es intencional. La parada deshabilita torque y HOME no lo reactiva automáticamente. Ejecuta:

```bash
ros2 service call /pincher/torque_enable std_srvs/srv/SetBool "{data: true}"
ros2 service call /pincher/home std_srvs/srv/Trigger "{}"
```

### 22.8 Se mezclaron instrucciones `ament_cmake` y `setup.py`

Este `pincher_description` es `ament_python`. Si se desea convertir a `ament_cmake`, debe crearse un `CMakeLists.txt` y cambiar el `<build_type>`; no se deben mantener ambos esquemas parcialmente.

### 22.9 `rosdep` intenta resolver Humble

Usa:

```bash
rosdep install -y -r -i --from-paths src --rosdistro jazzy
```

---

## 23. Actividad propuesta para estudiantes

### Objetivo

Validar el modelo cinemático y controlar el brazo primero sin hardware y después con un único motor verificado.

### Entregables

1. Captura de RViz con `RobotModel` y TF.
2. Captura de la GUI enviando una configuración articular.
3. Salida de `ros2 topic echo /joint_states --once`.
4. Resultado del escaneo de IDs.
5. Tabla con:
   - ID;
   - nombre de articulación;
   - signo;
   - posición HOME;
   - modelo de motor.
6. Respuesta corta:
   - ¿por qué AX-12A y XL430 no comparten las mismas direcciones?
   - ¿qué diferencia existe entre `Goal Position` y `Present Position`?
   - ¿por qué no debe publicarse `/joint_states` desde dos nodos simultáneamente?
   - ¿por qué una parada de software no reemplaza una parada física?

### Reto adicional

Añadir un botón de secuencia que envíe tres configuraciones predefinidas sin exceder los límites articulares y que pueda cancelarse con la parada de software.

---

## 24. Publicación en GitHub

Antes de publicar:

1. reemplaza `pendiente@ejemplo.invalid` por el correo definido por los responsables;
2. verifica que las ocho mallas STL estén incluidas en `pincher_description/meshes`;
3. valida el modo sin hardware;
4. revisa que no existan `build/`, `install/` ni `log/` en el commit.

```bash
cd ~/PhantomX_Pincher_X100_ROS2_Jazzy
git init
git add .
git commit -m "Guía PhantomX Pincher X100 para ROS 2 Jazzy"
git branch -M main
git remote add origin <URL_DEL_REPOSITORIO>
git push -u origin main
```

No se incluye una URL inventada: reemplaza `<URL_DEL_REPOSITORIO>` por la dirección real cuando el repositorio haya sido creado.

---

## 25. Cambios respecto a una implementación Humble

| Elemento | Implementación antigua o inconsistente | Esta versión Jazzy |
|---|---|---|
| Distribución | `--rosdistro humble` | `--rosdistro jazzy` |
| Ubuntu | 22.04 | 24.04 |
| Python | 3.10 | 3.12 |
| Ruta del workspace | rutas mezcladas | una única ruta documentada |
| Paquete descripción | se indicaba `ament_cmake` pero se entregaba `setup.py` | `ament_python` consistente |
| Estado articular | no se publicaba realmente en el código básico | publicación periódica de `/joint_states` |
| GUI | no integrada | nodo Tkinter separado |
| Sin hardware | no disponible | modo completo `use_hardware:=false` |
| HOME al arrancar | movimiento automático | desactivado por defecto |
| Fallo parcial | podía dejar torque habilitado | recuperación y cierre del puerto |
| XL430 torque | dirección tratada como Torque Limit | no se escribe un registro no equivalente |
| Mallas ausentes | RViz fallaba | geometría simplificada opcional |
| Escaneo de IDs | no incluido | herramienta `scan_dynamixel` |

---

## 26. Bibliografía

[1] ROBOTIS, “AX-12A,” DYNAMIXEL e-Manual. Disponible: https://emanual.robotis.com/docs/en/dxl/ax/ax-12a/

[2] ROBOTIS, “XL430-W250-T,” DYNAMIXEL e-Manual. Disponible: https://emanual.robotis.com/docs/en/dxl/x/xl430-w250/

[3] ROBOTIS, “DYNAMIXEL SDK,” e-Manual. Disponible: https://emanual.robotis.com/docs/en/software/dynamixel/dynamixel_sdk/overview/

[4] Open Robotics, “robot_state_publisher,” ROS 2 Jazzy Documentation. Disponible: https://docs.ros.org/en/ros2_packages/jazzy/api/robot_state_publisher/

[5] Open Robotics, “joint_state_publisher,” ROS 2 Jazzy Documentation. Disponible: https://docs.ros.org/en/jazzy/p/joint_state_publisher/

[6] Open Robotics, “xacro,” ROS 2 Jazzy Documentation. Disponible: https://docs.ros.org/en/jazzy/p/xacro/

[7] snt-spacer, “phantomx_pincher,” GitHub. Disponible: https://github.com/snt-spacer/phantomx_pincher

</div>
