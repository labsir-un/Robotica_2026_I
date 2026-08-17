<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=180&section=header&text=Robótica-LAB02%20%E2%80%A2%20RoboDK&fontSize=36&desc=Práctica%20de%20Laboratorio%20%E2%80%A2%20Motoman%20MH6&descSize=14&animation=fadeIn" width="100%" />

<a href="https://robodk.com/"><img src="https://img.shields.io/badge/RoboDK-Latest-00F5FF?style=for-the-badge&logoColor=white&labelColor=0a0a1a" /></a>
<a href="https://www.motoman.com/en-us/products/robots/industrial/assembly-handling/mh-series/mh6"><img src="https://img.shields.io/badge/Robot-Motoman%20MH6-7B2FBE?style=for-the-badge&logoColor=white&labelColor=0a0a1a" /></a>
<a href="https://new.abb.com/products/robotics/robots/articulated-robots/irb-140"><img src="https://img.shields.io/badge/LENGUAJE-PYTHON-FF006E?style=for-the-badge&logoColor=white&labelColor=0a0a1a" /></a>
<a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-00F5FF?style=for-the-badge&labelColor=0a0a1a" /></a>

</div>

---

<div align="center">

```
╔══════════════════════════════════════════════════════════════════╗
║  🤖  Análisis y Operación del Manipulador Motoman MH6            ║
║  Comparación  ·  Movimiento Manual  ·  RoboDK  ·  Trayectoria   ║
╚══════════════════════════════════════════════════════════════════╝
```

</div>

> **Resumen del laboratorio:** Práctica de laboratorio donde se analiza y opera el manipulador **Motoman MH6** de Yaskawa. Se realiza una comparación técnica con el ABB IRB140, se exploran los modos de operación manual, se estudia el software RoboDK y su comunicación con el manipulador, y se diseña y ejecuta una trayectoria polar tanto en simulación como en el robot físico.

---

## 📋 Tabla de contenidos

