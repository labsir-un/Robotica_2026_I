# Laboratorio No. 03 — Robótica Industrial
### Análisis y Operación del Manipulador EPSON T3-401S.
**Universidad Nacional de Colombia · Robótica 2026-I**

---

## Integrantes

| Nombre | URL del Repositorio |
|--------|-------------------|
| Julian Benitez | https://github.com/JulianI3 |
| Juan Salamanca | https://github.com/JuanSalan |

---

## Descripción de la Solución

En este laboratorio se trabajó con el simulador EPSON RC+ 7.0 para la programación y validación de tareas de manipulación utilizando el robot SCARA EPSON T3-401S. Mediante el desarrollo de un programa en lenguaje SPEL+, se implementó una estrategia de paletizado para el transporte de dos huevos en una cubeta, empleando un manipulador neumático como elemento de agarre. Para definir la secuencia de posiciones de depósito, se generó un pallet basado en el recorrido del caballo en ajedrez, garantizando que los huevos fueran ubicados en posiciones diferentes sin repetir casillas previamente ocupadas. La solución fue validada en el entorno de simulación, permitiendo verificar el correcto funcionamiento de las rutinas de pick-and-place.

---
## Tabla comparativa de especificaciones entre robot manipulador Motoman MH6 y IRB 140

La siguiente tabla muestra las características técnicas de los 3 Robots manipuladores utilizados en los últimos laboratorios
<table align="center">
  <tr>
    <th align="center">Característica</th>
    <th align="center">Motoman MH6</th>
    <th align="center">IRB 140</th>
    <th align="center">EPSON T3-401S</th>
  </tr>

  <tr>
    <td align="center">Fabricante</td>
    <td align="center">Yaskawa Motoman</td>
    <td align="center">ABB</td>
    <td align="center">EPSON</td>
  </tr>

  <tr>
    <td align="center">Controlador</td>
    <td align="center">DX100</td>
    <td align="center">IRC5</td>
    <td align="center">Controlador integrado T3 (EPSON RC+ 7.0)</td>
  </tr>

  <tr>
    <td align="center">Carga útil</td>
    <td align="center">6 kg</td>
    <td align="center">6 kg</td>
    <td align="center">3 kg</td>
  </tr>

  <tr>
    <td align="center">Alcance</td>
    <td align="center">1422 mm</td>
    <td align="center">800 mm</td>
    <td align="center">400 mm</td>
  </tr>

  <tr>
    <td align="center">Número de grados de libertad</td>
    <td align="center">6</td>
    <td align="center">6</td>
    <td align="center">4</td>
  </tr>

  <tr>
    <td align="center">Peso</td>
    <td align="center">130 kg</td>
    <td align="center">98 kg</td>
    <td align="center">16 kg</td>
  </tr>

  <tr>
    <td align="center">Repetibilidad</td>
    <td align="center">±0,08 mm</td>
    <td align="center">±0,08 mm</td>
    <td align="center">±0,02 mm</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje S / A / 1</td>
    <td align="center">140 °/s</td>
    <td align="center">200 °/s</td>
    <td align="center">3,7 m/s</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje L / B / 2</td>
    <td align="center">130 °/s</td>
    <td align="center">200 °/s</td>
    <td align="center">3,7 m/s</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje U / C / 3</td>
    <td align="center">135 °/s</td>
    <td align="center">260 °/s</td>
    <td align="center">1,0 m/s</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje R / D / 4</td>
    <td align="center">270 °/s</td>
    <td align="center">360 °/s</td>
    <td align="center">260 °/s</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje B / E / 5</td>
    <td align="center">270 °/s</td>
    <td align="center">360 °/s</td>
    <td align="center">N.A.</td>
  </tr>

  <tr>
    <td align="center">Velocidad eje T / F / 6</td>
    <td align="center">400 °/s</td>
    <td align="center">450 °/s</td>
    <td align="center">N.A.</td>
  </tr>

  <tr>
    <td align="center">Aplicaciones típicas</td>
    <td align="center">Soldadura por arco, corte y manipulación de materiales</td>
    <td align="center">Ensamblaje de precisión, pick and place y educación</td>
    <td align="center">Pick and place, ensamblaje, clasificación, manipulación de pequeñas piezas y automatización de laboratorio</td>
  </tr>
</table>
<div align="center">

<div align="center">

