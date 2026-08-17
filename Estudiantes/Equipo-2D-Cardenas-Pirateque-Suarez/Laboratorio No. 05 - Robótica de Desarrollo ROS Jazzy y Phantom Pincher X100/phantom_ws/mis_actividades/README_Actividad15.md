# Actividad 15 - Reto Final: Coreografía Robótica Data-Driven

## 📖 Descripción General
Este es el proyecto integrador y el clímax del laboratorio: una **Suite de Coreografía Robótica Data-Driven**. A diferencia de los enfoques tradicionales donde los movimientos se programan paso a paso (hardcoding) o mediante cinemática inversa estática, este sistema dota al Phantom X Pincher de la capacidad de "escuchar" y reaccionar orgánicamente a la música.

Para lograr este nivel de autonomía y sincronización, la Actividad 15 se divide en dos componentes de software fundamentales que trabajan en sinergia: el **Analizador de Audio** (el cerebro matemático) y la **Interfaz de Control Coreográfico** (el ejecutor físico). Cumpliendo estrictamente con los lineamientos del reto final, el robot inicia y finaliza en posiciones seguras, utiliza las 5 articulaciones, respeta los límites de hardware en todo momento y ejecuta rutinas autónomas de más de 45 segundos para las majestuosas obras musicales "Chipi Chipi Chapa Chapa" y "Pedro, Pedro, Pe-".

---

## 🧠 Componente 1: El Analizador de Audio (Pre-procesamiento FFT)

Antes de que el robot pueda bailar, necesita un mapa físico de la canción. El script `analizador_audio.py` utiliza la librería de procesamiento de señales `librosa` para aplicar la **Transformada Rápida de Fourier (FFT)** a los archivos `.mp3`. 

El algoritmo "escucha" la pista y la descompone en 10 fotogramas por segundo (10 Hz), extrayendo tres características vitales:
*   **Energía (RMS / Volumen):** Se normaliza de 0.0 a 1.0 y define la amplitud e intensidad de los barridos de la base y el codo.
*   **Frecuencia (Centroide Espectral):** Captura el brillo y la agudeza del sonido, mapeándose matemáticamente a la elevación del hombro y la muñeca.
*   **Beats (Percusión):** Un detector de transitorios que marca con un `1` lógico los golpes de batería, detonando acciones súbitas como el cierre rápido de la pinza.

El resultado de este análisis se exporta a dos bases de datos que definen el "ADN" de la coreografía: `datos_dubidubidu.csv` y `datos_pedro.csv`.

---

## 🤖 Componente 2: Interfaz de Control Coreográfico

El script principal `actividad15.py` levanta el Centro de Control. Esta interfaz gráfica (GUI) lee los archivos `.csv` generados en el paso anterior y los inyecta en un bucle de control de alta frecuencia (10 Hz). A medida que `pygame` reproduce el audio, el programa lee el fotograma exacto del CSV, calcula la cinemática articular respetando los "Clamps" (límites seguros absolutos) y envía los comandos a los servomotores Dynamixel.

### Características Clave de la Interfaz:
*   **Monitor Cinemático en Vivo:** Dos columnas de datos te permiten auditar el comportamiento del hardware en tiempo real. "Set" muestra el ángulo teórico exigido por la música, mientras que "Read" muestra la posición física real reportada por los encoders del robot.
*   **Selector de Entorno Dinámico:** Permite alternar entre "Simulación (RViz)" y "Robot Físico". El sistema ajusta autónomamente los parámetros de velocidad (150 para proteger el hardware físico, y hasta 378 para máxima fluidez en simulación).
*   **Línea de Tiempo Independiente (Seek):** Sliders gemelos que permiten saltar a cualquier segundo de la canción (tanto en el reproductor de audio como en la postura del robot) para facilitar la depuración de momentos específicos del baile.
*   **Lírica Integrada:** La consola imprime la letra de la canción y las transiciones de estado exactamente en el milisegundo en que ocurren.

---

## 🛠️ Requisitos e Instalación

Debido al procesamiento de señales complejas de audio y la integración de interfaces multimedia, **es de carácter obligatorio el uso de un Entorno Virtual de Python**. Esto aísla las librerías avanzadas y evita la corrupción del entorno global de Ubuntu y ROS 2.

**1. Dependencias del Sistema Operativo:**
```bash
sudo apt update
sudo apt install python3-tk python3-venv
```

**2. Creación y Configuración del Entorno Virtual (Una sola vez):**
```bash
cd ~/ros2_jazzy/Lab5/Codigos/phantom_ws
python3 -m venv mi_entorno
source mi_entorno/bin/activate
pip install librosa numpy pandas pygame pillow
```

---

## 🚀 Flujo de Ejecución del Laboratorio

### Fase 1: Generación del ADN Musical
*Asegúrate de tener los archivos `pedro.mp3` y `dubidubidu.mp3` en la misma carpeta.*
Abre una terminal, activa tu entorno virtual y extrae las características:

```bash
cd ~/ros2_jazzy/Lab5/Codigos/phantom_ws
source mi_entorno/bin/activate
python3 mis_actividades/analizador_audio.py
```
*   **Resultado esperado:** La terminal confirmará la creación de `datos_dubidubidu.csv` y `datos_pedro.csv`.

### Fase 2: Ejecución del Baile
Sin cerrar la terminal (y manteniendo `mi_entorno` activo), lanza la suite principal:

```bash
python3 mis_actividades/actividad15.py
```
*   **Resultado esperado:** Se abrirá el Centro de Control Coreográfico. Selecciona el modo "Físico" o "RViz", haz clic en el póster de tu canción preferida, y observa cómo el Phantom X Pincher cobra vida sincronizado a la perfección con la música.

---

## ⚠️ Protocolos de Seguridad del Hardware
*   **🏠 IR A HOME:** Retorna suavemente todas las articulaciones a su posición de reposo ($0^\circ$).
*   **🛑 DETENER:** Interrumpe el hilo musical, detiene la interpolación de comandos CSV y aterriza el brazo de manera controlada.
*   **🚨 EMERGENCIA:** El nivel de seguridad más alto. Corta el audio, destruye el bucle de datos y desactiva el torque (fuerza electromagnética) de los 5 servomotores de forma instantánea para evitar daños estructurales ante comportamientos oscilatorios imprevistos.
*   **Fade-Out Algorítmico:** Al finalizar los 227 segundos de Dubidubidu o los 120 segundos de Pedro, una ecuación matemática reduce gradualmente las amplitudes de los 5 motores a cero, garantizando que el robot aterrice en la posición segura dictaminada por la guía sin latigazos bruscos.