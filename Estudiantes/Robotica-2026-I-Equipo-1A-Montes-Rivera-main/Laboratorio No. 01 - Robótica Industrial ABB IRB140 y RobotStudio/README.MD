<h1 style="color: orange; text-align: center;">
  Video Lab 1
</h1>
<div align="center">
  <a href="https://youtu.be/4CsLBjqpxs0">
    <img src="https://img.youtube.com/vi/4CsLBjqpxs0/0.jpg" 
         alt="Video" 
         style="width:80%; max-width:800px;">
  </a>
</div>

<h2>Descripción detallada de la solución planteada</h2>

<p>
La solución desarrollada implementa un sistema automatizado de decoración de una torta virtual mediante el uso de un robot industrial programado en lenguaje RAPID. El sistema integra el control de trayectorias, manejo de entradas y salidas digitales, y coordinación con una banda transportadora, permitiendo simular un proceso industrial completo.
</p>

<h3>1. Arquitectura general del sistema</h3>

<p>
El programa está estructurado en un módulo principal (MODULE Module1) que contiene:
</p>

<ul>
<li>Definición de múltiples posiciones (robtarget) que representan puntos específicos en el espacio de trabajo.</li>
<li>Un procedimiento principal (main) encargado del control lógico del sistema.</li>
<li>Diversos procedimientos (Path_x) que encapsulan trayectorias específicas del robot.</li>
</ul>

<p>
El sistema opera en un ciclo continuo mediante un bucle WHILE TRUE, lo que permite que el robot esté constantemente monitoreando señales de entrada digital para ejecutar diferentes rutinas.
</p>

<h3>2. Control por entradas digitales</h3>

<p>El comportamiento del sistema está gobernado por tres señales de entrada digital:</p>

<h4>Entrada DI_01 – Rutina básica</h4>
<ul>
<li>Se enciende una salida digital (DO_01) como indicador.</li>
<li>El robot ejecuta la trayectoria Path_120, la cual corresponde a una posición HOME.</li>
<li>Se apaga la salida digital.</li>
</ul>

<p>
Esta rutina funciona como un retorno seguro o inicialización del sistema.
</p>

<h4>Entrada DI_02 – Rutina principal de decoración</h4>

<ul>
<li>Activación de señal de estado: se activa DO_02 indicando operación en curso.</li>
<li>Posicionamiento inicial: el robot se desplaza a HOME (Path_120) para iniciar desde una referencia conocida.</li>
<li>Control de banda transportadora: se activa el movimiento hacia adelante (FWD_Conveyor), se detiene, luego se invierte (BWD_Conveyor). Se utilizan tiempos de espera (WaitTime) para simular el transporte del pastel.</li>
<li>Ejecución de trayectorias: se ejecuta una secuencia extensa de procedimientos Path_x que representan trazos continuos sobre la superficie de la torta.</li>
<li>Estas trayectorias combinan movimientos articulares (MoveJ), lineales (MoveL) y circulares (MoveC).</li>
<li>Cada Path corresponde a una parte del dibujo o escritura, como letras o decoraciones.</li>
<li>Finalización: el robot retorna a posiciones de referencia y se desactiva la señal DO_02.</li>
</ul>

<h4>Entrada DI_03 – Modo mantenimiento</h4>
<ul>
<li>Se enciende DO_03.</li>
<li>El robot se mueve a una posición de mantenimiento (Home_2) mediante Path_130.</li>
<li>Se realiza una espera de 5 segundos.</li>
<li>Se retorna a HOME (Path_120).</li>
<li>Se apaga la salida digital.</li>
</ul>

<p>
Esta rutina permite manipulación segura de la herramienta.
</p>

<h3>3. Generación de trayectorias</h3>

<p>
Las trayectorias están definidas mediante procedimientos modulares (Path_10, Path_20, ..., Path_360), cada uno compuesto por secuencias de movimientos:
</p>

<ul>
<li>MoveJ (Joint Move): utilizado para desplazamientos rápidos entre puntos sin requerir precisión en la trayectoria.</li>
<li>MoveL (Linear Move): asegura un trazo recto, ideal para dibujar líneas.</li>
<li>MoveC (Circular Move): permite generar curvas suaves, fundamentales para decoraciones.</li>
</ul>