<table>
<tr>
<td align="center">
<img src="Diagramas-Imágenes/Ejes%20manipulador%20Motoman%20MH6.png"
     width="340"
     height="400">
<br>
<b>(a)</b> Notación de ejes para el manipulador Motoman MH6
</td>

<td align="center">
<img src="Diagramas-Imágenes/Ejes%20manipulador%20IRB%20140.png"
     width="320"
     height="400">
<br>
<b>(b)</b> Notación de ejes para el manipulador IRB 140
</td>

<td align="center">
<img src="Diagramas-Imágenes/epson.png"
     width="320"
     height="400">
<br>
<b>(c)</b> Notación de ejes para el manipulador EPSON T3-401S
</td>

</tr>
</table>

</div>
</div>


---
### Configuración HOME del robot EPSON T3-401S

La configuración **HOME** define la posición de referencia del robot EPSON T3-401S, la cual es utilizada como punto seguro para el inicio y finalización de tareas, recuperación ante errores y procedimientos de calibración. Esta configuración se establece desde el entorno de programación **EPSON RC+ 7.0** y se define mediante los valores de posición de cada articulación medidos en pulsos de codificador (*encoder pulses*).

En la práctica realizada, la posición HOME fue configurada con los siguientes valores:


| Articulación | Posición HOME |
| ------------ | ------------: |
| J1           | 204800 pulsos |
| J2           |      0 pulsos |
| J3           |      0 pulsos |
| J4           |      0 pulsos |


Las articulaciones del robot corresponden a los siguientes movimientos:

* **J1:** rotación de la base del robot alrededor del eje vertical.
* **J2:** rotación del brazo principal.
* **J3:** desplazamiento vertical del eje prismático.
* **J4:** rotación de la herramienta o efector final.

Adicionalmente, el sistema permite definir el orden en que cada articulación se desplaza durante el retorno a HOME. Para esta configuración se estableció el siguiente esquema:


| Articulación | Orden de movimiento |
| ------------ | ------------------- |
| J1           | Paso 2              |
| J2           | Paso 2              |
| J3           | Paso 1              |
| J4           | Paso 2              |



De acuerdo con esta configuración, el eje vertical (**J3**) se desplaza primero hasta alcanzar su posición de referencia. Posteriormente, las articulaciones **J1**, **J2** y **J4** realizan el movimiento hacia sus respectivas posiciones HOME. Esta estrategia permite incrementar la seguridad operacional del sistema, ya que el efector final se eleva antes de ejecutar desplazamientos horizontales o movimientos de orientación, reduciendo la probabilidad de colisiones con piezas, herramientas o elementos del entorno de trabajo.


---
### Movimientos manuales del robot EPSON T3-401S en EPSON RC+ 7.0

La pestaña **Mover y enseñar** de EPSON RC+ 7.0 permite realizar el control manual del robot EPSON T3-401S para tareas de enseñanza de puntos, verificación de trayectorias y posicionamiento del efector final. Desde esta interfaz es posible operar el manipulador tanto en coordenadas articulares como en coordenadas cartesianas, además de visualizar en tiempo real la posición actual del robot y configurar la magnitud de cada desplazamiento.

Para realizar movimientos manuales, inicialmente se debe seleccionar el modo de operación en el menú **Modo**. El software ofrece dos alternativas principales:

* **Articulación:** permite controlar individualmente cada eje del robot.
* **Cartesiano (Mundo):** permite controlar directamente la posición del efector final respecto al sistema de referencia global.

#### Movimiento en modo articulación

Al seleccionar el modo Articulación, se habilitan los controles correspondientes a los ejes del robot:
<div align="center">
    <img src="Diagramas-Imágenes/Articular.png" width="600">
</div>

* **J1:** rotación de la base.
* **J2:** rotación del brazo principal.
* **J3:** desplazamiento vertical.
* **J4:** rotación de la herramienta.

El movimiento se realiza mediante los botones de incremento y decremento asociados a cada articulación. Cada pulsación produce un desplazamiento de magnitud definida por el tamaño de paso seleccionado, mientras que manteniendo presionado el botón puede obtenerse un movimiento continuo.

#### Movimiento en modo cartesiano

Al seleccionar el modo cartesiano, los controles permiten desplazar el efector final directamente en el espacio de trabajo. En este modo pueden realizarse:

<div align="center">
    <img src="Diagramas-Imágenes/EJES.png" width="600">
</div>

