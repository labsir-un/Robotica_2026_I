[![Ver video](https://img.youtube.com/vi/0VXu4NlrAs8/0.jpg)](https://youtu.be/0VXu4NlrAs8)

# Comparativa Técnica de Manipuladores Industriales: Motoman MH6 vs. ABB IRB 140 vs. EPSON T3-401S

Este documento presenta un cuadro comparativo detallado de las especificaciones técnicas de tres robots industriales con morfologías distintas. Esta información es útil para la caracterización física, el cálculo de matrices de transformación homógeneas (Denavit-Hartenberg) y la simulación cinemática/dinámica en **MATLAB**.

---

## Cuadro Comparativo Detallado

| Característica Técnica | Yaskawa Motoman MH6 | ABB IRB 140 | EPSON T3-401S |
| :--- | :--- | :--- | :--- |
| **Tipo de Estructura** | Antropomórfica (Articulado de 6 ejes) | Antropomórfica (Articulado de 6 ejes) | SCARA (Selective Compliance Assembly Robot Arm) |
| **Grados de Libertad (DoF)** | 6 | 6 | 4 |
| **Configuración de Juntas <br> *(Matriz en MATLAB)*** | `R-R-R-R-R-R` <br> (6 Revolutas) | `R-R-R-R-R-R` <br> (6 Revolutas) | `R-R-P-R` <br> (2 Revolutas, 1 Prismática, 1 Revoluta) |
| **Carga Máxima (Payload)** | 6.0 kg | 6.0 kg | 3.0 kg (Nominal: 1.0 kg) |
| **Alcance Máximo Horizontal** | 1422 mm | 810 mm (hasta eje 5) | 400 mm |
| **Carrera Vertical (Eje Z)** | N/A (Definido por su alcance articular) | N/A (Definido por su alcance articular) | 150 mm (Junta prismática J3) |
| **Repetibilidad** | ±0.08 mm | ±0.03 mm | ±0.02 mm (X, Y) / ±0.02 mm (Z) |
| **Velocidad Máxima por Eje** | **J1:** 220°/s <br> **J2:** 200°/s <br> **J3:** 220°/s <br> **J4:** 410°/s <br> **J5:** 410°/s <br> **J6:** 610°/s | **J1:** 200°/s <br> **J2:** 200°/s <br> **J3:** 260°/s <br> **J4:** 360°/s <br> **J5:** 360°/s <br> **J6:** 450°/s | **Tiempo de ciclo estándar:** 0.54 s <br> *(Velocidad angular combinada alta para Pick & Place)* |
| **Rango de Movimiento** | **J1:** ±170° <br> **J2:** -90° a +155° <br> **J3:** -175° a +250° <br> **J4:** ±180° <br> **J5:** -45° a +225° <br> **J6:** ±360° | **J1:** ±180° <br> **J2:** ±90° <br> **J3:** +110° a -230° <br> **J4:** ±200° (Estándar) <br> **J5:** ±115° <br> **J6:** ±400° | **J1:** ±132° <br> **J2:** ±141° <br> **J3:** 0 a 150 mm <br> **J4 (U):** ±360° |
| **Peso del Manipulador** | ~130 kg | ~98 kg | ~16 kg (All-in-One, controlador integrado) |
| **Controlador de Fábrica** | DX100 / DXM100 | IRC5 | Integrado (Software EPSON RC+) |
| **Aplicaciones Típicas** | • Soldadura por arco (Arc Welding)<br>• Ensamble mecánico<br>• Inyección de plásticos<br>• Manipulación de materiales pesados | • Cuidado de máquinas (Machine Tending)<br>• Rebabado y pulido<br>• Empaque y paletizado<br>• Aplicaciones en cuartos limpios | • Pick and Place de alta velocidad<br>• Ensamble de componentes electrónicos<br>• Automatización de laboratorios químicos<br>• Empaque farmacéutico primario |

---

## Notas de Relevancia para Simulación en MATLAB

Al implementar estos modelos robóticos mediante scripts de MATLAB, ten en cuenta las siguientes restricciones morfológicas:

### 1. Modelado de los Robots Antropomórficos (Motoman MH6 e IRB 140)
* Ambos comparten una configuración clásica de 6 Grados de Libertad con muñeca esférica.
* Al usar comandos como `rigidBodyTree` (Robotics System Toolbox) o la función `Link` (Peter Corke), todas las articulaciones deben ser configuradas como `'revolute'`.
* El **Motoman MH6** destaca por tener un alcance horizontal considerablemente mayor (casi el doble que el IRB 140), lo que expande drásticamente su matriz de espacio de trabajo (*Workspace*).

### 2. Modelado del Robot SCARA (EPSON T3-401S)
* A diferencia de los otros dos, el EPSON T3 posee únicamente 4 grados de libertad.
* En MATLAB, la tercera junta **(J3)** debe ser definida estrictamente como **`'prismatic'`** (prismática/lineal), configurando su movimiento en metros o milímetros en lugar de radianes/grados.
* El espacio de trabajo es cilíndrico. Es ideal para matrices de transformación bidimensionales en planos XY acoplados con una altura Z independiente.

# Configuración de Posición Home - EPSON T3-401S

## 1. Descripción física de la postura

cuando se manda al robot a su posición de inicio ejecutando el comando `Home`, se colocará en la siguiente posición exacta:

* **J1 (Base) = 204800 pulsos (90°):** El cuerpo o primer brazo del robot no apunta hacia el frente, sino que está apuntando completamente hacia la izquierda (alineado de forma paralela al eje Y positivo del robot).
* **J2 (Codo) = 0 pulsos (0°):** El segundo brazo está completamente estirado en línea recta respecto al primer brazo. No tiene ningún doblez en el codo.
* **J3 (Eje Z Vertical) = 0 pulsos (0 mm):** El eje vertical se encuentra en su punto más alto posible (retraído). La pinza o herramienta está levantada al máximo para evitar chocar con nada en la mesa de trabajo.
* **J4 (Eje U Rotación) = 0 pulsos (0°):** El giro final de la punta de la herramienta se encuentra en su ángulo de referencia inicial.

## 2. ¿Por qué el programador configuró el Home así?

Esta es una de las configuraciones de seguridad más utilizadas en celdas de manufactura automatizada por las siguientes razones:

1.  **Home Lateral de Seguridad (Side Park):** Al girar 90° a la izquierda y retraer el eje Z, el robot se "quita de en medio" de la zona central de trabajo. Esto permite que un operador humano pueda meter las manos al frente de la máquina de forma segura, o que pasen cajas/piezas por una banda transportadora central sin riesgo de que choquen con el robot mientras este descansa.

2.  **Prevención de colisiones al arrancar:** Al iniciar el día o tras un paro de emergencia, si el operario presiona "Home", el robot primero subirá el eje Z (porque está en `0`) y luego girará hacia la izquierda. Esto garantiza que la herramienta no arrastrará ni golpeará ningún componente o producto que se haya quedado a medio procesar en la mesa de trabajo.

# Procedimiento para Movimientos Manuales (Jogging) - EPSON T3-401S

Para realizar movimientos manuales en el robot **EPSON T3-401S**, se utiliza la interfaz virtual del software **EPSON RC+** desde una computadora conectada al manipulador. El epson del laboratorio carece de una consola física (*Teach Pendant*), por lo que todo el control se realiza mediante software.

---

## Paso 1: Abrir la ventana de Movimiento Manual (Jog & Teach)

1. Encienda el controlador y el robot. Posteriormente, ejecute el software **EPSON RC+** en su computadora.
2. Asegúrese de que el entorno esté conectado en modo **Online** con el robot.
3. En la barra de herramientas superior, haga clic en el icono **Jog & Teach** (representado por un robot con una mano) o presione la combinación de teclas `Ctrl + J`.
4. Se abrirá la ventana de control denominada *Jog & Teach*.

---

## Paso 2: Encender Motores (Motor ON)

Por motivos de seguridad, los servomotores arrancan en estado desenergizado. Antes de desplazar el robot, es necesario habilitarlos:

1. En la ventana de *Jog & Teach*, localice el botón etiquetado como **Motor On**.
2. Al hacer clic, se escucharán los frenos físicos liberándose en la base del manipulador y el indicador de estado en la pantalla cambiará a color **verde**.

---

## Paso 3: Selección del Modo de Operación (Coordenadas)

En la sección **Mode** o **Coordinate System**, se debe conmutar el tipo de trayectoria matemática que ejecutará el robot:

### Opción A: Modo Articulaciones (Joint)
* **Descripción:** Cada control físico o virtual actúa sobre un motor de forma independiente, ignorando la geometría cartesiana del espacio.
* **Comportamiento de los ejes:**
  * **J1 / J2:** Rotan de forma independiente el brazo de la base y el codo (valores en grados).
  * **J3:** Desplaza el vástago vertical hacia arriba o hacia abajo (valores en milímetros).
  * **J4:** Rota la herramienta en el extremo (eje U) en grados.

### Opción B: Modo Cartesiano (Base / World)
* **Descripción:** El software calcula la cinemática inversa en tiempo real para que el extremo de la herramienta se desplace en líneas rectas perfectas siguiendo el plano tridimensional de la celda de trabajo.

---

## Paso 4: Ejecución de Movimientos, Traslaciones y Rotaciones

Una vez seleccionado el modo, se habilitará el panel de botones con direcciones positivas

---

## 1. Clasificación de los Niveles de Velocidad Manual

En el entorno de programación **EPSON RC+**, la velocidad durante los movimientos manuales (*Jogging*) está estrictamente regulada para garantizar la integridad del personal operativo y la preservación mecánica del manipulador EPSON T3-401S. A diferencia del modo automático, el movimiento manual impone restricciones de potencia basándose en un porcentaje (%) de la velocidad máxima de jog programada en el sistema.

El software categoriza formalmente estos rangos en tres niveles operativos:

* **Nivel Bajo (Low): Rango operativo estándar de 1% a 10%.**
    * *Aplicación:* Utilizado para la aproximación de alta precisión a puntos de trabajo específicos (*Teaching*), calibración del sistema de coordenadas de la herramienta (TCP) o manipulación en la cercanía inmediata de obstáculos mecánicos (herramental, tolvas o sensores de la celda).
* **Nivel Medio (Med): Rango operativo estándar de 11% a 50%.**
    * *Aplicación:* Orientado a la verificación visual de trayectorias generales fuera de zonas críticas de colisión, o para el despeje del manipulador tras la activación de una parada de emergencia.
* **Nivel Alto (High): Rango operativo estándar de 51% a 100%.**
    * *Aplicación:* Restringido exclusivamente para desplazamientos a través de grandes distancias dentro de un espacio de trabajo libre de obstrucciones. 


---

## 2. Procedimiento Operativo para la Modificación de Niveles de Velocidad

La modificación de la velocidad de jog se realiza de manera interactiva y en tiempo real (en caliente), sin requerir la desenergización de los servomotores. El proceso documentado es el siguiente:

1.  **Acceso a la interfaz:** Despliegue la ventana de control manual mediante la combinación de comandos `Ctrl + J` o seleccionando el icono **Jog & Teach** en la barra de herramientas principal de EPSON RC+.
2.  **Localización del panel de control:** Ubique la sección indexada como **Jog Speed**, situada comúnmente en la sección inferior de la interfaz gráfica del panel de control manual.
3.  **Método de selección indexada (Ajuste rápido):** Seleccione mediante un clic el botón radial correspondiente al nivel requerido (*Low*, *Med* o *High*). El sistema cargará inmediatamente el valor porcentual predeterminado de fábrica para dicha categoría.
4.  **Método de selección directa (Ajuste fino):** Para configuraciones personalizadas independientes de los tres niveles estándar, desplace la barra analógica (*Slider*) o introduzca un valor entero directamente en el campo numérico porcentual (por ejemplo, `5` para fijar el límite al 5% de la capacidad de jog). La instrucción entrará en vigor en el siguiente pulso de movimiento ejecutado.

---

## 3. Métodos de Identificación del Nivel de Velocidad Establecido

Para cumplir con las normativas de seguridad industrial, el entorno EPSON RC+ dispone de cuatro mecanismos concurrentes para verificar el estado de velocidad activo antes y durante la manipulación física del brazo robótico:



# 1. Principales Funcionalidades de EPSON RC+ 7.0

## A. Entorno de Desarrollo (IDE) y Lenguaje SPEL+

El software integra un editor de código optimizado para **SPEL+**, un lenguaje de programación de alto nivel, multitarea y estructurado desarrollado por EPSON.

El IDE incluye:

- Herramientas de depuración (*debugging*) en tiempo real.
- Puntos de interrupción (*breakpoints*).
- Ejecución paso a paso.
- Compilador sintáctico que detecta errores antes de la transferencia de datos al controlador.

## B. Gestor del Robot (Robot Manager)

Es el núcleo de configuración de los parámetros físicos del manipulador.

Permite realizar:

- Calibración y definición del origen de los encoders (*Hof*).
- Configuración de herramientas y sistemas de coordenadas locales (*TCP - Tool Center Point*).
- Definición de límites de software (*Soft Limits*) para prevenir colisiones mecánicas accidentales.
- Gestión de la posición de inicio personalizada (*HomeDef*).

## C. Simulador 3D Avanzado

Permite modelar celdas de manufactura completas sin necesidad de hardware físico.

Ofrece:

- Detección virtual de colisiones.
- Cálculo de tiempos de ciclo estimados.
- Validación del espacio de trabajo (*Workspace*).
- Facilitación de la ingeniería preliminar, reduciendo significativamente los riesgos de puesta en marcha.

## D. Gestión de Entradas/Salidas (I/O) y Conectividad

Proporciona una interfaz para mapear, monitorear y forzar señales digitales y de buses de campo (como EtherNet/IP, PROFINET o DeviceNet).

Asimismo, permite integrar sistemas de visión artificial embebidos (*Vision Guide*) para el guiado de robots mediante cámaras.

# 2. Mecanismos de Comunicación con el Manipulador

En el caso específico del robot **EPSON T3-401S**, el controlador está integrado físicamente en la base del propio manipulador (*All-in-One*).

La comunicación entre la computadora host (donde corre EPSON RC+ 7.0) y el robot se realiza bajo la siguiente arquitectura:

```text
[ Computadora Host (EPSON RC+ 7.0) ]
                 │
                 ▼  (Capa Física: Ethernet TCP/IP o USB)
[ Interfaz de Red del Controlador Embebido ]
                 │
                 ▼  (Procesador de Control de Movimiento)
[ Drivers / Servoamplificadores Internos ] ──▶ [ Motores del Robot ]
```

## A. Capa Física y Protocolo de Red

La comunicación se establece principalmente a través de un enlace Ethernet estándar mediante el protocolo TCP/IP (o alternativamente mediante una conexión directa USB).

Se asigna una dirección IP estática al controlador del robot para asegurar un canal de datos dedicado y de baja latencia.

## B. Modelo Host-Controlador

### Modo de Desarrollo / Monitor

Cuando el programador interactúa con la interfaz gráfica (por ejemplo, realizando *Jogging* o modificando parámetros), EPSON RC+ 7.0 envía comandos en formato de cadena de texto estructurada a través de sockets TCP/IP.

El controlador embebido recibe, interpreta y ejecuta la acción de forma inmediata.

### Modo de Ejecución Autónomo

Una vez finalizado el código en SPEL+, este se compila y se descarga directamente en la memoria no volátil del controlador embebido del robot.

A partir de ese momento, el robot puede operar de manera autónoma sin necesidad de mantener la computadora host conectada, procesando la lógica internamente.

## C. Lazo de Realimentación (Feedback)

Durante la operación, el controlador envía de vuelta al software host un flujo continuo de datos de telemetría a alta frecuencia.

Este flujo incluye:

- Las posiciones actuales de los encoders de las articulaciones.
- Vectores de fuerza estimados.
- Estados de error.
- El estado de las líneas de seguridad (*Safety Circuit*).

# 3. Procesos Internos para la Ejecución de Movimientos

Cuando el controlador recibe una instrucción de movimiento en código SPEL+ (por ejemplo, un comando lineal `Move P1` o un comando de interpolación SCARA `Jump P2`), se desencadena una secuencia cíclica y determinista de procesos matemáticos y electrónicos:

```text
[ Comando SPEL+ (ej. Move P1) ]
               │
               ▼
1. Interpretación y Parsing del Comando
               │
               ▼
2. Planificación de la Trayectoria (Perfil de velocidad Curva en S)
               │
               ▼
3. Transformación Cinemática (Cinemática Inversa: Cartesiano ➔ Pulsos)
               │
               ▼
4. Lazo de Servocontrol (PID, Generación de PWM y Feedback del Encoder)
```

## 1. Interpretación y Parsing del Comando

El procesador interno del controlador decodifica la línea de comando.

Identifica:

- El tipo de trayectoria solicitada (articular, lineal o arco).
- Las coordenadas del punto de destino (definidas en pulsos o milímetros).
- Los modificadores de velocidad (`Speed`) y aceleración (`Accel`).

## 2. Planificación de la Trayectoria (Generación de Perfiles)

El algoritmo de control calcula el perfil de movimiento óptimo en el tiempo.

Utiliza perfiles de velocidad de aceleración/desaceleración controlada (típicamente curvas trapezoidales o en forma de S, *S-Curve*) para:

- Suavizar el movimiento.
- Minimizar las fuerzas de inercia.
- Evitar vibraciones que degraden la vida útil de los reductores mecánicos.

## 3. Transformación Cinemática (Cinemática Inversa)

Dado que los puntos suelen programarse en coordenadas cartesianas del espacio de trabajo $(X, Y, Z, U)$, el procesador ejecuta las ecuaciones de cinemática inversa.

Este proceso matemático:

- Traduce las trayectorias cartesianas continuas en valores angulares y lineales específicos para cada una de las cuatro articulaciones del robot SCARA.
- Convierte dichos valores en pulsos de encoder digitales.

## 4. Lazo de Servocontrol (Servo Loop)

Una vez calculados los pulsos objetivo para cada intervalo de muestreo (frecuencia de lazo cerrado típicamente en el rango de los kHz), las señales se envían a los servoamplificadores internos.

### Funcionamiento

1. Los servoamplificadores modulan la corriente eléctrica mediante PWM enviada a los servomotores síncronos *brushless* de cada eje.

2. A medida que los motores giran, los encoders absolutos acoplados a los ejes miden la posición real del brazo y la devuelven al controlador.

3. Un algoritmo de control PID (Proporcional–Integral–Derivativo) compara la posición real con la posición teórica calculada, corrigiendo instantáneamente cualquier error de seguimiento.

### Resultado

El robot alcanza el punto exacto con la repetibilidad milimétrica especificada por el fabricante.

# Análisis Comparativo de Entornos de Software: EPSON RC+ 7.0 vs. RoboDK vs. RobotStudio

En el ámbito de la automatización industrial, la selección del entorno de software es tan crítica como la del propio hardware. A continuación, se presenta un análisis comparativo profundo entre tres de las plataformas más utilizadas en el diseño, programación y simulación de celdas robóticas: **EPSON RC+ 7.0**, **RoboDK** y **ABB RobotStudio**.

---

## 1. EPSON RC+ 7.0: Entorno Propietario Dedicado

**EPSON RC+ 7.0** es un entorno de desarrollo integrado (IDE) de tipo cerrado y propietario, diseñado exclusivamente para la programación y control de la gama de robots de EPSON (SCARA, 6-Ejes y series *All-in-One* como el T3-401S).

* **Ventajas:**
    * **Integración de hardware nativa y absoluta:** Al ser un software de la marca, no requiere traductores ni *post-procesadores*. La comunicación con los controladores (física y lógica) es directa y en tiempo real.
    * **Optimización para robots SCARA:** Su motor de cálculo cinemático y el lenguaje **SPEL+** están perfectamente estructurados para operaciones de ensamblaje rápido y manipulación *Pick & Place* de alta velocidad.
    * **Ecosistema embebido:** Permite integrar de manera nativa sistemas de visión artificial (*Vision Guide*) y control de fuerza sin salir de la misma interfaz.
* **Limitaciones:**
    * **Incompatibilidad multimarca:** Es completamente inútil si se intenta programar o simular un robot de cualquier otro fabricante (ABB, KUKA, Yaskawa, etc.).
    * **Entorno gráfico de simulación básico:** Aunque cuenta con un simulador 3D para validación de espacios de trabajo y cálculo de tiempos de ciclo, sus capacidades de renderizado gráfico y modelado de entornos complejos de fábrica son limitadas en comparación con plataformas dedicadas de simulación.
* **Aplicaciones Típicas:**
    * Líneas de ensamble de componentes electrónicos de alta precisión.
    * Celdas de empaque y clasificación (*kitting*) en la industria farmacéutica y cosmética.
    * Automatización de laboratorios clínicos y manipulación de bandejas de semiconductores.

---

## 2. RoboDK: Plataforma Multimarca Agnóstica

**RoboDK** es un software de programación fuera de línea (OLP - *Off-Line Programming*) y simulación en 3D de carácter universal y agnóstico, lo que significa que es compatible con más de 50 fabricantes de robots diferentes y posee una biblioteca nativa de más de 900 modelos.



* **Ventajas:**
    * **Versatilidad multimarca:** Permite simular y programar robots de diferentes marcas (incluyendo EPSON y ABB) dentro de una misma celda de trabajo.
    * **Post-procesadores robustos:** Traduce la simulación visual a los lenguajes de código nativos de cada marca (convierte a SPEL+, RAPID, INFORM, JBI, etc.) de manera limpia.
    * **Asequible y liviano:** Requiere menos recursos de computación que los entornos de grandes corporaciones y su curva de aprendizaje es de las más rápidas del mercado.
    * **Programación avanzada por APIs:** Soporta extensiones y scripts complejos mediante Python, C++, C# y MATLAB, facilitando la integración con algoritmos de Inteligencia Artificial o trayectorias generadas por software CAD/CAM.
* **Limitaciones:**
    * **Lazo cerrado limitado en tiempo real:** No está diseñado para actuar como un controlador de producción en tiempo real directo de fábrica; es una herramienta de simulación y generación de código *offline*.
    * **Falta de optimización fina nativa:** Al abarcar tantas marcas, puede omitir funciones ultra-específicas de firmware o configuraciones de seguridad profunda de un fabricante concreto, requiriendo ajustes manuales posteriores en el controlador real.
* **Aplicaciones Típicas:**
    * Mecanizado robótico de moldes, fresado 3D, grabado y corte por plasma (conversión directa de archivos G-code/CAM a trayectorias de robot).
    * Impresión 3D a gran escala mediante brazos robóticos.
    * Celdas educativas e integradores medianos que configuran robots reutilizados de diferentes marcas.

---

## 3. ABB RobotStudio: El Estándar de Oro en Simulación Propietaria

**ABB RobotStudio** es una de las herramientas de simulación y programación fuera de línea más potentes del mercado. Aunque es un entorno propietario para robots ABB, está construido sobre el motor gráfico de Microsoft Virtual Reality y el controlador virtual de ABB (*VirtualController*).



* **Ventajas:**
    * **Gemelo Digital Perfecto (Digital Twin):** Utiliza exactamente el mismo software de control que corre dentro del hardware real de ABB. Esto garantiza que una simulación en RobotStudio tenga una precisión del 99% en tiempos de ciclo, trayectorias y comportamiento dinámico real.
    * **Programación en RAPID sofisticada:** Ofrece un entorno inigualable para depurar el lenguaje **RAPID** de ABB, permitiendo simular lógicas complejas de seguridad de fábrica (*SafeMove*).
    * **Simulación de sistemas complejos:** Es capaz de modelar celdas con múltiples robots cooperativos controlados por una sola CPU (*MultiMove*), bandas transportadoras interconectadas y sistemas neumáticos avanzados.
* **Limitaciones:**
    * **Cerrado a la marca ABB:** No procesa código ni simula de forma fidedigna la cinemática interna de robots competidores como EPSON o Fanuc.
    * **Alto costo de licenciamiento:** Es una herramienta de nivel empresarial con un esquema de licencias costoso (tanto de adquisición como de mantenimiento anual).
    * **Altos requerimientos de hardware:** Exige estaciones de trabajo con tarjetas gráficas dedicadas de alta gama para renderizar simulaciones industriales masivas.
* **Aplicaciones Típicas:**
    * Líneas robotizadas completas en la industria automotriz (soldadura por puntos, pintura, manipulación de chasis).
    * Paletizado masivo en finales de línea logísticos y de alimentos.
    * Puestas en marcha virtuales complejas donde el tiempo de inactividad de la planta física debe reducirse al mínimo.

---

## 4. Cuadro Comparativo de Síntesis

| Criterio Técnico | EPSON RC+ 7.0 | RoboDK | ABB RobotStudio |
| :--- | :--- | :--- | :--- |
| **Tipo de Entorno** | Propietario (EPSON) | Universal / Multimarca | Propietario (ABB) |
| **Lenguaje de Programación** | `SPEL+` | Gráfico / Python, C#, C++ / MATLAB | `RAPID` |
| **Precisión del Tiempo de Ciclo** | Alta (en hardware EPSON) | Estimada (depende del post-procesador) | Idéntica al robot real (Gemelo Digital) |
| **Capacidades CAD / CAM** | Básicas (Primitivas 3D) | Excelentes (Importación de trayectorias NC/G-code) | Altas (Herramientas internas de modelado y ensamble) |
| **Enfoque de Mercado** | Celdas pequeñas/medianas de alta velocidad (SCARA) | Integradores multimarca, Educación, Aplicaciones CAD-to-Robot | Grandes plantas industriales, Automotriz, Líneas pesadas |
| **Curva de Aprendizaje** | Corta (Orientada al código estructurado) | Muy corta (Interfaz intuitiva e interactiva) | Moderada a larga (Complejidad de opciones de ingeniería) |

---

## Conclusión del Análisis

La elección entre estas herramientas depende del objetivo del proyecto de ingeniería:

1. Si la celda se compone exclusivamente de brazos **SCARA o compactos de EPSON** orientados a la electrónica o ensamble rápido, **EPSON RC+ 7.0** es insustituible debido a su comunicación directa y control de periféricos nativos.
2. Si el proyecto requiere **flexibilidad**, el uso de robots de distintas marcas, o proviene de un flujo de trabajo basado en **diseño CAD/CAM** (fresado, escultura, impresión 3D), **RoboDK** ofrece la plataforma de traducción más versátil del mercado.
3. Si se está diseñando una línea de producción de **alta complejidad industrial con robots ABB**, donde el error de sincronización de un milisegundo cuesta miles de dólares, **RobotStudio** se posiciona como la única herramienta capaz de garantizar un gemelo digital exacto antes de tocar el suelo de la fábrica.

## Diseño técnico del gripper neumático por vacío,
![Diseño Chupa](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2003%20-%20Rob%C3%B3tica%20Industrial%20EPSON%20T3%20401S%20y%20EPSON%20RC%2B/Dise%C3%B1o_Chupa.jpeg?raw=true)

Se Uso el Bit #9 llamado Succ con logica negada para encender y apagar el gripper

![I/O Monitor](https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/main/Laboratorio%20No.%2003%20-%20Rob%C3%B3tica%20Industrial%20EPSON%20T3%20401S%20y%20EPSON%20RC%2B/I0.png)

## Diagrama de Flujo 
![Funciones EPSON RC+](https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/main/Laboratorio%20No.%2003%20-%20Rob%C3%B3tica%20Industrial%20EPSON%20T3%20401S%20y%20EPSON%20RC%2B/Funciones.png)

![Interfaz Principal EPSON RC+](https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/main/Laboratorio%20No.%2003%20-%20Rob%C3%B3tica%20Industrial%20EPSON%20T3%20401S%20y%20EPSON%20RC%2B/Main.png)

### Plano de planta

![Plano de Planta](https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/main/Laboratorio%20No.%2003%20-%20Rob%C3%B3tica%20Industrial%20EPSON%20T3%20401S%20y%20EPSON%20RC%2B/plano-de-planta.jpeg)

*Figura. Plano de planta de trabajo diseñada para el robot EPSON T3-401S, mostrando la distribución de los elementos dentro del espacio de operación.*

