<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h3>Curso de Robótica 2026-I</h3>

<h1>Informe Laboratorio #5</h1>

<h2>Profesores: <br>Pedro Fabián Cárdenas Herrera <br> Manuel Felipe Carranza Montenegro<br></h2>

</div>

# Integrantes
1. Juan Andrés Moreno Benavides [jumorenobe@unal.edu.co](Jumorenobe)
2. Mateo Ramos Cujer [mramoscu@unal.edu.co](MateoKGR)


# Índice

1. [Descripción detallada de la solución planteada](#Descripción-detallada-de-la-solución-planteada)
2. [Diagrama de flujo de las acciones del robot](#Diagrama-de-flujo-de-las-acciones-del-robot)
3. [Código fuente](#Código-fuente)
4. [Plano de planta](#Plano-de-planta)
5. [Diagramas digitales y DH utilizado](#Diagramas-digitales-y-DH-utilizado)
6. [Calibración](#Calibración)
7. [Gráficas de interpolación y trayectoria sinusoidal](#Gráficas-de-interpolación-y-trayectoria-sinusoidal)
8. [Videos](#videos)
9. [Conclusiones](#Conclusiones)


## Descripción detallada de la solución planteada
Se desarrolló un nodo de ROS 2 en Python que permite:

Comunicación directa con los motores Dynamixel mediante puerto serial.
Control individual y conjunto de cada articulación del manipulador.
Publicación del mensaje `/joint_states` para animación del modelo en RViz.
Implementación de una interfaz gráfica con control articular, visualización en RViz y aplicación de los diferentes modos pedidos en el laboratorio.

La arquitectura del sistema integra tres componentes principales:
1. Nodo ROS 2 de control de motores.
2. Interfaz gráfica (GUI) en Tkinter.
3. Modelo del robot visualizado en RViz.

### Funciones utilizadas

Se presentan a continuación las funciones utilizadas en la interfaz gráfica tanto en todos los modos como en modos específicos

---
### Todos los modos

* **Movimiento Simultáneo:** Todas las articulaciones se mueven simultáneamente a la posición enviada.
* **Movimiento Secuencial:** Todas las articulaciones se mueven en orden a la posición enviada (Base-Hombro-Codo-Muñeca-Pinza).
* **Velocidad Por Ingreso Numérico:** Permite ingresar directamente valores de velocidad para todos los motores y enviarlas al sistema.
* **Home:** Manda al robot a Home.
* **Torque On / Torque Off:** Energiza y desenergiza los motores.
* **Parada De Software:** Desenergiza el sistema de inmediato por software (Recomendable no confiarse totalmente y tener la mano cerca al botón de energía de la multitoma).
* **Estado:** Muestra el estado del robot y qué instrucción se encuentra realizando.
* **Visualización en RViz:** Se sincroniza el robot físico con el modelo virtual del PhantomX Pincher X100 usando `robot_state_publisher`.

---

### Modo Manual

* **Control articular por ingreso numérico:** Permite ingresar directamente valores de posición para cada articulación en un rango seguro y enviarlas al sistema.

---
### Modo Presets 

**Se presenta el envío por botones de diferentes poses predefinidas al robot presentadas en el laboratorio**

<div align="center">

| Articulación | Pose 1 | Pose 2 | Pose 3 | Pose 4 | Pose 5 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 00 | 25 | -35 | 85 | 80 |
| 2 | 00 | 25 | 35 | -20 | -35 |
| 3 | 00 | 20 | -30 | 55 | 55 |
| 4 | 00 | -20 | 30 | 25 | -45 |
| 5 | 00 | 00 | 00 | 00 | 00 |

</div>

<h4>Los primeros cuatro valores corresponden al brazo y el quinto corresponde a la pinza. </h4>

---
### Modo Trayectoria

**Genera una trayectoria entre dos configuraciones alejadas y compara la suavidad de la interpolación lineal frente a la cúbica / quíntica**

* **Pose Inicial:** Ingresar directamente de qué posición ya preestablecida o actual va a iniciar el robot.
* **Pose Final:** Ingresar directamente a cuál posición ya preestablecida va a ir el robot.
* **Articulación a graficar:** Seleccionar cuál recorrido de las 5 articulaciones se va a graficar.
* **Duración:** Duración en segundos de la gráfica.
* **Muestras:** Cuántas muestras se van a tomar para la interpolación.
* **Interpolación:** Seleccionar el tipo de interpolación (Lineal,Cúbica,Quíntica).
* **Enviar Trayectoria:** Envía la trayectoria que se le indicó al robot.
* **Graficar Trayectoria:** Gráfica la trayectoria en posición angular vs tiempo con su respectiva interpolación lineal vs cúbica/quíntica.
* **Gráfica Trayectoria:** Muestra la gráfica.

---
### Modo Senoidal

**Selecciona una articulación y le da los parámetros con  $q(t) = q_0 + A \sin(2\pi f t)$**


* **Articulación:** Ingresar a cuál articulación se le va a aplicar la función.
* **Q0:**  Ingresar numéricamente el centro de la función.
* **Amplitud A1/A2:** Ingresar numéricamente las amplitudes de las funciones.
* **Frecuencia F1/F2:** Ingresar numéricamente las frecuencias de las funciones.
* **Articulación a graficar:** Seleccionar cuál recorrido de las 5 articulaciones se va a graficar.
* **Duración:** Duración en segundos de la gráfica.
* **Ejecutar:** Ejecuta las 4 pruebas.
* **Ver Prueba:** Ve la prueba seleccionada.
* **Error:** Muestra un error si este se ha presentado.
* **Posición enviada vs Posición medida:** Gráfica de la operación.

---
### Modo Enseñanza

**Registra poses con su respectivo nombre de acuerdo a la posición del robot en el espacio gracias al modo manual, guarda el registro de las poses y sus parámetros en un yaml , las reproduce en orden con el tiempo de transición que se desea al igual que reproducir la que el usuario quiera**


* **Nombre de la pose:** Ingresar por teclado el nombre de la pose actual.
* **Guardar:** Guarda la pose actual con su respectivo nombre.
* **Poses Registradas:** Lista de poses en orden de creación con sus parámetros.
* **Ir a la Pose seleccionada:** Envía la pose seleccionada al robot.
* **Eliminar Pose seleccionada:**  Elimina la pose seleccionada de la lista.
* **Guardar yaml:** Guarda el archivo yaml en /home/juan-moreno/pincher_taught_poses.yaml.
* **Recargar yaml:** Elimina variables nuevas y va al último archivo yaml creado.
* **Tiempo de transición :** Tiempo en segundos entre poses cuando se reproduzcan en orden.
* **Reproducir Todas:** Reproduce las poses de la lista en el tiempo preestablecido.
* **Detener:** Detiene la reproducción de las poses.

---

### Modo Triángulo

**Ejecuta una secuencia de poses para el desarrollo de un Triángulo previamente encontradas gracias a cinemática inversa (Tres vértices) e interpolación lineal, se utilizan 60 muestras totalmente editables para quitar o agregar más en la constante Triangle_Poses**


* **Secuencia:** Lista de poses de Triangle_Poses con sus respectivos parámetros.
* **Ejecutar:** Ejecuta la secuencia de Triángulo.
* **Detener:** Detiene la secuencia de Triángulo.

---

### Modo Baile

**Ejecuta una coreografía de poses definidas, cada pose tiene su propio retardo y reproduce automáticamente la canción "Chipi chipi" al inicio de la coreografía**


* **Coreografía:** Lista de poses de la coreografía con sus respectivos parámetros.
* **Ejecutar:** Ejecuta la coreografía y la música.
* **Detener:** Detiene la coreografía y la música.

---

## Diagrama de flujo de las acciones del robot

El siguiente diagrama detalla la interacción exhaustiva entre la interfaz gráfica de usuario (`PincherGui`), el nodo de ROS 2 (`PincherGuiNode`) y el controlador de hardware.


```md
```mermaid
flowchart TD
    Inicio["Inicio del sistema (main)"]
    Inicializar_ROS["Inicializar ROS 2 (rclpy.init)"]
    Crear_Nodo["Crear PincherGuiNode (Pubs, Subs, Clients)"]
    Crear_GUI["Crear Interfaz PincherGui (Tkinter Notebook)"]
    Bucle_Eventos["Bucle de eventos (mainloop + _spin_ros)"]

    %% Categorías Principales
    Controles_Generales["Controles Generales"]
    Modos_Operacion["Modos de Operación (Pestañas)"]

    %% Modos de la GUI (Notebook Tabs)
    Modo_Manual["1. Manual"]
    Modo_Presets["2. Presets"]
    Modo_Ensenanza["3. Modo Enseñanza"]
    Modo_Triángulo["4. Triángulo"]
    Modo_Baile["5. Baile"]
    Modo_Trayectorias["6. Trayectorias"]
    Modo_Senoidal["7. Senoidal"]

    %% Acciones específicas de cada modo
    Accion_Manual["Leer entradas de usuario (grados)"]
    Accion_Presets["Cargar diccionario PRESETS"]
    Accion_Ensenanza["Cargar/Guardar en YAML y reproducir poses"]
    Accion_Triángulo["Ejecutar secuencia TRIANGLE_POSES"]
    Accion_Baile["Ejecutar DANCE_POSES y reproducir audio"]
    Accion_Trayectorias["Interpolar (Lineal, Cúbica, Quíntica)"]
    Accion_Senoidal["Generar q(t) = q0 + A·sin(2πf·t)"]

    %% Despacho de comandos
    Dispatch["Función _dispatch()"]
    Selector_Modo{"Modo de envío seleccionado"}
    Envio_Simultaneo["Envío Simultáneo"]
    Envio_Secuencial["Envío Secuencial (Base -> Pinza)"]
    Publicar_Comando["Publicar en /pincher/command"]

    %% Servicios
    Llamar_Servicios["Llamar servicios (/home, /torque_enable, /software_stop, /profile_velocity)"]

    %% Conexiones iniciales
    Inicio --> Inicializar_ROS
    Inicializar_ROS --> Crear_Nodo
    Crear_Nodo --> Crear_GUI
    Crear_GUI --> Bucle_Eventos

    %% Bifurcación de la interfaz
    Bucle_Eventos --> Controles_Generales
    Bucle_Eventos --> Modos_Operacion

    %% Controles Generales
    Controles_Generales --> Llamar_Servicios

    %% Pestañas
    Modos_Operacion --> Modo_Manual
    Modos_Operacion --> Modo_Presets
    Modos_Operacion --> Modo_Ensenanza
    Modos_Operacion --> Modo_Triángulo
    Modos_Operacion --> Modo_Baile
    Modos_Operacion --> Modo_Trayectorias
    Modos_Operacion --> Modo_Senoidal

    %% Flujo de las pestañas hacia sus acciones
    Modo_Manual --> Accion_Manual
    Modo_Presets --> Accion_Presets
    Modo_Ensenanza --> Accion_Ensenanza
    Modo_Triángulo --> Accion_Triángulo
    Modo_Baile --> Accion_Baile
    Modo_Trayectorias --> Accion_Trayectorias
    Modo_Senoidal --> Accion_Senoidal

    %% Los modos discretos usan la función _dispatch
    Accion_Manual --> Dispatch
    Accion_Presets --> Dispatch
    Accion_Ensenanza --> Dispatch
    Accion_Triángulo --> Dispatch
    Accion_Baile --> Dispatch

    Dispatch --> Selector_Modo
    Selector_Modo -->|Simultáneo| Envio_Simultaneo
    Selector_Modo -->|Secuencial| Envio_Secuencial
    Envio_Simultaneo --> Publicar_Comando
    Envio_Secuencial --> Publicar_Comando

    %% Los modos continuos/calculados publican directamente saltándose el _dispatch
    Accion_Trayectorias -->|Paso a paso iterativo| Publicar_Comando
    Accion_Senoidal -->|Paso a paso iterativo| Publicar_Comando
```
```mermaid
flowchart TD
    Inicio["Inicio del sistema (main)"]
    Inicializar_ROS["Inicializar ROS 2 (rclpy.init)"]
    Crear_Nodo["Crear PincherGuiNode (Pubs, Subs, Clients)"]
    Crear_GUI["Crear Interfaz PincherGui (Tkinter Notebook)"]
    Bucle_Eventos["Bucle de eventos (mainloop + _spin_ros)"]

    %% Categorías Principales
    Controles_Generales["Controles Generales"]
    Modos_Operacion["Modos de Operación (Pestañas)"]

    %% Modos de la GUI (Notebook Tabs)
    Modo_Manual["1. Manual"]
    Modo_Presets["2. Presets"]
    Modo_Ensenanza["3. Modo Enseñanza"]
    Modo_Triángulo["4. Triángulo"]
    Modo_Baile["5. Baile"]
    Modo_Trayectorias["6. Trayectorias"]
    Modo_Senoidal["7. Senoidal"]

    %% Acciones específicas de cada modo
    Accion_Manual["Leer entradas de usuario (grados)"]
    Accion_Presets["Cargar diccionario PRESETS"]
    Accion_Ensenanza["Cargar/Guardar en YAML y reproducir poses"]
    Accion_Triángulo["Ejecutar secuencia TRIANGLE_POSES"]
    Accion_Baile["Ejecutar DANCE_POSES y reproducir audio"]
    Accion_Trayectorias["Interpolar (Lineal, Cúbica, Quíntica)"]
    Accion_Senoidal["Generar q(t) = q0 + A·sin(2πf·t)"]

    %% Despacho de comandos
    Dispatch["Función _dispatch()"]
    Selector_Modo{"Modo de envío seleccionado"}
    Envio_Simultaneo["Envío Simultáneo"]
    Envio_Secuencial["Envío Secuencial (Base -> Pinza)"]
    Publicar_Comando["Publicar en /pincher/command"]

    %% Servicios
    Llamar_Servicios["Llamar servicios (/home, /torque_enable, /software_stop, /profile_velocity)"]

    %% Conexiones iniciales
    Inicio --> Inicializar_ROS
    Inicializar_ROS --> Crear_Nodo
    Crear_Nodo --> Crear_GUI
    Crear_GUI --> Bucle_Eventos

    %% Bifurcación de la interfaz
    Bucle_Eventos --> Controles_Generales
    Bucle_Eventos --> Modos_Operacion

    %% Controles Generales
    Controles_Generales --> Llamar_Servicios

    %% Pestañas
    Modos_Operacion --> Modo_Manual
    Modos_Operacion --> Modo_Presets
    Modos_Operacion --> Modo_Ensenanza
    Modos_Operacion --> Modo_Triángulo
    Modos_Operacion --> Modo_Baile
    Modos_Operacion --> Modo_Trayectorias
    Modos_Operacion --> Modo_Senoidal

    %% Flujo de las pestañas hacia sus acciones
    Modo_Manual --> Accion_Manual
    Modo_Presets --> Accion_Presets
    Modo_Ensenanza --> Accion_Ensenanza
    Modo_Triángulo --> Accion_Triángulo
    Modo_Baile --> Accion_Baile
    Modo_Trayectorias --> Accion_Trayectorias
    Modo_Senoidal --> Accion_Senoidal

    %% Los modos discretos usan la función _dispatch
    Accion_Manual --> Dispatch
    Accion_Presets --> Dispatch
    Accion_Ensenanza --> Dispatch
    Accion_Triángulo --> Dispatch
    Accion_Baile --> Dispatch

    Dispatch --> Selector_Modo
    Selector_Modo -->|Simultáneo| Envio_Simultaneo
    Selector_Modo -->|Secuencial| Envio_Secuencial
    Envio_Simultaneo --> Publicar_Comando
    Envio_Secuencial --> Publicar_Comando

    %% Los modos continuos/calculados publican directamente saltándose el _dispatch
    Accion_Trayectorias -->|Paso a paso iterativo| Publicar_Comando
    Accion_Senoidal -->|Paso a paso iterativo| Publicar_Comando
```
## Código fuente

Esta sección describe el código de la interfaz gráfica desarrollada para el laboratorio 

El archivo que contiene el código completo del sistema es:

```text
code/pincher_gui.py
```
1. Importación de librerías
```
import rclpy
from rclpy.node import Node
from dynamixel_sdk import PortHandler, PacketHandler
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import subprocess
import math
import numpy as np
```
Estas librerías permiten la creación del nodo ROS 2, la comunicación con los motores Dynamixel, la construcción de la interfaz gráfica de usuario, la ejecución de RViz y la realización de los cálculos matemáticos necesarios para la cinemática directa.

2. Selección del tipo de motor Dynamixel
```
USE_XL430 = False
```
Esta variable define el modelo de motor Dynamixel utilizado. Dependiendo de su valor, el código adapta automáticamente el protocolo de comunicación, las direcciones de memoria y los rangos de operación.

3. Funciones auxiliares de comunicación

```
def write_goal_position(packet, port, dxl_id, position):
def write_moving_speed(packet, port, dxl_id, speed):
def read_present_position(packet, port, dxl_id):
```
Estas funciones encapsulan la lectura y escritura de registros en los motores Dynamixel. Su objetivo es abstraer las diferencias entre protocolos y simplificar el envío de comandos a los actuadores.

4. Nodo ROS 2 – PincherController
```
class PincherController(Node):
```
Esta clase define el nodo principal del sistema. Se encarga de inicializar la comunicación serial con los motores, configurar los parámetros operativos, publicar los estados articulares, calcular la cinemática directa y gestionar la parada de emergencia.

5. Parámetros ROS configurables
```
self.declare_parameter('port', '/dev/ttyUSB0')
self.declare_parameter('baudrate', 1000000)
self.declare_parameter('dxl_ids', [1, 2, 3, 4, 5])
```
Estos parámetros permiten modificar la configuración del sistema sin necesidad de alterar el código fuente, utilizando el sistema de parámetros de ROS 2.

6. Publicación de estados articulares
```
self.joint_state_pub = self.create_publisher(
    JointState, '/joint_states', 10)
```
El nodo publica periódicamente el estado de las articulaciones en el tópico /joint_states, lo que permite sincronizar el robot físico con su modelo virtual en RViz.

7. Conversión entre valores Dynamixel y radianes
```
def dxl_to_radians(self, dxl_value):
def radians_to_dxl(self, radians):
```
Estas funciones convierten los valores de posición de los motores Dynamixel a radianes y viceversa, facilitando los cálculos cinemáticos y la correcta visualización del estado del robot.

8. Cálculo de la cinemática directa
```
def dh_transform(self, a, alpha, d, theta):
```
Esta función calcula la matriz de transformación homogénea utilizando los parámetros Denavit–Hartenberg para cada articulación del robot.
```
def update_tcp_position(self):
```
A partir de la matriz homogénea total se obtienen las coordenadas cartesianas X, Y y Z del TCP, las cuales se muestran en tiempo real en la interfaz gráfica.

9. Interfaz gráfica de usuario (GUI)
```
class PincherGUI:
```
La interfaz gráfica fue desarrollada utilizando Tkinter y organizada en varias pestañas que permiten los diferentes modos presentados anteriormente.

10. Integración con RViz
```
ros2 launch phantomx_pincher_description display.launch.py
```
Desde la interfaz gráfica es posible ejecutar RViz y visualizar el modelo tridimensional del manipulador sincronizado con el robot real.

11. Parada de emergencia
```
def emergency_stop(self):
```
La parada de emergencia desactiva el torque de todos los motores y bloquea el envío de nuevos comandos, garantizando la seguridad del sistema y del usuario.

Aclaraciones importantes
```

def r2_all_motors(self, list_q):

    # Convertir radianes a Dynamixel
        point_q = [self.radians_to_dxl(q) for q in list_q]

    # Enviar cada posición al motor correspondiente
        for index, motor_id in enumerate(self.dxl_ids):
            if motor_id == 5:      # no mover la pinza
                break

            self.move_motor(motor_id, point_q[index])
```

## Plano de planta
A continuación se muestra el plano de planta

<p align="center">
  <img src="images/PlanoPlanta.png" alt="PlanoPlanta" width="800">
</p>


## Diagramas digitales y DH utilizado

<svg width="44" height="44" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
<rect width="44" height="44" rx="16" fill="url(#paint0_linear_107_117)"/>
<g clip-path="url(#clip0_107_117)">
<g clip-path="url(#clip1_107_117)">
<g clip-path="url(#clip2_107_117)">
<mask id="mask0_107_117" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="8" y="8" width="28" height="28">
<path d="M36 8H8V36H36V8Z" fill="white"/>
</mask>
<g mask="url(#mask0_107_117)">
<g opacity="0.9">
<mask id="mask1_107_117" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="8" y="8" width="28" height="28">
<path d="M36 8H8V36H36V8Z" fill="white"/>
</mask>
<g mask="url(#mask1_107_117)">
<mask id="mask2_107_117" style="mask-type:luminance" maskUnits="userSpaceOnUse" x="8" y="8" width="28" height="28">
<path d="M36 8H8V36H36V8Z" fill="white"/>
</mask>
<g mask="url(#mask2_107_117)">
<path d="M35.7634 8H8V35.7634H35.7634V8Z" fill="url(#pattern0_107_117)"/>
</g>
</g>
</g>
</g>
</g>
</g>
</g>
<defs>
<pattern id="pattern0_107_117" patternContentUnits="objectBoundingBox" width="1" height="1">
<use xlink:href="#image0_107_117" transform="scale(0.01)"/>
</pattern>
<linearGradient id="paint0_linear_107_117" x1="0" y1="0" x2="44" y2="44" gradientUnits="userSpaceOnUse">
<stop stop-color="#F6B640"/>
<stop offset="1" stop-color="#F6B63D"/>
</linearGradient>
<clipPath id="clip0_107_117">
<rect width="28" height="28" fill="white" transform="translate(8 8)"/>
</clipPath>
<clipPath id="clip1_107_117">
<rect width="28" height="28" fill="white" transform="translate(8 8)"/>
</clipPath>
<clipPath id="clip2_107_117">
<rect width="28" height="28" fill="white" transform="translate(8 8)"/>
</clipPath>
<image id="image0_107_117" width="100" height="100" preserveAspectRatio="none" xlink:href="data:image/png;base64,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"/>
</defs>
</svg>

La cinemática directa se implementó usando parámetros Denavit-Hartenberg medidos directamente del robot:
<div align="center">

| i | θᵢ | dᵢ | aᵢ | αᵢ |
| :---: | :---: | :---: | :---: | :---: |
| 1 | q1 | L1 | 0 | -π/2 |
| 2 | q2 | 0 | L2 | 0 |
| 3 | q3 | 0 | L3 | 0 |
| 4 | q4 | 0 | 0 | π/2 |

</div>

A continuación los diagramas utilizados.

<p align="center">
  <img src="images/dh.jpg" alt="Diagrama DH" width="450">
</p>


Visualización completa en MATLAB

<p align="center">
  <img src="images/dhcompleto.jpg" alt="MATLAB" width="450">
</p>

<p align="center">
  <img src="images/dhcompleto2.jpg" alt="alt text" width="450">
</p>
  


## Gráficas digitales comparativas

<div align="center">

| Articulación | Pose 1 | Pose 2 | Pose 3 | Pose 4 | Pose 5 |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 00 | 25 | -35 | 85 | 80 |
| 2 | 00 | 25 | 35 | -20 | -35 |
| 3 | 00 | 20 | -30 | 55 | 55 |
| 4 | 00 | -20 | 30 | 25 | -45 |
| 5 | 00 | 00 | 00 | 00 | 00 |

</div>

A continuación los diagramas digitales de las diferentes poses empezando por HOME :

<p align="center">
  <img src="images/diagramadig2.png" alt="Diagrama digital pose HOME" width="450">
</p>

Poses R2 y R3, estas dos poses son equivalentes, solamente cambia q1.

<p align="center">
  <img src="images/rutinar2yr3.png" alt="Diagrama digital pose R2 y R3" width="450">
</p>


Continuamos con la pose R4:

<p align="center">
  <img src="images/diagramadig.jpg" alt="Diagrama digital pose R4" width="450">
</p>


Poses implementadas Físicamente y en Simulación:

HOME/ Pose 1:
<p align="center">
  <img src="images/homereal.jpg" alt="Home" width="250" style="border: none !important; box-shadow: none !important;">
  <img src="images/Pose1HomeS.jpeg" alt="Pose1HomeS" width="600" style="border: none !important; box-shadow: none !important;">
</p>
Pose 2:
<p align="center">
  <img src="images/r2.jpg" alt="Rutina R2" width="250" style="border: none !important; box-shadow: none !important;">
  <img src="images/Pose2S.jpeg" alt="Pose2S" width="600" style="border: none !important; box-shadow: none !important;">
</p>
Pose 3:
<p align="center">
  <img src="images/r3.jpg" alt="Rutina R3" width="250" style="border: none !important; box-shadow: none !important;">
  <img src="images/Pose3S.jpeg" alt="Pose3S" width="600" style="border: none !important; box-shadow: none !important;">
</p>
Pose 4:
<p align="center">
  <img src="images/r4.jpg" alt="Rutina R4" width="250" style="border: none !important; box-shadow: none !important;">
  <img src="images/Pose4S.jpeg" alt="Pose4S" width="600" style="border: none !important; box-shadow: none !important;">
</p>
Pose 5:
<p align="center">
  <img src="images/r5.jpg" alt="Rutina R5" width="250" style="border: none !important; box-shadow: none !important;">
  <img src="images/Pose5S.jpeg" alt="Pose5S" width="600" style="border: none !important; box-shadow: none !important;">
</p>

## Calibración

A continuación las imágenes de la posición real en las poses implementadas anteriormente con su respectivo error en cada articulación medido en radianes :


Error Pose 1/Home:

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 00 | 00 |
| 2 | 00 | 00 | 
| 3 | 00 | 00 | 
| 4 | 00 | 00 | 
| 5 | 00 | 00 | 

</div>

<p align="center">
  <img src="images/Posicion1.jpeg" alt="Home" width="450">
</p>

<div align="center">

| Articulación | Deseado | Medido | Error articular |
| :---: | :---: | :---: | :---: | 
| 1 | 00 | -0.051 | 0.0511 |
| 2 | 00 | -0.051 | 0.0511 |  
| 3 | 00 | -0.051 | 0.0511 | 
| 4 | 00 | -00000 | 00000 |
| 5 | 00 | -0.051 | 0.0511 |

</div>

Error Pose 2:

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 25 | 0.4363 |
| 2 | 25 | 0.4363 |
| 3 | 20 | 0.3491 |
| 4 | -20 | -0.3491 |
| 5 | 00 | 0.0000 |

</div>

<p align="center">
  <img src="images/Posicion2.jpeg" alt="Rutina R2" width="450">
</p>

<div align="center">

| Articulación | Deseado | Medido | Error articular |
| :---: | :---: | :---: | :---: | 
| 1 | 0.4363 | 0.4350 | 0.0013 |
| 2 | 0.4363 | 0.4606 | 0.0243 | 
| 3 | 0.3491 | 0.3633 | 0.0142 |
| 4 | -0.3491 | -0.3480 | 0.0011 |
| 5 | 0.0000 | -0.0511 | 0.0511 |

</div>

Error Pose 3:

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | -35 | -0.6109 |
| 2 | 35 | 0.6109 |
| 3 | -30 | -0.5236 |
| 4 | 30 | 0.5236 |
| 5 | 00 | 0.0000 |

</div>

<p align="center">
  <img src="images/Posicion3.jpeg" alt="Rutina R3" width="450">
</p>


<div align="center">

| Articulación | Deseado | Medido | Error articular |
| :---: | :---: | :---: | :---: | 
| 1 | -0.6109 | -0.6141 | 0.0032|
| 2 |  0.6109 | 0.6295 | 0.0186 | 
| 3 | -0.5236 | -0.5271 | 0.0035 |
| 4 | 0.5236 | 0.5322 | 0.0086 |
| 5 | 0.0000 | -0.0511 | 0.0511 |

</div>

Error Pose 4:

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 85 | 1.4835 |
| 2 | -20 | -0.3491 |
| 3 | 55 | 0.9599 |
| 4 | 25 | 0.4363 |
| 5 | 00 |0.0000|

</div>

<p align="center">
  <img src="images/Posicion4.jpeg" alt="Rutina R4" width="450">
</p>

<div align="center">

| Articulación | Deseado | Medido | Error articular |
| :---: | :---: | :---: | :---: | 
| 1 | 1.4835 | 1.4894 | 0.0059|
| 2 | -0.3491 | -0.3378 | 0.0113 | 
| 3 | 0.9599 | 0.9827 | 0.0228 |
| 4 | 0.4363 | 0.4452 | 0.0089 |
| 5 |0.0000| -0.0511 | 0.0511 |

</div>

Error Pose 5 :

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 80 | 1.3963 |
| 2 | -35 | -0.6109 |
| 3 | 55 | 0.9599 |
| 4 | -45 | -0.7854 |
| 5 | 00 | 0.0000 |

</div>

<p align="center">
  <img src="images/Posicion5.jpeg" alt="Rutina R5" width="450">
</p>

<div align="center">

| Articulación | Deseado | Medido | Error articular |
| :---: | :---: | :---: | :---: | 
| 1 | 1.3963 | 1.4024 | 0.0061|
| 2 | -0.6109 | -0.6244 | 0.0135 | 
| 3 | 0.9599 | 0.9673 | 0.0074 |
| 4 | -0.7854 | 0.7882 | 0.0028 |
| 5 | 0.0000 | -0.0511 | 0.0511 |

</div>

Error Máximo

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 2.9278 | 0.0511 |
| 2 | 2.9278 | 0.0511 | 
| 3 | 2.9278 | 0.0511 | 
| 4 | 0.5099 | 0.0089 | 
| 5 | 2.9278 | 0.0511 | 

</div>

Error Promedio

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 0.7735 | 0.0135 |
| 2 | 1.3636 | 0.0238 | 
| 3 | 1.1345 | 0.0198 | 
| 4 | 0.2464 | 0.0043 | 
| 5 | 2.9278 | 0.0511 | 

</div>

Desplazamiento de Cero

<div align="center">

| Articulación | grados | Radianes |
| :---: | :---: | :---: |
| 1 | 2.9278 | 0.0511 |
| 2 | 2.9278 | 0.0511 | 
| 3 | 2.9278 | 0.0511 | 
| 4 | 0.0000 | 0.0000 | 
| 5 | 2.9278 | 0.0511 | 

</div>

## Gráficas de interpolación y trayectoria sinusoidal
---
### Interpolación

Se presentan a continuación las gráficas de interpolación lineal y cúbica de las diferentes articulaciones (menos de la pinza ya que no cambia) para una trayectoria de Home a la Pose 5 con una duración de 5 segundos.

<div align="center">

| Articulación | Home | Pose 5|
| :---: | :---: | :---: |
| 1 | 00 | 80 |
| 2 | 00 | -35 |
| 3 | 00 | 55 |
| 4 | 00 | -45 |
| 5 | 00 | 00 |

</div>

Base 

<p align="center">
  <img src="images/Base.jpeg" alt="Base" width="250">
</p>

Hombro

<p align="center">
  <img src="images/Hombro.jpeg" alt="Hombro" width="250">
</p>

Codo

<p align="center">
  <img src="images/Codo.jpeg" alt="Codo" width="250">
</p>

Muñeca

<p align="center">
  <img src="images/Muñeca.jpeg" alt="Muñeca" width="250">
</p>

---
### Trayectoria sinusoidal

Se presentan a continuación las gráficas de 4 pruebas de la trayectoria de la articulación 1 (Base) de acuerdo a la función  $q(t) = q_0 + A \sin(2\pi f t)$ con una duración de 10 segundos a una frecuencia de envío de 20 Hz cambiando los parámetros de amplitud A y Frecuencia F con los siguientes valores :

- A1 : 10 grados
- A2 : 19 grados
- F1 : 0.09 Hz
- F2 : 0.2 Hz

Se hace la aclaración que las pruebas presentadas se realizaron en la implementación física pero por un error de archivos no se pudieron encontrar las gráficas de dichas pruebas, por lo anterior se presentan las pruebas hechas en simulación

Prueba 1 ( A1 y F1 / 10 grados y 0.09 Hz)

<p align="center">
  <img src="images/Prueba1.jpeg" alt="Prueba1" width="550">
</p>

Prueba 2 ( A1 y F2 / 10 grados y 0.2 Hz)

<p align="center">
  <img src="images/Prueba2.jpeg" alt="Prueba2" width="550">
</p>

Prueba 3 ( A2 y F1 / 19 grados y  0.09 Hz)

<p align="center">
  <img src="images/Prueba3.jpeg" alt="Prueba3" width="550">
</p>

Prueba 4 ( A2 y F2 / 19 grados y   0.2 Hz)

<p align="center">
  <img src="images/Prueba4.jpeg" alt="Prueba4" width="550">
</p>


---

## Videos 

A continuación se presentan los videos de implementación de la interfaz gráfica con todos sus modos, el video en físico de la realización de la figura (Triángulo) y por último el video con la coreografía propuesta:

<p align="center">
  <b>

     Implementación de la Interfaz Gráfica

  </b><br>
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1kGw2yJDOtI3jXdlSQUl3BQY8gadnQ37S/view?usp=drive_link">
    <img src="images/Interfaz.png" alt="Ver video de Simulación" width="600">
  </a>
</p>

<p align="center">
  <b>

    Realización del Triángulo
      
  </b><br>
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1JVY8RK-ZjUBz8cqOHkR_KZ-Letxmoqsy/view?usp=drive_link">
    <img src="images/Triangulo.png" alt="Ver video en Drive" width="600">
  </a>
</p>

<p align="center">
  <b>

    Coreografía
      
  </b><br>
</p>

<p align="center">
  <a href="https://drive.google.com/file/d/1aq7QyFYzW7-oRnuxK7H2QA2z3oO8PaTD/view?usp=drive_link">
    <img src="images/Baile.png" alt="Ver video en Drive" width="600">
  </a>
</p>









## Conclusiones
- La arquitectura distribuida en tres ejes (nodo de control en ROS 2, interfaz en Tkinter y visualización en RViz) demostró ser robusta. La separación de responsabilidades permitió ejecutar tareas discretas, diferentes modos de prueba y procesos continuos de cálculo iterativo (trayectorias sinusoidales e interpolación) de manera simultánea sin bloquear la interfaz de usuario, garantizando una comunicación serial estable con los motores Dynamixel, se encontró un problema de comunicación en cuanto al cable usb que realiza esta pero ya es cuestión de problemas de hardware y su desgaste a través de los años.

- El modelo matemático construido a partir de los parámetros Denavit-Hartenberg (DH) representa fielmente la estructura física del robot, validado por la correspondencia visual entre el entorno de RViz y las poses físicas (R1 a R5).

- La inclusión de interpolación cúbica y quíntica frente a la lineal clásica es un paso vital para garantizar arranques y paradas suaves, mitigando aceleraciones bruscas que podrían inducir estrés mecánico o vibraciones.

- Las articulaciones 1, 2, 3 y 5 presentan exactamente el mismo desplazamiento de cero inicial (0.0511 radianes) en la Pose 1 (Home). Se intuye que hay un desfase sistemático de calibración en los encoders o potenciómetros , o una holgura mecánica compartida en su diseño.

- La articulación 4 (muñeca) es la más precisa de todo el sistema al no presentar desplazamiento de cero en la posición Home y cuenta con el error promedio más bajo (0.0043 rad) y el error máximo más bajo (0.0089 rad) de todas las articulaciones.

- La articulación 5 mantiene un error constante de 0.0511 radianes en todas y cada una de las poses. Esto significa que el error no es dinámico; es puramente un offset de cero que no fue compensado en el controlador de la pinza.

- Para las articulaciones 1, 2 y 3, el Error Máximo se registra en la posición de reposo (Pose 1). Cuando el robot se mueve a posiciones articulares distintas de cero (Poses 2 a 5), los errores articulares disminuyen considerablemente en comparación con el offset inicial,Esto apunta a una desalineación mecánica inicial o al juego de engranajes (backlash) inherente de los servomotores que el control de lazo abierto actual no logra compensar por completo.

- Fue un reto bastante grande el baile al tener que sincronizar ritmo , delays , posiciones y velocidades para que el resultado fuera agradable , dando comprensión que todo en conjunto es de vital importancia.

- En la figura de Triángulo se utilizó cinemática inversa para sus vértices y de ahí se utilizó interpolación lineal para encontrar los valores de las articulaciones en los otros puntos , dotando de gran practicidad el uso de estas herramientas teóricas aprendidas en el curso.







      