* Traslaciones sobre el eje **X**.
* Traslaciones sobre el eje **Y**.
* Traslaciones sobre el eje **Z**.
* Rotaciones alrededor del eje **U**, correspondiente a la orientación de la herramienta.

Este modo resulta especialmente útil para posicionar el efector final respecto a objetos o estaciones de trabajo sin necesidad de manipular individualmente cada articulación.

#### Lectura de posición

La interfaz muestra permanentemente la posición actual del robot, permitiendo visualizarla en diferentes sistemas de referencia:

* **Mundo (World):** coordenadas cartesianas globales del efector final.
* **Articulación (Joint):** posición individual de cada eje.
* **Pulso (Pulse):** valores internos del controlador expresados en pulsos de codificador.

Esta funcionalidad facilita la enseñanza de puntos y la verificación de configuraciones específicas del manipulador.

#### Configuración del tamaño de paso

EPSON RC+ permite seleccionar la distancia recorrida en cada movimiento manual mediante cuatro niveles de desplazamiento:

* **Corto:** 0,1 unidades (mm o grados).
* **Medio:** 1 unidad (mm o grado).
* **Largo:** 10 unidades (mm o grados).
* **Continuo:** movimiento constante mientras se mantenga presionado el control correspondiente.


Finalmente, la velocidad de movimiento puede ajustarse mediante el selector de velocidad disponible en la interfaz, permitiendo realizar operaciones de enseñanza de forma segura y controlada.

---
### Niveles de velocidad para movimientos manuales

EPSON RC+ 7.0 permite realizar movimientos manuales del robot mediante dos niveles de velocidad: "Baja (Low)" y "Alta (High)". Estos niveles determinan la rapidez con la que el manipulador responde a las órdenes de desplazamiento ejecutadas desde la pestaña **Mover y enseñar**, tanto en modo articular como cartesiano.

El nivel "Baja" está orientado a tareas de programación, enseñanza de puntos y verificación de trayectorias. Debido a la menor velocidad de desplazamiento, el operador dispone de un mayor control sobre los movimientos del robot, lo que facilita la realización de ajustes precisos y reduce los riesgos asociados a errores de programación o posicionamiento.

Por su parte, el nivel "Alta" permite efectuar desplazamientos manuales más rápidos dentro del espacio de trabajo. Este modo resulta útil cuando se requiere recorrer distancias relativamente grandes durante las etapas de configuración o validación de una aplicación, disminuyendo el tiempo necesario para posicionar el manipulador.

El cambio entre niveles de velocidad puede realizarse directamente desde la interfaz de EPSON RC+ 7.0. En la pestaña "Mover y enseñar" se encuentra el selector Velocidad, el cual permite elegir entre los modos "Baja" y "Alta". 

La identificación del nivel activo se realiza observando el valor mostrado en el campo "Velocidad" de la ventana de movimiento manual. El modo seleccionado permanece activo hasta que el usuario lo modifique nuevamente, aplicándose a todos los movimientos ejecutados desde la interfaz de enseñanza.




## Diagrama de flujo 

##  Flujo principal del código:
[Diagrama de flujo principal](Diagramas-Imágenes/flujo_principal_robot.png)

##  Flujo del movimiento ventosa:
[Diagrama de flujo ventosas](Diagramas-Imágenes/detalle_ciclo_movimiento_huevo.png)

# Análisis Comparativo: EPSON RC+ 7.0 vs RoboDK vs RobotStudio

## Introducción

Estos tres software representan enfoques distintos dentro del ecosistema de programación y simulación robótica industrial: una plataforma de programación nativa de fabricante (EPSON RC+), una plataforma de simulación/programación off-line independiente del fabricante (RoboDK), y una plataforma de simulación nativa de fabricante (RobotStudio, de ABB). A continuación se presenta un análisis comparativo de cada una.

---

## 1. EPSON RC+ 7.0

### Descripción general
Entorno de desarrollo integrado (IDE) propietario de Epson para programar, simular y controlar sus robots industriales (series SCARA, 6 ejes, y robots cartesianos) mediante el lenguaje SPEL+.

