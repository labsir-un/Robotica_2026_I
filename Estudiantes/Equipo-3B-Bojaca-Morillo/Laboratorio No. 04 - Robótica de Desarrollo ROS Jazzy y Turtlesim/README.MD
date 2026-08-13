<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Gabriel+Eduardo+Bojaca+Munar">
</p>
<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Maria+Fernanda+Morillo+Tovar">
</p>

## Descripción

En este laboratorio se exploró el entorno de desarrollo **ROS 2 Jazzy** mediante el simulador **Turtlesim**, con el objetivo de comprender los conceptos fundamentales de la programación de sistemas robóticos. Se realizaron ejercicios enfocados en la creación y ejecución de nodos, la comunicación mediante tópicos, servicios y acciones, así como el control del movimiento de la tortuga desde la terminal y mediante programas propios. Además, se reforzó el uso de paquetes, espacios de trabajo (*workspaces*) y herramientas básicas de ROS 2, permitiendo adquirir una base sólida para el desarrollo de aplicaciones robóticas más complejas.


## Diagrama general

```mermaid
graph TD
    subgraph "Entradas (Inputs)"
        K[Teclado - pynput] -->|Eventos de teclas| KeyHandler[on_key_press]
        P1_Pose[Pose Turtle 1] -->|Subscription| PoseCallback[pose_callback]
        P2_Pose[Pose Turtle 2] -->|Subscription| Pose2Callback[pose2_callback]
    end

    subgraph "Nodo: TurtleController"
        KeyHandler -->|Cambia estados/trayectorias| State[Variables de Estado: manual_mode, posiciones, etc.]
        State --> ControlLogic[Timer Control - 100Hz]
        
        subgraph "Lógica de Control"
            ControlLogic --> Follower[seguir_lider]
            ControlLogic --> PathFollow[Seguimiento de Trayectoria]
            ControlLogic --> Manual[Control Manual]
        end
        
        PathFollow --> Navigation[Cálculo de Distancia/Ángulo]
        Navigation --> PenControl[Gestión de Lápiz z=0]
    end

    subgraph "Salidas (Outputs)"
        Manual -->|Twist| Pub1[Publisher /turtle1/cmd_vel]
        PathFollow -->|Twist| Pub1
        Follower -->|Twist| Pub2[Publisher /turtle2/cmd_vel]
        
        ControlLogic -->|Servicios| PenSrv[SetPen]
        ControlLogic -->|Servicios| TeleportSrv[TeleportAbsolute]
        ControlLogic -->|Servicios| ClearSrv[Clear]
        ControlLogic -->|Servicios| SpawnSrv[Spawn]
    end

    Pub1 --> Turtlesim[Turtlesim Environment]
    Pub2 --> Turtlesim
    PenSrv --> Turtlesim
    TeleportSrv --> Turtlesim
    ClearSrv --> Turtlesim
    SpawnSrv --> Turtlesim
```
 
 ## Diagrama ciclo principal

```mermaid
flowchart TD
    Start([Timer 0.01s]) --> Follower{¿Seguir líder activo?}
    Follower -- Sí --> ExecuteFollower[Ejecutar seguir_lider]
    Follower -- No --> CheckStop{¿Detenido por usuario?}
    
    ExecuteFollower --> CheckStop
    
    CheckStop -- Sí --> PublishEmpty[Publicar Twist Vacío]
    CheckStop -- No --> ManualMode{¿Manual Mode?}
    
    ManualMode -- Sí --> PublishManual[Publicar manual_twist]
    ManualMode -- No --> CheckPath{¿Trayectoria finalizada?}
    
    CheckPath -- Sí --> Finish[Publicar Twist Vacío + Log]
    CheckPath -- No --> NavCalc[Cálculo Navegación Punto Objetivo]
    
    NavCalc --> PenLogic{¿Z == 0?}
    PenLogic -- Sí --> PenDown[Lápiz Abajo]
    PenLogic -- No --> PenUp[Lápiz Arriba]
    
    PenDown --> PublishNav[Publicar Twist Movimiento]
    PenUp --> PublishNav
    
    PublishManual --> End([Fin Ciclo])
    PublishNav --> End
    PublishEmpty --> End
    Finish --> End
```

## Diagrama interacción con teclas

```mermaid
stateDiagram-v2
    [*] --> EsperandoTecla
    EsperandoTecla --> ModoManual: Flechas (Up/Down/Left/Right)
    EsperandoTecla --> ModoTrayectoria: s, t, v, g, e, b, m, f
    EsperandoTecla --> ModoAleatorio: a
    EsperandoTecla --> Teletransporte: r
    EsperandoTecla --> Detener: q
    EsperandoTecla --> Limpiar: c
    EsperandoTecla --> Lapiz: p

    ModoManual: Actualiza manual_twist
    ModoTrayectoria: Llama a ajustar_trayectoria() y dibuja la trayetoria centrada en la posición actual
    ModoAleatorio: Genera y dibuja trayectoria con puntos aleatorios
    Teletransporte: Llama a TeleportAbsolute para ir al centro de la ventana
    Detener: Detiene la trayectoria actual 
    Limpiar: Limpia la ventana
    Lapiz: Alterna el estado del pen
```

