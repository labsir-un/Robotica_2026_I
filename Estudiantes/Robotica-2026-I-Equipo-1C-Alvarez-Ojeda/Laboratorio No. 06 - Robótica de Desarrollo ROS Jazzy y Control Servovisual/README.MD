# Robótica - 2026-I - Laboratorio No. 05: Phantom X Pincher X100 – ROS 2 Jazzy – RViz

> Esta práctica de laboratorio se enfoca en el análisis, medición, simulación y control del manipulador Phantom X Pincher X100 utilizando el entorno de ROS 2 Jazzy y RViz. Durante el desarrollo de la práctica se modeló la geometría del robot, se configuró su espacio de trabajo y se implementaron algoritmos para movimientos individuales, simultáneos, secuenciales e interpolados.
> 
> Además, se desarrolló e implementó la cinemática directa e inversa del manipulador, lo que permitió realizar tareas complejas como el trazado de figuras geométricas, rutinas de enseñanza y repetición de poses, culminando con la ejecución de una coreografía robótica sincronizada.

### Integrantes del Equipo
* **[Nombre 1]** - [Correo]
* **[Nombre 2]** - [Correo]

---

### 1. Descripción de la solución planteada

El presente laboratorio aborda el control del manipulador Phantom X Pincher X100. Para ello, se configuró un espacio de trabajo utilizando `colcon` bajo la distribución de ROS 2 Jazzy. La arquitectura del software se dividió principalmente en dos paquetes: `pincher_control` y `pincher_description`.

[Pendiente: Completar descripción de la arquitectura de nodos, comunicación con tópicos y manejo de la interfaz gráfica...]

---

### 2. Estructura del Repositorio

El proyecto fue desarrollado dentro del espacio de trabajo `phantom_ws`. Se han excluido los directorios de compilación y cachés mediante el archivo `.gitignore`. La estructura del código fuente es la siguiente:

<pre>
phantom_ws/
├── lab05_results_A11/
│   └── actividad11_cinematica_directa.csv
├── src/
│   ├── pincher_control/
│   │   ├── config/ 
│   │   │   ├── ax12a.yaml
│   │   │   └── xl430.yaml
│   │   ├── launch/ 
│   │   │   └── pincher_system.launch.py
│   │   ├── pincher_control/ 
│   │   │   ├── control_servo.py
│   │   │   ├── dynamixel_profiles.py
│   │   │   ├── interfazpunto4.py
│   │   │   ├── interfazpunto9.py
│   │   │   ├── interfazpunto13.py
│   │   │   ├── pincher_gui.py
│   │   │   ├── scan_dynamixel.py
│   │   │   └── rutina_guardada.yaml
│   │   ├── package.xml
│   │   └── setup.py
│   └── pincher_description/
│       ├── launch/ 
│       │   ├── display_gui.launch.py
│       │   └── display.launch.py
│       ├── meshes/ 
│       │   └── (Archivos .stl)
│       ├── rviz/ 
│       │   └── pincher.rviz
│       ├── urdf/ 
│       │   └── robot.xacro
│       ├── package.xml
│       └── setup.py
└── docs/ 
</pre>

---

### 3. Identificación y Mediciones del Robot

#### 3.1. Identificación de motores y articulaciones

Se identificaron físicamente los actuadores DYNAMIXEL del manipulador:

| Articulación | ID DYNAMIXEL | Referencia (Modelo) | Sentido Positivo | Función |
|---|:---:|---|---|---|
| **Base** | | | | Rotación del robot respecto al plano horizontal. |
| **Hombro** | | | | Elevación principal del brazo. |
| **Codo** | | | | Extensión y flexión del brazo. |
| **Muñeca** | | | | Orientación del efector final (Pitch). |
| **Pinza** | | | | Apertura y cierre del efector final. |

#### 3.2. Medición del robot y Diagrama Geométrico

Las dimensiones físicas del manipulador se obtuvieron para el modelado cinemático:

* **Altura de la base:** `[ ] mm`
* **Distancia entre eje Base y Hombro:** `[ ] mm`
* **Longitud eslabón Hombro-Codo (L2):** `[ ] mm`
* **Longitud eslabón Codo-Muñeca (L3):** `[ ] mm`
* **Distancia desde la Muñeca hasta el TCP:** `[ ] mm`
* **Dimensiones principales de la pinza:** `[ ] x [ ] mm`

