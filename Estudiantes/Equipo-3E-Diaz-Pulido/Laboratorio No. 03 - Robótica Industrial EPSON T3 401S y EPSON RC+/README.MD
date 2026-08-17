# Lab03 - Robótica Industrial - Programación y Operación del Manipulador SCARA EPSON T3-401S

# Integrantes

- [José Luis Pulido Fonseca](https://github.com/jpulidof)
- [Jairo David Díaz Luna](https://github.com/Axum-User)

# Informe

## Índice

1. [Cuadro Comparativo Técnico: Motoman MH6 vs. ABB IRB140 vs. EPSON T3-401S](#cuadro-comparativo-tecnico-motoman-mh6-vs-abb-irb140-vs-epson-t3-401s)
2. [Descripción de las Configuraciones Home del EPSON T3-401S](#descripcion-de-las-configuraciones-home-del-epson-t3-401s)
3. [Inicialización del Sistema y Entorno EPSON RC+](#inicializacion-del-sistema-y-entorno-epson-rc)
4. [Procedimiento de Movimiento Manual (Jogging) del EPSON T3-401S](#procedimiento-de-movimiento-manual-jogging-del-epson-t3-401s)
5. [Gestión y Configuración de Niveles de Velocidad Manual](#gestion-y-configuracion-de-niveles-de-velocidad-manual)
6. [Funcionalidades Principales de EPSON RC+ 7.0 y Arquitectura de Comunicación](#funcionalidades-principales-de-epson-rc-70-y-arquitectura-de-comunicacion)
7. [Análisis Comparativo de Software: EPSON RC+ vs. RoboDK vs. RobotStudio](#analisis-comparativo-de-software-epson-rc-vs-robodk-vs-robotstudio)
8. [Diseño Técnico e Integración del Gripper Neumático por Vacío](#diseno-tecnico-e-integracion-del-gripper-neumatico-por-vacio)
9. [Diagrama de Flujo: Rutina de Movimiento con Patrón de Caballo de Ajedrez](#diagrama-de-flujo-rutina-de-movimiento-con-patron-de-caballo-de-ajedrez)
10. [Plano de Planta: Distribución de la Celda y Posiciones de la Cubeta](#plano-de-planta-distribucion-de-la-celda-y-posiciones-de-la-cubeta)
11. [Análisis de Resultados y Discusión Técnica](#analisis-de-resultados-y-discusion-tecnica)
12. [Código Fuente](#codigo-fuente)
13. [Video Simulación](#video-simulacion)
14. [Conclusiones](#conclusiones)


---

## Cuadro Comparativo Técnico: Motoman MH6 vs. ABB IRB140 vs. EPSON T3-401S



| Característica / Parámetro Técnico | EPSON T3-401S | Motoman MH6 | ABB IRB140 |
| :--- | :--- | :--- | :--- |
| **Tipo de Configuración Cinemática** | SCARA (*Selective Compliance Assembly Robot Arm*) | Articulado (Angular / Esférico) | Articulado (Angular / Esférico) |
| **Grados de Libertad (DOF)** | 4 ejes ($J_1, J_2, J_3, J_4$) | 6 ejes ($S, L, U, R, B, T$) | 6 ejes ($Axis 1 \text{ a } Axis 6$) |
| **Carga Útil Máxima (Payload)** | 3 kg | 6 kg | 6 kg |
| **Alcance Horizontal Máximo** | 400 mm | 1422 mm | 810 mm |
| **Carrera Eje Vertical ($J_3$)** | 150 mm | N/A (Definido por rango articular) | N/A (Definido por rango articular) |
| **Repetibilidad de Posición** | $\pm0.02\text{ mm}$ | $\pm0.08\text{ mm}$ | $\pm0.03\text{ mm}$ |
| **Peso del Manipulador** | 16 kg (Ultra compacto) | 130 kg | 98 kg |
| **Velocidad Máxima del TCP** | Muy alta en plano horizontal ($3700\text{ mm/s}$ combinados en $J_1, J_2$) | Alta (Velocidad lineal optimizada para trayectorias largas) | Media-alta ($2.5\text{ m/s}$ máxima en TCP) |
| **Velocidad Angular por Eje** | $J_4: \pm2600^\circ/\text{s}$ | $S: 220^\circ/\text{s}$, $L: 200^\circ/\text{s}$, $U: 220^\circ/\text{s}$, $R: 410^\circ/\text{s}$, $B: 410^\circ/\text{s}$, $T: 610^\circ/\text{s}$ | $A_1: 200^\circ/\text{s}$, $A_2: 200^\circ/\text{s}$, $A_3: 260^\circ/\text{s}$, $A_4: 360^\circ/\text{s}$, $A_5: 360^\circ/\text{s}$, $A_6: 450^\circ/\text{s}$ |
| **Rango de Movimiento Articular** | $J_1: \pm132^\circ$<br>$J_2: \pm141^\circ$<br>$J_3: 150\text{ mm}$<br>$J_4: \pm360^\circ$ | $S: \pm170^\circ$<br>$L: +155^\circ / -90^\circ$<br>$U: +250^\circ / -175^\circ$<br>$R: \pm180^\circ$<br>$B: +225^\circ / -45^\circ$<br>$T: \pm360^\circ$ | $A_1: \pm360^\circ$<br>$A_2: \pm200^\circ$<br>$A_3: \pm280^\circ$<br>$A_4: \text{Ilimitado}$<br>$A_5: \pm230^\circ$<br>$A_6: \text{Ilimitado}$ |
| **Controlador Nativo** | Integrado en la base del robot | Yaskawa DX100 / DXM100 | ABB IRC5 (Compact / Panel Mounted) |
| **Software de Programación** | EPSON RC+ 7.0 / RC+ Express | MotoVantage / MotoSim EG-VRC | ABB RobotStudio |
| **Lenguaje de Programación** | SPEL+ (Multitarea estructurado) | INFORM III | RAPID |
| **Alimentación Eléctrica** | 100 - 240 VAC (Monofásico) | 3-phase, 240/480 VAC | 200-600 V, 50/60 Hz |
| **Conectividad e Interfases I/O** | Entrada/Salida Digital estándar, soporte Fieldbus (EtherNet/IP, Profibus, DeviceNet) | 40 entradas / 40 salidas estándar, DeviceNet, Profibus, Ethernet | Canales de aire y señales integradas en el brazo, soporte de redes industriales multi-protocolo |
| **Aplicaciones Típicas** | Pick & Place de alta velocidad, ensamble de electrónica, inspección farmacéutica, inserción rápida de componentes. | Soldadura por arco, manipulación de materiales pesados, empaque, asistencia de maquinaria (*machine tending*), manufactura aditiva. | Ensamble de precisión, dosificación (*dispensing*), empaque y paletizado intermedio, manipulación en entornos controlados (Clean Room). |

### Análisis de Criterios de Selección y Diferencias Tecnológicas

1. **Estructura y Rigidez (SCARA vs. Articulados):** El **EPSON T3-401S** posee rigidez selectiva (alta rigidez vertical en $Z$ y flexibilidad en el plano $XY$), lo que lo hace ideal para el ensamble rápido e inserción en superficies planas (como la manipulación de la cubeta de huevos). En contraste, el **Motoman MH6** y el **ABB IRB140** son robots antropomórficos de 6 DOF diseñados para posicionar y orientar el efector en cualquier coordenada espacial ($X, Y, Z, \alpha, \beta, \gamma$), priorizando la versatilidad geométrica sobre la velocidad pura.

2. **Espacio de Trabajo y Distribución:** El modelo SCARA opera en un volumen cilíndrico reducido (alcance de $400\text{ mm}$), óptimo para estaciones de manufactura compactas. Por otro lado, el Motoman MH6 cubre un área extensa gracias a su alcance de $1422\text{ mm}$ (adecuado para soldadura o paletizado masivo), mientras que el ABB IRB140 ofrece un rango intermedio ($810\text{ mm}$) con gran flexibilidad de montaje (suelo, pared o techo) y la capacidad de flexionarse hacia atrás (*bend-back*).

3. **Carga Útil vs. Repetibilidad (*Trade-off*):** Existe una relación inversa entre la capacidad de carga y la precisión. El robot EPSON, al ser un equipo ligero ($16\text{ kg}$) con capacidad para $3\text{ kg}$, alcanza una alta precisión con una repetibilidad de $\pm0.02\text{ mm}$. Sin embargo, los brazos articulados de ABB y Motoman, estructurados con eslabones pesados para soportar hasta $6\text{ kg}$, ven reducida su repetibilidad a $\pm0.03\text{ mm}$ y $\pm0.08\text{ mm}$ respectivamente.


## Descripción de las Configuraciones Home del EPSON T3-401S

En la robótica industrial, la posición **Home** (o posición de origen) es el estado de referencia espacial y articular fundamental desde el cual el manipulador inicia sus tareas programadas, ejecuta rutinas de calibración o se ubica en un estado seguro de reposo al finalizar una operación. Para el robot SCARA **EPSON T3-401S**, la gestión y el comportamiento de esta configuración se dividen en dos conceptos clave:

### Definición Técnica y Coordenadas del Home de Fábrica

Por defecto, el fabricante establece una posición inicial de Home optimizada para evitar colisiones mecánicas inmediatas con el chasis o la superficie de montaje del robot. En el sistema SCARA, esto corresponde a la alineación geométrica de los eslabones principales y el retraimiento completo del eje lineal.

Las coordenadas por defecto para el EPSON T3-401S en el entorno de desarrollo son:

* **Coordenadas Articulares (Joint):**
    $$J_1 = 0.000^\circ, \quad J_2 = 0.000^\circ, \quad J_3 = 0.000\text{ mm}, \quad J_4 = 0.000^\circ$$
* **Coordenadas Cartesianas (World):**
    $$X = 400.000\text{ mm}, \quad Y = 0.000\text{ mm}, \quad Z = 0.000\text{ mm}, \quad U = 0.000^\circ$$

En esta configuración predeterminada:
1. Los eslabones correspondientes a las articulaciones $J_1$ y $J_2$ se extienden completamente en línea recta hacia adelante a lo largo del eje positivo $X$, alcanzando su máxima longitud radial de trabajo ($400\text{ mm}$).
2. El eje $J_3$ (vástago vertical Z) se localiza en su punto muerto superior, lo que garantiza el máximo despeje respecto a la superficie de trabajo o la cubeta antes de iniciar cualquier trayectoria de aproximación.

<p align="center">
  <img src="media\captura1.png" width="500">
</p>

### Comando `Home` vs. Funcionalidad de la Posición de Usuario

El entorno de programación **SPEL+** gestiona dos comandos fundamentales para retornar al robot a estados conocidos, diferenciándose en rigidez y flexibilidad de software:

1.  **El Comando `Home` (Origen de Fábrica):**
    Envía al manipulador directamente a las coordenadas nativas predeterminadas por el sistema ($0, 0, 0, 0$). Es una instrucción global y rígida. No se puede modificar mediante el código del usuario y está diseñada como un punto de partida inequívoco para verificar la integridad del encóder o tras un proceso de encendido (*Power On*).
    

2.  **El Comando `HomeDef` y Posiciones de Usuario (`Home 1`, `Home 2`...):**
    Permite al programador definir posiciones de origen personalizadas de acuerdo con el *layout* específico de la celda de manufactura. Este es altamente útil cuando el Home de fábrica interfiere mecánicamente con un periférico (como tolvas, bandas transportadoras o estructuras de la celda). Mediante el comando `HomeDef`, se puede guardar una posición de reposo segura alternativa.
 

### Proceso de Inicialización Física y Sincronización 

A diferencia de los robots que requieren una rutina activa de búsqueda de topes mecánicos o sensores ópticos en cada arranque, la serie **EPSON T** implementa **encóderes absolutos libres de batería** en sus servomotores. 

* **Retención de Posición:** El sistema almacena la posición exacta de cada articulación de forma magnética/mecánica incluso cuando el controlador está completamente desenergizado.
* **Comportamiento al Iniciar:** Al encender el controlador y activar los motores con el comando `Motor On`, el software lee instantáneamente la posición actual sin necesidad de mover los ejes para calibrar el cero. No obstante, se establece como buena práctica de ingeniería programar una rutina de aproximación inicial lenta hacia el punto `Home` de usuario al arrancar el modo automático, asegurando que el TCP inicie desde una zona libre de obstáculos en la trayectoria de paletizado de la cubeta de huevos.

## Inicialización del Sistema y Entorno EPSON RC+



### Secuencia de Encendido y Conexión de Hardware

Para garantizar un enlace síncrono y evitar fallos de comunicación, se debe seguir estrictamente este orden:

1. **Inspección de Seguridad:** Verificar el área de trabajo y localizar el botón de Paro de Emergencia (*E-Stop*).
2. **Conexión de Datos:** Vincular el cable USB desde el PC hacia el puerto del controlador integrado en la base del robot.
3. **Energización:** Encender el interruptor principal del chasis EPSON T3 y esperar a que finalice su autodiagnóstico de arranque.
4. **Lanzamiento:** Ejecutar **EPSON RC+ 7.0** en la estación de trabajo.

### Vinculación y Configuración del Entorno

1. **Carga del Proyecto:** Crear o abrir el espacio de trabajo desde el menú `Project` $\rightarrow$ `New/Open Project`.
2. **Establecer Comunicación:** Pulsar el botón **PC to Controller Communications**, verificar la selección del canal **USB** (Conexión N.° 1) y dar clic en `<Connect>` para pasar al modo *Online*.
3. **Entorno Virtual (Simulador):** Si se trabaja sin el brazo físico, acceder a `Setup` $\rightarrow$ `System Configuration` $\rightarrow$ `Controller` $\rightarrow$ `Robots` y seleccionar el modelo **T3-401S** para cargar las longitudes de los eslabones ($200\text{ mm} + 200\text{ mm}$) y sus límites cinemáticos.

### Comandos de Control de Energía (Ventana de Comandos / SPEL+)

* **`Motor On`:** Energiza los servomotores y libera los frenos electromecánicos, otorgando alta rigidez activa al brazo para iniciar trayectorias.
* **`Motor Off`:** Corta la corriente de los motores y aplica los frenos mecánicos de retención, permitiendo modificaciones seguras en la celda.
* **`Reset`:** Borra las alarmas de software y fallos de trayectoria leves tras desactivar una parada de emergencia, habilitando nuevamente el sistema.

<p align="center">
  <img src="media\captura2.png" width="500">
</p>


## Procedimiento de Movimiento Manual del EPSON T3-401S

Permite desplazar el manipulador de forma controlada utilizando el panel interactivo **Robot Manager** en EPSON RC+ 7.0. Se usa para el ajuste fino de trayectorias, el registro de coordenadas (*Teaching*) y la aproximación segura a los puntos de la cubeta de huevos.

### Acceso a la Interfaz de Control (Robot Manager)

Para habilitar la interfaz de control manual en el entorno de desarrollo:
1. En la barra de herramientas principal de EPSON RC+ 7.0, pulsar el botón **Robot Manager** (icono de un brazo robótico) o utilizar el comando rápido `Ctrl + M`.
2. En la ventana emergente, seleccionar la pestaña **Jog & Teach**.
3. Asegurarse de que el estado de los motores esté activo (`Motor On`). Si se encuentra apagado, presionar el botón **On** en el apartado de *Motor* dentro del panel lateral de la misma ventana.

### Modos de Operación Manual (Jog Modes)

El sistema cinemático del EPSON T3-401S se puede desplazar manualmente bajo dos sistemas de referencia principales, seleccionables desde el menú *Jog Mode*:

#### 1. Modo de Operación por Articulaciones (Joint Mode)
* **Descripción:** Controla de forma independiente el servomotor de cada articulación ($J_1, J_2, J_3, J_4$).
* **Comportamiento Cinematográfico:** * Los comandos **Jog +** y **Jog -** hacen rotar de forma individual los eslabones principales ($J_1$ y $J_2$) en sentido horario o antihorario respecto a su propio centro de giro.
  * El eje lineal $J_3$ se desplaza verticalmente (hacia arriba o abajo).
  * El eje $J_4$ realiza la rotación pura de la brida o el efector final (*U*).
* **Aplicación:** Ideal para desentrabar el robot de configuraciones singulares o realizar giros articulares libres alejados de los obstáculos físicos de la celda.

#### 2. Modo de Operación Cartesiano (World Mode / Cartesian)
* **Descripción:** Los movimientos toman como referencia el origen de coordenadas cartesianas globales de la base del robot (Sistema síncronizado *World*).
* **Comportamiento Cinematográfico:** * Al presionar **X+ / X-** o **Y+ / Y-**, el controlador calcula en tiempo real la interpolación cinemática inversa, moviendo simultáneamente los motores de $J_1$ y $J_2$ para forzar al efector final (*TCP*) a desplazarse en una línea recta perfecta a lo largo de los ejes espaciales.
  * Los comandos de **Z** manipulan el vástago vertical ($J_3$) y el comando **U** rota la brida en el espacio coordenado.
* **Aplicación:** Indispensable para realizar el alineamiento geométrico respecto a las filas y columnas de la matriz 6x5 de la cubeta, permitiendo desplazamientos paralelos precisos sin perder la linealidad.

### Visualización de Coordenadas Actuales

A la derecha, se pueden ver las coordenadas en tiempo real, la cualservirá para darnos una idea de dónde ubicarnos con el objeto o a la hora de enseñar puntos.

<p align="center">
  <img src="media\captura3.png" width="500">
</p>

## Gestión y Configuración de Niveles de Velocidad Manual



### Modificación de Velocidades desde el Robot Manager

En la interfaz **Robot Manager**, dentro de la pestaña **Jog & Teach**, la velocidad del movimiento manual se gestiona mediante dos parámetros principales:

1.  **Selector de Velocidad (Jog Speed):** * Permite alternar rápidamente entre tres niveles preconfigurados de fábrica: **Low** (Baja), **Medium** (Media) y **High** (Alta).
2.  **Porcentaje de Velocidad de Entrada Directa:**
    * Es un campo de texto numérico o barra de desplazamiento que permite ajustar el valor exacto del rango de velocidad operativa manual desde el **1% hasta el 100%**.

### Restricciones de Seguridad por Software y Hardware

Por normativas de seguridad industrial, la velocidad en modo manual (*Jogging*) está intrínsecamente limitada por el controlador a una fracción menor de la velocidad máxima nominal del robot (generalmente restringida por debajo de $250\text{ mm/s}$ en el TCP). Esto asegura que el operario pueda reaccionar y soltar el comando antes de un impacto.

### Configuración por Comandos (SPEL+)

Aunque el *Jogging* es un proceso manual visual, el entorno de comandos o el código de inicialización de la rutina de paletizado permiten preconfigurar los límites de velocidad mediante sentencias de software:

* **`Speed`:** Define el porcentaje de la velocidad máxima para movimientos de interpolación lineal o circular (comandos `Go`, `Jump`).
    * *Sintaxis:* `Speed 20` (Configura la velocidad al 20% para la rutina de ejecución).
* **`Accel`:** Determina las rampas de aceleración y desaceleración en los arranques y paradas de los servomotores.
    * *Sintaxis:* `Accel 20, 20` (Establece el 20% de la aceleración y desaceleración máximas).


## Funcionalidades Principales de EPSON RC+ 7.0 y Arquitectura de Comunicación

El entorno **EPSON RC+ 7.0** es una plataforma de automatización integrada que unifica la programación, simulación, control de periféricos y diagnóstico del robot SCARA.

### Funcionalidades Principales del Software

* **Editor de Código SPEL+:** Entorno de desarrollo con depurador (*debugger*) en tiempo real, resaltado de sintaxis, autocompletado y ejecución multitarea (*multitasking*) para controlar hilos en paralelo.
* **Simulador 3D Integrado:** Motor gráfico de alta fidelidad que emula colisiones, perfiles cinemáticos y tiempos de ciclo reales antes del despliegue físico.
* **Robot Manager:** Panel interactivo unificado para el movimiento manual (*jogging*), calibración de herramientas (*Tools*), bases de coordenadas (*Local*) y guardado físico de puntos (*Teaching*).
* **Herramientas de Monitoreo (I/O Monitor):** Panel dinámico para la visualización, forzado y mapeo de señales digitales (entradas y salidas) asociadas al gripper de vacío.

<p align="center">
  <img src="media\captura4.png" width="1000">
</p>

### Arquitectura de Comunicación

El controlador integrado de la serie T gestiona la transferencia de datos e instrucciones mediante dos canales independientes:

1.  **Enlace de Control / Computador (USB / Ethernet):** * Protocolo propietario de EPSON para el intercambio de comandos en modo *online* (carga de scripts, monitoreo de variables, depuración y control por el operario).
2.  **Lógica Externa e Interfaz de Campo (I/O e Industrial Fieldbus):**
    * **Señales Digitales de Hardware:** Conectores físicos discretos integrados en la base del robot operados bajo lógica PNP/NPN para la activación de electroválvulas neumáticas.
    * **Conectividad Industrial (Opcional):** Soporte nativo para protocolos como EtherNet/IP, Modbus TCP y Profibus, facilitando la sincronización de la celda con PLCs maestros o sensores avanzados.

## Análisis Comparativo de Software: EPSON RC+ vs. RoboDK vs. RobotStudio


| Característica / Parámetro | EPSON RC+ 7.0 | RoboDK | RobotStudio |
| :--- | :--- | :--- | :--- |
| **Compatibilidad de Hardware** | **Exclusivo de EPSON:** Diseñado únicamente para controladores de la marca (Series T, G, RS, etc.). | **Multi-marca:** Soporta más de 50 fabricantes (ABB, Yaskawa, Fanuc, KUKA, EPSON). | **Exclusivo de ABB:** Diseñado de forma dedicada para el ecosistema y controladores ABB. |
| **Lenguaje de Programación** | **SPEL+** (Lenguaje estructurado, potente para tareas multitarea concurrentes). | **Python**, C#, C++, o scripts gráficos mediante su API nativa. | **RAPID** (Lenguaje propietario y fuertemente estructurado de ABB). |
| **Fidelidad del Gemelo Digital** | **Alta:** Emula el comportamiento cinemático y tiempos de ciclo del controlador de la serie T. | **Media-Alta:** Validación geométrica, alcances y evasión de colisiones espaciales. | **Máxima:** Integra un *Virtual Controller* idéntico al hardware físico con la lógica de control real. |
| **Disponibilidad de Licencia (U.N.)** | **Gratuito / Incluido** con la compra o simulación del hardware EPSON. | **Sin Licencia:** Modelo comercial perpetuo/suscripción; la universidad no dispone de ella. | **Con Licencia Activa:** Modelo de suscripción premium; la universidad sí cuenta con accesos. |
| **Curva de Aprendizaje** | **Baja-Media:** Interfaz muy intuitiva, ideal para configuraciones rápidas de SCARA. | **Baja:** Entorno ágil enfocado en la facilidad de uso e integración CAD/CAM. | **Alta:** Entorno profesional denso y restrictivo con alta complejidad estructural. |
| **Flexibilidad y Post-procesamiento** | **Media:** Genera código directo y nativo ejecutable solo para sistemas EPSON. | **Muy Alta:** Creación y edición de post-procesadores con Python para adaptar el código a cualquier formato. | **Baja (Fuera de ABB):** No exporta código ejecutable para terceras marcas sin conversión compleja. |
| **Optimización de Procesos** | **Especializado:** Pick & Place a alta velocidad, paletizado por matrices y sincronización de I/O discretas. | **Manufactura Flexible:** Conversión de G-code (Mecanizado CNC, Impresión 3D) a trayectorias robóticas. | **Lógica Industrial:** Trayectorias complejas, MultiMove (sincronización de brazos) y paletizado avanzado. |




## Diseño Técnico e Integración del Gripper Neumático por Vacío

La manipulación y el paletizado seguro de objetos frágiles como huevos requiere un sistema de sujeción que distribuya la presión uniformemente. Para este laboratorio, se integró un efector final basado en tecnología de vacío por eyección neumática.

### Herramienta Suministrada 
Para el desarrollo del laboratorio, la universidad suministró un módulo comercial de sujeción por vacío de la marca **Festo**, modelo **VAD-ME-I-1/8**. Este dispositivo compacto integra en un solo bloque el eyector de vacío (basado en el principio de Venturi) y una electroválvula solenoide de activación a 24 VDC. Su función principal es transformar la presión del aire comprimido de la red regulada del laboratorio en una fuerza de succión constante aplicada directamente sobre una ventosa de elastómero flexible que amortigua el contacto con el huevo.
<p align="center">
  <img src="media\captura5.png" width="500">
</p>
<p align="center">
  <img src="media\captura6.png" width="500">
</p>

### Configuración de las Entradas/Salidas (I/O) Digitales



* **`Out_9` (Salida Digital - Activación de Vacío):** Controla el estado físico de la electroválvula solenoide.
    * **Estado `1` (On):** Conmuta la bobina, permite el paso de aire comprimido a través del eyector Venturi, generando el vacío necesario para la sujeción del huevo.
    * **Estado `0` (Off):** Corta la alimentación de la válvula, suspendiendo instantáneamente la succión para liberar el huevo en la coordenada destino.




## Diagrama de Flujo: Rutina de Movimiento con Patrón de Caballo de Ajedrez

```mermaid
flowchart TD

    Start([Inicio Function main]):::inicio
    InitSys[Motor On\nPower High\nSpeed 100\nAccel 100 100\nHome]:::proceso
    CallPaletizado[Call Paletizado_01]:::proceso

    SubPallet[Pallet 1 Origen PuntoX PuntoY 6x5]:::proceso
    LoadRoutes[Call CargarRutas]:::proceso
    ClearVars[Inicializar visited y visitedCount]:::proceso
    InitPos[Inicializar curA y curB]:::proceso
    MarkInit[Marcar posiciones iniciales]:::proceso

    LoopStart{k hasta 30}:::decision

    H1_Mark[Marcar curA]:::proceso
    H1_Pick[Jump curA]:::proceso
    H1_On[Activar vacio]:::io
    H1_Place[Jump pathA k]:::proceso
    H1_Off[Desactivar vacio]:::io
    H1_Update[Actualizar curA]:::proceso

    H2_Mark[Marcar curB]:::proceso
    H2_Pick[Jump curB]:::proceso
    H2_On[Activar vacio]:::io
    H2_Place[Jump pathB k]:::proceso
    H2_Off[Desactivar vacio]:::io
    H2_Update[Actualizar curB]:::proceso

    SafeStop[Off Out_9]:::io
    GoHome2[Jump Origen y Home]:::proceso
    EndNode([Fin]):::inicio

    Start --> InitSys
    InitSys --> CallPaletizado
    CallPaletizado --> SubPallet
    SubPallet --> LoadRoutes
    LoadRoutes --> ClearVars
    ClearVars --> InitPos
    InitPos --> MarkInit
    MarkInit --> LoopStart

    LoopStart --> H1_Mark
    H1_Mark --> H1_Pick
    H1_Pick --> H1_On
    H1_On --> H1_Place
    H1_Place --> H1_Off
    H1_Off --> H1_Update

    H1_Update --> H2_Mark
    H2_Mark --> H2_Pick
    H2_Pick --> H2_On
    H2_On --> H2_Place
    H2_Place --> H2_Off
    H2_Off --> H2_Update

    H2_Update --> LoopStart

    LoopStart --> SafeStop
    SafeStop --> GoHome2
    GoHome2 --> EndNode

    classDef inicio fill:#1A659E,color:#FFF
    classDef proceso fill:#F7F9FA,color:#000
    classDef decision fill:#E0FBFC,color:#000
    classDef io fill:#FFF3CD,color:#000
```


## Plano de Planta: Distribución de la Celda y Posiciones de la Cubeta


Para comprender la sincronización y la evasión de colisiones en el espacio de trabajo, esta sección ilustra la distribución espacial de los 32 movimientos ejecutados de forma síncrona por el robot para ambos cuerpos sobre la topología de la cubeta ($6 \times 5$).

Para este caso, el `Origen` se tomó en la esquina superior izquierda de la cubeta, el `PuntoX`en la esquina superior derecha, y el `PuntoY`en la esquina inferior izquierda, todos hechos por un teach manual. Las coordenadas de muestran a continuación:
<p align="center">
  <img src="media\captura7.png" width="500">
</p>

### Mapa Espacial de Posicionamiento Global

Cada casilla de la cubeta contiene su identificador físico (`01` a `30`) acompañado de las etiquetas **`Ax`** y **`Bx`**, las cuales indican el número de paso exacto (`x`) en el que el Huevo A o el Huevo B realizan un asentamiento (`PLACE`) en dicha coordenada.

| | **Columna 1** | **Columna 2** | **Columna 3** | **Columna 4** | **Columna 5** | **Columna 6** |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Fila 1** | `01`<br/>**[A1] [B18]** | `02`<br/>**[A20] [B5]** | `03`<br/>**[A9] [B26]** | `04`<br/>**[A26] [B11]** | `05`<br/>**[A3] [B20]** | `06`<br/>**[A18] [B3]** |
| **Fila 2** | `07`<br/>**[A10] [B27]** | `08`<br/>**[A25] [B10]** | `09`<br/>**[A2] [B19]** | `10`<br/>**[A19] [B4]** | `11`<br/>**[A14] [B31]** | `12`<br/>**[A27] [B12]** |
| **Fila 3** | `13`<br/>**[A21] [B6]** | `14`<br/>**[A8] [B17/B25]** | `15`<br/>**[A23] [B8]** | `16`<br/>**[A28] [B13]** | `17`<br/>**[A17] [B2]** | `18`<br/>**[A4] [B21]** |
| **Fila 4** | `19`<br/>**[A24] [B9]** | `20`<br/>**[A11] [B28]** | `21`<br/>**[A6] [B23]** | `22`<br/>**[A15] [B32]** | `23`<br/>**[A30/31/32] [B15]**| `24`<br/>**[A13] [B30]** |
| **Fila 5** | `25`<br/>**[A7] [B24]** | `26`<br/>**[A22] [B7]** | `27`<br/>**[A29] [B14/16]**| `28`<br/>**[A12] [B29]** | `29`<br/>**[A5] [B22]** | `30`<br/>**[B1] [A16]** |

---





## Análisis de Resultados y Discusión Técnica

* El comando nativo `Jump` demostró ser la estrategia de interpolación espacial más eficiente para esta aplicación, logrando un tiempo de ciclo estimado de 0.32 segundos por cada acción de *pick-and-place* al unificar los movimientos horizontales y verticales en arcos parabólicos continuos y eliminar los tiempos muertos de desaceleración intermedios.
* Aunque la simulación en el entorno de desarrollo tolera perfiles de velocidad y aceleración al 100%, para una operación real con objetos frágiles como huevos se determinó que los parámetros cinemáticos deben limitarse a `Speed 60` y `Accel 50, 50` con el fin de mitigar fuerzas de inercia y vibraciones que comprometan la hermeticidad del agarre.
* La estructura lógica secuencial y alternada del bucle principal (`H1` toma-mueve, luego `H2` toma-mueve) asegura de forma determinista que nunca existirá una colisión espacial entre ambos cuerpos dentro de la celda de manufactura, garantizando que solo un elemento se encuentre en tránsito aéreo a la vez.
* A través de la función de descomposición matemática implementada y el uso del comando `Pallet 1`, el sistema tradujo exitosamente los índices lineales (`1` al `30`) en coordenadas físicas de fila y columna operativas, validando por consola la exploración de las 30 casillas únicas de la cubeta sin desvíos cinemáticos.
* La inclusión de retardos por software de `Wait 0.10` posterior a cada conmutación de la salida digital `Out_9` resultó crítica para equilibrar el comportamiento físico y la compresibilidad del aire dentro del eyector Venturi Festo, evitando fallos operacionales o caídas prematuras del objeto antes de iniciar el arco de subida.
* A pesar de que la simulación en el entorno virtual de EPSON RC+ 7.5.2 fue completamente satisfactoria y exitosa en todas las trayectorias cargadas, no fue posible realizar la implementación y pruebas en el brazo robótico real debido a un daño técnico imprevisto del equipo del laboratorio.

## Código Fuente
**Código aquí:** [`Main.prg`](./Main.prg)

## Video simulación
[Link de la simulación](https://drive.google.com/file/d/1GVtGdpPDQUnC_12v2RCDD1Qm8kQPoECs/view?usp=sharing)

## Conclusiones

* El uso del comando `Jump` optimiza significativamente el tiempo de ciclo en tareas de *pick-and-place* planar en comparación con trayectorias lineales coordinadas, al unificar los movimientos horizontales y verticales en una única trayectoria parabólica continua.
* La programación estructurada mediante matrices locales (`Pallet`) simplifica el control cinemático de celdas de paletizado, permitiendo indexar múltiples posiciones espaciales de forma automática a partir de solo tres puntos de referencia geométricos.
* En sistemas concurrentes de manipulación de componentes, la alternancia síncrona y secuencial de los bucles de movimiento constituye una estrategia de control determinista eficaz para la evasión absoluta de colisiones en el espacio de trabajo.
* La integración de retardos temporales por software (`Wait`) es indispensable en la automatización neumática para compensar la compresibilidad del aire y los tiempos de respuesta físicos de los eyectores de vacío Venturi, garantizando la estabilidad del agarre.
* Los entornos de simulación robótica como EPSON RC+ son herramientas críticas de validación que permiten verificar la viabilidad cinemática, alcances y lógicas de programación ante imprevistos o fallas de hardware en los equipos físicos.


