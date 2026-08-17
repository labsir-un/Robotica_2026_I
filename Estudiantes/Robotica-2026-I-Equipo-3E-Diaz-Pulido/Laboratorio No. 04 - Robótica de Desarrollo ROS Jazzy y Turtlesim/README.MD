
# Laboratorio No. 04: Robótica de Desarrollo, Intro a ROS 2 Jazzy Jalisco - Turtlesim



## Integrantes

- [José Luis Pulido Fonseca](https://github.com/jpulidof)
- [Jairo David Díaz Luna](https://github.com/Axum-User)
---

## Índice

1. [Descripción General del Laboratorio](#descripción-general-del-laboratorio)
2. [Estructura del Repositorio](#estructura-del-repositorio)
3. [Diagrama de Flujo (Mermaid)](#diagrama-de-flujo-mermaid)
4. [Explicación de la Solución Implementada](#explicación-de-la-solución-implementada)
5. [Descripción de Componentes ROS 2](#descripción-de-componentes-ros-2)
6. [Evidencias de Ejecución](#evidencias-de-ejecución)
7. [Código Fuente](#código-fuente)
8. [Video Explicativo](#video-explicativo)
9. [Conclusiones](#conclusiones)

---

## Descripción General del Laboratorio

El laboratorio tiene como finalidad el aprendizaje y familiarizacion del estudiante con Ubuntu y ROS usando turtlesim mediante la creacion de un script de Python con ejecucion multhilo y la implementacion de nodos se controle una tortuga por medio de comandos de teclado en la terminal. Ademas, se programan trayectorias automaticas tanto predefinidas por el usuario (letras y figuras) como la implementación de un sistema de seguimiento líder-seguidor de dos tortugas usando en ambos control de lazo cerrado.

---

## Estructura del repositorio

```text
turtlesim_workspace
├── build
├── install
├── log
└── src
    └── my_turtle_controller
        ├── my_turtle_controller
        │   ├── __init__.py
        │   ├── move_turtle.py
        │   
        ├── resource
        │   └── my_turtle_controller
        ├── test
        │     
        ├── package.xml
        ├── setup.cfg
        └── setup.py

```

---

## Diagrama de Flujo (Mermaid)

A continuación se presenta la lógica de funcionamiento del programa, abarcando desde la inicialización del nodo hasta su finalización segura:

```mermaid
graph TD
    A([Inicio de Programa]) --> B[Inicializar rclpy]
    B --> C[Instanciar TurtleController y TurtleFollower]
    C --> D[Lanzar Hilo Secundario: keyboard_listener]
    C --> E[Lanzar MultiThreadedExecutor: spin]

    %% HILO DE TECLADO
    subgraph "Hilo del Teclado (keyboard_listener)"
        D --> F[Configurar Terminal en Modo Raw]
        F --> G[/Lectura de Tecla no Bloqueante/]
        G --> H{¿Qué tecla se presionó?}
        
        %% Control Manual
        H -- Flechas Direccionales --> I[Publicar Twist manual en /turtle1/cmd_vel]
        
        %% Trayectorias y Modos
        H -- S / T / L / F / J / D --> J[Cargar Trayectoria Waypoints y fijar CLOSED_LOOP]
        H -- A --> K[Fijar Modo AVOIDANCE]
        H -- P --> L[Llamar asíncronamente a /turtle1/set_pen]
        H -- R --> M[Llamar asíncronamente a /clear y TeleportAbsolute]
        H -- Q --> N[Limpiar Waypoints y Publicar Twist en cero]
        
        I --> G
        J --> G
        K --> G
        L --> G
        M --> G
        N --> G
    end

    %% BUCLES DE CONTROL CONCURRENTES
    subgraph "Ejecutor Multihilo (Bucle Principal)"
        E --> O[Bucle de Control turtle1: control_loop a 100 Hz]
        E --> P[Bucle de Seguimiento turtle2: follow_loop a 50 Hz]
        
        O --> Q{¿Modo de turtle1?}
        Q -- CLOSED_LOOP --> R[Control Proporcional hacia Waypoint actual]
        Q -- AVOIDANCE --> S[Caminata Aleatoria + Evasión de Muros]
        Q -- MANUAL --> T[Esperar comandos de velocidad]
        
        R --> O
        S --> O
        T --> O
        
        P --> U[Calcular error de Distancia y Ángulo respecto a turtle1]
        U --> V[Publicar Ley de Control Proporcional en /turtle2/cmd_vel]
        V --> P
    end

    %% CIERRE Y DETENCIÓN SEGURA
    G -- Ctrl+C o Interrupción --> W([Captura de KeyboardInterrupt])
    O -- Ctrl+C o Interrupción --> W
    P -- Ctrl+C o Interrupción --> W
    
    W --> X[Restaurar configuración de terminal tcsetattr]
    X --> Y[Destruir Nodos y Apagar rclpy]
    Y --> Z([Fin del Programa])

    %% Estilos para destacar Inicio y Fin
    classDef inicioFin fill:#1A659E,color:#FFF,stroke:#023E8A,stroke-width:2px;
    class A,Z inicioFin;

```

---

## Explicación de la Solución Implementada

### 1. Control Manual de la Tortuga

* **Lógica y funciones:** Para capturar el teclado sin bloquear la ejecución paralela y los temporizadores del nodo de ROS 2, se implementó una lectura no bloqueante (usando la configuración de la terminal con los módulos `termios` y `sys`) mediante un hilo secundario con `threading`. Al presionar las flechas direccionales (↑, ↓, ←, →), el programa genera un mensaje de tipo `geometry_msgs/msg/Twist`. Las flechas Arriba/Abajo modifican la componente de velocidad lineal (`linear.x`) y las flechas Izquierda/Derecha modifican la velocidad angular (`angular.z`), enviando los datos directamente a través del tópico `/turtle1/cmd_vel`.

### 2. Funciones Automáticas Implementadas

**Lógica del Controlador:** El nodo lee constantemente su posición desde `/turtle1/pose`. Al solicitar una figura, se calculan las coordenadas absolutas $(x,y)$ a visitar. El controlador ajusta dinámicamente la velocidad lineal proporcional a la distancia y la velocidad angular proporcional al error de orientación, minimizando ambos hasta llegar a una tolerancia (0.03 a 0.15 dependiendo del modo suave/estricto).

* **Teclas S, T, L, F (Estricto):** Genera secuencias de waypoints ortogonales o agudos (ej. Cuadrado, Triángulo, letras L y F). El sistema prioriza alinearse (velocidad angular pura) si el error angular es mayor a 0.05 rads antes de avanzar, logrando trazos precisos.
* **Teclas J, D (Fluido/Smooth):** Genera curvas calculadas con funciones paramétricas trigonométricas (seno y coseno) interpolando el arco. Permite cierto desplazamiento lineal simultáneo con el giro angular, logrando curvas limpias.
* **Tecla R (Reiniciar):** En lugar de usar el servicio `/reset` nativo que reinicia completamente el simulador, se realiza un reseteo inteligente para no perder a turtle2. Instancia clientes para invocar asíncronamente el servicio `/clear` (borrando los trazos) y servicios de `/turtle1/teleport_absolute` y `/turtle2/teleport_absolute`, regresando a turtle1 a (5.5, 5.5) y a turtle2 a (2.0, 2.0).
* **Tecla P (Lápiz):** Alterna el estado del lápiz invocando asíncronamente `/turtle1/set_pen`, modificando el parámetro off y enviando blanco (255, 255, 255) si dibuja o negro (0, 0, 0) si está inactivo.
* **Tecla A (Evasión de límites - Avoidance):** Activa un comportamiento de "caminata aleatoria" cambiando el giro cada cierto tiempo. Si la posición censada supera los márgenes de seguridad ($x, y < 1.5$ o $x, y > 9.5$), el nodo frena ligeramente, calcula el ángulo directo hacia el centro de la pantalla $(5.5, 5.5)$ y aplica un fuerte giro corrector proporcional para forzar el rebote y evitar estrellarse contra los muros.
* **Tecla Q (Detener):** Detiene las rutinas automáticas limpiando la lista de waypoints (`target_waypoints.clear()`) y envía de inmediato un mensaje Twist en cero para frenar en seco.

### 3. Sistema Líder-Seguidor con Dos Tortugas

* **Creación de la segunda tortuga:** Durante la inicialización del nodo, se realiza un llamado directo al servicio `/spawn` para generar a `turtle2` en una posición determinada.
```python
req.x = 2.0
req.y = 2.0

```


* **Algoritmo de seguimiento:** El nodo se suscribe simultáneamente a `/turtle1/pose` y `/turtle2/pose`. Calcula continuamente el error de posición euclidiana y el error angular:
$$e_{distancia} = \sqrt{(x_1 - x_2)^2 + (y_1 - y_2)^2}$$


$$\theta_{deseada} = \text{atan2}(y_1 - y_2, x_1 - x_2)$$


$$\theta_{error} = \theta_{deseada} - \theta_{actual}$$


**Constantes Proporcionales ($K_p$):** Si la distancia es mayor a 0.3 metros (zona de tolerancia), se envían las siguientes velocidades limitadas (saturación):
$$V_{lineal} = \min(1.5, 1.2 \times e_{distancia})$$


$$V_{angular} = \max(-2.5, \min(2.5, 3.0 \times \theta_{error}))$$



---

## Descripción de Componentes ROS 2

* **Nodos Utilizados:** `turtle_controller` y `turtle_follower` (nodos propios desarrollados en Python ejecutados en un ejecutor multihilo) y `turtlesim_node` (nodo gráfico de simulación suministrado por el sistema).
* **Tópicos Utilizados:**  `/turtle1/cmd_vel` y `/turtle2/cmd_vel`: Mensajes de tipo `geometry_msgs/msg/Twist` para enviar velocidades lineales y angulares a los actuadores.
* `/turtle1/pose` y `/turtle2/pose`: Mensajes de tipo `turtlesim/msg/Pose` para leer posiciones (x, y) y orientaciones espaciales en tiempo real.


* **Servicios Utilizados:** `/spawn` (creación e instanciación de la segunda tortuga), `/reset` (reinicio global del entorno y limpieza de trazos) y `/turtle1/set_pen` (control del color y rastro de la tortuga principal).

---

## Evidencias de Ejecución

* **Movimiento Manual:**
<p align="center">
  <img src="media/rqtscreenshot.png"width="700">
</p>  

* **Dibujo de Figuras Geométricas:** 
<p align="center">
  <img src="media/Letrasyfiguras.jpeg"width="700">
</p> 
* **Dibujo de Letras Personalizadas:** 
<p align="center">
  <img src="media/Letrasyfiguras.jpeg"width="700">
</p> 
* **Funcionamiento del Sistema Líder-Seguidor:** 
<p align="center">
  <img src="media/Persecucion Automatica.png"width="700">
</p> 

### Salidas de Comandos de Inspección

1. `ros2 node list**`


<p align="center">
  <img src="media/Ros2nodelist.png"width="700">
</p> 

2. `ros2 topic list**`

<p align="center">
  <img src="media/Ros2topiclist.png"width="700">
</p> 

3. `ros2 topic echo /turtle1/pose**`

<p align="center">
  <img src="media/Ros2topicechoturtle1pose.png.png"width="700">
</p>

4. `ros2 topic info /turtle1/cmd_vel**`

<p align="center">
  <img src="media/Ros2topicinfoturtle1cmdvel.png"width="700">
</p>

5. `ros2 service list**`

<p align="center">
  <img src="media/ros2servicelist1.png"width="700">
</p>

<p align="center">
  <img src="media/ros2servicelist2.png"width="700">
</p>

**6. Visualización de la Arquitectura (rqt_graph)**

<p align="center">
  <img src="media/rqtscreenshot.png"width="700">
</p> 


Muestra visualmente la topología de la red de ROS, donde nuestro nodo lee las poses y escribe comandos Twist en ambas tortugas.

---
 
## Código Fuente

**Código** [`aquí`](./move_turtle.py)

---

## Video Explicativo

[Link](https://drive.google.com/drive/folders/1SVrb7ClZb8VMEGBJR8mviIBYOKBtLPtp?usp=drive_link)


---

## Conclusiones

* El desarrollo de este laboratorio bajo ROS 2 Jazzy Jalisco permitió asimilar de forma práctica los conceptos de Middleware y la programación orientada a eventos mediante callbacks empleando rclpy.
* Diseñar esquemas de control cinemático síncronos (como el sistema líder-seguidor) recalca la importancia de estructurar arquitecturas de software eficientes y de carácter no bloqueante para garantizar la estabilidad de sistemas robóticos en tiempo real.


