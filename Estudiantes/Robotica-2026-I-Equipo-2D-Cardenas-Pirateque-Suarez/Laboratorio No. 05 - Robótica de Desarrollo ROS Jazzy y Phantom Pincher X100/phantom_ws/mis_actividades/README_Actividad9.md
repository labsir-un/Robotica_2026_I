# Actividad 9: Interpolación de Trayectorias (Lineal vs Cúbica)

## 📖 Descripción
En la presente actividad se implementa una Interfaz Gráfica de Usuario (GUI) orientada a la evaluación y comparación de la suavidad en el desplazamiento del manipulador Phantom X Pincher X100, empleando para ello dos métodos matemáticos distintos: **Interpolación Lineal** e **Interpolación Cúbica**.

En estricto cumplimiento con los requerimientos de la guía de laboratorio, el sistema permite la definición de dos configuraciones articulares distantes (Pose A y Pose B). Al inicializar la rutina, el algoritmo ejecuta de forma secuencial las siguientes fases:
1. **Cálculo Matemático:** Se calculan los vectores de posición para ambas trayectorias, los cuales son exportados automáticamente al archivo local `trayectorias_act9.csv`.
2. **Ejecución Física y/o Simulada:** Se comanda el traslado del manipulador desde su posición de origen (Home) hacia la Pose A, para posteriormente ejecutar la interpolación discreta hacia la Pose B (evaluando primeramente el método lineal, seguido de una repetición bajo el método cúbico). Se incorporan pausas de 3 segundos para garantizar la confirmación de llegada y estabilización del sistema en cada parada.
3. **Análisis Gráfico:** Exclusivamente tras la culminación de la rutina física, se despliega y almacena de forma automática un gráfico (`grafica_act9_todas_articulaciones.png`), en el cual se superponen las trayectorias angulares en función del tiempo para facilitar el análisis comparativo de la suavidad cinemática.

---

## 📐 Fundamento Matemático e Implementación
Para la generación de las trayectorias, el algoritmo calcula los puntos intermedios entre una posición angular inicial ($q_0$) y una posición angular final ($q_f$), abarcando un lapso de tiempo desde $t_0 = 0$ hasta un tiempo final definido como $t_f$.

### 1. Interpolación Lineal (Polinomio de Grado 1)
Este método genera una ruta de velocidad constante entre ambos puntos. La ecuación de posición escalar se define como:

$$q(t) = a_0 + a_1 t$$

Aplicando las condiciones de frontera para la posición inicial ($q(0) = q_0$) y final ($q(t_f) = q_f$), se determinan los coeficientes polinomiales:

$$a_0 = q_0$$
$$a_1 = \frac{q_f - q_0}{t_f}$$

**Consideración Dinámica:** Al derivar la ecuación de posición, se obtiene una velocidad constante equivalente a $a_1$. Esto implica requerimientos de aceleración teóricamente infinitos en los instantes de arranque ($t=0$) y frenado ($t=t_f$). En la implementación física, esto se traduce en sobreesfuerzos mecánicos y movimientos bruscos por parte de los servomotores Dynamixel.

### 2. Interpolación Cúbica (Polinomio de Grado 3)
Con el objetivo de mitigar las discontinuidades de velocidad y garantizar un desplazamiento suave, se implementa un polinomio de tercer grado. Este modelo permite imponer restricciones de velocidad nula en los extremos del movimiento:

$$q(t) = a_0 + a_1 t + a_2 t^2 + a_3 t^3$$

La ecuación de velocidad se obtiene mediante la derivada de la posición con respecto al tiempo:

$$v(t) = \dot{q}(t) = a_1 + 2a_2 t + 3a_3 t^2$$

El modelo exige el cumplimiento de cuatro condiciones de frontera geométricas y cinemáticas:
1. Posición inicial: $q(0) = q_0$
2. Posición final: $q(t_f) = q_f$
3. Velocidad de arranque nula: $v(0) = 0$
4. Velocidad de llegada nula: $v(t_f) = 0$

Al evaluar estas condiciones en las ecuaciones polinomiales, se establece un sistema de ecuaciones cuya resolución define los coeficientes articulares:

$$a_0 = q_0$$
$$a_1 = 0$$
$$a_2 = \frac{3(q_f - q_0)}{t_f^2}$$
$$a_3 = -\frac{2(q_f - q_0)}{t_f^3}$$

**Consideración Dinámica:** La adición de restricciones de velocidad nula genera un perfil de posición en forma de "S". Esto asegura un arranque progresivo y una desaceleración suave en la proximidad del objetivo, optimizando el seguimiento de trayectoria y prolongando la vida útil del hardware robótico.

---

## 🛠️ Requisitos
Para garantizar la estabilidad del sistema en el entorno operativo Ubuntu bajo ROS 2 Jazzy, y prevenir conflictos con el gestor de paquetes de Python, se requiere la instalación de las dependencias a través del repositorio del sistema operativo (`apt`):

```bash
sudo apt update
sudo apt install python3-tk python3-numpy python3-matplotlib
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de interpolación
python3 mis_actividades/actividad9.py
```

## 🎯 Interfaz y Flujo de Trabajo
1. **Configuración de Poses:** Es necesario definir los parámetros angulares de cada articulación correspondientes a la **Pose A (Inicio)** y a la **Pose B (Destino)**. El sistema inicializa por defecto con dos configuraciones espacialmente alejadas, sugeridas en la guía de práctica.
2. **Parámetros Temporales:** Se debe configurar el *Tiempo Total* proyectado para la transición entre las Poses A y B, así como el *Paso (dt)*, el cual determina la resolución temporal (frecuencia de discretización) del algoritmo de interpolación.
3. **Ejecución de la Rutina:** Se debe accionar el control principal de ejecución (**▶ CALCULAR, MOVER ROBOT Y LUEGO GRAFICAR**).
4. **Desarrollo Automático:** A través de la "Consola de Operaciones" integrada, el sistema reportará de manera progresiva el estado de ejecución: traslado a Home, evaluación de la trayectoria Lineal y posterior evaluación de la trayectoria Cúbica, realizando pausas de comprobación de estado estacionario durante cada parada.
5. **Resultados y Visualización:** Al finalizar el ciclo, se desplegará una ventana interactiva de Matplotlib ilustrando el comportamiento temporal de los 5 grados de libertad. Esto permite el análisis empírico y visual de la mitigación de las discontinuidades de velocidad (arranques y paradas bruscas) propia del perfil cúbico, en contraste con la velocidad constante del perfil lineal.

## ⚠️ Consideraciones de Seguridad
* **🚨 PARADA DE EMERGENCIA:** Se dispone de un control superior dedicado cuya activación suprime de forma inmediata el torque de los actuadores e interrumpe el bucle de interpolación de trayectoria.
* **Control Manual y Retorno:** Se incluyen comandos de acceso rápido para la habilitación o deshabilitación manual del torque (Torque ON/OFF) y para forzar un retorno seguro a la configuración de reposo (Home a 0°) de manera previa o posterior a la ejecución de la rutina.