A partir de estas medidas, se construyó el siguiente diagrama geométrico y de sistemas coordenados:

<p align="center">
  <img src="docs/diagrama_geometrico.png" alt="Diagrama geométrico" width="500">
</p>
<p align="center">
  <em>Figura 1. Diagrama de eslabones, dimensiones y sistemas de coordenadas del Phantom X Pincher.</em>
</p>

---

### 4. Determinación de límites seguros

Los límites articulares seguros establecidos experimentalmente para evitar colisiones mecánicas son:

| Articulación | Límite Inferior (grados/rad) | Límite Superior (grados/rad) | Margen de Seguridad |
|---|:---:|:---:|:---:|
| **Base** | | | |
| **Hombro** | | | |
| **Codo** | | | |
| **Muñeca** | | | |
| **Pinza** | | | |

---

### 5. Cinemática del Robot

#### 5.1. Parámetros Denavit-Hartenberg (Cinemática Directa)

Tabla de parámetros DH extraída a partir del diagrama geométrico:

| Articulación ($i$) | $\theta_i$ (Rotación Z) | $d_i$ (Traslación Z) | $a_i$ (Traslación X) | $\alpha_i$ (Rotación X) |
|:---:|:---:|:---:|:---:|:---:|
| **1 (Base)** | $q_1$ | $L_1$ | $0$ | $90^\circ$ |
| **2 (Hombro)** | $q_2$ | $0$ | $L_2$ | $0$ |
| **3 (Codo)** | $q_3$ | $0$ | $L_3$ | $0$ |
| **4 (Muñeca)**| $q_4$ | $0$ | $L_4$ | $0$ |

[Pendiente: Análisis de resultados de cinemática directa y evaluación contra RViz]

#### 5.2. Cinemática Inversa

[Pendiente: Redacción sobre el método de desacople cinemático implementado, filtrado de múltiples soluciones (codo arriba/abajo) y manejo de límites.]

---

### 6. Diagrama de flujo de las acciones del robot

Lógica principal implementada en el paquete `pincher_control`:

<pre>
[Inicio ROS 2 Jazzy]
       │
       ▼
[Cargar YAML de Configuración (ax12a.yaml) y URDF]
       │
       ▼
[Subscripción a JointStates / Publicación en Command]
       │
       ▼
[Menú de Interfaces (interfazpunto4.py, interfazpunto9.py, etc.)]
       │
       ├──► (Movimiento Individual/Simultáneo) ──► Validar Límites ──► Enviar Q a Servos
       │
       ├──► (Cinemática Inversa) ──► Calcular Soluciones ──► Filtrar (Codo Arriba/Abajo) ──► Ejecutar
       │
       └──► (Teach & Play) ──► Leer 'rutina_guardada.yaml' ──► Interpolar Tiempos ──► Ejecutar Secuencia
</pre>

---

### 7. Resultados y Gráficas de Análisis

#### 7.1. Calibración de cero y error articular

<p align="center">
  <img src="docs/grafica_calibracion.png" alt="Gráfica de calibración" width="500">
</p>

[Pendiente: Análisis del error máximo, promedio y desplazamiento de cero calculado.]

#### 7.2. Interpolación de Trayectorias

<p align="center">
  <img src="docs/grafica_interpolacion.png" alt="Gráfica de interpolación" width="500">
</p>

[Pendiente: Comparación de suavidad entre interpolación lineal y cúbica/quíntica.]

#### 7.3. Trayectoria Sinusoidal

<p align="center">
  <img src="docs/grafica_sinusoidal.png" alt="Gráfica sinusoidal" width="500">
</p>

[Pendiente: Tabla de error cuadrático medio para las pruebas de amplitud y frecuencia.]

---

### 8. Plano de Planta de la Tarea de Trazado

<p align="center">
  <img src="docs/plano_planta.png" alt="Plano de planta del entorno" width="500">
</p>
<p align="center">
  <em>Figura 2. Plano de planta y área de alcance para la figura trazada.</em>
</p>

---

### 9. Coreografía y Demostraciones en Video

**Video 1: Funcionalidades base y Trazado**
* 🔗 **Enlace al video:** [Pendiente de subir]

**Video 2: Reto final - Coreografía Robótica**
* 🔗 **Enlace al video:** [Pendiente de subir]

---

### 10. Conclusiones Individuales

**[Nombre 1]:**
> [Redacción pendiente]

**[Nombre 2]:**
> [Redacción pendiente]