### Ventajas
- **Integración nativa total** con controladores Epson; comunicación directa sin capas de traducción adicionales.
- **Acceso completo a funciones específicas del fabricante**: E/S del controlador, visión Epson (Epson RC+ Vision Guide), fuerza/par, y configuraciones de seguridad propias.
- **Depuración en tiempo real** directamente sobre el robot físico o el simulador integrado, con monitoreo de variables y ejecución paso a paso.
- **Lenguaje SPEL+** relativamente sencillo de aprender para tareas básicas de movimiento y lógica secuencial.
- **Costo incluido** generalmente con la compra del controlador (no requiere licencias adicionales para funciones básicas).

### Limitaciones
- **Exclusividad de marca**: solo funciona con robots Epson; no es transferible a otras plataformas.
- **Simulación 3D limitada** en comparación con RoboDK o RobotStudio; el entorno gráfico es funcional pero menos sofisticado para verificación de colisiones o celdas complejas.
- **Curva de aprendizaje en errores de compilación específicos del entorno** (como se ha evidenciado en tareas con trayectorias tipo "salto de caballo"), ya que los mensajes de error no siempre son intuitivos.
- **Personalización de interfaz y herramientas de análisis de movimiento** (cinemática inversa visual, optimización de trayectoria) más limitada que en plataformas de simulación dedicadas.

### Aplicaciones típicas
- Programación y puesta en marcha de celdas de trabajo con robots Epson en producción real.
- Tareas de pick-and-place, ensamblaje de precisión y aplicaciones SCARA en electrónica.
- Prácticas académicas de programación robótica orientadas a lógica de control y E/S (como ejercicios de trayectorias y secuencias condicionales).

---

## 2. RoboDK

### Descripción general
Software de simulación y programación off-line (OLP) independiente del fabricante, compatible con más de 500 modelos de robots de distintas marcas (ABB, KUKA, Fanuc, Epson, Universal Robots, entre otros).

### Ventajas
- **Independencia de marca**: permite simular y generar código para múltiples fabricantes desde una sola interfaz, facilitando comparaciones entre robots.
- **Programación off-line robusta**: permite diseñar trayectorias, celdas de trabajo y verificar colisiones sin necesidad del robot físico, reduciendo tiempos de inactividad en producción.
- **API en Python y otros lenguajes**, lo que permite automatizar tareas, generar trayectorias paramétricas y conectar con herramientas externas (MATLAB, CAD, visión artificial).
- **Importación directa de modelos CAD** (STEP, IGES, STL) para construir celdas virtuales fieles a la geometría real.
- **Generación de código nativo** para el controlador específico del robot una vez validada la simulación (post-processors).
- **Herramientas de cinemática avanzada**: cálculo de espacio de trabajo, singularidades, y optimización de orientación de herramienta.

### Limitaciones
- **No es un controlador en tiempo real**: la ejecución final depende de transferir el programa generado al controlador nativo del robot, lo que puede generar diferencias menores entre simulación y ejecución real.
- **Costo de licencia** para funciones avanzadas (post-procesadores específicos, módulos de machining, etc.), aunque existe una versión gratuita con funcionalidad básica.
- **Fidelidad de simulación dependiente de la calidad del modelo importado**; celdas mal modeladas pueden dar falsas garantías de ausencia de colisión.
- **Sin acceso directo a funciones de bajo nivel** propias de cada fabricante (a menos que se programen manualmente en el código nativo generado).

### Aplicaciones típicas
- Diseño y validación de celdas robóticas multi-marca antes de la instalación física.
- Aplicaciones de manufactura aditiva, fresado, soldadura y pulido con trayectorias complejas generadas por CAD/CAM.
- Educación e investigación en robótica donde se requiere comparar cinemática y desempeño entre diferentes modelos de robot.
- Generación de trayectorias para brazos robóticos en proyectos académicos (cálculo de cinemática directa/inversa, visualización DH).

---

## 3. RobotStudio

### Descripción general
Software de simulación y programación off-line desarrollado por ABB exclusivamente para su línea de robots industriales, basado en el lenguaje RAPID.

### Ventajas
- **Gemelo digital de alta fidelidad** específico para robots ABB, con modelos virtuales que replican el comportamiento real del controlador (incluyendo el motor de simulación virtual IRC5/OmniCore).
- **VirtualRobot™**: tecnología que ejecuta el mismo software controlador que el robot físico, lo que minimiza la brecha entre simulación y comportamiento real.
- **Herramientas especializadas integradas**: RobotStudio incluye módulos para soldadura, paletizado, pintura y manejo de prensas, optimizados para aplicaciones industriales ABB.
- **Multi-Move**: simulación avanzada de múltiples robots ABB trabajando coordinadamente en una misma celda.
- **Generación automática de trayectorias** a partir de geometría CAD importada (AutoPath), útil en aplicaciones de mecanizado o seguimiento de contornos.

