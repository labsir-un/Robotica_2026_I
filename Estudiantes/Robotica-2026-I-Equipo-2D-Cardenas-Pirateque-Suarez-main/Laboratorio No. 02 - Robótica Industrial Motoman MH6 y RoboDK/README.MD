<div align="center">
<picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
</picture>

<h1>Laboratorio No. 02 - Robótica Industrial - Análisis y Operación del Manipulador Motoman MH6.</h1>
<h2>Profesores: <br>Pedro Fabián Cárdenas Herrera <br> Manuel Felipe Carranza Montenegro</h2>

<br>
<img src="Images/motoman.png" alt="Motoman" style="border-radius: 5px; width: 200px;"><br>
<b>Figura 1. Manipulador Motoman MH6.</b>
</div>

---

## 1. Introducción

La evolución de la manufactura moderna exige una integración cada vez más profunda de los sistemas robóticos, donde la versatilidad y el conocimiento de múltiples marcas se han convertido en competencias indispensables en la ingeniería. En este contexto, el presente informe documenta el desarrollo del Laboratorio No. 02 del curso de Robótica Industrial, cuyo objetivo principal es la inmersión en la arquitectura, operación y programación del brazo antropomórfico Yaskawa Motoman MH6. Como punto de partida, se establecerá una comparación técnica entre las capacidades de este equipo y las del manipulador ABB IRB 140 (utilizado durante el laboratorio anterior), permitiendo dimensionar las fortalezas y aplicaciones ideales de cada plataforma.

Para operar el Motoman MH6 de manera eficiente y segura dentro de la celda de trabajo, resulta imperativo comprender la disposición de sus articulaciones y sus configuraciones cinemáticas de referencia. Por ello, se analizará en detalle la distinción técnica y funcional entre sus posiciones *Home 1* (posición de transporte) y *Home 2* (cero mecánico de calibración). Asimismo, el desarrollo de la práctica abarca el dominio de la interfaz física de control, el *Teach Pendant*. A través de este dispositivo, se exploran los procedimientos estandarizados para realizar movimientos manuales (jogging), la navegación entre sistemas de coordenadas (articulares y cartesianos), y la correcta gestión de los niveles de velocidad, parámetros críticos para garantizar la integridad tanto del equipo físico como de los operadores durante la puesta a punto.

Más allá de la manipulación manual, la automatización industrial contemporánea depende de herramientas de software robustas que cierren la brecha entre el diseño de trayectorias y la ejecución en planta. En consecuencia, este documento introduce el uso de RoboDK, una potente plataforma de simulación y Programación Fuera de Línea (OLP) que destaca por su compatibilidad con múltiples fabricantes. Se abordarán sus aplicaciones fundamentales, su método de comunicación en línea con el controlador del Motoman, y se presentará un análisis crítico de sus ventajas, limitaciones y enfoques de uso frente a entornos de simulación propietarios y de alta fidelidad como RobotStudio.

Finalmente, como culminación práctica de la sesión, se expone el diseño, simulación y ejecución de una trayectoria paramétrica polar. Este ejercicio no solo valida los conceptos de cinemática inversa y generación de trayectorias, sino que demuestra la viabilidad técnica de comandar movimientos complejos desde un computador hacia el manipulador Motoman MH6 real, consolidando un flujo de trabajo integral desde la estructuración del código en RoboDK hasta la respuesta física del robot en el laboratorio.

## 2. Comparación: Motoman MH6 vs ABB IRB140

En el desarrollo de competencias en robótica industrial, es esencial familiarizarse con diversas arquitecturas y entornos de programación. Puesto que a lo largo del curso se han utilizado los manipuladores ABB IRB140 y Yaskawa Motoman MH6, resulta importante identificar las diferencias entre ambos. A pesar de que los dos equipos pertenecen a la clasificación de brazos de estructura articulada vertical y comparten una carga útil máxima de 6 kg, presentan variaciones técnicas significativas en sus dimensiones, velocidades y rangos de movimiento, tal como se detalla a continuación en el siguiente análisis estructurado:

### 2.1 Datos Generales y Alcance

<br>
<div align="center">

| Característica | **Motoman MH6** | **ABB IRB140** |
| :--- | :--- | :--- |
| **Fabricante** | Yaskawa Motoman | ABB |
| **Modelo Oficial** | YR-MH00006-A00 | IRB 140-6/0.8 |
| **Estructura** | Articulada vertical | Articulada vertical |
| **Grados de libertad (ejes)** | **6 + 2 externos** | 6 |
| **Carga máxima (payload)** | 6 kg | 6 kg |
| **Alcance horizontal máximo** | 1.422 mm | 810 mm |
| **Alcance vertical máximo** | 2.486 mm | 1.243 mm (aprox.) |
| **Repetibilidad (ISO)** | ±0,08 mm | ±0,03 mm |
| **Peso del manipulador** | ~130 kg | 98 kg |
| **Controlador** | DX100 | IRC5 |
| **Montajes disponibles** | Suelo, pared, techo | Suelo, invertido, pared (cualquier ángulo) |
| **Temperatura de operación** | 0°C a +45°C | +5°C a +45°C |
| **Humedad relativa máxima** | 95% | 95% (temperatura constante) |
| **Nivel de protección** | IP54 | IP67 (todas las variantes) |
| **Consumo de potencia** | 1.5 kVA (promedio) | 0.44 kW a 1000 mm/s |
| **Aceleración máx. TCP** | No especificada por fabricante | 57 m/s² |
| **Software de programación** | MotoSim EG, RoboDK | RobotStudio, RoboDK |
| **Lenguaje de programación** | INFORM III / Python | RAPID |

