<h1 style="color: orange; text-align: center;">
  Video Lab 2
</h1>

<div align="center">
  <a href="https://youtu.be/ERJf6F7LVco">
    <img src="https://img.youtube.com/vi/ERJf6F7LVco/0.jpg" 
         alt="Video" 
         style="width:80%; max-width:800px;">
  </a>
</div>

## 1. Análisis y Cuadros Comparativos

### 1.1 Comparación de Manipuladores: Motoman MH6 vs. ABB IRB 140

A continuación, se presenta un cuadro comparativo detallando las principales características técnicas de los dos manipuladores industriales estudiados:

| Característica Técnica | Yaskawa Motoman MH6 | ABB IRB 140 |
| :--- | :--- | :--- |
| **Carga máxima (Payload)** | 6 kg | 6 kg |
| **Alcance máximo (Reach)** | 1422 mm | 810 mm |
| **Número de Grados de Libertad** | 6 ejes rotacionales | 6 ejes rotacionales |
| **Velocidad máxima por eje** | Eje 1: 170 °/s <br> Eje 2: 170 °/s <br> Eje 3: 175 °/s | Eje 1: 200 °/s <br> Eje 2: 200 °/s <br> Eje 3: 260 °/s |
| **Velocidad máxima TCP** | ~ 2.7 m/s | ~ 2.5 m/s |
| **Repetibilidad** | ± 0.08 mm | ± 0.03 mm |
| **Controlador compatible** | DX100 | IRC5 |
| **Aplicaciones típicas** | Soldadura por arco, ensamblaje, manipulación de materiales, empaquetado y dispensado. Ideal para tareas que requieren un espacio de trabajo amplio. | Soldadura por arco, ensamblaje, limpieza/pulido, alimentación de máquinas y empaquetado. Ideal para ciclos rápidos en espacios reducidos. |


---

### 1.2 Comparación de Software de Simulación: RoboDK vs. RobotStudio

Las herramientas de simulación son fundamentales para la programación *offline*. A continuación se detallan las ventajas, limitaciones y aplicaciones de RoboDK y RobotStudio.

| Característica | RoboDK | RobotStudio |
| :--- | :--- | :--- |
| **Enfoque / Fabricante** | Software universal (independiente del fabricante). | Software propietario y exclusivo de ABB. |
| **Compatibilidad** | Alta. Compatible con más de 50 marcas de robots (Yaskawa, ABB, KUKA, Fanuc, Universal Robots, etc.). | Baja. Compatible únicamente con robots y controladores de la marca ABB. |
| **Ventajas** | - Interfaz muy intuitiva y ligera.<br>- Permite cambiar la marca del robot en la simulación sin reprogramar todo.<br>- Excelente integración con lenguajes externos como Python.<br>- Extensa biblioteca de robots en línea. | - Precisión absoluta gracias a la tecnología *Virtual Controller* (usa el mismo RobotWare que el robot real).<br>- Tiempos de ciclo y dinámicas idénticos a la realidad al milisegundo.<br>- Herramientas avanzadas para el diseño de células complejas. |
| **Limitaciones** | - La simulación de tiempos de ciclo es una estimación y puede no ser exacta.<br>- Depende de post-procesadores que a veces requieren ajustes manuales para controladores muy específicos. | - Ecosistema cerrado (solo ABB).<br>- Curva de aprendizaje más pronunciada.<br>- Requiere un equipo con mejores especificaciones de hardware (más pesado). |
| **Aplicaciones** | Programación offline general, simulación rápida de trayectorias (como la trayectoria polar del laboratorio), investigación académica, e integración de sistemas multi-marca. | Comisionamiento virtual preciso, diseño de *layouts* de producción, optimización de tiempos de ciclo y programación avanzada de rutinas en RAPID para la industria. |

## 2. Operación y Configuración del Robot Motoman MH6

### 2.1 Configuraciones Iniciales (Home)
El manipulador Motoman MH6, operado mediante el controlador DX100, cuenta típicamente con dos posiciones de referencia o *Home* predeterminadas para su operación:

* **Home 1 (Posición de Calibración / Cero Articular):** En esta configuración, todos los ejes del robot (S, L, U, R, B, T) se encuentran alineados en su posición de cero absolutos (**0°**). Visualmente, el robot suele estar con el brazo extendido hacia adelante o en una postura rígida vertical (dependiendo del engranaje del eje U).

![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Home1.jpeg?raw=true)

* **Home 2 (Posición de Reposo / Plegada):** Es una configuración de trabajo segura pre-programada donde el brazo se encuentra plegado sobre sí mismo. Las coordenadas articulares típicas forman ángulos agudos u ortogonales (por ejemplo, el eje L reclinado hacia atrás y el eje U hacia adelante), manteniendo el efector final apuntando hacia abajo y cerca del cuerpo principal.

![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Home2.jpeg?raw=true)

