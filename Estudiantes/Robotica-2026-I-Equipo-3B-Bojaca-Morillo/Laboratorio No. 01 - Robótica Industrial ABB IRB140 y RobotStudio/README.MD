<!-- ===== EQUIPO ===== -->

<div align="center">

<!-- ================== INTEGRANTE 1 ================== -->

<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Gabriel+Eduardo+Bojaca+Munar">
</p>

<b>Carrera:</b> Ingeniería Mecatrónica <br>
<b>Correo:</b> gbojaca@unal.edu.co <br>
<b>GitHub:</b> <a href="https://github.com/usuariogithub">usuariogithub</a> <br>
<b>Rol:</b> Simulación y documentación <br>
<b>Intereses:</b> Robótica móvil, automatización <br><br>

<p style="max-width:500px;">
Me interesa mucho la simulación y cómo se pueden modelar sistemas mecatrónicos para entender mejor su comportamiento. También me gusta la automatización y la robótica , sobre todo ver cómo funcionan y cómo se pueden mejorar.
</p>

<br><br>

<!-- ================== INTEGRANTE 2 ================== -->
<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Maria+Fernanda+Morillo+Tovar">
</p>


<b>Carrera:</b> Ingeniería Mecatrónica <br>
<b>Correo:</b> mmorillot@unal.edu.co <br>
<b>GitHub:</b> <a href="https://github.com/mmorillot">mmorillot</a> <br>
<b>Rol:</b> Modelado, programación y control <br>
<b>Intereses:</b> Control de robots, manipulación.<br><br>

<p style="max-width:500px;">
Actualmente estoy en décimo semestre de Ingeniería. Me interesa el área de control de robots, especialmente entender cómo funcionan y cómo se pueden hacer más precisos. También me llama la atención la parte de manipulación.
</p>

</div>

# Laboratorio No. 01 - Robótica Industrial: Trayectorias, Entradas y Salidas Digitales.
## Introduccion
En este laboratorio se trabaja la generación de trayectorias en un robot industrial ABB utilizando RAPID. A través de una simulación, el robot realiza el trazado de figuras sobre una superficie, permitiendo entender cómo se definen movimientos, herramientas y sistemas de referencia para lograr precisión y continuidad en las trayectorias.

## Descripción detallada de la solución planteada
La solución desarrollada consiste en la implementación de un sistema de trayectoria para un robot industrial ABB, programado en lenguaje RAPID, con el objetivo de simular la decoración de una torta mediante el trazado de figuras y texto sobre una superficie plana.

En primer lugar, se definió una herramienta de trabajo (tooldata) que representa un marcador acoplado al efector final del robot. Esta herramienta fue calibrada considerando la posición del TCP (Tool Center Point), permitiendo que el robot realice trazos precisos sobre la superficie de trabajo.

Adicionalmente, se configuró un sistema de referencia mediante el uso de un workobject, el cual define el plano donde se realiza la trayectoria. Esto permite desacoplar la programación de la posición absoluta del robot, facilitando la reutilización de trayectorias en diferentes ubicaciones.

La lógica principal del programa se basa en una secuencia de movimientos definidos mediante múltiples puntos (robtargets). Estos puntos representan coordenadas específicas en el espacio cartesiano que, al ser recorridas secuencialmente mediante instrucciones MoveL, permiten generar trazos continuos simulando letras y figuras decorativas.

El flujo de operación inicia desde una posición segura denominada Home, desde donde el robot se desplaza hacia el punto inicial del trazado. Posteriormente, ejecuta una serie de movimientos lineales (MoveL) entre los diferentes puntos definidos, asegurando continuidad en el trazo y respetando las restricciones de velocidad y zona de aproximación establecidas.

Para garantizar la calidad del trazado:

Se utilizan movimientos lineales (MoveL) para mantener precisión en las trayectorias.
Se define una altura segura en algunos puntos (offset en Z) para evitar colisiones al desplazarse entre secciones.
Se controla la orientación del efector final mediante cuaterniones, asegurando que el marcador mantenga contacto adecuado con la superficie.