</div>
<br>

**Análisis:** La diferencia de escala es evidente. El Motoman MH6 posee un volumen de trabajo significativamente mayor, logrando casi el doble de alcance vertical y horizontal frente al IRB140, sacrificando a cambio un poco de precisión (repetibilidad de ±0.08mm vs ±0.03mm) y requiriendo un chasis más pesado (130 kg). El detalle más importante radica en los **dos ejes externos adicionales** que posee la celda del Motoman, otorgando un nivel de configuración superior para posicionadores o rieles en comparación al estándar de 6 ejes del ABB.

### 2.2 Rangos de Movimiento por Eje

<br>
<div align="center">

| Eje | **Motoman MH6** | **ABB IRB140** |
| :--- | :--- | :--- |
| **Eje 1 (S - giro base)** | ±170° | +180° / -180° |
| **Eje 2 (L - brazo inferior)**| +155° / -90° | +110° / -90° |
| **Eje 3 (U - brazo superior)**| +250° / -175° | +50° / -230° |
| **Eje 4 (R - rotación muñeca)**| ±180° | ±200° (por defecto) |
| **Eje 5 (B - pitch/yaw)** | +225° / -45° | ±115° |
| **Eje 6 (T - giro muñeca)** | ±360° | ±400° (por defecto) |

</div>
<br>

**Análisis:** Es interesante notar cómo se distribuyen los movimientos. El Motoman MH6 presenta un rango excepcionalmente amplio en el Eje 3 (+250°/-175°) permitiéndole articularse sobre sí mismo de maneras muy flexibles para alcanzar puntos lejanos, mientras que el ABB IRB140 compensa con mayor rotación en la muñeca (Ejes 4 y 6), facilitando maniobras ágiles con la herramienta en espacios reducidos sin riesgo de enredos.

### 2.3 Velocidades Máximas por Eje

<br>
<div align="center">

| Eje | **Motoman MH6** | **ABB IRB140** |
| :--- | :--- | :--- |
| **Eje 1 (S)** | 220 °/s | 200 °/s |
| **Eje 2 (L)** | 200 °/s | 200 °/s |
| **Eje 3 (U)** | 220 °/s | 260 °/s |
| **Eje 4 (R)** | 410 °/s | 360 °/s |
| **Eje 5 (B)** | 410 °/s | 360 °/s |
| **Eje 6 (T)** | 610 °/s | 450 °/s |

</div>
<br>

**Análisis:** En términos de dinámica, el Motoman MH6 es notablemente más rápido en su muñeca (Ejes 4, 5 y 6), alcanzando hasta 610 °/s en el giro de la herramienta. Esto lo hace muy eficiente para reposicionamientos constantes en procesos como soldadura. El ABB IRB140, por su parte, mantiene un equilibrio en todo el brazo, destacando en la velocidad del Eje 3 (260 °/s).

### 2.4 Aplicaciones Típicas

<br>
<div align="center">

| **Motoman MH6** | **ABB IRB140** |
| :--- | :--- |
| Soldadura por arco y láser | Soldadura por arco |
| Ensamble | Ensamble de piezas |
| Paletizado y empaque | Mecanizado |
| Alimentación de máquinas CNC | Manipulación de piezas |
| Manejo de materiales | Dispensado / pegamento |
| Aplicaciones multipropósito | Sala limpia (variante Clean Room, ISO clase 6) |
| — | Fundición (variante Foundry Plus 2) |

</div>
<br>

**Análisis final:** Al observar las aplicaciones ideales, el ABB IRB140 sobresale en entornos que demandan control minucioso o ambientes especializados (Clean Room, Foundry), donde su alta precisión y tamaño compacto son vitales. En contraposición, la robustez, el extenso alcance y la velocidad en la muñeca del Motoman MH6 lo consolidan como un manipulador versátil (multipropósito) ideal para operaciones a mayor escala como paletizado, empaque y soldadura láser.

## 3. Configuraciones Home 1 y Home 2 del Motoman MH6

En la programación y operación del manipulador Motoman MH6, se establecen dos posiciones de referencia predefinidas en el controlador denominadas *Home 1* y *Home 2*. Estas configuraciones articulares son fundamentales dentro de la celda de manufactura, ya que sirven como puntos seguros de inicio, finalización de rutinas y verificación del sistema de coordenadas. A continuación, se detalla la posición de cada articulación en ambas configuraciones para dar cumplimiento a los requerimientos del análisis.

