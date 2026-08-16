# Laboratorio No. 03: Robótica Industrial - Manipulador EPSON T3-401S

## 1. Cuadro Comparativo de Manipuladores
| Característica | EPSON T3-401S | Motoman MH6 | ABB IRB 140 |
| :--- | :--- | :--- | :--- |
| **Carga Máxima** | 3 kg | 6 kg | 6 kg |
| **Alcance** | 400 mm | 1422 mm | 800 mm |
| **Grados de Libertad** | 4 ejes (SCARA) | 6 ejes | 6 ejes |
| **Velocidad Máxima** | J1-J2: 3700 mm/s, J3: 1000 mm/s, J4: 2600°/s | Hasta 1000°/s aprox. según eje | Hasta 200°/s según eje |
| **Aplicaciones Típicas** | Pick & place, ensamblaje de piezas pequeñas, manipulación veloz | Soldadura, empaquetado, cuidado de máquinas, manipulación | Ensamblaje, desbarbado, soldadura, cuidado de máquinas |


# 2. Configuraciones Iniciales (Home)
## Definición de Home

En EPSON RC+ 7.0, la posición Home puede configurarse como un **Teach Point**, es decir, un punto enseñado y almacenado en el sistema de coordenadas del robot, que posteriormente puede ser llamado desde cualquier programa mediante instrucciones de movimiento en SPEL+. Esta posición representa el punto de referencia seguro al cual el manipulador regresa al inicio o al final de una rutina, garantizando una configuración articular conocida y reproducible.

Para el robot EPSON T3-401S del laboratorio se tienen definidos dos puntos Home:

- **Home predeterminado del laboratorio** (ver Figura 1): definido en las coordenadas cartesianas **(400, 0, 0)** mm respecto al sistema de referencia del robot. Corresponde a la posición de fábrica establecida en la configuración del sistema.

<div align="center">
  <a href="./img/origen_real  manipulador.png">
    <img src="./img/origen_real  manipulador.png" alt="Home predeterminado — coordenadas (400, 0, 0)" width="500"/>
  </a>
  <p><em>Figura 1. Home predeterminado del laboratorio — coordenadas (400, 0, 0).</em></p>
</div>

- **Home configurado en el laboratorio** (ver Figura 2): establecido en las coordenadas **(−120, 150, 0)** mm. Esta posición fue ajustada para las condiciones específicas del espacio de trabajo disponible en el laboratorio, evitando colisiones con elementos del entorno cercano al robot.

<div align="center">
  <a href="./img/Home_lab  manipulador.png">
    <img src="./img/Home_lab  manipulador.png" alt="Home lab — coordenadas (0, 400, 0)" width="500"/>
  </a>
  <p><em>Figura 2. Home lab — coordenadas (0, 400, 0).</em></p>
</div>

## Posición Articular en Home

El EPSON T3-401S es un robot SCARA de 4 grados de libertad. En la posición Home, cada articulación se encuentra en su posición de referencia cero, lo que sitúa al manipulador en una configuración extendida y alineada respecto a su base, tal como se describe a continuación:

| Articulación | Descripción | Posición en Home |
|:------------|:------------------------------|:-------------------|
| J1 | Rotación de la base | 0°  |
| J2 | Rotación del brazo| 0°  |
| J3 | Desplazamiento vertical (Z)  | 0 mm (pos. superior) |
| J4 | Rotación de la muñeca | 0°  |

## Rangos de Movimiento

Los rangos de movimiento de cada articulación definen el espacio de trabajo del manipulador y establecen los límites dentro de los cuales pueden definirse puntos Home y trayectorias de forma segura:

| Articulación | Descripción | Rango de Movimiento |
|------|-------------------|-------------------|
| J1 | Rotación de la base | ±132° |
| J2 | Rotación del brazo | ±141° |
| J3 | Desplazamiento vertical (Z) | 150 mm |
| J4 | Rotación de la muñeca | ±360° |


# 3. Operación Manual

## Modos de Movimiento

### Movimiento Articular (Joint)

El modo articular permite controlar de forma independiente cada eje del robot, permitiendo reconfigurar la postura del manipulador sin desplazar necesariamente el TCP en el espacio cartesiano.

**Procedimiento:**

1. Colocar el robot en modo Teach.
2. Abrir la ventana **Mover y enseñar** en EPSON RC+.
3. Seleccionar el modo **articular** en el selector de modo de movimiento.
4. Mover cada articulación utilizando los controles de desplazamiento (`+` / `−`).

**Ejes disponibles:**

| Articulación | Movimiento| Botones |
|------------|---------------------|-------|
| J1 | Rotación de la base | +  /  − |
| J2 | Rotación del brazo  | +  /  − |
| J3 | Desplazamiento en Z | +  /  − |
| J4 | Rotación de la muñeca | +  /  − |