### Limitaciones
- **Exclusividad de marca**: limitado a robots ABB; no permite programar ni simular robots de otros fabricantes de forma nativa.
- **Costo de licencias** relativamente alto para módulos avanzados (PowerPacs especializados por industria).
- **Curva de aprendizaje del lenguaje RAPID** y de la arquitectura de controladores ABB para usuarios sin experiencia previa con la marca.
- **Menor flexibilidad para proyectos académicos comparativos**, ya que no permite evaluar otras arquitecturas robóticas dentro del mismo entorno.

### Aplicaciones típicas
- Programación, simulación y puesta en marcha virtual de celdas robóticas ABB en entornos industriales (automotriz, manufactura pesada).
- Aplicaciones de soldadura robotizada, paletizado y manejo de materiales a gran escala.
- Validación de tiempos de ciclo y detección de colisiones antes de la implementación física en líneas de producción ABB.

---

## Tabla comparativa resumen

| Criterio | EPSON RC+ 7.0 | RoboDK | RobotStudio |
|---|---|---|---|
| **Fabricante / alcance** | Epson (exclusivo) | Multi-marca (~500 robots) | ABB (exclusivo) |
| **Tipo de software** | Programación + control nativo | Simulación/programación off-line | Simulación/programación off-line nativa |
| **Lenguaje de programación** | SPEL+ | Python / API propia / código nativo generado | RAPID |
| **Fidelidad de simulación** | Media | Media-Alta (depende del modelo CAD) | Alta (VirtualRobot™) |
| **Costo** | Incluido con controlador | Gratuito (básico) / licencia paga (avanzado) | Licencia paga (módulos especializados costosos) |
| **Mejor uso** | Producción real con robots Epson | Comparación multi-marca, CAD/CAM, prototipado | Producción industrial a gran escala con ABB |
| **Integración CAD** | Limitada | Alta (STEP, IGES, STL) | Alta (AutoPath) |
| **Curva de aprendizaje** | Baja-Media | Media | Media-Alta |

---

## Conclusión general

- **EPSON RC+ 7.0** es la opción obligada cuando se trabaja directamente con hardware Epson, priorizando el control real sobre la simulación.
- **RoboDK** destaca en flexibilidad y neutralidad de marca, siendo ideal para fases de diseño, prototipado académico y proyectos que requieren comparar cinemática entre distintos robots.
- **RobotStudio** es superior en fidelidad de simulación y herramientas industriales especializadas, pero solo dentro del ecosistema ABB, por lo que su uso se justifica en proyectos de gran escala con esa marca específica.

La elección entre estas herramientas depende principalmente de si el proyecto está atado a una marca específica de robot (Epson o ABB) o si se busca una solución agnóstica de fabricante (RoboDK) para fases de diseño, validación y comparación.


# EPSON RC+ 7.0: Funcionalidades, Comunicación y Ejecución de Movimientos

## 1. Funcionalidades principales

- **Editor/Depurador SPEL+**: programación, compilación y ejecución paso a paso con breakpoints e inspección de variables.
- **Robot Manager**: configuración de tipo de robot, herramientas (Tool), sistemas de coordenadas (Local), cargas y zonas de exclusión.
- **Vision Guide**: visión artificial integrada para localización de piezas y calibración cámara-robot.
- **Simulador 3D**: visualización de trayectorias y detección básica de colisiones antes de ejecutar en el robot real.
- **Monitor de E/S**: visualización en vivo de entradas/salidas y estado del controlador.
- **Tareas concurrentes**: ejecución de hasta 16 tareas SPEL+ en paralelo, sincronizadas con semáforos o variables compartidas.

## 2. Comunicación con el manipulador

**PC ↔ Controlador**: RC+ se conecta al controlador (RC700, RC90, etc.) vía USB, Ethernet/TCP-IP o RS-232, transfiriendo el programa compilado, puntos y parámetros (Tool, Local, velocidad).

**Controlador ↔ Manipulador**: el controlador ejecuta el programa de forma autónoma y se comunica con los servomotores de cada eje mediante buses internos (encoders, corriente, posición). El manipulador no interpreta SPEL+ directamente; el controlador es quien traduce las instrucciones a movimiento real.