### 3.1 Home 1 (Work Home Position)

La posición *Home 1* constituye la postura base o neutral de trabajo del manipulador. Físicamente, en esta configuración el eje U (Upper Arm) se orienta de forma horizontal y el eje R (Rotate) queda en posición vertical, resultando en una postura de reposo característica. Esta configuración facilita las verificaciones rápidas del área de trabajo, minimiza los torques estáticos sobre los actuadores y es comúnmente empleada como posición de inicio (*Origin*) en aplicaciones de embalaje y manipulación de materiales.

Los valores de las articulaciones para esta posición, expresados en pulsos de encoder tal como los reporta el controlador DX100, son los siguientes:

<br>
<div align="center">

| Articulación | Denominación | Origen (pulsos) | Actual (pulsos) |
| :---: | :---: | :---: | :---: |
| **Eje 1** | S (Shoulder/Base) | 0 | 1 |
| **Eje 2** | L (Lower Arm) | −115.290 | −115.291 |
| **Eje 3** | U (Upper Arm) | −111.622 | −111.621 |
| **Eje 4** | R (Rotate) | 1 | 0 |
| **Eje 5** | B (Bend) | 42.647 | 42.646 |
| **Eje 6** | T (Twist/Tool) | 1.392 | 1.393 |

</div>
<br>

> *Nota técnica: La columna "Actual" corresponde a la posición medida en el Teach Pendant al momento de la captura. La desviación máxima respecto al origen es de apenas ±1 pulso, lo que confirma una excelente calibración del sistema.*

<br>
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="Images/home1.png" alt="Home 1 físico" width="350"><br>
        <b>Figura 2. Vista física del manipulador en configuración Home 1.</b>
      </td>
      <td align="center">
        <img src="Images/tp_home1.jpeg" alt="Teach Pendant Home 1" width="350"><br>
        <b>Figura 3. Interfaz del Teach Pendant mostrando los pulsos para Home 1 (Work Home Position).</b>
      </td>
    </tr>
  </table>
</div>
<br>

### 3.2 Home 2 (Second Home Position)

La posición *Home 2* corresponde a una postura elevada y retraída. En esta configuración, el brazo adopta una geometría casi extendida verticalmente, lo cual proporciona un amplio espacio de acceso a los elementos mecánicos del robot. Por su naturaleza compacta frente al entorno, está diseñada específicamente para operaciones de mantenimiento, cambio seguro de efectores finales (herramientas) y para el tránsito libre del manipulador reduciendo el riesgo de colisiones.

Los valores de las articulaciones para esta posición, que se acercan considerablemente al cero mecánico en los ejes principales, son los siguientes:

<br>
<div align="center">

| Articulación | Denominación | Especificado (pulsos) | Actual (pulsos) | Diferencia |
| :---: | :---: | :---: | :---: | :---: |
| **Eje 1** | S (Shoulder/Base) | 0 | 0 | 0 |
| **Eje 2** | L (Lower Arm) | 2.037 | 2.037 | 0 |
| **Eje 3** | U (Upper Arm) | 2.359 | 2.359 | 0 |
| **Eje 4** | R (Rotate) | 0 | 0 | 0 |
| **Eje 5** | B (Bend) | −121 | −121 | 0 |
| **Eje 6** | T (Twist/Tool) | 1.392 | 1.392 | 0 |

</div>
<br>

> *Nota técnica: Los valores de los ejes L, U y B próximos a cero evidencian la postura extendida. La diferencia nula (0) en todas las articulaciones demuestra que el robot alcanzó exactamente el target especificado en la memoria del controlador.*

<br>
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="Images/home2.png" alt="Home 2 físico" width="350"><br>
        <b>Figura 4. Vista física del manipulador en configuración Home 2 (Postura de mantenimiento).</b>
      </td>
      <td align="center">
        <img src="Images/tp_home2.jpeg" alt="Teach Pendant Home 2" width="350"><br>
        <b>Figura 5. Interfaz del Teach Pendant mostrando los pulsos para Home 2 (Second Home Position).</b>
      </td>
    </tr>
  </table>
</div>
<br>

### 3.3 Análisis: ¿Cuál posición es óptima?

Respondiendo a la interrogante sobre cuál de las dos configuraciones es mejor, la respuesta depende estrictamente del escenario de uso, sin embargo, desde el punto de vista operativo estándar, **el Home 1 representa la posición óptima** como referencia habitual para la celda de manufactura. 

Esta elección se fundamenta técnica y mecánicamente en los siguientes criterios:

1. **Minimización de Torques Gravitacionales:** Al mantener el antebrazo horizontal y el brazo compensado, la postura del *Home 1* distribuye de forma equilibrada las cargas gravitacionales sobre los actuadores. Esto reduce drásticamente el torque estático que deben soportar los frenos eléctricos de los motores mientras el robot está inactivo, prolongando su vida útil.
2. **Referencia de Calibración:** Al estar predefinida como el origen de trabajo, facilita la verificación visual y de software de la calibración del robot, permitiendo detectar de forma temprana desvíos en la repetibilidad antes de iniciar la producción.
3. **Coherencia de Ciclo:** La programación industrial exige puntos de inicio y retorno predecibles. El *Home 1* sitúa la herramienta en una zona media de fácil acercamiento a las mesas de trabajo, optimizando los tiempos de ciclo.

