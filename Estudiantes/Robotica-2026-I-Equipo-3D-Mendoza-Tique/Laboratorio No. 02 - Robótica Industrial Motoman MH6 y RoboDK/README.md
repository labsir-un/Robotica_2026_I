# Laboratorio No. 02 - Robótica Industrial
## Análisis y Operación del Manipulador Motoman MH6

**Universidad Nacional de Colombia — 2026-I**  
**Integrantes:** Luis Mendoza · Duvan  
**Asignatura:** Robótica Industrial

---

## 📋 Tabla de Contenidos

1. [Resultados de Aprendizaje](#1-resultados-de-aprendizaje)
2. [Cuadro Comparativo: Motoman MH6 vs ABB IRB140](#2-cuadro-comparativo-motoman-mh6-vs-abb-irb140)
3. [Configuraciones Iniciales: Home1 y Home2](#3-configuraciones-iniciales-home1-y-home2)
4. [Movimientos Manuales del Manipulador](#4-movimientos-manuales-del-manipulador)
5. [Control de Velocidad](#5-control-de-velocidad)
6. [Software RoboDK](#6-software-robodk)
7. [Comparación RoboDK vs RobotStudio](#7-comparación-robodk-vs-robotstudio)
8. [Trayectoria Polar — Diseño y Ejecución](#8-trayectoria-polar--diseño-y-ejecución)
9. [Diagrama de Flujo](#9-diagrama-de-flujo)
10. [Plano de Planta](#10-plano-de-planta)
11. [Videos de Evidencia](#11-videos-de-evidencia)
12. [Código Fuente](#12-código-fuente)

---

## 1. Resultados de Aprendizaje

- Comprender las diferencias entre las características técnicas del manipulador **Motoman MH6** y el **IRB140**.
- Identificar y describir las configuraciones iniciales del Motoman MH6, incluyendo **home1** y **home2**.
- Realizar movimientos manuales en distintos modos de operación: articulaciones, cartesianos, traslaciones y rotaciones.
- Cambiar y controlar los **niveles de velocidad** para el movimiento manual.
- Comprender las principales aplicaciones del software **RoboDK** y su comunicación con el manipulador.
- Comparar y analizar las diferencias entre **RobotStudio** y **RoboDK**.
- Diseñar y ejecutar una **trayectoria polar** en RoboDK e implementarla físicamente en el Motoman MH6.

---

## 2. Cuadro Comparativo: Motoman MH6 vs ABB IRB140

| Característica              | Motoman MH6              | ABB IRB140               |
|-----------------------------|--------------------------|--------------------------|
| **Fabricante**              | Yaskawa                  | ABB                      |
| **Grados de libertad**      | 6                        | 6                        |
| **Carga útil máxima**       | 6 kg                     | 6 kg                     |
| **Alcance máximo**          | 1422 mm                  | 810 mm                   |
| **Repetibilidad**           | ±0.08 mm                 | ±0.03 mm                 |
| **Velocidad máx. muñeca**   | 1000 °/s                 | 450 °/s                  |
| **Peso del robot**          | 130 kg                   | 98 kg                    |
| **Controlador**             | DX100 / YRC1000          | IRC5                     |
| **Software de programación**| INFORM III / RoboDK      | RAPID / RobotStudio      |
| **Montaje**                 | Suelo, techo, pared      | Suelo, techo, inclinado  |
| **Protección**              | IP54                     | IP54                     |
| **Aplicaciones típicas**    | Soldadura, manipulación  | Ensamble, pick & place   |

**Análisis:** El Motoman MH6 tiene mayor alcance (1422 mm vs 810 mm), lo que lo hace más adecuado para tareas que requieren cubrir un área de trabajo amplia. El IRB140 ofrece mayor repetibilidad (±0.03 mm), siendo preferible para tareas de alta precisión como ensamble electrónico.

---

## 3. Configuraciones Iniciales: Home1 y Home2

### Home1
La posición **Home1** corresponde a la postura de "cero mecánico" del robot, donde todos los ejes articulares se encuentran en 0°. En esta posición el robot queda completamente extendido de forma vertical.

- **Valores articulares:** S=0°, L=0°, U=0°, R=0°, B=0°, T=0°
- **Uso:** Posición de referencia para calibración y verificación de encoders.

### Home2
La posición **Home2** es una postura de reposo segura, con el brazo recogido y alejado de posibles obstáculos en el entorno de trabajo.

- **Valores articulares típicos:** S=0°, L=-30°, U=+45°, R=0°, B=-15°, T=0°
- **Uso:** Posición de inicio y fin de ciclos de trabajo, más segura operativamente.

### ¿Cuál es mejor?
**Home2 es la posición preferida** para operaciones cotidianas porque:
1. Mantiene el brazo en una postura compacta, reduciendo el riesgo de colisiones con el entorno.
2. Permite transiciones más suaves hacia las posiciones de trabajo.
3. Reduce el estrés mecánico en las articulaciones al no mantener el brazo completamente extendido.

Home1 se reserva para calibración y mantenimiento.

---

## 4. Movimientos Manuales del Manipulador

El teach pendant del Motoman MH6 (DX100) permite los siguientes modos de movimiento manual:

### 4.1 Modo Articulaciones (Joint)
Mueve cada eje de forma independiente.

| Tecla        | Acción                        |
|--------------|-------------------------------|
| `S+` / `S-`  | Gira eje S (base)             |
| `L+` / `L-`  | Gira eje L (hombro)           |
| `U+` / `U-`  | Gira eje U (codo)             |
| `R+` / `R-`  | Gira eje R (muñeca rotación)  |
| `B+` / `B-`  | Gira eje B (muñeca inclinación)|
| `T+` / `T-`  | Gira eje T (muñeca giro)      |

**Cambio de modo:** Presionar `COORD` en el teach pendant hasta seleccionar `JOINT`.

### 4.2 Modo Cartesiano (XYZ)
Mueve el TCP en los ejes del sistema de coordenadas del mundo o del usuario.

| Tecla        | Acción                  |
|--------------|-------------------------|
| `X+` / `X-`  | Traslación en eje X     |
| `Y+` / `Y-`  | Traslación en eje Y     |
| `Z+` / `Z-`  | Traslación en eje Z     |

**Cambio de modo:** Presionar `COORD` hasta seleccionar `RECTANGULAR`.

### 4.3 Modo Traslación
Igual al cartesiano pero referenciado al frame de la herramienta (Tool Frame).

**Cambio de modo:** Presionar `COORD` hasta seleccionar `TOOL`.

### 4.4 Modo Rotación
Permite rotar el TCP alrededor de los ejes Rx, Ry, Rz sin desplazar el punto de contacto.

| Tecla        | Acción                  |
|--------------|-------------------------|
| `Rx+`/`Rx-`  | Rotación alrededor de X |
| `Ry+`/`Ry-`  | Rotación alrededor de Y |
| `Rz+`/`Rz-`  | Rotación alrededor de Z |

> **Nota:** Para activar el movimiento se debe mantener presionado el **deadman switch** (interruptor de hombre muerto) en el teach pendant junto con la tecla de dirección deseada.

---

## 5. Control de Velocidad

El Motoman MH6 dispone de los siguientes niveles de velocidad en modo manual (Jog):

| Nivel | Denominación | Velocidad aproximada |
|-------|-------------|----------------------|
| 1     | INCHING     | Movimiento paso a paso (~0.1%) |
| 2     | LOW (Bajo)  | ~1% de la velocidad máxima     |
| 3     | MEDIUM (Medio) | ~10% de la velocidad máxima |
| 4     | HIGH (Alto) | ~50% de la velocidad máxima    |
| 5     | FAST (Rápido) | ~100% de la velocidad máxima |

### Visualización en pantalla
El nivel de velocidad actual se muestra en la **barra de estado superior** del teach pendant DX100, indicado como un porcentaje numérico (ej. `SPEED: 10%`). Para cambiar el nivel:
- Presionar `↑` (flecha arriba) para aumentar velocidad.
- Presionar `↓` (flecha abajo) para disminuir velocidad.

---

## 6. Software RoboDK

### ¿Qué es RoboDK?
RoboDK es un software de simulación y programación offline para robots industriales compatible con más de 500 modelos de diferentes fabricantes, incluyendo Yaskawa (Motoman).

### Principales aplicaciones
- **Simulación offline:** Programar y simular trayectorias sin necesidad del robot físico.
- **Generación de código:** Exporta programas en el lenguaje nativo del robot (INFORM III para Motoman).
- **Calibración:** Herramientas para calibrar el frame de trabajo y la herramienta.
- **Análisis de alcance:** Verificar si una trayectoria es alcanzable antes de ejecutarla.
- **Post-procesadores:** Adaptación del código a distintos controladores.

### Comunicación con el Motoman MH6
RoboDK se comunica con el robot a través de:
1. **Conexión Ethernet (TCP/IP):** El PC y el controlador DX100 deben estar en la misma red local.
2. **Configuración en el controlador:** Activar el modo de comunicación remota (`REMOTE`) en el DX100.
3. **Driver RoboDK:** Se instala un programa servidor en el controlador que recibe comandos de RoboDK.
4. **API de Python:** Usando `robodk.robolink.Robolink()` se establece la conexión y se envían comandos de movimiento en tiempo real.

```python
from robodk.robolink import *
RDK = Robolink()
robot = RDK.ItemUserPick("Selecciona un robot", ITEM_TYPE_ROBOT)
robot.Connect()  # Conecta al robot físico
```

---

## 7. Comparación RoboDK vs RobotStudio

| Característica              | RoboDK                          | RobotStudio                     |
|-----------------------------|---------------------------------|---------------------------------|
| **Fabricante**              | RoboDK Inc.                     | ABB                             |
| **Compatibilidad**          | +500 marcas (universal)         | Solo robots ABB                 |
| **Lenguaje de programación**| Python, C#, MATLAB, etc.        | RAPID (propietario ABB)         |
| **Licencia**                | Comercial (versión educativa)   | Gratuito para robots ABB        |
| **Interfaz**                | Intuitiva, multiplataforma      | Completa pero más compleja      |
| **Simulación física**       | Básica                          | Avanzada (colisiones, física)   |
| **Post-procesadores**       | Amplia librería incluida        | Solo para ABB                   |
| **API**                     | Python nativa, muy documentada  | SDK .NET / RAPID                |
| **Uso en industria**        | Integración multi-marca         | Entornos exclusivos ABB         |
| **Curva de aprendizaje**    | Baja-Media                      | Media-Alta                      |

**Conclusión:** RoboDK es más versátil para entornos con múltiples marcas de robots y ofrece una API de Python muy accesible. RobotStudio es la herramienta definitiva para robots ABB, con simulación más fiel y herramientas avanzadas de análisis, pero limitada a ese ecosistema.

---

## 8. Trayectoria Polar — Diseño y Ejecución

### Ecuación de la trayectoria
La trayectoria implementada combina una **rosa polar espiral** con la escritura de los nombres de los integrantes en modo espejo:

**Rosa polar:**
$$r = A \cdot \theta \cdot \sin(10\theta)$$

Donde:
- `A = 30` mm (amplitud)
- `θ ∈ [0, 2π]` (ángulo en radianes)
- `num_points = 30` (resolución de la curva)

**Conversión a coordenadas cartesianas:**
$$x = r \cdot \cos(\theta), \quad y = r \cdot \sin(\theta)$$

### Parámetros de ejecución
| Parámetro       | Valor       |
|-----------------|-------------|
| Velocidad       | 300 mm/s    |
| Rounding        | 10 mm       |
| Z superficie    | 0 mm        |
| Z seguro        | -50 mm      |
| Frame           | Frame_from_Target1 |

### Secuencia de movimientos
1. Mover a **Target home** (MoveJ)
2. Aproximación al plano de trabajo (MoveJ → MoveL)
3. Ejecución de la **rosa polar** (30 puntos MoveL)
4. Retiro al plano seguro
5. Escritura de **"LUIS"** en modo espejo
6. Escritura de **"DUVAN"** en modo espejo
7. Retorno a **Target home**

### Modo espejo
Las letras se dibujan con el eje X invertido para que, al verse reflejadas en una superficie, aparezcan correctamente orientadas.

---

## 9. Diagrama de Flujo

```
┌─────────────────────────────────┐
│           INICIO                │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Conectar RoboDK ↔ Robot        │
│  (Robolink + robot.Connect())   │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Configurar Frame, Velocidad    │
│  y Rounding                     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Mover a Target Home (MoveJ)    │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Aproximar al plano Z=0         │
│  (MoveJ → MoveL)                │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Calcular puntos Rosa Polar     │
│  r = A·θ·sin(10θ)               │
│  Para i = 0 → num_points        │
│    x = r·cos(θ), y = r·sin(θ)  │
│    MoveL(x, y, z_surface)       │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Retirar a Z seguro (MoveL)     │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Dibujar "LUIS" en espejo       │
│  (L → U → I → S)               │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Dibujar "DUVAN" en espejo      │
│  (D → U → V → A → N)           │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│  Retornar a Target Home (MoveJ) │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│              FIN                │
└─────────────────────────────────┘
```

---

## 10. Plano de Planta

El plano de trabajo del area de operacion del robot Motoman MH6 se encuentra en el siguiente archivo:

📄 **[Ver Plano de Trabajo (PDF)](PLANO%20DE%20TRABAJO.pdf)**
---


## Visualización de Resultados y Videos

* [Video de Simulación en RoboDK](https://drive.google.com/file/d/1yIWU5hbhEdyYTmu87mEXbJjnmFTXK-vE/view?usp=sharing)
* [Video de la Trayectoria Real](https://drive.google.com/file/d/1vcbr-21bJV0XpfhTrjit9lN6acf1Ggzb/view?usp=sharing)
---

## 12. Código Fuente

El código principal se encuentra en [`trayectoria_polar.py`](./trayectoria_polar.py).

### Requisitos
```bash
pip install robodk
```

### Ejecución
1. Abrir RoboDK y cargar la estación con el Motoman MH6.
2. Asegurarse de que el frame `Frame_from_Target1` y el target `Target home` existen en la estación.
3. Conectar el robot físico en modo REMOTE.
4. Ejecutar el script:
```bash
python trayectoria_polar.py
```

---

## Referencias

- Yaskawa. *Motoman MH6 Technical Manual*. Yaskawa Electric Corporation.
- ABB Robotics. *IRB140 Product Specification*. ABB Group.
- RoboDK Inc. *RoboDK Documentation*. https://robodk.com/doc
- Universidad Nacional de Colombia. *Guía Laboratorio No. 02 — Robótica Industrial*. 2026-I.
