# Actividad 11: Cinemática Directa (Parámetros DH)

## 📖 Descripción
En la presente actividad se implementa la Cinemática Directa del manipulador robótico Phantom X Pincher X100, fundamentada en la convención estándar de matrices de transformación de Denavit-Hartenberg (DH). 

En estricto cumplimiento con los lineamientos de la práctica, se establece que el algoritmo obtenga los parámetros Denavit-Hartenberg del robot e implemente la cinemática directa. El sistema debe recibir los valores articulares de los cuatro eslabones principales ($q_1, q_2, q_3, q_4$) y calcular las coordenadas cartesianas espaciales junto con los ángulos de Euler de la herramienta ($x, y, z, roll, pitch, yaw$). 

Adicionalmente, la interfaz permite evaluar la cinemática directa para las cinco configuraciones de la Actividad 7, facilitando la validación matemática al comparar la posición calculada teóricamente con la posición gráfica observada en el simulador RViz.

---

## 📐 Fundamento Matemático (Parámetros DH)

La cinemática directa se resuelve mediante la asignación sistemática de sistemas de referencia a cada eslabón del manipulador. A continuación, se presenta la tabla de parámetros de Denavit-Hartenberg extraída de la arquitectura mecánica del Phantom X Pincher:

| Articulación ($i$) | $\theta_i$ (Angulo en Zi) | $d_i$ (Distancia en Zi) | $a_i$ (Traslación Xi) | $\alpha_i$ (Angulo en Xi) |
| :---: | :---: | :---: | :---: | :---: |
| **1 (Base)** | $\theta_1$ | $L_1$ | $0$ | $-\frac{\pi}{2}$ |
| **2 (Hombro)** | $\theta_2$ | $0$ | $L_2$ | $0^\circ$ |
| **3 (Codo)** | $\theta_3$ | $0$ | $L_3$ | $0^\circ$ |
| **4 (Muñeca)** | $\theta_4$ | $0$ | $L_4$ | $0^\circ$ |

*(Nota: Los términos L1, L2, L3 y L4 corresponden a las longitudes físicas de los eslabones medidas en milímetros).*

### Matrices de Transformación Homogénea
La matriz general de transformación que relaciona el sistema de coordenadas de un eslabón $i$ con respecto al eslabón anterior $i-1$, se define de la siguiente manera:

$$
^{i-1}T_i =
\left\lbrack
\begin{matrix}
\cos\theta_i & -\sin\theta_i\cos\alpha_i & \sin\theta_i\sin\alpha_i & a_i\cos\theta_i \\
\sin\theta_i & \cos\theta_i\cos\alpha_i & -\cos\theta_i\sin\alpha_i & a_i\sin\theta_i \\
0 & \sin\alpha_i & \cos\alpha_i & d_i \\
0 & 0 & 0 & 1
\end{matrix}
\right\rbrack
$$

El modelo cinemático completo se obtiene mediante la premultiplicación encadenada de las matrices individuales, determinando la pose espacial de la herramienta respecto al sistema de coordenadas inercial (Base):

$$
^{0}T_4 = ^{0}T_1 \cdot ^{1}T_2 \cdot ^{2}T_3 \cdot ^{3}T_4
$$

El resultado de este producto matricial genera la matriz $^{0}T_4$, de la cual se extraen directamente las coordenadas cartesianas ($x, y, z$) desde el vector de traslación (última columna), y la orientación espacial (Roll, Pitch, Yaw) mediante la descomposición geométrica de la submatriz de rotación de $3 \times 3$.

### ⚙️ Consideración Geométrica (Offset de Hombro)
Se incorpora un "Offset Geométrico" de forma analítica en el desarrollo del algoritmo. Mecánicamente, la coordenada $0^\circ$ de la articulación del hombro ($\theta_2$) sitúa el eslabón en posición totalmente vertical (apuntando hacia arriba). No obstante, bajo la convención DH estándar, la posición $0^\circ$ se alinea perpendicularmente sobre el eje longitudinal $X_1$. Para conciliar el modelo matemático analítico con la respuesta del hardware físico, se introduce una compensación de fase de $-\frac{\pi}{2}$ radianes ($-90^\circ$) sobre el ángulo $\theta_2$, garantizando un seguimiento exacto en el cálculo tridimensional.

---

## 🛠️ Requisitos
El cálculo matricial avanzado requiere la disponibilidad de la librería `numpy`. Al operar bajo el entorno de Ubuntu con ROS 2 Jazzy, se requiere la instalación de las dependencias mediante el gestor de paquetes del sistema para preservar la integridad del entorno local:

```bash
sudo apt update
sudo apt install python3-tk python3-numpy
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de cinemática directa
python3 mis_actividades/actividad11.py
```

## 🎯 Interfaz y Flujo de Trabajo
1. **Configuraciones de Prueba:** Mediante el menú de selección superior, es posible cargar de manera instantánea cualquiera de las 5 configuraciones de prueba predefinidas (Actividad 7). Al accionar el control "Cargar Configuración", los valores angulares poblarán las variables de entrada automáticamente.
2. **Entrada Manual:** El sistema permite el ingreso manual de vectores articulares ($q_1, q_2, q_3, q_4$) mediante selectores numéricos. El algoritmo restringe estructuralmente la inserción de datos, limitándolos al rango de seguridad definido empíricamente en la Actividad 6.
3. **Cálculo y Movimiento:** Al accionar el comando **▶ MOVER Y CALCULAR CINEMÁTICA**, el sistema despliega dos rutinas concurrentes:
   * Ejecuta el producto matricial de las transformaciones homogéneas e hila la extracción de resultados espaciales.
   * Transmite el comando de vector articular hacia el controlador de hardware o simulador en RViz.
4. **Análisis de Resultados:** El panel de "Resultados Teóricos" se actualiza de forma síncrona, exponiendo las coordenadas cartesianas $x, y, z$ (expresadas en milímetros para efectos de precisión de lectura) y la orientación espacial en ángulos de Euler (Roll, Pitch, Yaw).
5. **Validación Visual:** El procedimiento experimental concluye al contrastar analíticamente los valores teóricos arrojados por el modelo matemático contra el posicionamiento espacial del TCP verificado sobre la retícula tridimensional del simulador RViz.