Por el contrario, el **Home 2 no es ideal para el reposo continuo**, sino que debe reservarse exclusivamente como una posición transitoria de servicio (mantenimiento preventivo, ajuste de herramental o resguardo en caso de ingreso de personal a la celda), donde su postura elevada garantiza la seguridad espacial.

## 4. Movimientos Manuales, modos, traslaciones y rotaciones 

La operación segura y precisa del manipulador Motoman MH6 requiere un conocimiento profundo de su interfaz física y de los protocolos de habilitación. Para este laboratorio, el control manual se realiza a través del terminal de programación portátil (*Teach Pendant*) asociado al controlador DX100.

<br>
<div align="center">
  <img src="Images/teachp2.png" alt="Interfaz del Teach Pendant" width="450">
  <br>
  <b>Figura 6. Elementos principales de control, seguridad y ejes externos en el Teach Pendant.</b>
</div>
<br>

### 4.1 Procedimiento de Encendido y Activación del Sistema

Antes de realizar cualquier desplazamiento, es imperativo seguir una secuencia de energización y configuración para garantizar que el sistema responda correctamente a los comandos:

1. **Energización de Potencia:** Se deben activar los *breakers* identificados como "MOTOMAN" en el tablero eléctrico principal de la celda y posteriormente el interruptor totalizador.
2. **Arranque del Controlador:** Girar la perilla de encendido en el cofre del controlador DX100.
3. **Preparación del Teach Pendant:** Liberar el botón de parada de emergencia (*E-Stop*) girándolo en sentido horario y verificar que el selector de modo se encuentre en la posición **TEACH**.
4. **Habilitación de Servos:** Navegar al menú "Robot" en la interfaz. Para energizar los motores, se debe presionar el botón **[SERVO ON READY]** mientras se mantiene pulsado a media carrera el interruptor de hombre muerto (*Deadman switch*) en la parte posterior del terminal. El LED de confirmación indicará que el robot está listo para moverse.

<br>
<div align="center">
  <table>
    <tr>
      <td align="center">
        <img src="Images/controlador_encendido.png" width="180"><br>
        <b>Figura 7. Perilla de encendido DX100.</b>
      </td>
      <td align="center">
        <img src="Images/paro_emergencia.png" width="180"><br>
        <b>Figura 8. Botón de paro de emergencia.</b>
      </td>
      <td align="center">
        <img src="Images/selector_modo_tp.png" width="160"><br>
        <b>Figura 9. Selector de modo TEACH.</b>
      </td>
      <td align="center">
        <img src="Images/habilitacion_servos.png" width="200"><br>
        <b>Figura 10. Activación de servos.</b>
      </td>
    </tr>
  </table>
</div>
<br>

### 4.2 Movimiento por Articulaciones (Modo JOINT)

En el modo articular, el control se ejerce sobre cada uno de los seis motores de forma independiente. Es el modo más intuitivo para alejar al robot de configuraciones singulares o para desplazamientos que no requieren una trayectoria rectilínea del efector final.

**Procedimiento de ejecución:**
* Presionar la tecla **[COORD]** hasta visualizar el icono de modo articular (JOINT) en la pantalla.
* Mantener presionado el interruptor de hombre muerto.
* Presionar simultáneamente la tecla **[L-SHIFT]** junto con la tecla del eje deseado (**S, L, U, R, B, T**).

<br>
<div align="center">
  <img src="Images/mov_articular.png" alt="Esquema de Movimiento de Articulaciones" width="550">
  <br>
  <b>Figura 11. Representación gráfica del movimiento por articulaciones (S, L, U, R, B, T).</b>
</div>
<br>

<div align="center">

| Articulación | Denominación | Sentido Positivo | Sentido Negativo |
| :---: | :--- | :---: | :---: |
| **Eje 1** | S (Shoulder/Base) | `[L-SHIFT] + [S+]` | `[L-SHIFT] + [S-]` |
| **Eje 2** | L (Lower Arm) | `[L-SHIFT] + [L+]` | `[L-SHIFT] + [L-]` |
| **Eje 3** | U (Upper Arm) | `[L-SHIFT] + [U+]` | `[L-SHIFT] + [U-]` |
| **Eje 4** | R (Rotate) | `[L-SHIFT] + [R+]` | `[L-SHIFT] + [R-]` |
| **Eje 5** | B (Bend) | `[L-SHIFT] + [B+]` | `[L-SHIFT] + [B-]` |
| **Eje 6** | T (Twist/Tool) | `[L-SHIFT] + [T+]` | `[L-SHIFT] + [T-]` |

</div>
<br>

### 4.3 Movimiento Cartesiano (Modo XYZ) y Selección de Coordenadas