| # | Sección |
|---|---------|
| 1 | [📊 Cuadro comparativo Motoman MH6 vs IRB140](#-cuadro-comparativo-motoman-mh6-vs-irb140) |
| 2 | [🏠 Configuraciones Home1 y Home2 del Motoman MH6](#-configuraciones-home1-y-home2-del-motoman-mh6) |
| 3 | [🕹️ Movimientos manuales — procedimiento y teclas](#️-movimientos-manuales--procedimiento-y-teclas) |
| 4 | [⚡ Niveles de velocidad para movimiento manual](#-niveles-de-velocidad-para-movimiento-manual) |
| 5 | [💻 Software RoboDK — aplicaciones y comunicación](#-software-robodk--aplicaciones-y-comunicación) |
| 6 | [⚖️ Comparación RoboDK vs RobotStudio](#️-comparación-robodk-vs-robotstudio) |
| 7 | [🔁 Diagrama de flujo de acciones del robot](#-diagrama-de-flujo-de-acciones-del-robot) |
| 8 | [🗺️ Plano de planta](#️-plano-de-planta) |
| 9 | [🌀 Trayectoria polar — código y simulación](#-trayectoria-polar--código-y-simulación) |
| 10 | [🎥 Videos de simulación e implementación](#-videos-de-simulación-e-implementación) |
| 11 | [🧾 Autores](#-autores) |

---

## 📊 Cuadro comparativo Motoman MH6 vs IRB140

| Característica | Motoman MH6 | ABB IRB140 |
|---|---|---|
| **Fabricante** | Yaskawa | ABB |
| **Grados de libertad** | 6 | 6 |
| **Carga máxima** | 6 kg | 6 kg |
| **Alcance máximo** | 1 422 mm | 810 mm |
| **Repetibilidad** | ±0.08 mm | ±0.03 mm |
| **Peso del robot** | 130 kg | 98 kg |
| **Velocidad máx. eje 1** | 190°/s | 200°/s |
| **Velocidad máx. eje 2** | 190°/s | 200°/s |
| **Velocidad máx. eje 3** | 190°/s | 260°/s |
| **Velocidad máx. eje 4** | 380°/s | 360°/s |
| **Velocidad máx. eje 5** | 380°/s | 360°/s |
| **Velocidad máx. eje 6** | 550°/s | 450°/s |
| **Controlador** | DX100 / YRC1000 | IRC5 |
| **Lenguaje de programación** | PYTHON | RAPID |
| **Montaje** | Suelo, techo, pared | Suelo, techo, pared |
| **Aplicaciones típicas** | Manipulación, ensamble, soldadura, paletizado | Manipulación, ensamble, soldadura por arco, limpieza |
| **Grado de protección** | IP54 | IP54 |
| **Software de simulación** | RoboDK, MotoSim | RobotStudio |

---

## 🏠 Configuraciones Home1 y Home2 del Motoman MH6

El manipulador Motoman MH6 tiene dos posiciones de referencia predefinidas con propósitos distintos dentro del ciclo de operación. Los valores se expresan en **pulsos de encoder** (unidad interna del controlador DX100), no en grados.

### Home1 — "Work Home Position"

Es la posición de reposo principal del robot. Al alcanzarla, el manipulador se **recoge sobre sí mismo**, con los eslabones superpuestos verticalmente, minimizando el espacio ocupado en la celda.

| Articulación | Valor ORIGIN (pulsos) | Valor CURRENT (pulsos) |
|---|---|---|
| S (eje 1) | -115290 | -115290 |
| L (eje 2) | 0 | 0 |
| U (eje 3) | -111622 | -111623 |
| R (eje 4) | 1 | -1 |
| B (eje 5) | 42647 | 42647 |
| T (eje 6) | 1392 | 1393 |

### Home2 — "Second Home Position"

Es una posición de trabajo de referencia secundaria. El robot adopta una **configuración en L invertida**, con el brazo extendido y la herramienta a mayor altura apuntando hacia abajo, lista para iniciar ciclos de trabajo.

| Articulación | Valor SPECIFIED (pulsos) | Valor CURRENT (pulsos) | Diferencia |
|---|---|---|---|
| S (eje 1) | 0 | 0 | 0 |
| L (eje 2) | 2037 | 2037 | 0 |
| U (eje 3) | 2359 | 2359 | 0 |
| R (eje 4) | -121 | -121 | 0 |
| B (eje 5) | 0 | 0 | 0 |
| T (eje 6) | 1392 | 1392 | 0 |

### ¿Cuál posición es mejor?

**Home2 resulta más conveniente como punto de inicio de ciclos de trabajo**, por las siguientes razones:

- La herramienta ya se encuentra orientada hacia abajo y a una altura operativa, reduciendo el recorrido necesario para llegar a la primera posición de trazado.
- La configuración en L invertida aleja el brazo del cuerpo del robot, disminuyendo el riesgo de colisiones internas al iniciar movimientos.
- Las diferencias entre los valores *Specified* y *Current* son todas cero, lo que indica que el robot llegó con precisión exacta a esa posición, confirmando su estabilidad como referencia.

**Home1 es preferible como posición de reposo y seguridad**, ya que al recoger todos los eslabones minimiza el espacio ocupado y reduce el par gravitacional sobre las articulaciones durante paradas prolongadas.

---

## 🕹️ Movimientos manuales — procedimiento y teclas

El pendant DX100 del Motoman MH6 permite operar en distintos modos de movimiento manual. La tecla central para gestionar esto es **COORD** (Coordenadas).

### Cambio entre modos de movimiento

| Modo | Descripción | Tecla de acceso |
|---|---|---|
| **JOINT (Articular)** | Mueve cada eje de forma independiente. S, L, U, R, B, T | Presionar **COORD** hasta seleccionar `JOINT` |
| **RECTANGULAR (Cartesiano)** | Mueve el TCP en el espacio cartesiano absoluto (X, Y, Z) | Presionar **COORD** hasta seleccionar `RECTANGULAR` |
| **CYLINDRICAL** | Movimiento en coordenadas cilíndricas | Presionar **COORD** hasta seleccionar `CYLINDRICAL` |
| **TOOL** | Movimiento relativo a la herramienta activa | Presionar **COORD** hasta seleccionar `TOOL` |

Cada vez que se presiona **COORD** el sistema rota cíclicamente entre los modos disponibles. El modo activo se indica en el **área de estado** de la pantalla del pendant.

### Traslaciones en ejes X, Y, Z (modo RECTANGULAR)

Una vez seleccionado el modo `RECTANGULAR`:

1. Activar los servomotores manteniendo presionado el **interruptor de hombre muerto** (Dead Man Switch) en el dorso del pendant.
2. Usar las **teclas de ejes** del pendant:

| Eje | Dirección positiva | Dirección negativa |
|---|---|---|
| X | Tecla `X+` | Tecla `X-` |
| Y | Tecla `Y+` | Tecla `Y-` |
| Z | Tecla `Z+` | Tecla `Z-` |

### Rotaciones en ejes X, Y, Z (modo RECTANGULAR)

En el mismo modo `RECTANGULAR`, las rotaciones del TCP se controlan con:

| Eje | Rotación positiva | Rotación negativa |
|---|---|---|
| Rx | Tecla `Rx+` | Tecla `Rx-` |
| Ry | Tecla `Ry+` | Tecla `Ry-` |
| Rz | Tecla `Rz+` | Tecla `Rz-` |

> En modo JOINT, las mismas teclas controlan directamente cada articulación: S, L, U, R, B, T en sus direcciones positiva y negativa.

---

## ⚡ Niveles de velocidad para movimiento manual

### Niveles disponibles

El Motoman MH6 con controlador DX100 dispone de **8 niveles de velocidad** para movimiento manual, organizados de menor a mayor:

| Nivel | Denominación | Descripción |
|---|---|---|
| 1 | **INCHING** | Movimiento mínimo paso a paso — máxima precisión |
| 2 | **LOW LOW** | Velocidad muy baja |
| 3 | **LOW** | Velocidad baja |
| 4 | **MEDIUM LOW** | Velocidad media-baja |
| 5 | **MEDIUM** | Velocidad media |
| 6 | **MEDIUM HIGH** | Velocidad media-alta |
| 7 | **HIGH** | Velocidad alta |
| 8 | **FULL SPEED** | Velocidad máxima permitida en modo manual |

### ¿Cómo se cambia el nivel de velocidad?

El cambio de velocidad se realiza mediante las teclas de **flecha arriba** y **flecha abajo** ubicadas en el lateral izquierdo del pendant DX100:

- **Flecha arriba (▲):** incrementa un nivel de velocidad.
- **Flecha abajo (▼):** reduce un nivel de velocidad.

El cambio es inmediato y no requiere detener el movimiento en curso.

### ¿Cómo se identifica el nivel en la pantalla?

El nivel de velocidad activo se muestra en el **área de estado** de la pantalla del pendant, en la esquina superior, mediante un indicador numérico o la etiqueta del nivel (LOW, MEDIUM, HIGH, etc.). El valor se actualiza en tiempo real cada vez que se presiona una tecla de cambio de velocidad.

---

## 💻 Software RoboDK — aplicaciones y comunicación

### Principales aplicaciones

RoboDK es una plataforma de simulación y programación offline compatible con más de 500 modelos de robots industriales de distintos fabricantes. Sus principales aplicaciones incluyen:

- **Simulación offline:** permite programar y simular trayectorias sin necesidad de conectarse al robot físico, reduciendo tiempos de paro en producción.
- **Programación independiente del fabricante:** genera código nativo para distintos robots (RAPID para ABB, INFORM para Yaskawa, KRL para KUKA, entre otros) desde un único entorno.
- **Post-procesadores personalizables:** adapta el código generado al controlador específico de cada robot mediante post-procesadores configurables.
- **Integración con Python:** permite automatizar rutinas, generar trayectorias complejas y controlar el robot en tiempo real mediante scripts Python a través de la API de RoboDK.
- **Control en tiempo real:** en modo conectado, RoboDK puede enviar comandos directamente al controlador del robot para ejecutar movimientos desde el PC.
- **Calibración y análisis de alcance:** herramientas para verificar que las trayectorias estén dentro del espacio de trabajo y evitar singularidades.

### ¿Cómo se comunica RoboDK con el manipulador Motoman?

RoboDK establece comunicación con el Motoman MH6 a través de una conexión **Ethernet (TCP/IP)** entre el PC y el controlador DX100. El proceso es el siguiente:

1. El PC con RoboDK y el controlador DX100 del Motoman se conectan a la misma red local.
2. El controlador debe estar configurado en **modo REMOTE** (selector de modo en el pendant en posición REMOTE).
3. RoboDK utiliza un **driver específico para Yaskawa/Motoman** que traduce los comandos al protocolo del controlador.
4. En el código Python, la conexión se establece explícitamente con `robot.Connect()` y se verifica con `robot.ConnectedState()`.
5. RoboDK envía instrucciones de posición (`MoveJ`, `MoveL`) al controlador, quien las convierte en movimientos de los servomotores articulación por articulación.

### ¿Qué hace RoboDK para mover el manipulador?

RoboDK calcula la **cinemática inversa** de cada punto de la trayectoria, determina los ángulos articulares necesarios y los transmite al controlador a través del driver de comunicación. El controlador DX100 ejecuta los movimientos interpolando entre puntos sucesivos, controlando la velocidad de cada eje y gestionando la seguridad del movimiento.

---

## ⚖️ Comparación RoboDK vs RobotStudio

| Aspecto | RoboDK | RobotStudio |
|---|---|---|
| **Fabricante** | RoboDK Inc. | ABB |
| **Compatibilidad de robots** | +500 marcas y modelos | Exclusivo para robots ABB |
| **Lenguaje nativo** | Python (API) + post-procesadores | RAPID |
| **Licenciamiento** | De pago con versión de prueba gratuita | Gratuito para simulación básica |
| **Curva de aprendizaje** | Media — interfaz intuitiva | Media-alta — mayor profundidad para ABB |
| **Fidelidad de simulación** | Alta — cinemática real del robot | Muy alta — gemelo digital certificado por ABB |
| **Control en tiempo real** | Sí, mediante driver y Ethernet | Sí, mediante OPC-UA y otros protocolos |
| **Generación de código** | Código nativo para múltiples fabricantes | Solo RAPID para ABB |
| **Uso típico** | Entornos multi-marca, educación, integración rápida | Celdas ABB de alta precisión, gemelo digital |

### ¿Qué significa cada herramienta?

**RoboDK** representa una solución de programación offline **universal e independiente del fabricante**. Su principal valor es la flexibilidad: permite trabajar con robots de distintas marcas desde un único entorno y automatizar trayectorias complejas mediante Python, como se demostró en este laboratorio con la generación de la curva de la mariposa y el trazado de nombres mediante la librería `matplotlib.textpath`.

**RobotStudio** representa el entorno oficial de ABB, orientado a obtener el **máximo nivel de fidelidad y precisión** para robots de esa marca. Al ser desarrollado por el mismo fabricante, ofrece un gemelo digital exacto del robot real y acceso completo a todas las funcionalidades del controlador IRC5. Fue la herramienta utilizada en el Laboratorio 01 con el IRB140.

---

## 🔁 Diagrama de flujo de acciones del robot


```mermaid
flowchart TD
    A([Inicio del script]) --> B[Inicializar RoboDK con Robolink]
    B --> C[Seleccionar robot con ItemUserPick]
    C --> D[Conectar al robot físico con robot.Connect]
    D --> E{¿Conexión exitosa?}
    E -- No --> F([Error: verificar modo REMOTE y red Ethernet])
    E -- Sí --> G[Cargar Frame_from_Target1]
    G --> H[Asignar frame al robot y configurar velocidad 300 mm/s y blending 5 mm]
    H --> I[MoveJ a TargetHome]
    I --> J[MoveJ al centro de la figura a altura segura z_safe = 50 mm]
    J --> K[MoveL bajar a superficie z = 0]

    K --> L{Bucle: i = 0 hasta num_points = 40}
    L --> M[Calcular θ = 12π · i / num_points]
    M --> N["Calcular r = A · ecos θ − 2·cos 4θ + sin⁵ θ/12"]
    N --> O[Calcular x = r·cos θ, y = r·sen θ]
    O --> P[MoveL al punto x, y, z_surface]
    P --> L
    L -- Bucle terminado --> Q[MoveL subir a altura segura z_safe]

    Q --> R{Bucle: nombre en Duvan, Mora, Gustavo}
    R --> S[Generar contorno del nombre con matplotlib TextPath]
    S --> T{Bucle: polígono en contornos de la letra}
    T --> U[MoveL al inicio del polígono a z_safe — herramienta alzada]
    U --> V[MoveL bajar a z_surface — inicio de trazo]
    V --> W{Bucle: punto en polígono}
    W --> X[Transformar punto: escala, espejo, rotación 90°, traslación]
    X --> Y[MoveL al punto transformado]
    Y --> W
    W -- Polígono terminado --> Z[MoveL subir a z_safe — herramienta alzada]
    Z --> T
    T -- Letra terminada --> R
    R -- Todos los nombres trazados --> AA[MoveJ a TargetHome]
    AA --> AB([Fin del script])
```


---

## 🗺️ Plano de planta

> 📂 Archivos disponibles en [`Diagrams_Lab2/`](./Diagrams_Lab2/): plano PDF de planta.

---

## 🌀 Trayectoria polar — código y simulación

### Fundamento matemático — Curva de la Mariposa

La figura implementada es la **curva de la mariposa**, una curva polar definida por:

```
r(θ) = e^cos(θ) − 2·cos(4θ) + sin⁵(θ/12)
```

La curva requiere un barrido de **θ ∈ [0, 12π]** para completar todos los detalles de las alas. La conversión a coordenadas cartesianas se realiza mediante:

```
x = r(θ) · cos(θ)
y = r(θ) · sin(θ)
```

Un factor de escala `A = 30` mm se aplica a `r(θ)` para adaptar la figura al espacio de trabajo del Motoman MH6.

### Descripción del código Python

El script desarrollado en RoboDK estructura la ejecución en las siguientes etapas:

1. **Conexión al robot:** se inicializa `Robolink()`, se selecciona el robot mediante `ItemUserPick` y se establece la conexión física con `robot.Connect()`. Se verifica el estado con `robot.ConnectedState()`.
2. **Configuración del frame de trabajo:** se carga el frame `"Frame_from_Target1"` previamente definido en la estación y se asigna al robot con `robot.setPoseFrame(frame)`.
3. **Parámetros de movimiento:** velocidad de 300 mm/s y blending de radio 5 mm.
4. **Retorno a Home:** el robot se desplaza primero al target `"TargetHome"` definido en la estación mediante `MoveJ`.
5. **Trazado de la mariposa:** se generan `n_points = 40` puntos distribuidos en `[0, 12π]`. Para cada punto se calcula `r`, luego `(x, y)` y se ejecuta un `MoveL` en el plano del frame a `z_surface = 0`. La aproximación y salida se realizan a `z_safe = 50 mm`.
6. **Trazado de nombres:** los nombres `["Duvan", "Mora", "Gustavo"]` se generan usando `matplotlib.textpath.TextPath` con tamaño de fuente 35. Cada letra se traza con `MoveL` punto a punto, con levantamiento de herramienta entre letras. El texto se rota 90° y se posiciona a la derecha de la figura.
7. **Retorno final a Home.**

### Código Python desarrollado en RoboDK

El código completo se encuentra adjunto en el repositorio. A continuación se muestra el fragmento principal de la curva de la mariposa:

```python
from robodk.robolink import *
from robodk.robomath import *
import math

RDK = Robolink()
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
robot.Connect()

frame = RDK.Item("Frame_from_Target1", ITEM_TYPE_FRAME)
robot.setPoseFrame(frame)
robot.setSpeed(300)
robot.setRounding(5)

A = 30          # Escala en mm
z_surface = 0
z_safe = 50
num_points = 40
full_turn = 12 * math.pi

# Retorno a Home
targetHome = RDK.Item("TargetHome", ITEM_TYPE_TARGET)
robot.MoveJ(targetHome)

# Aproximación al centro
robot.MoveJ(transl(0, 0, z_surface - z_safe))
robot.MoveL(transl(0, 0, z_surface))

# Trazado de la curva de la mariposa
for i in range(num_points + 1):
    theta = full_turn * (i / num_points)
    r = A * (math.exp(math.cos(theta))
             - 2 * math.cos(4 * theta)
             + math.pow(math.sin(theta / 12), 5))
    x = r * math.cos(theta)
    y = r * math.sin(theta)
    robot.MoveL(transl(x, y, z_surface))

robot.MoveL(transl(x, y, z_surface - z_safe))

# Retorno final
robot.MoveJ(targetHome)
```

> El código completo incluyendo el trazado de nombres con `matplotlib.textpath` se encuentra en el archivo `Code_Lab02.py` adjunto en el repositorio.

---

## 🎥 Videos de simulación e implementación

> **Video de simulación en RoboDK.**

<div align="center">

<a href="https://www.youtube.com/watch?v=XH8yssTJhJg">
  <img src="https://img.shields.io/badge/%E2%96%B6%20Ver%20video-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=0a0a1a" />
</a>

</div>

> **Video de implementación física en el Motoman MH6.**

<div align="center">

<a href="https://youtu.be/rmHUBdt_6uA">
  <img src="https://img.shields.io/badge/%E2%96%B6%20Ver%20video-YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white&labelColor=0a0a1a" />
</a>

</div>

---

## 🧾 Autores

<div align="center">

| Integrante | GitHub |
|---|---|
| **Duvan Felipe Pacheco Rodriguez** | <a href="https://github.com/dupachecor"><img src="https://img.shields.io/badge/GitHub-%40dupachecor-00F5FF?style=for-the-badge&amp;logo=github&amp;logoColor=white&amp;labelColor=0a0a1a" /></a> |
| **Juan Andrés Mora Henao** | <a href="https://github.com/JuanMora345"><img src="https://img.shields.io/badge/GitHub-%40JuanMora345-7B2FBE?style=for-the-badge&amp;logo=github&amp;logoColor=white&amp;labelColor=0a0a1a" /></a> |
| **Andrés Gustavo Pinilla Martínez** | <a href="https://github.com/AndresPinilla20"><img src="https://img.shields.io/badge/GitHub-%40AndresPinilla20-002FBE?style=for-the-badge&amp;logo=github&amp;logoColor=white&amp;labelColor=0a0a1a" /></a> |

</div>

---

<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0d003b,30:1a0533,60:0d0d2b,100:0a0a1a&height=120&section=footer&text=LabSIR%20%E2%80%A2%20Robótica%20Industrial%202026-I&fontSize=18&fontColor=7B2FBE&animation=twinkling" width="100%" />

<img src="https://img.shields.io/badge/Last%20updated-2026-FF006E?style=flat-square&labelColor=0a0a1a" />
<img src="https://img.shields.io/badge/Universidad%20Nacional%20de%20Colombia-FFD700?style=flat-square&labelColor=0a0a1a" />

</div>