**Justificación Analítica: ¿Cuál posición es mejor?**
Analíticamente, la configuración **Home 2** resulta ser muy superior y es la preferida como punto de inicio y fin de las rutinas de trabajo. Las razones cinemáticas y dinámicas son:
1. **Minimización de Torques Estáticos:** Al estar el brazo plegado, el centro de masa de la cadena cinemática se ubica mucho más cerca del eje vertical de la base (Eje S). Esto reduce significativamente el brazo de palanca y, por consiguiente, el torque estático que los servomotores de los ejes S, L y U deben contrarrestar por acción de la gravedad.
2. **Evasión de Singularidades:** La configuración *Home 1* (con el brazo totalmente extendido) suele situar al robot en una "singularidad de borde de espacio de trabajo" (workspace boundary singularity). En esta posición, el robot pierde al menos un grado de libertad y el determinante del Jacobiano se vuelve cero, lo que imposibilita los movimientos cartesianos en la dirección de la extensión. El *Home 2* mantiene el efector final dentro del volumen de trabajo manipulable.

---

### 2.2 Procedimiento Detallado de Movimientos Manuales (Teach Pendant DX100)

Para operar el manipulador Motoman de forma manual y segura, el procedimiento que seguimos en el laboratorio fue el siguiente:

#### Paso 1: Activación y Seguridad
1. Tomar el Teach Pendant y asegurarse de que el selector de llave del controlador esté en modo **TEACH** (modo manual/enseñanza).
2. Presionar el botón **[SERVO ON READY]** en el teclado del Teach Pendant. El indicador parpadeará.
3. Sujetar el **Deadman Switch** (interruptor de hombre muerto) ubicado en la parte posterior del Teach Pendant presionándolo hasta su posición intermedia (si se presiona muy fuerte o se suelta, el robot se bloqueará). Al hacerlo, se escucharán los contactores y los motores estarán energizados.

#### Paso 2: Selección de Coordenadas (Modos de Operación)
Para cambiar la forma en que el robot interpreta nuestros comandos de movimiento, utilizamos el botón **[COORD]** en el Teach Pendant. Al presionarlo, el icono en la parte superior de la pantalla cambia cíclicamente:
* **Modo Articular (Joint):** El icono muestra el dibujo de unos ejes rotacionales. Al mover el robot, cada articulación (S, L, U, R, B, T) se mueve de manera independiente e individual.
* **Modo Cartesiano (Rectangular/World):** El icono muestra un sistema coordenado X-Y-Z. Al usarlo, el controlador interpola los movimientos de todos los motores en tiempo real para mover el efector final (TCP) en líneas rectas a lo largo de los ejes espaciales.

#### Paso 3: Ejecución de Traslaciones y Rotaciones
Manteniendo presionado el *Deadman Switch*, se utilizan las teclas de ejes ubicadas al lado izquierdo del Teach Pendant:
* **En Modo Cartesiano:**
  * **Traslaciones:** Presionar **[X+ / X-]**, **[Y+ / Y-]**, o **[Z+ / Z-]** para mover el efector final linealmente por el espacio.
  * **Rotaciones:** Presionar **[Rx+ / Rx-]**, **[Ry+ / Ry-]**, o **[Rz+ / Rz-]** para modificar la orientación de la herramienta (Roll, Pitch, Yaw) sin cambiar su posición espacial.
* **En Modo Articular:** Esas mismas teclas corresponden físicamente a cada eje (S: Base, L: Brazo inferior, U: Brazo superior, R: Rotación de muñeca, B: Flexión de muñeca, T: Giro de herramienta).

#### Paso 4: Control de Niveles de Velocidad
Para evitar colisiones y mover el robot con precisión, es vital ajustar la velocidad manual.
1. Se utilizan los botones **[FAST]** (Rápido) y **[SLOW]** (Lento) del Teach Pendant.
2. Al presionarlos, se observa el cambio en el indicador de velocidad en la pantalla del Teach Pendant.
3. Los niveles disponibles para movimiento manual son:
   * **Inching (Pulsos):** Movimiento paso a paso microscópico para precisiones submilimétricas.
   * **Low (Lenta):** Ideal para acercamientos finales o cuando se está muy cerca de un obstáculo.
   * **Medium (Media):** Velocidad estándar de operación manual.
   * **High (Alta):** Permite movimientos rápidos por articulación (limitada por software por seguridad en modo manual a no más de 250mm/s típicamente).

#### Diagrama De Flujo 

![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Diagrama%20de%20Flujo%20Inicio.jpeg?raw=true)
![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Diagrama%20de%20Flujo%20Nombres.jpeg?raw=true)
![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Diagrama%20de%20flujo%20Figura.jpeg?raw=true)

#### PLANO
![Imagen](https://github.com/labsir-un/Robotica-2026-I-Equipo-1A-Montes-Rivera/blob/main/Laboratorio%20No.%2002%20-%20Rob%C3%B3tica%20Industrial%20Motoman%20MH6%20y%20RoboDK/Plano.jpeg?raw=true)