Este modo permite desplazar el Punto Central de la Herramienta (TCP) a lo largo de líneas rectas respecto a un sistema de coordenadas definido, usualmente la **BASE** del robot o la **TOOL** (herramienta). Es indispensable para aproximaciones precisas a objetos o para seguir bordes lineales.

**Cambio de sistema de referencia:**
Mediante pulsaciones sucesivas de la tecla **[COORD]**, el operador puede alternar entre los distintos sistemas de coordenadas. La pantalla del *Teach Pendant* mostrará el icono correspondiente al sistema activo en ese momento:

<br>
<div align="center">
  <img src="Images/seleccion_coordenadas.png" alt="Selección de Coordenadas" width="350">
  <br>
  <b>Figura 12. Iconos de selección de coordenadas mediante la tecla COORD.</b>
</div>
<br>

<div align="center">
  <img src="Images/mov_cartesiano.png" alt="Esquema de Movimiento Cartesiano" width="450">
  <br>
  <b>Figura 13. Representación del movimiento en el espacio de trabajo (Coordenadas Cartesianas/Base).</b>
</div>
<br>

### 4.4 Traslaciones y Rotaciones en el Espacio Cartesiano

Una vez seleccionado el modo cartesiano (XYZ) o de herramienta (TOOL), las teclas de movimiento cambian su función de control articular a control espacial. En este estado, el controlador ejecuta automáticamente la cinemática inversa para coordinar todos los motores y producir un movimiento lineal o una rotación pura sobre el TCP.

#### 4.4.1 Traslaciones Lineales
Las traslaciones desplazan el TCP manteniendo constante la orientación de la herramienta:

<br>
<div align="center">

| Dirección de Movimiento | Combinación de Teclas |
| :--- | :--- |
| Desplazamiento en **+X / -X** | `[L-SHIFT] + [X+]` / `[L-SHIFT] + [X-]` |
| Desplazamiento en **+Y / -Y** | `[L-SHIFT] + [Y+]` / `[L-SHIFT] + [Y-]` |
| Desplazamiento en **+Z / -Z** | `[L-SHIFT] + [Z+]` / `[L-SHIFT] + [Z-]` |

</div>
<br>

#### 4.4.2 Rotaciones y Coordenadas de Herramienta (TOOL)
Las rotaciones permiten girar la herramienta alrededor de los ejes X, Y o Z, manteniendo el TCP en una posición fija en el espacio. Cuando se selecciona específicamente el sistema **TOOL**, los ejes X, Y, Z se alinean con la geometría del efector final, facilitando aproximaciones directas hacia la pieza de trabajo.

<br>
<div align="center">
  <img src="Images/mov_herramienta.png" alt="Esquema de Coordenadas de Herramienta" width="550">
  <br>
  <b>Figura 14. Movimientos espaciales referenciados al sistema de Coordenadas de Herramienta (TOOL).</b>
</div>
<br>

<div align="center">

| Eje de Rotación | Combinación de Teclas |
| :--- | :--- |
| Rotación en **+Rx / -Rx** | `[L-SHIFT] + [Rx+]` / `[L-SHIFT] + [Rx-]` |
| Rotación en **+Ry / -Ry** | `[L-SHIFT] + [Ry+]` / `[L-SHIFT] + [Ry-]` |
| Rotación en **+Rz / -Rz** | `[L-SHIFT] + [Rz+]` / `[L-SHIFT] + [Rz-]` |

</div>
<br>


## 5. Niveles de Velocidad para Movimientos Manuales

Durante la operación manual del manipulador Motoman MH6, la gestión de la velocidad de desplazamiento (*Jog Speed*) es un factor crítico que vincula la eficiencia operativa con la seguridad industrial. El controlador DX100 permite ajustar este parámetro para adaptarse a las diferentes etapas del proceso de enseñanza (*Teaching*), desde aproximaciones milimétricas hasta traslaciones rápidas en áreas despejadas.

### 5.1 Caracterización de los Niveles de Velocidad (Modo TEACH)

El sistema dispone de cuatro niveles preestablecidos que limitan la velocidad máxima de los motores al accionar las teclas de movimiento. La siguiente tabla detalla la función y el uso recomendado para cada nivel:

<br>
<div align="center">

| Nivel | Denominación | Característica Técnica | Aplicación en Laboratorio |
| :---: | :---: | :---: | :--- |
| **1** | **INCHING** | Avance por pulsos (< 1 mm/s) | Posicionamiento de extrema precisión y calibración de puntos finos. |
| **2** | **SLOW** | Velocidad Baja (≈ 1–20 mm/s) | Aproximación segura a la pieza de trabajo o zonas con posibles obstáculos. |
| **3** | **MEDIUM** | Velocidad Media (≈ 20–150 mm/s) | Desplazamientos generales controlados dentro de la celda de manufactura. |
| **4** | **FAST** | Velocidad Alta (≈ 150–300+ mm/s) | Traslaciones de gran amplitud en zonas completamente libres de interferencias. |

</div>
<br>

### 5.2 Control y Ajuste de Velocidad

