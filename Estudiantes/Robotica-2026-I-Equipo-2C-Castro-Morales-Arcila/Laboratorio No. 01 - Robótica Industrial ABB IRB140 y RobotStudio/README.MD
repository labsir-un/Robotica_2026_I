<div align="center">
  <picture>
    <source srcset="https://imgur.com/5bYAzsb.png" media="(prefers-color-scheme: dark)">
    <source srcset="https://imgur.com/Os03JoE.png" media="(prefers-color-scheme: light)">
    <img src="https://imgur.com/Os03JoE.png" alt="Escudo UNAL" width="350px">
  </picture>

  <h1>Laboratorio No. 01 Robótica Industrial - Trayectorias, Entradas y Salidas Digitales.</h1>
</div>

---

## Solución planteada:

Para la implementación física dentro del laboratorio, se comenzó realizando mediciones del espacio de trabajo y el área de operación: dimensiones de la banda, distancia de la banda al manipulador y dimensiones de la caja, esta última simulando el pastel sobre el que se realizará el grabado. Con esta información, se procedió a construir el montaje virtual del área de trabajo en el software de **RobotStudio 2024**, con el fin de obtener una aproximación lo más parecida del entorno físico y lograr que la rutina coincidiera entre ambos espacios.

Una vez desarrollada y verificada la implementación virtual de las rutinas, se llevó a cabo la implementación física en el laboratorio, lo que permitió identificar y corregir errores no contemplados en la simulación, así como reajustar ciertos parámetros, donde tras algunas modificaciones, se comprobó que las rutinas satisfacen los requerimientos planteados, operando de la siguiente manera:

#### Rutina de mantenimiento — `DI_02`

Para facilitar la instalación y desinstalación de la herramienta, se programó una **posición de mantenimiento** la cual se activa mediante el botón `DI_02`, el cual, al oprimirlo, se activa el indicador asociado y el robot ejecuta la trayectoria de mantenimiento, cuyo objetivo es posicionar el manipulador de forma que el acceso a la herramienta sea cómodo y seguro para el operario.

#### Rutina de preparación — `DI_03`

Con el fin de garantizar que el desplazamiento de la caja por la banda permita dibujar sobre ella sin necesidad de mediciones adicionales de tiempo o distancia, se implementó una **rutina de preparación** activada mediante el botón `DI_03`, al oprimirlo, se activa el indicador correspondiente y el robot realiza las siguientes tareas:

1. Posiciona la herramienta en un punto asociado a una esquina de la caja y **detiene el robot durante 30 segundos**, permitiendo que el operario ubique la caja correctamente sobre la banda y quede alineada con el plano de trabajo.
2. Una vez transcurrido ese tiempo, el robot toca con la punta de la herramienta las **esquinas extremas de la caja** y espera **5 segundos**.
3. Después de esto, el manipulador regresa a la posición de *home* y, una vez alcanzada, **activa la banda durante 7 segundos**, donde este tiempo sirve como referencia temporal para determinar cuánto debe funcionar la banda en dirección contraria durante la rutina principal, asegurando que la caja regrese a la posición de trabajo establecida por el operario.

#### Rutina principal — `DI_01`

La rutina principal se activa mediante el botón `DI_01`, el cual al oprimirlo, se activa el indicador asociado y se ejecuta la siguiente rutina:

1. Se enciende la banda en la **dirección contraria** a la utilizada en la rutina de preparación durante los mismos **7 segundos**, reposicionando la caja en la posición de trabajo.
2. Seguido a ello, el robot ejecuta las **trayectorias de aproximación y dibujo**, donde durante este proceso ningún operario debe introducir sus manos dentro del área de trabajo del robot.
3. Al finalizar las trayectorias, el manipulador regresa a la posición de *home*, espera **5 segundos** y activa la banda durante **2 segundos**, dando por concluida la rutina.

---

## Diagrama de flujo de acciones del robot

A continuación, se presenta el diagrama de flujo correspondiente a la secuencia de acciones programadas para el robot dentro de la estación de trabajo. En este se resume la lógica de operación implementada en la rutina principal, considerando la verificación de entradas digitales, la activación de salidas, el control de la banda transportadora y la ejecución de las trayectorias definidas para las rutinas de trabajo, mantenimiento y preparación. De esta manera, el diagrama permite visualizar de forma clara el orden de ejecución del sistema y la interacción entre las señales de control y los movimientos del manipulador.

<div align="center">
  <img src="https://github.com/labsir-un/Robotica-2026-I-Equipo-2C-Castro-Morales-Arcila/blob/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/img/diagrama_flujo_robot.png" alt="Diagrama de flujo de acciones del robot" width="400"/>
</div>

---

## Plano de planta:

A continuación se presenta un plano visto desde la vista superior de la estación de trabajo y los elementos que interactúan en ella, en los cuales encontramos:

- Manipulador IRB140
- Controlador IRC5
- Banda transportadora
- La caja (simula el pastel)

<div align="center">
  <img src="https://github.com/labsir-un/Robotica-2026-I-Equipo-2C-Castro-Morales-Arcila/blob/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/img/Plano%20de%20Planta.png" alt="Vista de Planta - Estacion de Trabajo" width="700"/>
</div>

---

## Descripción de las funciones utilizadas:

Durante la implementación de la rutina se hizo uso de las siguientes funciones:

- **`MoveL`:** Esta función es la más utilizada en el código, donde permite mover el TCP del robot desde una posición actual hasta una posición de destino. En la rutina fue utilizada mayormente para trazar las líneas rectas de las letras y la figura.

