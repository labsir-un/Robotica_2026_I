<div align="center">
  <picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo de la Universidad Nacional de Colombia" width="350px">
  </picture>

  <h1>Laboratorio No. 05 - Robótica</h1>
  <h2>Phantom X Pincher X100 - ROS 2 Jazzy - RViz</h2>

  <p>
    <strong>Robótica - 2026-I</strong><br>
    Ingeniería Mecatrónica<br>
    Facultad de Ingeniería<br>
    Universidad Nacional de Colombia<br>
    Sede Bogotá
  </p>
</div>

## a) Documentación del desarrollo

### Descripción general

En este laboratorio se desarrolló una solución en ROS 2 Jazzy Jalisco para modelar, visualizar y controlar virtualmente el robot Phantom X Pincher X100. El sistema integra tres componentes:

- `pincher_description`: modelo Xacro, mallas STL, configuración de RViz y archivos de lanzamiento.
- `pincher_control`: controlador articular, interfaz gráfica, perfiles DYNAMIXEL y publicación de estados.
- `pincher_lab`: programas correspondientes a las actividades del laboratorio.

El desarrollo se realizó exclusivamente en simulación mediante RViz, donde las actividades 1, 2, 3 y 6 se resolvieron usando el modelo virtual, el archivo Xacro, las mallas STL y la configuración de control, mientras que las actividades 5 y 13, no forman parte del alcance de esta entrega.

Todos los movimientos parten de una configuración segura y, al terminar, llevan el manipulador nuevamente a la posición de referencia:

```text
HOME = [0, 0, 0, 0, 0] rad
```

### Repositorios base

El desarrollo toma como referencia los siguientes repositorios de LabSIR de la Universidad Nacional de Colombia:

- [labsir-un/06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ](https://github.com/labsir-un/06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ): visualización y control del robot en ROS 2 Jazzy.
- [KIT_Phantom_X_Pincher_ROS2](https://github.com/labsir-un/KIT_Phantom_X_Pincher_ROS2): descripción y recursos del kit Phantom X Pincher.
- [3DModels_KIT_Phantom_Pincher_X100](https://github.com/labsir-un/3DModels_KIT_Phantom_Pincher_X100): modelos tridimensionales del manipulador.

### Arquitectura del sistema

El paquete `pincher_control` ejecuta el nodo `/pincher_controller`. Los programas del laboratorio publican comandos articulares en `/pincher/command` y reciben el estado reportado mediante `/joint_states`. El paquete `pincher_description` publica la descripción del robot y las transformaciones utilizadas por RViz.

```mermaid
flowchart TD
    A["Programas de pincher_lab"] --> B["Tópico /pincher/command"]
    B --> C["Nodo /pincher_controller"]
    C --> D["Tópico /joint_states"]
    D --> A
    D --> E["robot_state_publisher"]
    F["robot.xacro y mallas STL"] --> E
    E --> G["Transformaciones TF"]
    G --> H["RViz 2"]
```

#### Nodos principales

| Nodo | Función |
| --- | --- |
| `/pincher_controller` | Recibir comandos, validar el perfil articular y publicar estados. |
| `/pincher_gui` | Enviar posiciones, velocidad, HOME, torque y parada de software. |
| `/robot_state_publisher` | Publicar las transformaciones del modelo Xacro. |
| `/rviz2` | Visualizar el robot, los marcos coordenados y sus movimientos. |

#### Tópicos principales

| Tópico | Tipo | Publicador | Suscriptor | Función |
| --- | --- | --- | --- | --- |
| `/pincher/command` | `sensor_msgs/msg/JointState` | Programas y GUI | `/pincher_controller` | Enviar objetivos articulares. |
| `/joint_states` | `sensor_msgs/msg/JointState` | `/pincher_controller` | Programas y `robot_state_publisher` | Reportar posiciones articulares. |
| `/pincher/status` | `std_msgs/msg/String` | `/pincher_controller` | GUI | Informar el estado del controlador. |
| `/pincher/profile_velocity` | `std_msgs/msg/UInt32` | GUI | `/pincher_controller` | Modificar la velocidad configurada. |

#### Servicios disponibles

| Servicio | Tipo | Función |
| --- | --- | --- |
| `/pincher/home` | `std_srvs/srv/Trigger` | Regresar a la posición de referencia. |
| `/pincher/software_stop` | `std_srvs/srv/Trigger` | Activar la parada de software. |
| `/pincher/torque_enable` | `std_srvs/srv/SetBool` | Habilitar o deshabilitar el torque. |

### Compilación y ejecución

Para la ejecucion y compilacion fue necesario tener configurado un `WorkSpace` de ROS 2 con los paquetes `pincher_control` y `pincher_description` alojados en la carpeta `src`, ver ``Labsir-un/06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ`, esto con el fin de contar con toda la configuración para la manipulacion y control del `Phantom X100`, sobre esta base se tuvo que modificar archivo `dynamixel_profile.py` y los `Modelos STL` dado a que el `Phantom Pincher` del laboratorio es una version antigua el cual cuenta con los servomotores `Dinamixel AX-12A`.

Los codigos implementados para llevar acabo las actividades, son los archivos de python ubicados en la carpeta `pincher_lab`, para la ejecución de los mismos no se requiere que la carpeta este alojada en la misma direccion que el `WS` del Phantom.

Para la replicación del taller se recomienda seguir los siguientes pasos en la terminal:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

El sistema completo se inicia en modo simulado mediante:

```bash
ros2 launch pincher_control pincher_system.launch.py \
  use_hardware:=false \
  use_meshes:=true \
  start_gui:=true \
  start_rviz:=true
```

En otra terminal:

```bash
source /opt/ros/jazzy/setup.bash
source ~/ros2_ws/install/setup.bash
cd ~/ros2_ws/src/Laboratorio5/pincher_lab
python3 actividad04_individual.py
```

El último comando se reemplaza por el programa de la actividad que se desee ejecutar.

---

### Actividad 1. Preparación virtual del robot

La preparación se realizó de manera virtual, donde mediante el archivo `pincher_system.launch.py` inicia:

1. El modelo Xacro.
2. `robot_state_publisher`.
3. RViz 2.
4. El controlador `pincher_controller`.
5. La interfaz gráfica opcional.

Con el fin de verificar que la postura comandada y el modelo correspondan correctamente, se observan los mensajes de /joint_states y las transformaciones TF, teniendo presente la configuración inicial segura, es decir HOME.

El modelo también puede examinarse de forma independiente mediante el siguiente comando:

```bash
ros2 launch pincher_description display_gui.launch.py use_meshes:=true
```

### Actividad 2. Identificación de motores y articulaciones

| Articulación | Nombre ROS 2 | ID | Referencia | Signo configurado | Función |
| --- | --- | ---: | --- | ---: | --- |
| Base | `waist` | 1 | 0 rad | +1 | Orientar el brazo alrededor del eje vertical. |
| Hombro | `shoulder` | 2 | 0 rad | -1 | Elevar o descender el primer eslabón. |
| Codo | `elbow` | 3 | 0 rad | -1 | Flexionar o extender el brazo. |
| Muñeca | `wrist` | 4 | 0 rad | -1 | Ajustar la orientación de la herramienta. |
| Pinza | `gripper` | 5 | 0 rad | +1 | Abrir o cerrar los dedos mediante articulaciones imitadoras. |

El sentido positivo de cada coordenada articular se interpreta mediante la regla de la mano derecha alrededor del eje local definido en el Xacro. La lista `joint_signs` relaciona ese sentido con el giro interno de cada servomotor.

### Actividad 3. Geometría del robot

### Dimensiones estructurales

La geometría del manipulador se obtuvo a partir del archivo `robot.xacro` y de los modelos STL del manipulador.

| Parámetro | Valor |
| --- | ---: |
| Altura de la base | 44,95 mm |
| Distancia Base – Hombro | 44,50 mm |
| Distancia Hombro – Codo | 105,80 mm |
| Distancia Codo – Muñeca | 101,00 mm |
| Distancia Muñeca – TCP | 129,15 mm |


### Longitud de los eslabones

| Eslabón | Longitud |
| --- | ---: |
| Eslabón 1 | 44,50 mm |
| Eslabón 2 | 105,80 mm |
| Eslabón 3 | 101,00 mm |

#### Dimensiones principales de la pinza

| Componente | Dimensiones aproximadas |
| --- | --- |
| Cuerpo de la pinza | 44.000 × 66.449 × 46.700 mm |
| Mecanismo de accionamiento | 20.499 × 5.000 × 36.490 mm |
| Barra de la pinza | 103.488 × 28.000 × 49.250 mm |
| Cada dedo | 55.300 × 16.047 × 29.000 mm |

#### Esquema geométrico

```mermaid
flowchart TD
    A["Base"] --> B["Cintura q1 - eje vertical"]
    B --> C["Hombro q2 - altura 0.08945 m"]
    C --> D["Codo q3 - longitud efectiva 0.10580 m"]
    D --> E["Muñeca q4 - longitud 0.10100 m"]
    E --> F["TCP - desplazamiento final"]
```

### Actividad 4. Movimiento individual de articulaciones

El programa [`actividad04_individual.py`](./src/pincher_lab/actividad04_individual.py) implementa dos modos:

1. Selección manual de una articulación y un ángulo en grados.
2. Prueba automática de todas las articulaciones.

Para la prueba automática utiliza como referencia los angulos:

```text
[20°, -20°, 35°]
```

Donde, cada articulación se mueve de manera independiente a las tres posiciones y regresa a HOME antes de continuar con la siguiente articulacion, en el caso de la pinza fue necesario aplicar un factor de escala de 0.4, esto según el mapeo usado por la visualización.

### Actividad 6. Determinación de límites seguros

Los límites se tomaron del modelo Xacro y se implementaron en `pincher_lab_utils.py` y `pincher_gui.py`.

| Articulación | Límite inferior | Límite superior | Criterio de seguridad |
| --- | ---: | ---: | --- |
| Base | -150° | 150° | Límite del modelo y validación de software. |
| Hombro | -115° | 115° | Límite del modelo y validación de software. |
| Codo | -150° | 150° | Límite del modelo y validación de software. |
| Muñeca | -100° | 100° | Límite del modelo y validación de software. |
| Pinza | -90° | 90° | Límite del modelo y articulaciones imitadoras. |

Al intentar enviar un objetivo exterior al intervalo permitido, `PincherLab.send()` genera un error y evita la publicación. Al tratarse de una simulación, estos límites corresponden al margen operativo definido por el modelo y no a una medición de topes físicos.

### Actividad 7. Movimiento simultáneo

El programa [`actividad07_simultaneo.py`](./src/pincher_lab/actividad07_simultaneo.py) convierte las configuraciones de grados a radianes y publica las cinco articulaciones dentro de un único mensaje `JointState`.

| Configuración | Base | Hombro | Codo | Muñeca | Pinza |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0° | 0° | 0° | 0° | 0° |
| 2 | 25° | 25° | 20° | -20° | 0° |
| 3 | -35° | 35° | -30° | 30° | 0° |
| 4 | 85° | -20° | 55° | 25° | 0° |
| 5 | 80° | -35° | 55° | -45° | 0° |

Después de completar las configuraciones, el programa agrega un último comando HOME.

### Actividad 8. Movimiento secuencial

El programa [`actividad08_secuencial.py`](./src/pincher_lab/actividad08_secuencial.py) utiliza la configuración 2:

```text
[25°, 25°, 20°, -20°, 0°]
```

Las articulaciones se actualizan en el orden:

1. Base.
2. Hombro.
3. Codo.
4. Muñeca.
5. Pinza.

| Criterio | Movimiento simultáneo | Movimiento secuencial |
| --- | --- | --- |
| Tiempo programado | Aproximadamente 2 s por configuración. | Aproximadamente 7.5 s para las cinco articulaciones. |
| Trayectoria del TCP | Cambian todas las coordenadas articulares a la vez. | Se forma una trayectoria por segmentos al mover una articulación por etapa. |
| Suavidad observada | Movimiento coordinado entre articulaciones. | Presenta cambios de dirección entre etapas. |
| Uso principal | Alcanzar una configuración completa. | Visualizar el efecto individual de cada articulación. |

### Actividad 9. Interpolación de trayectorias

El programa [`actividad09_interpolacion.py`](./src/pincher_lab/actividad09_interpolacion.py) desplaza simultáneamente las articulaciones entre:

```text
qi = [0.0, 0.0, 0.0, 0.0, 0.0] rad
qf = [1.2, -0.8, 0.9, 0.5, 0.3] rad
```

Cada tramo dura 3 s y se evalúa a 50 Hz.

#### Interpolación lineal

Sea:

$$
\tau=\frac{t}{T}, \qquad 0\leq \tau\leq 1
$$

La trayectoria lineal se calcula mediante:

$$
q(t)=q_i+\tau(q_f-q_i)
$$

Al implementar la trayetoria del manipulador mediante este método se evidencio una velocidad constante durante el recorrido, pero con cambios abruptos de velocidad al inicio y al final de la trayectoria.

#### Interpolación quíntica

La función de mezcla utilizada es:

$$
s(\tau)=10\tau^3-15\tau^4+6\tau^5
$$

Por tanto:

$$
q(t)=q_i+s(\tau)(q_f-q_i)
$$

Caso contrario al anterior, la interpolación quíntica garantiza velocidad y aceleración nulas en los extremos. 

Cabe recalcar que en la prueba, el movimiento de ida utiliza interpolación lineal y el regreso a HOME utiliza interpolación quíntica, comportamiento que podemos evidenciar mediante la siguiente imagen.

<div align="center">
  <img src="./img/P9.png" alt="Posición angular de la base durante la interpolación lineal y quíntica" width="850"/>
</div>

<p align="center"><em>Figura 1. Movimiento lineal de ida y retorno quíntico de la articulación de la base.</em></p>

La curva lineal alcanza 1.2 rad en $t=3\ \mathrm{s}$. A partir de ese instante comienza el retorno quíntico, cuya pendiente inicia y finaliza suavemente.

### Actividad 10. Trayectoria sinusoidal de una articulación

El programa [`actividad10_sinusoidal.py`](./pincher_lab/actividad10_sinusoidal.py) controla la articulación de la muñeca mediante:

$$
q(t)=q_0+A\sin(2\pi ft)
$$

con:

$$
q_0=0\ \mathrm{rad}
$$

Cada prueba dura 10 s y se ejecuta a 50 Hz.

| Prueba | Amplitud $A$ | Frecuencia $f$ |
| ---: | ---: | ---: |
| 1 | 0.2 rad | 0.1 Hz |
| 2 | 0.2 rad | 0.3 Hz |
| 3 | 0.4 rad | 0.1 Hz |
| 4 | 0.4 rad | 0.3 Hz |

El error instantáneo se define como:

$$
e(t)=q_{\mathrm{deseado}}(t)-q_{\mathrm{reportado}}(t)
$$

El error máximo y la raíz del error cuadrático medio se calculan con:

$$
e_{\max}=\max |e(t)|
$$

$$
\mathrm{RMSE}=
\sqrt{\frac{1}{N}\sum_{k=1}^{N}e_k^2}
$$

En la simulación, `pincher_controller` actualiza el estado simulado inmediatamente después de recibir cada comando. Por esta razón, la posición deseada y la posición reportada prácticamente se superponen, y los errores impresos con cuatro cifras decimales son cercanos a cero.

<table>
  <tr>
    <td align="center">
      <img src="./img/P10_1.png" alt="Trayectoria sinusoidal A igual a 0.2 rad y f igual a 0.1 Hz" width="390"/><br>
      <em>Figura 2. A = 0.2 rad, f = 0.1 Hz.</em>
    </td>
    <td align="center">
      <img src="./img/P10_2.png" alt="Trayectoria sinusoidal A igual a 0.2 rad y f igual a 0.3 Hz" width="390"/><br>
      <em>Figura 3. A = 0.2 rad, f = 0.3 Hz.</em>
    </td>
  </tr>
  <tr>
    <td align="center">
      <img src="./img/P10_3.png" alt="Trayectoria sinusoidal A igual a 0.4 rad y f igual a 0.1 Hz" width="390"/><br>
      <em>Figura 4. A = 0.4 rad, f = 0.1 Hz.</em>
    </td>
    <td align="center">
      <img src="./img/P10_4.png" alt="Trayectoria sinusoidal A igual a 0.4 rad y f igual a 0.3 Hz" width="390"/><br>
      <em>Figura 5. A = 0.4 rad, f = 0.3 Hz.</em>
    </td>
  </tr>
</table>

Las leyendas “posición medida” de las figuras corresponden al estado publicado por la simulación y no a una medición física de los servomotores.

### Actividad 11. Cinemática directa

Para el Phantom X100, el desarrollo de su cinemática directa parte de la formulación de un modelo Denavit-Hartenberg equivalente, construido a partir de la geometría del robot y de los desplazamientos fijos definidos en el archivo Xacro. Con este modelo se establece la relación entre las articulaciones y la pose final del efector.

<div align="center">
  <img src="./Cinematicas/Cinematica%20directa.jpeg" alt="Modelo DH equivalente de la cinemática directa" width="850"/>
</div>

<p align="center"><em>Figura 6. Cinemática directa - Phantom X100.</em></p>

A partir de esta formulación, el manipulador puede representarse mediante el siguiente modelo equivalente:

| $i$ | Elemento | $\theta_i$ | $d_i$ | $a_i$ | $\alpha_i$ |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Base | $q_1$ | $0.08945$ | $0$ | $\pi/2$ |
| 2 | Hombro | $q_2$ | $0$ | $L_r$ | $0$ |
| 3 | Codo | $q_3$ | $0$ | $L_3$ | $0$ |
| 4 | Muñeca | $q_4$ | $0$ | $0$ | $0$ |
| 5 | TCP fijo | $0$ | $0$ | $L_4$ | $0$ |

Para el modelo analítico:

$$
L_r=0.10595\ \mathrm{m},\qquad
L_3=0.10000\ \mathrm{m},\qquad
L_4=0.12915\ \mathrm{m}
$$

La posición del centro de la muñeca se obtiene con:

$$
\rho =
0.10595\cos q_2+
0.10000\cos(q_2+q_3)
$$

$$
x_w=\rho\cos q_1
$$

$$
y_w=\rho\sin q_1
$$

$$
z_w=
0.08945+
0.10595\sin q_2+
0.10000\sin(q_2+q_3)
$$

La orientación depende de la suma articular:

$$
q_{234}=q_2+q_3+q_4
$$

y se expresa mediante:

$$
\mathrm{roll}=
\mathrm{atan2}\left(0,-\cos(q_{234})\right)
$$

$$
\mathrm{pitch}=
\mathrm{atan2}
\left(
-\sin q_{234},
\sqrt{
(\cos q_1\cos q_{234})^2+
(\sin q_1\cos q_{234})^2
}
\right)
$$

$$
\mathrm{yaw}=
\mathrm{atan2}
\left(
\sin q_1\cos q_{234},
\cos q_1\cos q_{234}
\right)
$$

La última fila de la tabla representa una transformación fija posterior a la muñeca. Por ello, el modelo analítico calcula inicialmente la pose en el centro de la muñeca y luego aplica la transformación adicional correspondiente al TCP seleccionado.

En la implementación, esta formulación teórica se llevó al programa [`actividad11_fk.py`](./src/pincher_lab/actividad11_fk.py), el cual recibe:

$$
q_1,\ q_2,\ q_3,\ q_4
$$

y calcula:

$$
x,\ y,\ z,\ \mathrm{roll},\ \mathrm{pitch},\ \mathrm{yaw}
$$

Los valores de $x$, $y$ y $z$ se reportan en el centro de la muñeca, mientras que $q_4$ modifica principalmente la orientación del efector final. Para comparar con RViz, se debe considerar siempre el mismo marco de referencia utilizado en el modelo cinemático.

#### Resultados

| Configuración | $x$ (m) | $y$ (m) | $z$ (m) | Roll (rad) | Pitch (rad) | Yaw (rad) |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | 0.2060 | 0.0000 | 0.0895 | 3.1416 | 0.0000 | 0.0000 |
| 2 | 0.1511 | 0.0705 | 0.2049 | 3.1416 | -0.4363 | 0.4363 |
| 3 | 0.1527 | -0.1069 | 0.1589 | 3.1416 | -0.6109 | -0.6109 |
| 4 | 0.0158 | 0.1808 | 0.1106 | 3.1416 | -1.0472 | 1.4835 |
| 5 | 0.0314 | 0.1780 | 0.0629 | 3.1416 | 0.4363 | 1.3963 |

<div align="center">
  <img src="./img/P11.png" alt="Resultados de la cinemática directa para las cinco configuraciones" width="800"/>
</div>

<p align="center"><em>Figura 7. Resultados calculados por el programa de cinemática directa.</em></p>

Para la configuración 2:

$$
\mathrm{atan2}(y,x) = \mathrm{atan2}(0.0705,0.1511) \approx 25^\circ
$$

Este valor coincide con la orientación horizontal observada en RViz. Las diferencias en distancia aparecen al comparar el centro de la muñeca con el marco `gripper_bar`, por lo que la validación debe realizarse siempre sobre el mismo sistema de referencia.

### Actividad 12. Cinemática inversa

El desarrollo teórico parte de un modelo analítico que considera la geometría del manipulador, el desacople de la muñeca y la reducción del problema a un mecanismo equivalente de dos grados de libertad en el plano de trabajo. A partir de esta formulación se obtienen las soluciones de codo arriba y codo abajo, y posteriormente se selecciona la más conveniente de acuerdo con los límites articulares y la postura actual del robot.

#### Modelo analítico

El programa [`actividad12_ik.py`](./src/pincher_lab/actividad12_ik.py) recibe como entrada:

$$
x_T,\ y_T,\ z_T,\ \theta
$$

Los parámetros del modelo analítico implementado son:

$$
L_1=0.08945\ \mathrm{m},\quad
L_2=0.10000\ \mathrm{m},\quad
L_m=0.03500\ \mathrm{m},\quad
L_3=0.10000\ \mathrm{m},\quad
L_4=0.12915\ \mathrm{m}
$$

#### Ángulo de la base

$$
q_1=\mathrm{atan2}(y_T,x_T)
$$

#### Desacople de muñeca

Las componentes del vector de aproximación de la herramienta son:

$$
a_x=\sin(\theta)\cos(q_1)
$$

$$
a_y=\sin(\theta)\sin(q_1)
$$

$$
a_z=\cos(\theta)
$$

La posición del centro de la muñeca se obtiene al retirar el desplazamiento de la herramienta respecto a la posición objetivo:

$$
x_w=x_T-L_4a_x=x_T-L_4\sin(\theta)\cos(q_1)
$$

$$
y_w=y_T-L_4a_y=y_T-L_4\sin(\theta)\sin(q_1)
$$

$$
z_w=z_T-L_4a_z=z_T-L_4\cos(\theta)
$$

#### Reducción a un mecanismo 2R

$$
r=\sqrt{x_w^2+y_w^2}
$$

$$
h=z_w-L_1
$$

$$
c=\sqrt{r^2+h^2}
$$

con:

$$
L_r=\sqrt{L_2^2+L_m^2}
$$

$$
\beta=\mathrm{atan2}(L_m,L_2)
$$

$$
\psi=\frac{\pi}{2}-\beta
$$

El punto es geométricamente alcanzable si:

$$
|L_r-L_3|\leq c\leq L_r+L_3
$$

Los ángulos auxiliares se calculan como:

$$
\phi=
\arccos
\left(
\frac{L_r^2+L_3^2-c^2}{2L_rL_3}
\right)
$$

$$
\alpha=
\arccos
\left(
\frac{L_r^2+c^2-L_3^2}{2L_rc}
\right)
$$

$$
\gamma=\mathrm{atan2}(h,r)
$$

#### Solución de codo arriba

$$
q_{2a}=
\frac{\pi}{2}-\beta-\alpha-\gamma
$$

$$
q_{3a}=
\pi-\psi-\phi
$$

$$
q_{4a}=
\theta-q_{2a}-q_{3a}-\frac{\pi}{2}
$$

#### Solución de codo abajo

$$
q_{2b}=
\frac{\pi}{2}-(\gamma-\alpha+\beta)
$$

$$
q_{3b}=
-\pi+(\phi-\psi)
$$

$$
q_{4b}=
\theta-q_{2b}-q_{3b}-\frac{\pi}{2}
$$

Los ángulos obtenidos se normalizan al intervalo $[-\pi,\pi)$. Después se descartan las configuraciones que incumplen los límites articulares y, si ambas son válidas, se elige la solución más cercana a la postura actual:

$$
q^*=
\mathrm{arg\,min}_{q\in\{q_a,q_b\}}
\left\|q-q_{\mathrm{actual}}\right\|_2
$$

#### Implementación en el programa

El programa [`actividad12_ik.py`](./src/pincher_lab/actividad12_ik.py) evalúa una posición cartesiana objetivo, calcula las posibles configuraciones articulares y verifica si el punto pertenece al espacio de trabajo del robot. En caso de existir más de una solución válida, el programa identifica las configuraciones de codo arriba y codo abajo, descarta aquellas que exceden los límites articulares y selecciona la más cercana a la postura actual del manipulador.

#### Pruebas cartesianas

| Objetivo $(x,y,z,\theta)$ | Resultado |
| --- | --- |
| $(0.15,0.05,0.15,0.3)$ | Ambas soluciones fuera de límites articulares. |
| $(0.20,0.00,0.10,0.5)$ | Codo arriba; validación geométrica igual a cero. |
| $(0.05,0.15,0.20,-0.2)$ | Codo arriba; validación geométrica igual a cero. |
| $(0.12,-0.06,0.14,0.1)$ | Ambas soluciones fuera de límites articulares. |
| $(0.40,0.40,0.40,0.0)$ | Punto fuera del espacio de trabajo. |

<div align="center">
  <img src="./img/P12.png" alt="Evaluación de cinco objetivos mediante cinemática inversa" width="720"/>
</div>

<p align="center"><em>Figura 8. Selección, validación y descarte de soluciones de cinemática inversa.</em></p>

### Actividad 14. Trazado virtual de una figura

En el programa [`actividad14_trazado.py`](./src/pincher_lab/actividad14_trazado.py) se define un cuadrado de 60 mm por 60 mm mediante cinco puntos cartesianos, donde cada punto se resuelve mediante la cinemática inversa, vista en la Actividad 12.

| Punto | $x$ (m) | $y$ (m) | $z$ (m) | $\theta$ (rad) |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 0.15 | -0.03 | 0.05 | 1.5708 |
| 2 | 0.21 | -0.03 | 0.05 | 1.5708 |
| 3 | 0.21 | 0.03 | 0.05 | 1.5708 |
| 4 | 0.15 | 0.03 | 0.05 | 1.5708 |
| 5 | 0.15 | -0.03 | 0.05 | 1.5708 |

Para cada objetivo:

1. Se calculan las soluciones de codo arriba y codo abajo.
2. Se descartan las que incumplen los límites.
3. Se selecciona la más cercana a la configuración actual.
4. Se interpola en el espacio articular mediante una trayectoria quíntica de 1.5 s.
5. Al cerrar el cuadrado, el robot regresa a HOME mediante otra interpolación quíntica.

### Actividad 15. Reto final: coreografía robótica

La coreografía se implementa mediante el programa [`actividad15_coreografia.py`](./src/pincher_lab/actividad15_coreografia.py), teniendo en cuenta tambien los archivos:

- `poses_coreografia.yaml`: configuraciones articulares.
- `guion.yaml`: tiempos, poses y duración de cada transición.

Donde, el archivo de poses contiene:

| Grupo | Poses |
| --- | --- |
| Seguridad | `neutro` |
| Secuencia izquierda-derecha | `u_izq_alta`, `u_izq_baja`, `u_der_baja`, `u_der_alta` |
| Movimientos altos | `alto_izq`, `alto_der` |
| Movimiento de la herramienta | `pinza_abre`, `pinza_cierra` |

El guion contiene 66 eventos sincronizados y una duración aproximada de 88 s. El programa:

1. Interpola desde la postura actual hasta `neutro`.
2. Espera el instante indicado por cada evento.
3. Ejecuta la transición mediante interpolación quíntica.
4. Utiliza base, hombro, codo, muñeca y pinza.
5. Finaliza nuevamente en `neutro`.

La secuencia supera el mínimo de 45 s y se ejecuta sin intervención manual después de iniciada.

## b) Diagrama de flujo

El siguiente diagrama representa la secuencia general del laboratorio y puede editarse directamente desde el código Markdown.

```mermaid
flowchart TD
    A["Inicio"] --> B["Inicializar ROS 2 Jazzy"]
    B --> C["Cargar Xacro, mallas y RViz"]
    C --> D["Iniciar pincher_controller"]
    D --> E["Publicar estado HOME"]
    E --> F{"Seleccionar actividad"}

    F --> G["Control articular"]
    F --> H["Trayectorias"]
    F --> I["Tareas cartesianas"]

    G --> G1["Movimiento individual - Actividad 4"]
    G1 --> G2["Movimiento simultáneo - Actividad 7"]
    G2 --> G3["Movimiento secuencial - Actividad 8"]

    H --> H1["Interpolación - Actividad 9"]
    H1 --> H2["Trayectoria sinusoidal - Actividad 10"]
    H2 --> H3["Registrar y graficar resultados"]

    I --> I1["Cinemática directa - Actividad 11"]
    I1 --> I2["Cinemática inversa - Actividad 12"]
    I2 --> I3["Trazado cartesiano - Actividad 14"]
    I3 --> I4["Coreografía - Actividad 15"]

    G3 --> J["Validar límites articulares"]
    H3 --> J
    I4 --> J

    J --> K{"¿Comando válido?"}
    K -->|No| L["Descartar e informar"]
    K -->|Sí| M["Publicar en /pincher/command"]
    L --> F
    M --> N["Actualizar /joint_states y TF"]
    N --> O["Visualizar en RViz"]
    O --> P["Regresar a HOME"]
    P --> Q["Cerrar nodos y finalizar"]
```

## c) Código fuente

El código completo se encuentra dentro de la carpeta [`src`](./src), de los cuales los archivos de mayor relevancia son:

### Pincher Control

| Archivo | Función |
| --- | --- |
| `control_servo.py` | Controlador articular en modo virtual o físico. |
| `pincher_gui.py` | Interfaz de control y seguridad. |
| `dynamixel_profiles.py` | Perfiles AX-12A y XL430-W250. |
| `scan_dynamixel.py` | Herramienta opcional de detección de motores físicos. |
| `pincher_system.launch.py` | Lanzamiento integrado del sistema. |

### Pincher Control

| Archivo | Función |
| --- | --- |
| `robot.xacro` | Geometría, articulaciones, límites y mallas. |
| `display.launch.py` | Visualización conectada con el controlador. |
| `display_gui.launch.py` | Inspección manual mediante `joint_state_publisher_gui`. |
| `pincher.rviz` | Configuración de RViz 2. |

### Programas del laboratorio

| Actividad | Archivo |
| ---: | --- |
| 4 | `actividad04_individual.py` |
| 7 | `actividad07_simultaneo.py` |
| 8 | `actividad08_secuencial.py` |
| 9 | `actividad09_interpolacion.py` |
| 10 | `actividad10_sinusoidal.py` |
| 11 | `actividad11_fk.py` |
| 12 | `actividad12_ik.py` |
| 14 | `actividad14_trazado.py` |
| 15 | `actividad15_coreografia.py` |


## d) Plano de planta 
<div align="center">
  <img src="./img/Plano%20de%20planta.png" alt="Plano de planta" width="720"/>
</div>

<p align="center"><em>Figura 9. Planto de planta Phantom X100.</em></p>


## e) Conclusiones individuales

### Pablo de Jesus Arcila Mora

El laboratorio permitió integrar el modelo geométrico del robot con la comunicación de ROS 2 y la visualización en RViz. La separación entre descripción, control y programas de aplicación facilitó probar cada estrategia de movimiento de forma independiente y mantener una posición segura al comenzar y finalizar las pruebas.

### Marco Alejandro Morales Pantoja

El desarrollo de las cinemáticas mostró la importancia de utilizar el mismo sistema coordenado y el mismo TCP al comparar resultados analíticos con RViz. El desacople de muñeca permitió obtener las soluciones de codo arriba y codo abajo, filtrar configuraciones por límites y detectar objetivos fuera del espacio de trabajo.

### Daniel Felipe Castro Galindo

Este fue un laboratorio interesante y retador dado que mediante este aplicamos de una manera mas directa las tematicas abordadas en la clase magistrar debido a que como la interfaz para la manipulacion del Phamtom es simple, tuvimos que definir las trayectorias del manipulador mediante los modelos cinematicos. 


## f) Video explicativo

En el video se presenta el funcionamiento de las actividades desarrolladas, la ejecución de los programas en ROS 2 Jazzy, los resultados de cinemática directa e inversa, el trazado virtual y la coreografía robótica.

<div align="center">
  <a href="https://www.youtube.com/watch?v=hjCt5STNxuI">
    <img src="https://img.youtube.com/vi/hjCt5STNxuI/0.jpg" alt="Video explicativo del Laboratorio No. 05 - Phantom X Pincher X100" width="550"/>
  </a>
</div>

<p align="center">
  <a href="https://www.youtube.com/watch?v=hjCt5STNxuI">
    Ver video completo en YouTube
  </a>
</p>


## g) Referencias

- LabSIR, Universidad Nacional de Colombia. `06_Rob_2026_I_ROS2_Jazzy_PhantomX100_RVIZ`. Visualización y control del Phantom X Pincher X100 en ROS 2 Jazzy.
- LabSIR, Universidad Nacional de Colombia. `KIT_Phantom_X_Pincher_ROS2`. Kit Phantom X Pincher para ROS 2.
- LabSIR, Universidad Nacional de Colombia. `3DModels_KIT_Phantom_Pincher_X100`. Modelos tridimensionales del Phantom X Pincher X100.
- Cychitivav. `px100_ikine`. Cinemática inversa y planificación básica de trayectorias para el PincherX 100.
