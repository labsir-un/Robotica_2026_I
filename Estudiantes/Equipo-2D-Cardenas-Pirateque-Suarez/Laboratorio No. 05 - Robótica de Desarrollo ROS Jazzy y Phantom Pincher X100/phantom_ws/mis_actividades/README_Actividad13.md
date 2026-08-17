# Actividad 13: Enseñanza y Repetición de Poses (Teach & Play)

## 📖 Descripción
En la presente actividad se configura la unidad de procesamiento como un Módulo de Enseñanza (*Teach Pendant*) de nivel industrial para el manipulador robótico Phantom X Pincher X100. 

Dando estricto cumplimiento a los requerimientos de la guía de laboratorio, la interfaz gráfica permite un flujo de trabajo bidireccional completo:
1. **Modo de Enseñanza (Teach):** Permite el posicionamiento espacial del manipulador mediante controladores cinemáticos por software, o alternativamente, la habilitación del estado de rueda libre (*Torque OFF*) para el guiado manual cinestésico.
2. **Captura y Registro:** Facilita la asignación paramétrica de identificadores nominales a las posturas físicas, extrayendo de manera síncrona los valores articulares desde los encoders físicos o la simulación en RViz hacia una matriz secuencial.
3. **Persistencia de Datos (YAML):** Garantiza la exportación e importación del vector de estados a través de archivos `.yaml` nativos, asegurando la trazabilidad y resguardo permanente de las trayectorias operativas.
4. **Modo de Reproducción (Play):** Ejecuta la matriz de estados en orden secuencial, integrando un interpolador dinámico que permite el ajuste paramétrico de la ventana de tiempo de transición temporal entre posturas.
5. **Control de Ejecución:** Incorpora protocolos de interrupción controlada y sistemas de parada de emergencia durante la interpolación de la trayectoria.

---

## 🧠 Lógica de Interpolación y Registro de Poses
El algoritmo fundamenta su captura de datos mediante el registro discreto del espacio articular. Cada coordenada registrada genera un vector de estado $Q = [q_1, q_2, q_3, q_4, q_5]$, el cual es almacenado de manera estructurada bajo el formato estándar de serialización de datos YAML. 

Durante la fase de reproducción (*Playback*), el controlador interpola temporalmente la trayectoria entre el vector de origen $Q_A$ y el vector de destino $Q_B$. El modelo matemático interno asegura que la velocidad geométrica de las articulaciones se escale proporcionalmente al diferencial de tiempo ($\Delta t$) parametrizado por el usuario, mitigando aceleraciones bruscas que puedan comprometer la integridad de los actuadores Dynamixel.

---

## 🛠️ Requisitos
Se requiere la disponibilidad del módulo nativo para la serialización de archivos YAML dentro del entorno de Ubuntu. Se debe ejecutar el siguiente comando para satisfacer las dependencias bajo ROS 2 Jazzy:

```bash
sudo apt update
sudo apt install python3-tk python3-yaml
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la consola de enseñanza
python3 mis_actividades/actividad13.py
```

## 🎯 Interfaz y Flujo de Trabajo
* **1. Entrenamiento Cinestésico (Enseñar):** 
  * Accionar el comando **TORQUE OFF** para deshabilitar la retención magnética y desplazar físicamente el brazo robótico hacia la coordenada espacial objetivo.
  * Ingresar un identificador alfanumérico en el campo "Nombre Pose" (e.g., `Aproximacion_Pieza_1`).
  * Accionar el comando **📸 CAPTURAR Y GUARDAR POSE ACTUAL**. El sistema actualizará de manera automática la matriz secuencial expuesta en el panel lateral.
  * Iterar el procedimiento para estructurar una trayectoria operativa completa.
* **2. Exportación a YAML:** Una vez validada la secuencia, accionar el comando **💾 Guardar YAML**. El algoritmo generará el archivo estructurado en el subdirectorio local `yamls`.
* **3. Reproducción de Trayectoria (Playback):**
  * Accionar el comando **TORQUE ON** para restablecer la rigidez estructural de los servomotores.
  * Parametrizar la ventana temporal de desplazamiento mediante el control de "Tiempo de transición" (e.g., $3.0$ s).
  * Accionar el comando **▶ REPRODUCIR SECUENCIA**. El manipulador ejecutará la interpolación de manera autónoma.
* **4. Entorno de Simulación:** Ante la ausencia temporal de hardware físico, el operador puede emplear los selectores articulares del panel lateral para posicionar el modelo cinemático en el simulador RViz y registrar los vectores de estado con idéntica precisión analítica.

## ⚠️ Consideraciones de Seguridad
* **🚨 PARADA DE EMERGENCIA:** Funcionalidad crítica de máxima prioridad que interrumpe el hilo de reproducción algorítmica y suprime el torque de los actuadores de forma instantánea.
* **Freno Controlado:** El comando **⏹ DETENER REPRODUCCIÓN** permite la finalización suave de la subrutina actual, preservando la tensión estructural en los servomotores y evitando el colapso gravitacional del sistema mecánico.