### Movimiento Cartesiano

El modo cartesiano permite desplazar directamente el TCP (*Tool Center Point*) en coordenadas espaciales, facilitando el posicionamienento del efector final a objetos o superficies que estan ubicadas en el area de trabajo, para ello, se selecciona el modo **Mundo** o **Herramienta** en la ventana **Mover y enseñar**, según si se desea referenciar el movimiento respecto al sistema global del robot o al sistema local de la herramienta.

#### Traslaciones

| Eje | Dirección positiva | Dirección negativa |
|---|-------------------|-------------------|
| X | Avance en X+ | Retroceso en X− |
| Y | Avance en Y+ | Retroceso en Y−|
| Z | Ascenso en Z+ | Descenso en Z− |

#### Rotación

| Eje | Movimiento  | Botones |
|---|---------------------|-------|
| Rz | Rotación en Z+/Z−  | + / − |

Este modo resulta útil para posicionar el efector final respecto al entorno de trabajo.

## Control de Velocidad

### Niveles Disponibles

El robot permite ajustar la velocidad de operación mediante porcentaje o velocidad lineal del TCP.

| Parámetro | Descripción | Rango           |
|---------|-------------------------------------|---------------|
|`Speed` | Velocidad en % de la máxima| 1 – 100 % |
|`SpeedS` | Velocidad lineal del TCP  | 0.1 – 2000 mm/s |


### Cambio de Nivel

### Mediante Codigo Spelt+

```spel
Function Main
    Motor On
    Power High
    Accel 100, 100
    *Speed 50* \\ modificar esta función por las mencionadas anteriormente
...
Fend
```

### Mediante el administrador del Robot
1. Abrir la ventana **Mover y enseñar**.
2. Localizar el parámetro **Velocidad**.
3. Seleccionar la velocidad deseada ("Baja" o "Alta").

## 4. Software y Entorno de Control

### EPSON RC+ 7.0

#### Funcionalidades

EPSON RC+ 7.0 es el entorno de desarrollo, programación, configuración y supervisión utilizado para trabajar con los robots industriales EPSON. En el caso del manipulador **EPSON T3-401S**, permite configurar el sistema, controlar manualmente el robot, enseñar posiciones y desarrollar programas de automatización mediante el lenguaje **SPEL+**.

Entre sus principales funcionalidades se encuentran:

- Creación y administración de proyectos de automatización.
- Programación del robot mediante el lenguaje SPEL+.
- Compilación, transferencia y ejecución de programas en el controlador.
- Movimiento manual del robot mediante la herramienta **Jog & Teach**.
- Movimiento por articulaciones y en coordenadas cartesianas.
- Enseñanza, modificación y almacenamiento de puntos.
- Configuración de sistemas de coordenadas locales y de herramienta.
- Configuración de velocidades, aceleraciones y desaceleraciones.
- Ejecución de movimientos articulares, lineales y trayectorias continuas.
- Simulación y comprobación de programas antes de ejecutarlos físicamente.
- Supervisión del estado del robot, los motores y el controlador.
- Visualización y diagnóstico de alarmas y errores.
- Depuración de programas mediante ejecución paso a paso, puntos de interrupción y monitoreo de variables.
- Configuración y supervisión de entradas y salidas digitales.
- Control de dispositivos externos, como electroválvulas, sensores y sistemas de vacío.
- Integración opcional con sistemas de visión, seguimiento de transportadores y control de fuerza.

Para este laboratorio, EPSON RC+ 7.0 se utiliza principalmente para enseñar las posiciones de la cubeta, programar la trayectoria de los huevos, controlar la activación del gripper neumático y ejecutar la rutina en el robot real.

#### Comunicación con el manipulador

El EPSON T3-401S posee un controlador integrado encargado de ejecutar los programas y controlar físicamente los motores del robot. EPSON RC+ 7.0 funciona como la interfaz entre la computadora de desarrollo y dicho controlador.

La computadora puede conectarse al robot mediante:

- **Conexión USB**, utilizada normalmente durante la configuración inicial y las prácticas de laboratorio.
- **Conexión Ethernet**, utilizada cuando se requiere integrar el robot a una red industrial o acceder al controlador mediante una dirección IP.

La conexión se configura desde la opción:

`Setup → PC to Controller Communications`

Después de seleccionar el tipo de comunicación, EPSON RC+ muestra el estado de la conexión con el controlador.

El procesamiento de los comandos se realiza de la siguiente manera:

1. El usuario crea el programa y define los movimientos, puntos, velocidades y señales de entrada o salida en EPSON RC+ 7.0.
2. El software revisa y compila las instrucciones escritas en lenguaje SPEL+.
3. El proyecto compilado se transfiere desde la computadora hacia el controlador integrado del T3-401S.
4. El controlador ejecuta las instrucciones del programa y genera las órdenes necesarias para mover cada articulación.
5. Los servomotores desplazan el manipulador hasta las posiciones programadas.
6. Durante la ejecución, el controlador supervisa el estado de los motores, los límites de movimiento, las señales digitales y las condiciones de seguridad.
7. La información de operación, los estados y los posibles errores son enviados nuevamente a EPSON RC+ para que puedan visualizarse en la computadora.

Por lo tanto, EPSON RC+ 7.0 no alimenta ni controla directamente los motores. El software permite crear, transferir y supervisar las instrucciones, mientras que el controlador integrado del robot se encarga de ejecutarlas físicamente.

Para el gripper neumático, una salida digital del robot puede utilizarse para activar la electroválvula que genera el vacío. También puede utilizarse una entrada digital para comprobar la señal de un sensor de vacío y confirmar que el huevo se encuentra correctamente sujetado antes de iniciar el desplazamiento.

### Análisis Comparativo de Software

| Herramienta | Ventajas | Limitaciones | Usos Específicos |
| :--- | :--- | :--- | :--- |
| **EPSON RC+ 7.0** | Integración directa con robots EPSON.<br><br>Permite configurar, programar, mover y supervisar el robot real.<br><br>Incluye herramientas de enseñanza de puntos, depuración, diagnóstico y control de E/S.<br><br>Permite programar mediante SPEL+ y transferir directamente los programas al controlador.<br><br>Ofrece una representación cercana al comportamiento real del robot EPSON. | Está orientado principalmente a robots y controladores EPSON.<br><br>No es una plataforma multimarca.<br><br>Requiere conocimiento del lenguaje SPEL+ para desarrollar aplicaciones avanzadas.<br><br>Las funciones adicionales de visión, fuerza o seguimiento de transportadores pueden requerir módulos o licencias específicas. | Configuración y puesta en funcionamiento del EPSON T3-401S.<br><br>Programación de movimientos y trayectorias.<br><br>Enseñanza de puntos.<br><br>Control de entradas y salidas digitales.<br><br>Activación del gripper neumático.<br><br>Diagnóstico y ejecución física del programa. |
| **RoboDK** | Plataforma multimarca compatible con numerosos fabricantes y modelos de robots.<br><br>Permite simulación y programación fuera de línea.<br><br>Cuenta con una amplia biblioteca de robots, herramientas y componentes industriales.<br><br>Permite importar modelos CAD y generar trayectorias complejas.<br><br>Dispone de postprocesadores para generar código compatible con diferentes controladores. | La precisión de la simulación depende del modelo, la calibración y la configuración de la celda.<br><br>No reproduce de forma exacta todos los detalles internos de cada controlador propietario.<br><br>El código generado debe verificarse antes de ejecutarlo en el robot real.<br><br>Algunas funciones avanzadas requieren una licencia comercial. | Diseño preliminar de celdas robotizadas.<br><br>Comparación entre robots de diferentes fabricantes.<br><br>Simulación de alcance y detección de posibles colisiones.<br><br>Programación fuera de línea.<br><br>Generación de trayectorias para mecanizado, soldadura, pintura, impresión 3D y manipulación de objetos. |
| **RobotStudio** | Utiliza el controlador virtual de ABB, basado en el mismo software empleado por los controladores físicos ABB.<br><br>Permite simulaciones de alta fidelidad.<br><br>Facilita la programación y prueba de código RAPID.<br><br>Permite realizar puesta en marcha virtual, análisis de tiempos de ciclo y validación de celdas.<br><br>Posee herramientas avanzadas para robots y equipos ABB. | Su principal aplicación se encuentra en el ecosistema ABB.<br><br>No permite programar directamente el EPSON T3-401S.<br><br>Puede presentar una curva de aprendizaje mayor debido a la cantidad de herramientas disponibles.<br><br>Algunas funciones requieren licencias adicionales y un computador con recursos gráficos adecuados. | Diseño y simulación de celdas con robots ABB.<br><br>Programación fuera de línea mediante RAPID.<br><br>Configuración de controladores virtuales.<br><br>Validación de trayectorias y tiempos de ciclo.<br><br>Puesta en marcha virtual y capacitación de operadores. |

### Interpretación de las herramientas

Para el desarrollo de este laboratorio, cada herramienta cumple una función diferente:

- **EPSON RC+ 7.0** es la herramienta principal de implementación, porque permite programar, configurar y controlar directamente el manipulador EPSON T3-401S.
- **RoboDK** es una herramienta general de simulación y programación fuera de línea que facilita la comparación y el trabajo con robots de diferentes fabricantes.
- **RobotStudio** es una plataforma especializada en robots ABB que ofrece una simulación de alta fidelidad mediante el controlador virtual de ABB.


