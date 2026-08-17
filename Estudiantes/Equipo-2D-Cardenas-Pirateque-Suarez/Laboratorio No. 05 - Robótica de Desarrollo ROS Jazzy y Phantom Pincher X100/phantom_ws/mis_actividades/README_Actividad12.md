# Actividad 12: Cinemática Inversa

## 📖 Descripción
En esta actividad se resuelve el problema geométrico de la Cinemática Inversa para el manipulador Phantom X Pincher X100 mediante una Interfaz Gráfica interactiva de usuario (GUI).

En estricto cumplimiento con las exigencias de la guía de laboratorio, el programa permite la inserción de una coordenada espacial objetivo del Efector Final o TCP ($x, y, z$) y un ángulo de ataque o *pitch* ($\Theta$). A partir de esta información espacial, el algoritmo realiza las siguientes operaciones:

1. **Cálculo Analítico:** Determina geométricamente las soluciones articulares posibles mediante la técnica de desacople cinemático.
2. **Bifurcación de Posturas:** Identifica y separa de forma matemática las configuraciones resultantes en posturas de "Codo Arriba" (*Elbow Up*) y "Codo Abajo" (*Elbow Down*).
3. **Restricción de Seguridad:** Descarta algorítmicamente cualquier solución matemática que requiera que un motor exceda los límites seguros experimentales parametrizados en la Actividad 6, previniendo colisiones físicas.
4. **Análisis de Singularidad:** Alerta al operador a través de la consola de diagnóstico si la coordenada solicitada se encuentra fuera del espacio de trabajo (*Workspace*) del manipulador (puntos inalcanzables).
5. **Toma de Decisión Autónoma:** Selecciona y ejecuta automáticamente la solución válida que requiera el menor costo de desplazamiento articular desde la posición actual de reposo.

Adicionalmente, la interfaz integra 5 perfiles cartesianos de prueba pre-programados (tales como posturas de agarre vertical, horizontal y reposo alto) para evaluar el algoritmo de forma integral.

---

## 📐 Fundamento Matemático (Desacople Cinemático)

Para la resolución analítica de la cinemática inversa de un manipulador de 4 grados de libertad (4-DOF), se emplea el método de **Desacople Cinemático**. Este método reduce el análisis espacial 3D a un problema trigonométrico planar 2D.

Dadas las coordenadas objetivo del TCP ($x, y, z$) y el ángulo de ataque de la herramienta ($\Theta$), el modelo matemático se desarrolla de la siguiente manera:

**1. Rotación de la Base ($q_1$):**
El ángulo de la base gobierna la rotación en el plano XY. Se obtiene mediante la proyección polar de las coordenadas cartesianas:
$$q_1 = \text{atan2}(y, x)$$

**2. Posición del Centro de la Muñeca (Wrist Center):**
Conocido el ángulo de ataque $\Theta$ y la longitud del eslabón de la pinza ($L_4$), se retrocede geométricamente a lo largo del plano radial ($r$) y vertical ($z$) para encontrar las coordenadas del Centro de la Muñeca ($r_w, z_w$):
$$r = \sqrt{x^2 + y^2}$$
$$r_w = r - L_4 \cos(\Theta)$$
$$z_w = z - L_1 - L_4 \sin(\Theta)$$
*(Donde $L_1$ representa la altura estructural del eslabón base).*

**3. Solución del Codo ($q_3$):**
Se aplica la Ley de los Cosenos sobre el triángulo formado por los eslabones $L_2$ y $L_3$. Definiendo la distancia al cuadrado desde el hombro hasta el centro de la muñeca como $D^2 = r_w^2 + z_w^2$:
$$\cos(q_3) = \frac{r_w^2 + z_w^2 - L_2^2 - L_3^2}{2 L_2 L_3}$$
Dependiendo del signo seleccionado en la función arcocoseno, se obtienen las dos soluciones físicas:
$$q_3 = \pm \arccos(\cos(q_3))$$
*(El signo positivo/negativo define si la postura resultante corresponde a "Codo Abajo" o "Codo Arriba").*

**4. Solución del Hombro ($q_2$):**
El ángulo del hombro se calcula restando el ángulo interno del triángulo al ángulo de elevación de la muñeca:
$$q_2 = \text{atan2}(z_w, r_w) - \text{atan2}(L_3 \sin(q_3), L_2 + L_3 \cos(q_3))$$

**5. Solución de la Muñeca ($q_4$):**
Dado que la orientación final es producto de la suma de los ángulos del plano vertical, el ángulo del motor de la muñeca se despeja como:
$$q_4 = \Theta - (q_2 + q_3)$$

---

## 🧠 Justificación de la Implementación (Selección de Postura)

El algoritmo implementa un criterio de selección basado en la **Distancia Euclidiana en el Espacio Articular**. Al calcular las soluciones de *Elbow Up* y *Elbow Down*, el sistema verifica ambas contra el diccionario de límites seguros de la Actividad 6. 

Si ambas configuraciones son físicamente válidas (ninguna genera colisión), el script extrae los ángulos actuales medidos por los encoders del robot ($q_{actual}$) y calcula el costo de movimiento $\Delta Q$ para cada solución $k$:

$$\Delta Q_k = \sqrt{\sum_{i=1}^{4} (q_{k,i} - q_{actual, i})^2}$$

El motor de control toma una decisión autónoma seleccionando la trayectoria con el menor $\Delta Q_k$, garantizando el movimiento más rápido, eficiente y con menor estrés dinámico para los actuadores.

---

## 🛠️ Requisitos
Se requiere la disponibilidad de la librería matemática `numpy` y el entorno gráfico `tkinter`. En Ubuntu bajo ROS 2 Jazzy, se instalan de la siguiente manera:

```bash
sudo apt update
sudo apt install python3-tk python3-numpy
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno de ROS 2 y ejecutar el script correspondiente:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de cinemática inversa
python3 mis_actividades/actividad12.py
```

## 🎯 Interfaz y Flujo de Trabajo
1. **Pruebas Rápidas:** Utiliza el menú desplegable superior para cargar automáticamente coordenadas de prueba comunes. Al dar clic en "Cargar Coordenadas", los valores $X, Y, Z$ y $\Theta$ se asignarán de manera automática a los selectores.
2. **Coordenadas Personalizadas:** El usuario puede ingresar manualmente vectores espaciales arbitrarios (en milímetros y grados) para evaluar la robustez del modelo.
3. **Validación y Ejecución:** Al presionar el comando **▶ CALCULAR INVERSA Y MOVER**, el sistema procesa el vector y transmite la orden a la base de datos de control.
4. **Análisis de Consola:** En la sección de estado inferior, el programa despliega su proceso de toma de decisiones:
   * Expone las posturas calculadas (Codo Arriba / Codo Abajo).
   * Indica la validez paramétrica de las mismas (justificando los descartes por límite articular).
   * Confirma la selección del vector articular óptimo (menor distancia euclidiana).
5. **Control de Velocidad:** El usuario dispone de un control deslizable (*slider*) de velocidad para dictaminar el factor de suavidad del interpolador dinámico.

## ⚠️ Herramientas de Seguridad
* **🚨 PARADA DE EMERGENCIA:** Funcionalidad crítica que anula instantáneamente el torque de los motores e interrumpe cualquier comando espacial en progreso.
* **Comandos Directos:** Interfaz rápida destinada a la liberación manual de actuadores (Torque OFF) y al restablecimiento estructural del brazo robótico a la postura de origen (HOME a $0^\circ$).