## Glosario variables de estado:

Estas variables del nodo determinan qué comportamiento debe priorizar el robot en cada ciclo de control (100Hz).

### 1. Control de Navegación y Trayectoria
| Variable | Tipo | Descripción | Función |
| :--- | :--- | :--- | :--- |
| `posiciones` | `list` | Lista de puntos de paso `[x, y, z]` que la tortuga debe visitar. | Define la ruta que la tortuga debe seguir automáticamente. |
| `indice` | `int` | Índice actual de la variable `posiciones`. | Indica en qué punto de la trayectoria se encuentra el robot en este momento. |
| `trayectoria_finalizada`| `bool` | Bandera que indica si el robot ya completó todos los puntos de la lista. | Evita que el robot reinicie la trayectoria o genere logs repetitivos al terminar. |

### 2. Modos de Operación (Prioridades)
| Variable | Tipo | Descripción | Función |
| :--- | :--- | :--- | :--- |
| `manual_mode` | `bool` | Indica si el control está en manos del usuario (teclado). | **Prioridad 1**: Si es `True`, el robot ignora las trayectorias y solo responde a las teclas. |
| `stopped` | `bool` | Bandera de "Pausa" activada por el usuario. | Interrumpe cualquier movimiento. Si es `True`, el robot se detiene inmediatamente. |

### 3. Retroalimentación de Sensores (Feedback)
| Variable | Tipo | Descripción | Función |
| :--- | :--- | :--- | :--- |
| `pose` | `Pose` | Datos de posición (x, y, theta) de la **Tortuga 1**. | Se usa para calcular la distancia y el ángulo hacia el objetivo. |
| `pose2` | `Pose` | Datos de posición (x, y, theta) de la **Tortuga 2**. | Se usa exclusivamente por el comportamiento de seguimiento de líder. |

### 4. Salidas
| Variable | Tipo | Descripción | Función |
| :--- | :--- | :--- | :--- |
| `pen_down` | `bool` | Estado del lápiz de la Tortuga 1 (True = Dibujando, False = Lápiz arriba). | Controla si el robot deja rastro en la pantalla. |
| `manual_twist` | `Twist` | Mensaje de velocidad lineal y angular temporal. | Almacena los movimientos del teclado para ser publicados en el siguiente ciclo. |


### Controles del Robot

| Tecla | Acción en la Simulación |
| :--- | :--- |
| **A** | **Trayectoria Aleatoria:** Genera y ejecuta un camino con 10 puntos al azar en la pantalla. |
| **B** | **Dibujar "B":** Dibuja la letra "B" centrada en la posición actual de la tortuga. |
| **C** | **Limpiar Pantalla:** Borra todos los trazos realizados en el entorno. |
| **E** | **Dibujar "E":** Dibuja la letra "E" centrada en la posición actual de la tortuga. |
| **F** | **Dibujar "F":** Dibuja la letra "F" centrada en la posición actual de la tortuga. |
| **G** | **Dibujar "G":** Dibuja la letra "G" centrada en la posición actual de la tortuga. |
| **M** | **Dibujar "M":** Dibuja la letra "M" centrada en la posición actual de la tortuga. |
| **P** | **Alternar Lápiz:** Activa o desactiva la capacidad de la tortuga para dibujar (deja de dejar rastro o empieza a hacerlo). |
| **Q** | **Parada de Emergencia:** Detiene inmediatamente el movimiento del robot y levanta el lápiz. |
| **R** | **Teletransporte:** Mueve instantáneamente a la tortuga a la posición (5.5, 5.5) con orientación 0. |
| **S** | **Dibujar Cuadrado:** Dibuja una forma de cuadrado centrada en la posición actual. |
| **T** | **Dibujar Triángulo:** Dibuja una forma de triángulo centrada en la posición actual. |
| **V** | **Dibujar "T":** Dibuja la letra "T" centrada en la posición actual de la tortuga. |
| **↑ (Flecha Arriba)** | **Mover Adelante:** Control manual para desplazar la tortuga hacia adelante. |
| **↓ (Flecha Abajo)** | **Mover Atrás:** Control manual para desplazar la tortuga hacia atrás. |
| **← (Flecha Izquierda)** | **Girar Izquierda:** Rotación manual de la tortuga hacia la izquierda. |
| **→ (Flecha Derecha)** | **Girar Derecha:** Rotación manual de la tortuga hacia la derecha. |
### Videos 
https://youtu.be/AThOkcXxe4c
