# Actividad 14: Trazado de Figuras y Letras (RViz)

## 📖 Descripción
En la presente actividad se implementa una Interfaz Gráfica de Usuario (GUI) que configura al manipulador Phantom X Pincher X100 como un trazador cartesiano (*plotter* espacial) dentro del entorno de simulación RViz. 

En estricto cumplimiento con los requerimientos experimentales, el algoritmo facilita el trazado de trayectorias complejas definidas exclusivamente mediante coordenadas cartesianas ($x, y, z$). Dichos vectores espaciales son procesados y resueltos en tiempo real mediante el motor de **Cinemática Inversa** estructurado en las fases previas del proyecto.

El sistema cuenta con la capacidad de ejecutar el trazado continuo de las siguientes geometrías:
1. **Triángulo:** Interpolación lineal entre tres vértices coplanares.
2. **Cuadrado:** Trazado ortogonal de cuatro segmentos equidistantes.
3. **Círculo:** Aproximación paramétrica mediante la interpolación discreta de múltiples puntos iterados sobre la ecuación de una circunferencia.
4. **Iniciales del Equipo:** Generación tipográfica mediante un diccionario vectorial que parametriza los trazos individuales de cada carácter, permitiendo el espaciado dinámico de secuencias alfanuméricas (e.g., 'D', 'S', 'P', 'C', 'F').

### 📍 Lógica de Renderizado y Desplazamiento (Offset Z)
Para la representación visual, el algoritmo pública mensajes de tipo `visualization_msgs/Marker` sobre el tópico de simulación, depositando esferas paramétricas (color cian, $10$ mm de diámetro) que emulan el rastro físico de la herramienta a lo largo del espacio de trabajo tridimensional. 

Adicionalmente, se integra una lógica analítica de control de altura (Offset sobre el eje $Z$), la cual simula la retracción del actuador final ("levantar el lápiz") durante los desplazamientos de transición entre trazos desconectados, previniendo colisiones mecánicas o interpolaciones erróneas sobre el plano de trabajo.

---

## 🛠️ Requisitos
La ejecución de este módulo requiere la integración de las librerías gráficas estándar de Python y la paquetería de visualización tridimensional nativa de ROS 2. Para satisfacer las dependencias en el entorno local, se deben ejecutar los siguientes comandos:

```bash
sudo apt update
sudo apt install python3-tk ros-jazzy-visualization-msgs
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, y garantizando la ejecución previa del simulador RViz con el tópico `/visualization_marker` habilitado, se debe proceder con las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución del motor de trazado
python3 mis_actividades/actividad14.py
```

## 🎯 Interfaz y Flujo de Trabajo
1. **Parametrización Cinética:** Mediante el control de "Tiempo de espera ($\Delta t$)", el operador puede regular la velocidad de interpolación del TCP entre los nodos cartesianos que componen la figura.
2. **Ejecución de Primitivas Geométricas:** Al accionar los comandos dedicados (Triángulo, Cuadrado, Círculo), el algoritmo calcula la matriz de puntos sobre un plano de trabajo predefinido (e.g., $x=140, z=50$) y transmite la secuencia al motor de cinemática inversa para su visualización progresiva en RViz.
3. **Trazado de Cadenas Alfanuméricas:** El sistema permite la inserción de arreglos tipográficos de hasta 5 caracteres (A-Z). Al confirmar la entrada, el algoritmo calcula el espaciado dinámico longitudinal, aplicando automáticamente la retracción en $Z$ entre letras para garantizar un trazado limpio y proporcionado.
4. **Purga del Entorno Visual:** Para mitigar la saturación de la memoria gráfica en el renderizador de RViz, se dispone del comando **🧹 LIMPIAR LIENZO RVIZ**, el cual emite una instrucción `DELETEALL` sobre el tópico de marcadores, restaurando el plano de trabajo a su estado inicial.

## ⚠️ Consideraciones de Seguridad y Control
* **🚨 PARADA DE EMERGENCIA:** Interrupción crítica que aborta el hilo computacional de interpolación de trazado y suprime instantáneamente el torque magnético de los actuadores físicos.
* **🛑 DETENCIÓN CONTROLADA:** Pausa la ejecución de la subrutina algorítmica actual, cediendo el control manual de vuelta al operador sin deshabilitar la retención electromagnética del manipulador.
* **🏠 RESTABLECIMIENTO (HOME):** Comando de retorno autónomo que dirige el brazo robótico hacia su configuración articular geométrica de reposo ($0^\circ$).