<p>
Los puntos (robtarget) están definidos en coordenadas cartesianas, garantizando precisión en la ejecución del dibujo.
</p>

<h3>4. Control de herramienta y sistema de referencia</h3>

<ul>
<li>Una herramienta personalizada (MyNewTool) que simula un marcador.</li>
<li>Un objeto de trabajo (Workobject_1) que define la superficie de la torta.</li>
</ul>

<p>
Esto permite que todas las trayectorias sean coherentes respecto al plano de trabajo.
</p>

<h3>5. Control de profundidad (eje Z)</h3>

<p>
Se utilizan posiciones duplicadas con variaciones en el eje Z (por ejemplo Target_80 y Target_80_2):
</p>

<ul>
<li>Z = 0: contacto con la superficie para dibujar.</li>
<li>Z negativo: levantar la herramienta.</li>
</ul>

<p>
Esto simula el efecto real de escribir o decorar.
</p>

<h3>6. Estrategia de solución</h3>

<ul>
<li>Modularidad: cada trazo es un procedimiento independiente.</li>
<li>Reutilización: los paths pueden combinarse para formar figuras complejas.</li>
<li>Control por eventos: el sistema responde a entradas digitales.</li>
<li>Simulación industrial realista: incluye banda transportadora y señales.</li>
</ul>

<h3>7. Aplicación práctica</h3>

<ul>
<li>Decoración automatizada de alimentos como tortas y galletas.</li>
<li>Procesos de pintura o marcado industrial.</li>
<li>Sistemas pick-and-place con trayectorias complejas.</li>
</ul>

<h1 style="text-align: center;">Movimientos en ABB RobotStudio</h1>

<h2>MoveJ (Movimiento por articulaciones)</h2>
<p>
El robot se mueve optimizando el giro de sus articulaciones. La trayectoria del extremo no es controlada de forma específica, por lo que puede resultar en un recorrido curvo o variable entre los puntos. Es el tipo de movimiento más rápido y se utiliza cuando solo importa llegar al punto final.
</p>

<h2>MoveL (Movimiento lineal)</h2>
<p>
El robot mueve la herramienta siguiendo una trayectoria recta entre dos puntos. Este tipo de movimiento garantiza precisión a lo largo de todo el recorrido, siendo fundamental en aplicaciones donde se requiere mantener una línea exacta.
</p>

<h2>MoveC (Movimiento circular)</h2>
<p>
El robot se desplaza siguiendo una trayectoria circular o en forma de arco. Para definir este movimiento se requieren puntos intermedios que permiten establecer la curvatura del recorrido. Se utiliza cuando se necesitan trayectorias suaves y continuas en forma curva.
</p>

<h2>Resumen</h2>
<table style="width: 100%; border-collapse: collapse;">
    <tr>
        <th style="border: 1px solid black; padding: 10px;">Instrucción</th>
        <th style="border: 1px solid black; padding: 10px;">Trayectoria</th>
        <th style="border: 1px solid black; padding: 10px;">Velocidad</th>
        <th style="border: 1px solid black; padding: 10px;">Aplicación</th>
    </tr>
    <tr>
        <td style="border: 1px solid black; padding: 10px;">MoveJ</td>
        <td style="border: 1px solid black; padding: 10px;">No definida (por articulaciones)</td>
        <td style="border: 1px solid black; padding: 10px;">Alta</td>
        <td style="border: 1px solid black; padding: 10px;">Movimiento rápido entre puntos</td>
    </tr>
    <tr>
        <td style="border: 1px solid black; padding: 10px;">MoveL</td>
        <td style="border: 1px solid black; padding: 10px;">Recta</td>
        <td style="border: 1px solid black; padding: 10px;">Media</td>
        <td style="border: 1px solid black; padding: 10px;">Alta precisión en el recorrido</td>
    </tr>
    <tr>
        <td style="border: 1px solid black; padding: 10px;">MoveC</td>
        <td style="border: 1px solid black; padding: 10px;">Circular</td>
        <td style="border: 1px solid black; padding: 10px;">Media</td>
        <td style="border: 1px solid black; padding: 10px;">Trayectorias curvas</td>
    </tr>
</table>