El ajuste de la velocidad no requiere navegar por menús complejos; se realiza de forma directa mediante teclas dedicadas en el panel central del *Teach Pendant*. Este diseño permite al operador reaccionar rápidamente ante cambios en el entorno de la celda:

* **Tecla [FAST] (▲):** Incrementa el nivel de velocidad un paso por cada pulsación.
* **Tecla [SLOW] (▼):** Reduce el nivel de velocidad un paso por cada pulsación.

<br>
<div align="center">
  <img src="Images/teclas_control_velocidad.png" alt="Botones de selección de velocidad" width="450">
  <br>
  <b>Figura 15. Teclas dedicadas FAST y SLOW para el ajuste dinámico de la velocidad de Jogging.</b>
</div>
<br>

### 5.3 Identificación del Nivel en la Interfaz

Para garantizar una operación consciente, el nivel de velocidad activo se muestra permanentemente en la barra de estado superior de la interfaz del DX100. El operador puede identificar la configuración actual mediante dos indicadores visuales:

1. **Icono de Jog:** Una barra progresiva que indica visualmente si se encuentra en niveles bajos o altos.
2. **Valor Porcentual:** Un indicador numérico (típicamente 5%, 25%, 50% o 100%) que escala la capacidad dinámica del robot para el modo manual.

<br>
<div align="center">
  <img src="Images/niveles_velocidad_pantalla.png" alt="Indicadores de velocidad en interfaz" width="300">
  <br>
  <b>Figura 16. Visualización de los niveles de velocidad y porcentajes en la pantalla del Teach Pendant.</b>
</div>
<br>

### 5.4 Criterios de Seguridad Operacional

La selección de la velocidad debe seguir protocolos estrictos para evitar colisiones o situaciones de riesgo:

* **Aproximación Progresiva:** Al acercarse al objetivo (target), se debe conmutar a niveles *SLOW* o *INCHING* para evitar errores de percepción de profundidad.
* **Validación de Trayectoria:** En las primeras pruebas de un programa (modo *Play*), se utiliza el **Speed Override** (generalmente iniciando al 5% o 10%) para verificar que la trayectoria simulada en RoboDK coincide con el entorno físico antes de operar a velocidad nominal.
* **Visibilidad Total:** El uso de la velocidad *FAST* queda restringido a momentos donde el operador tiene una línea de visión clara y total sobre todos los ejes del brazo y posibles obstáculos.


## 6. Software RoboDK – Aplicaciones y Comunicación

RoboDK es un potente software de simulación y programación de robots industriales diseñado para ser compatible con más de 40 fabricantes de robots incluyendo Yaskawa/Motoman, ABB, KUKA, Universal Robots, entre otros. Sus aplicaciones principales en el entorno industrial y académico incluyen:

- Programación Fuera de Línea (Offline Programming - OLP): Permite diseñar, simular y programar el robot en un entorno virtual tridimensional sin necesidad de detener la máquina física en la línea de producción.

- Simulación de trayectorias y validación: Sirve para verificar alcances, detectar posibles colisiones entre el brazo, la herramienta y el entorno, y evitar singularidades articulares antes de ejecutar el movimiento real.

- Manufactura avanzada: Es ampliamente utilizado para generar trayectorias complejas a partir de modelos CAD/CAM para aplicaciones como fresado robótico, impresión 3D, soldadura, pintura, y operaciones de pick and place (recoger y colocar).

Para que el manipulador físico realice los movimientos simulados, RoboDK actúa como un "traductor". A nivel interno, el software calcula la cinemática inversa para transformar las coordenadas cartesianas y trayectorias del entorno virtual en los ángulos específicos requeridos por las articulaciones del robot.

El elemento clave que hace posible el movimiento es el Post-procesador. Dado que cada fabricante de robots tiene su propio lenguaje de programación (por ejemplo, código INFORM para Yaskawa/Motoman o RAPID para ABB), el post-procesador de RoboDK toma las instrucciones genéricas de la simulación y genera automáticamente un archivo de código en el lenguaje nativo del controlador del robot específico que se está utilizando.

La comunicación entre el software en el PC y el controlador del robot se puede realizar mediante dos métodos principales:

**Comunicación Fuera de Línea (Generación de programas):** RoboDK compila el programa a través de su post-procesador y genera un archivo de código. Este archivo se transfiere al controlador del manipulador de forma manual mediante una memoria USB o a través de una red local usando un protocolo FTP. Una vez cargado, el robot lo ejecuta de forma autónoma.

**Comunicación en Línea (Robot Drivers / Modo Online):** Este es el método utilizado durante el desarrollo del laboratoio en donde se controlar el robot en tiempo real desde el PC. El computador se conecta a la red donde esta conectado físicamente el controlador del robot mediante un cable de red (Ethernet) utilizando protocolos TCP/IP. Para que esto funcione, la llave del *Teach Pendant* debe estar en la posición **REMOTE**. A través de sus "Drivers", RoboDK establece una conexión servidor-cliente y envía las instrucciones de la trayectoria (como la polar) paso a paso directamente a los motores, sin necesidad de descargar un archivo completo en la memoria del robot.