## 5. Trayectoria: Patrón de Caballo (Ajedrez)

### Plano de planta

### Diagrama de flujo

La lógica de la rutina se basa en el movimiento alternado de dos huevos, donde cada uno es tomado desde una posición inicial, trasladado a una nueva ubicación siguiendo el patrón del caballo de ajedrez y posteriormente liberado para continuar con el otro huevo. Este procedimiento se repite hasta recorrer todas las posiciones definidas en la matriz.

<div align="center">
  <a href="./img/Diagrama_Flujo.jpeg">
    <img src="./img/Diagrama_Flujo.jpeg" alt="DIAGRAMA_FLUJO" width="600"/>
  </a>
  <p><em>Figura 3. DIAGRAMA_FLUJO.</em></p>
</div>
### Secuencia de recorrido de cada huevo

Para definir la secuencia de movimiento de cada huevo, se parte de una cuadrícula de **6 × 5**, la cual representa los espacios del cartón de huevos. En esta matriz, los huevos se ubican en esquinas opuestas, probando así una rutina capaz de recorrer todo el tablero siguiendo un patrón equivalente al movimiento del caballo en ajedrez.

La secuencia de recorrido definida para cada huevo es la siguiente:

**Huevo A**

`1 → 9 → 5 → 18 → 29 → 21 → 25 → 14 → 27 → 19 → 8 → 16 → 20 → 7 → 3 → 11 → 24 → 28 → 15 → 4 → 12 → 23 → 10 → 2 → 13 → 26 → 22 → 30 → 17 → 6`

**Huevo B**

`30 → 22 → 26 → 13 → 2 → 10 → 6 → 17 → 4 → 12 → 23 → 15 → 11 → 24 → 28 → 20 → 7 → 3 → 16 → 27 → 19 → 8 → 21 → 29 → 18 → 5 → 9 → 1 → 14 → 25`

A partir de la rutina ya especificada, se estableció la distribución de los huevos sobre un cartón común de 6 × 5 posiciones, el cual simula la matriz de trabajo del manipulador. Para definir esta matriz, se tuvo en cuenta que la distancia entre centros del cartón es de **48 mm**, lo que permitió delimitar un espacio de trabajo adecuado para que el robot pudiera recorrer todas las posiciones sin presentar problemas de alcance ni singularidades durante la ejecución de la trayectoria. En función de esta distribución, se definieron los siguientes puntos sobre la matriz del pallet, los cuales sirven como referencia para el recorrido de los huevos.

<div align="center">
   <a href="img/Cuadricula huevos.png">
    <img src="./img/Cuadricula huevos.png" alt="matriz 6x5" width="500"/>
  </a>
  <p><em>Figura 4. matriz 6x5 - Espacio de trabajo sobre la caja de huevos.</em></p>
</div>

Con esta organización, se implementó la secuencia en SPEL+, tomando como base los espacios definidos en la matriz del pallet. La rutina consiste en tomar el huevo en un punto de origen, trasladarlo al punto destino y luego repetir el mismo procedimiento con el otro huevo, alternando el movimiento entre ambos hasta completar el recorrido total.
<div align="center">
  <a href="img/Definicion de puntos .png">
    <img src="./img/Definicion de puntos .png" alt="Puntos Pallet" width="500"/>
  </a>
  <p><em>Figura 5. Puntos Pallet.</em></p>
</div>

### Código (EPSON RC+ 7.0)

```spel
Function Main
    Motor On
    Power High
    Accel 100, 100
    Speed 50
    Wait 10
    Home
    Call SecuenciaMovimientos
    Home
Fend

Function MoverHuevo(huevo As Integer, origen As Integer, destino As Integer)
    Pallet 1, Origen, PuntoX, PuntoY, 6, 5

    ' Ir a la posición inicial del huevo
    Jump Pallet(1, origen)
    Move Pallet(1, origen) :Z(-90)

    ' Encender la ventosa y agarrar el huevo
    On 9
    Wait 0.2
    Move Pallet(1, origen) :Z(0)

    ' Ir a la posición final del huevo
    Jump Pallet(1, destino)
    Move Pallet(1, destino) :Z(-90)

    ' Soltar el huevo
    Off 9
    Wait 0.2
    Move Pallet(1, destino) :Z(0)
Fend
```
Para ampliar el codigo ver: <a href="./src/main.prg" target="_blank">Codigo Completo</a> 
## 6. Evidencias
<div align="center">
  <a href="https://youtu.be/iY24xKc1f0Y">
    <img src="https://img.youtube.com/vi/iY24xKc1f0Y/0.jpg" alt="Simulación - Patrón de Caballo (Ajedrez)" width="500"/>
  </a>
</div>