El programa contempla una gran cantidad de puntos intermedios que permiten representar formas complejas, como curvas y detalles finos, logrando una simulación más realista del proceso de decoración.

Finalmente, el robot retorna a la posición Home, completando el ciclo de trabajo. Esta estructura garantiza repetibilidad, seguridad operativa y facilidad de adaptación para futuras modificaciones, como el cambio de diseño o la implementación en otro sistema de referencia.

### Herramienta de trabajo  flange

#### Imagenes de la herramienta 1 (Construida y Modelo CAD)

<p align="center">
  <img src="https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/refs/heads/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/img/Assembly1.jpg" alt="Planta" width="1080">
</p>


### Pastel - superficie de dibujo

<p align="center">
  <img src="https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/refs/heads/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/img/Detalle_caja_2.jpeg" alt="Planta" width="1080">
</p>


## Diagrama de flujo de acciones del robot 

```mermaid
flowchart TD

    A[Inicio] --> B[Robot en HOME]

    B --> C{Entrada digital}

    C -- Entrada 1 --> D[Encender luz indicadora]
    D --> E[Ejecutar rutina de decorado]
    E --> F[Realizar trayectorias nombres y decoracion]
    F --> G[Fin de trayectoria]
    G --> H[Apagar luz indicadora]
    H --> B

    C -- Entrada 2 --> J[Encender luz indicadora]
    J --> K[Ir a posicion de mantenimiento]
    K --> L[Apagar luz indicadora]

    L --> M{¿Las dos entradas estan activadas?}
    M -- No --> K
    M -- Sí --> B
```



## Descripción de las funciones utilizadas 
- **MoveL**  
  Permite realizar movimientos lineales entre puntos, asegurando trayectorias continuas y precisas para el trazado.

- **MoveJ**  
  Usado para movimientos rápidos entre posiciones, como el desplazamiento desde y hacia la posición Home.

- **robtarget**  
  Estructura que define la posición y orientación del robot en el espacio cartesiano.

- **tooldata**  
  Define las características de la herramienta (marcador) y la ubicación del TCP.

- **wobjdata (workobject)**  
  Permite establecer el sistema de referencia donde se ejecutan las trayectorias.

- **CONST**  
  Se utiliza para declarar puntos fijos que no cambian durante la ejecución.

- **PROC**  
  Permite organizar el programa en procedimientos para estructurar mejor la lógica.

- **MoveAbsJ**  
  Utilizado para mover el robot directamente a configuraciones articulares específicas, como la posición Home.

## Código Rapid
[Hacer clic aquí para ver el código RAPID](https://github.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/blob/c7ba862daa8eb41e73f25fe1edb4bccd65b58798/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/src/Module1.mod)

## Plano de planta de los elementos de trabajo
EJEMPLO. [Hacer clic aquí para ver el plano de planta en RobotStudio](https://github.com/Nicolas-Eule/Laboratorio_Robotica_1/blob/main/assets/img/Plano_de_planta.png)


<p align="center">
  <img src="https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/refs/heads/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/img/Planta_Lab_1.jpg" alt="Planta" width="1080">
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/refs/heads/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/img/Planta_Lab_2.jpg" alt="Planta2" width="1080">
</p>



## Herramientas en RobotStudio
Se muestra la implementacion de las dos herramientas en RobotStudio

EJEMPLO:
<p align="center">
  <img src="https://raw.githubusercontent.com/labsir-un/Robotica-2026-I-Equipo-3B-Bojaca-Morillo/refs/heads/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/assets/img/Render.jpg" alt="Render" width="1080">
</p>



#  Videos del Laboratorio – Robótica Industrial

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=800&size=20&duration=2400&pause=900&color=00E5FF&center=true&vCenter=true&width=900&repeat=true&lines=Aqu%C3%AD+puedes+visualizar%3A;Video+de+la+pr%C3%A1ctica+(laboratorio);Video+de+la+simulaci%C3%B3n+(RobotStudio)" alt="Animación videos">
</p>
##  Video del proyecto

[![Ver video](https://img.youtube.com/vi/Kp8faPYFbeI/0.jpg)](https://www.youtube.com/watch?v=Kp8faPYFbeI)
---







---