<br>
<div align="center">
  <img src="Images/robodk_simulacion.png" alt="Simulación en RoboDK" width="550">
  <br>
  <b>Figura 17. Entorno de simulación en RoboDK ejecutando la validación de trayectoria con el manipulador Motoman MH6.</b>
</div>
<br>

## 7. Comparación: RoboDK vs RobotStudio

Para comprender mejor el ecosistema de herramientas de Programación Fuera de Línea (OLP) utilizadas a lo largo del curso, es fundamental establecer las diferencias operativas y enfoques de uso entre RoboDK y RobotStudio. A continuación, se presenta un cuadro comparativo con sus características principales:

<br>
<div align="center">

| Característica | **RoboDK** | **RobotStudio** |
|---|---|---|
| **Fabricante** | RoboDK Inc. (spin-off CoRo Lab, Canadá) | ABB Robotics |
| **Compatibilidad** | +40 fabricantes (Yaskawa, KUKA, FANUC, ABB, UR, etc.) | Exclusivo para robots ABB |
| **Fidelidad de simulación** | Alta (cinemática correcta), pero sin controlador virtual real | Máxima fidelidad: usa el controlador virtual ABB (VRC) idéntico al real |
| **Lenguaje de robot** | Genera código nativo vía post-procesadores (no ejecuta INFORM/RAPID directamente) | Ejecuta y depura RAPID directamente |
| **Multi-robot** | Sí, múltiples marcas en la misma simulación | Solo robots ABB |
| **API / Programación** | Python, C#, .NET, C++ | Visual Basic, RAPID, C# |

</div>
<br>

**Análisis y Usos Específicos:**

La elección entre ambas plataformas depende directamente de la arquitectura de la celda de manufactura y los objetivos de programación:

* **RobotStudio:** Representa el entorno definitivo y de máxima fidelidad cuando se trabaja en un ecosistema exclusivo de ABB. Su mayor fortaleza es la integración del Controlador Virtual (VRC), lo que significa que el código RAPID escrito y depurado en la simulación tendrá un comportamiento cinemático y lógico idéntico en el controlador físico (como el IRC5). Su uso específico es ideal para la puesta en marcha, depuración de lógica compleja y optimización de tiempos de ciclo precisos en equipos ABB.
* **RoboDK:** Representa universalidad y flexibilidad. Para el ingeniero, esta herramienta significa no depender de un solo fabricante, ya que permite integrar manipuladores Yaskawa (Motoman), ABB, KUKA, entre otros, en un mismo entorno de trabajo unificado. Aunque carece de la fidelidad del VRC propietario, su uso específico brilla en la generación de trayectorias complejas guiadas por modelos CAD/CAM mediante su API en Python o C#. Actúa como un traductor universal: genera la trayectoria independiente de la marca y utiliza sus post-procesadores para exportar el código nativo final (como INFORM III para el Motoman).

## 8. Diagrama de Flujo del Robot

El siguiente diagrama de flujo ilustra la secuencia lógica estructurada para la ejecución de la trayectoria polar y el trazado de texto mediante el software RoboDK. 

Este esquema detalla el proceso paso a paso de la rutina programada: inicia con la validación de la conexión y configuración del entorno (Robot, Frame y posición Home), establece la velocidad de operación, y procede a la ejecución secuencial de los movimientos para dibujar los lóbulos correspondientes a la ecuación polar. Posteriormente, procesa las coordenadas para realizar el trazado del texto ("David, Daniel") a través de un bucle, garantizando finalmente un retorno seguro a la posición de *Target_Home* antes de dar por finalizada la ejecución.

<br>
<div align="center">
  <img src="Images/diagrama de flujo.png" alt="Diagrama de flujo de la rutina" style="border-radius: 5px; width: 450px;">
  <br>
  <b>Figura 18. Diagrama de flujo de la secuencia de ejecución para la trayectoria polar en RoboDK.</b>
</div>
<br>

## 9. Plano de Planta del Laboratorio

La disposición física de los elementos dentro de la celda de manufactura es un factor determinante para la seguridad y la eficiencia de la operación. Esta distribución asegura que el radio de acción del robot se mantenga dentro del cerramiento de seguridad, permitiendo la supervisión visual directa sin exponer al personal a riesgos mecánicos.

Como soporte técnico de la distribución espacial de la celda, se adjunta el plano detallado en formato PDF:

* **[Plano de Planta - Celda de Manufactura (PDF)](Anexos/plano_de_planta_laboratorio.pdf)**

<br>

## 10. Código de la Trayectoria Polar: Diseño, Simulación e Implementación

En esta fase final, se diseñó una trayectoria basada en coordenadas polares para ser ejecutada por el manipulador Motoman MH6. El objetivo es validar la capacidad de interpolación del robot y la precisión de la comunicación en línea desde RoboDK.