## 3. Proceso de ejecución de un movimiento

1. **Interpretación**: el controlador lee la instrucción (`Go`, `Jump`, `Move`) y extrae punto destino, sistema de coordenadas y parámetros de velocidad/aceleración.
2. **Cinemática inversa**: si el punto es cartesiano, se calculan los ángulos articulares necesarios y se valida que sea alcanzable.
3. **Planificación de trayectoria**: se genera un perfil de movimiento (trapezoidal o en S) por articulación, optimizando tiempo de ciclo.
4. **Verificación de seguridad**: chequeo de límites articulares, zonas de exclusión y señales de seguridad (paros de emergencia, sensores).
5. **Generación de setpoints**: el controlador envía consignas periódicas a los drivers de los servomotores.
6. **Control y retroalimentación**: cada eje tiene un lazo cerrado que compara posición real (encoder) vs. deseada y ajusta torque; al alcanzar la tolerancia, el movimiento se marca como completado y el programa continúa.

## 4. Flujo resumido

```
PC (RC+ 7.0) → compila y transfiere programa SPEL+
      ↓
Controlador → interpreta, calcula cinemática inversa, planifica trayectoria, verifica seguridad
      ↓
Servomotores/Encoders → ejecutan movimiento con lazo de control cerrado
      ↓
Controlador confirma posición → continúa el programa
```

El controlador es el "cerebro" en tiempo real que ejecuta cinemática y control; la PC con RC+ funciona como interfaz de desarrollo y supervisión.

# EPSON RC+ 7.0: Funcionalidades, Comunicación y Ejecución de Movimientos

## 1. Funcionalidades principales

- **Editor/Depurador SPEL+**: programación, compilación y ejecución paso a paso con breakpoints e inspección de variables.
- **Robot Manager**: configuración de tipo de robot, herramientas (Tool), sistemas de coordenadas (Local), cargas y zonas de exclusión.
- **Vision Guide**: visión artificial integrada para localización de piezas y calibración cámara-robot.
- **Simulador 3D**: visualización de trayectorias y detección básica de colisiones antes de ejecutar en el robot real.
- **Monitor de E/S**: visualización en vivo de entradas/salidas y estado del controlador.
- **Tareas concurrentes**: ejecución de hasta 16 tareas SPEL+ en paralelo, sincronizadas con semáforos o variables compartidas.

## 2. Comunicación con el manipulador

**PC ↔ Controlador**: RC+ se conecta al controlador (RC700, RC90, etc.) vía USB, Ethernet/TCP-IP o RS-232, transfiriendo el programa compilado, puntos y parámetros (Tool, Local, velocidad).

**Controlador ↔ Manipulador**: el controlador ejecuta el programa de forma autónoma y se comunica con los servomotores de cada eje mediante buses internos (encoders, corriente, posición). El manipulador no interpreta SPEL+ directamente; el controlador es quien traduce las instrucciones a movimiento real.

## 3. Proceso de ejecución de un movimiento

1. **Interpretación**: el controlador lee la instrucción (`Go`, `Jump`, `Move`) y extrae punto destino, sistema de coordenadas y parámetros de velocidad/aceleración.
2. **Cinemática inversa**: si el punto es cartesiano, se calculan los ángulos articulares necesarios y se valida que sea alcanzable.
3. **Planificación de trayectoria**: se genera un perfil de movimiento (trapezoidal o en S) por articulación, optimizando tiempo de ciclo.
4. **Verificación de seguridad**: chequeo de límites articulares, zonas de exclusión y señales de seguridad (paros de emergencia, sensores).
5. **Generación de setpoints**: el controlador envía consignas periódicas a los drivers de los servomotores.
6. **Control y retroalimentación**: cada eje tiene un lazo cerrado que compara posición real (encoder) vs. deseada y ajusta torque; al alcanzar la tolerancia, el movimiento se marca como completado y el programa continúa.

## 4. Flujo resumido

```
PC (RC+ 7.0) → compila y transfiere programa SPEL+
      ↓
Controlador → interpreta, calcula cinemática inversa, planifica trayectoria, verifica seguridad
      ↓
Servomotores/Encoders → ejecutan movimiento con lazo de control cerrado
      ↓
Controlador confirma posición → continúa el programa
```

El controlador es el "cerebro" en tiempo real que ejecuta cinemática y control; la PC con RC+ funciona como interfaz de desarrollo y supervisión.