- **`MoveC`:** Esta función describe una trayectoria mediante dos puntos adicionales al punto inicial, los cuales definen un radio y una longitud de arco, teniendo en cuenta que el ángulo del arco no supere los 180°, dado que al superarlos genera conflicto. En la rutina fue usada para trazar las partes redondeadas de letras como la `P`, `C`, `D`, entre otras letras.

- **`SET`:** Configura una salida digital con el valor lógico de `1`. Es usado para encender los indicadores al activar los pulsadores y también es usada para activar y desactivar las bandas transportadoras (`BWD_Conveyor` / `FWD_Conveyor`).

- **`RESET`:** Desactiva las señales digitales descritas anteriormente, asignando el valor lógico de `0`.

- **`WaitTime`:** Pausa la ejecución del programa durante un tiempo determinado y es comúnmente utilizado en la rutina para sincronizar el movimiento de las bandas transportadoras con las trayectorias del robot.

---

## Diseño de la herramienta:

<div align="center">
  <img src="https://github.com/labsir-un/Robotica-2026-I-Equipo-2C-Castro-Morales-Arcila/blob/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/img/Herramienta%20Explosionada.png" alt="Partes de la herramienta" width="500"/>
</div>

1. **`Base`:** Es la sección inferior de la herramienta, la cual genera la unión directa con el flange del manipulador. Su geometría está diseñada para acoplarse de forma rígida al último eje del robot, mediante 4 tornillos `M6` y un agujero guía, garantizando que la herramienta quede fija y alineada con el TCP definido en la configuración del sistema. Además de ello, con el fin de evitar problemas de singularidad con el manipulador, el segmento donde se conecta el cojín cuenta con una inclinación de **30°** respecto a la base.

2. **`Cojín`:** Es la parte intermedia de la herramienta y cumple la función de sostener y alojar el marcador. El mecanismo de conexión entre el cojín y la base se realiza mediante pines fijos al cojín, los cuales encajan en cavidades o guías de la base, impidiendo cualquier desplazamiento relativo entre las piezas durante la operación.

3. **`Marcador`:** Es el elemento funcional de la herramienta, encargado de realizar directamente el trazado sobre la superficie de trabajo. Al estar alojado y retenido por el cojín y presionado mediante un **`resorte`** instalado en la base de la herramienta, el cual cumple la función de darle un margen de compensación al marcador con el fin de que se mantenga una presión de contacto casi constante en la superficie de trabajo.

**`Nota`:** Los modelos STL de la herramienta se pueden encontrar mediante el siguiente link: [Ver modelados](https://github.com/labsir-un/Robotica-2026-I-Equipo-2C-Castro-Morales-Arcila/tree/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/models)

---

## Código en RAPID:

En esta sección se mostrará un fragmento del código, específicamente las rutinas implementadas en la sección principal. Para ver el código completo, se puede acceder mediante el siguiente link: [Ver código fuente](https://github.com/labsir-un/Robotica-2026-I-Equipo-2C-Castro-Morales-Arcila/blob/main/Laboratorio%20No.%2001%20-%20Rob%C3%B3tica%20Industrial%20ABB%20IRB140%20y%20RobotStudio/src/Module1.mod)

```bash
PROC main()
    
    WHILE TRUE DO
        RESET DO_01;
        RESET DO_02;
        RESET DO_03;
        
        IF DI_01 = 1 THEN
            SET DO_01;
            SET BWD_Conveyor;
            WaitTime 7;
            RESET BWD_Conveyor;
            WaitTime 5;
            
            Path_Aprox_1_1;
            Path_Pablo;
            Path_Marco;
            Path_Daniel;
            Path_Figura;
            Path_Aprox_1_2;
            
            WaitTime 5;
            SET BWD_Conveyor;
            WaitTime 2;
            RESET BWD_Conveyor;
            RESET DO_01;
            WaitTime 5;
        ENDIF
        
        IF DI_02=1 THEN
            SET DO_02;
            Path_Mantenimiento;
        ENDIF
        
        IF DI_03 = 1 THEN
            SET DO_03;
            Path_Aprox_1_1;
            WaitTime 30;
            Path_Aprox_1;
            WaitTime 5;
            Path_Aprox_1_2;
            SET FWD_Conveyor;
            WaitTime 7;
            RESET FWD_Conveyor;
            RESET DO_03;
        ENDIF
        
    ENDWHILE

ENDPROC
```

---

## Vídeos

#### Vídeo de simulación de la decoración de una torta virtual

<div align="center">
  <a href="https://www.youtube.com/watch?v=O-p1SuG4cyI">
    <img src="https://img.youtube.com/vi/O-p1SuG4cyI/0.jpg" alt="Vídeo de simulación de la decoración de una torta virtual" width="500"/>
  </a>
</div>

#### Vídeo de control de transporte - simulación

<div align="center">
  <a href="https://www.youtube.com/watch?v=f315TsI2odc">
    <img src="https://img.youtube.com/vi/f315TsI2odc/0.jpg" alt="Vídeo de control de transporte - simulación" width="500"/>
  </a>
</div>

#### Vídeo de control de transporte dentro del laboratorio

<div align="center">
  <a href="https://www.youtube.com/watch?v=tSsM_temUiw">
    <img src="https://img.youtube.com/vi/tSsM_temUiw/0.jpg" alt="Vídeo de control de transporte dentro del laboratorio" width="500"/>
  </a>
</div>