### 10.1 Conceptos de la Trayectoria Polar
Una trayectoria polar define la posición de un punto mediante un radio ($r$) y un ángulo ($\theta$), a diferencia de las coordenadas cartesianas convencionales ($X, Y$). Para este laboratorio, se implementó una variante de la **Rosa de Grandi** (curva de rosa) definida por la ecuación:

$$r(\theta)=A\cdot\cos(k\theta)$$

Donde $A$ representa el radio máximo del lóbulo y $k$ determina el número de pétalos. En nuestro código, se utilizó $k=2$ para generar lóbulos independientes en ejes ortogonales. La conversión a coordenadas cartesianas para el comando `MoveL` del robot se realiza mediante:

$$x=r\cdot\cos(\theta)$$
$$y=r\cdot\sin(\theta)$$

### 10.2 Justificación Técnica de la Trayectoria (2 Pétalos)
Aunque la ecuación permite generar múltiples pétalos, se seleccionó una configuración de **dos pétalos (0 y $\pi/2$ rad)** por los siguientes motivos técnicos:

1. **Validación de Ejes Principales:** Permite verificar de forma independiente la precisión del robot tanto en el eje longitudinal como en el transversal del plano de trabajo.
2. **Gestión de Memoria y Buffer:** Al trabajar con comunicación en línea (*Robot Drivers*), reducir la trayectoria a dos pétalos permite una ejecución más fluida sin saturar el buffer de comandos del controlador DX100, asegurando que el robot no realice pausas entre puntos.
3. **Optimización de Tiempo de Ciclo:** En un entorno de manufactura real, se busca validar la lógica de control con la menor cantidad de movimientos necesarios, priorizando la calidad del trazo sobre la complejidad geométrica repetitiva.

### 10.3 Anexos de Código Python (RoboDK API)

Como requerimiento del laboratorio, se adjuntan los scripts desarrollados para la ejecución de la rutina. Debido a las diferencias entre el entorno virtual y la respuesta dinámica del robot real, se generaron dos versiones localizadas en la carpeta de anexos:

* **[Código Versión Virtual (Alta Fidelidad)](Anexos/trayectoria_polar_simulacion_180pts.py):** Configurado con **180 puntos** por lóbulo para una curva visualmente perfecta.
* **[Código Versión Física (Optimizado)](Anexos/trayectoria_polar_robot_fisico_40pts.py):** Configurado con **40 puntos** por lóbulo para garantizar una velocidad constante y sin vibraciones en el manipulador real.

### 10.4 Visualización Previa (Script para Google Colab)

Para validar la geometría de los pétalos y el posicionamiento exacto del texto (horizontal y centrado debajo de la figura) antes de la implementación, se utiliza el siguiente script de validación:

```python
import numpy as np
import matplotlib.pyplot as plt

def generar_previsualizacion():
    A = 150 
    plt.figure(figsize=(10, 10))
    
    # Dibujo de pétalos polares
    for angulo_central in [0, np.pi/2]:
        theta = np.linspace(angulo_central - np.pi/4, angulo_central + np.pi/4, 180)
        r = np.maximum(0, A * np.cos(2 * (theta - angulo_central)))
        plt.plot(r * np.cos(theta), r * np.sin(theta), linewidth=3)

    # Representación del texto procesado (David.P, Daniel, David.C)
    # Ubicado horizontalmente debajo de los pétalos
    plt.text(0, -100, "David.P, Daniel, David.C", fontsize=14, color='red', 
             ha='center', va='top', fontweight='bold', rotation=0)

    plt.title("Previsualización de Trayectoria Polar y Texto - Lab 2", fontsize=14)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.axis('equal')
    plt.xlim(-200, 200)
    plt.ylim(-200, 200)
    plt.show()

generar_previsualizacion()
```

<br>
<div align="center">
  <img src="Images/previsualizacion_colab.png" alt="Previsualización de trayectoria" width="450">
  <br>
  <b>Figura 20. Resultado esperado de la trayectoria generado mediante el script de validación.</b>
</div>
<br>

## 11. Demostración en Video: Validación de Trayectoria Polar

Como evidencia final del cumplimiento de los objetivos del laboratorio, se presenta el registro audiovisual de la ejecución del sistema. Este video documenta la integración exitosa entre la Programación Fuera de Línea (OLP) y la operación del manipulador físico en tiempo real.

En el material se puede observar la sincronización lograda mediante los *drivers* de RoboDK, validando que la trayectoria polar diseñada y simulada en el entorno virtual se traslada con precisión milimétrica al manipulador Motoman MH6. La demostración incluye tanto la fase de aproximación segura como la ejecución de los pétalos de la Rosa de Grandi y el trazado de texto, confirmando la robustez de la comunicación vía Ethernet y la correcta configuración de los sistemas de referencia (Frame) y herramienta (TCP).

<br>

<div align="center">
  <a href="https://youtu.be/QDgljY2Wygw" target="_blank">
    <img src="https://img.shields.io/badge/Ver_Video_en_YouTube-FF0000?style=for-the-badge&logo=youtube&logoColor=white" alt="Ver Video" />
  </a>
  <br>
</div>
