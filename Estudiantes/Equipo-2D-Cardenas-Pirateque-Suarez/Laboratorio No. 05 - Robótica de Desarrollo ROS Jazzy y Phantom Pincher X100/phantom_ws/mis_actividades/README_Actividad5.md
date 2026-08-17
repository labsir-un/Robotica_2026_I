# Actividad 5: Calibración de Cero y Error Articular

## 📖 Descripción
En la presente actividad se implementa un **Asistente Gráfico de Calibración** interactivo para el manipulador Phantom X Pincher X100. El objetivo principal consiste en evaluar la precisión de los servomotores Dynamixel mediante el envío de posiciones conocidas y la medición de la respuesta física real del hardware.

El algoritmo diseñado cumple con los siguientes lineamientos de calibración:
1. Se envían cinco posiciones angulares distribuidas dentro del rango operativo seguro de cada articulación.
2. Se registra la posición solicitada (Deseada) frente a la reportada por el servomotor (Medida).
3. Se calcula el error articular matemático mediante la expresión: $e_q = q_{deseado} - q_{medido}$
4. Se determina de forma automática el error máximo, el error promedio y el desplazamiento de cero (offset).
5. Se genera de forma autónoma una gráfica comparativa, la cual es almacenada en el directorio local.

## 🛠️ Requisitos
Para un entorno Ubuntu con ROS 2 Jazzy, es necesario garantizar la instalación de las dependencias del sistema mediante el gestor de paquetes `apt`, con el fin de evitar conflictos de entorno. Se debe ejecutar el siguiente comando:

```bash
sudo apt update
sudo apt install python3-matplotlib python3-numpy python3-tk
```

## 🚀 Instrucciones de Ejecución
Para la ejecución del nodo gráfico, se requiere ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de calibración
python3 mis_actividades/actividad5.py
```

## 🎯 Interfaz y Guía de Uso
1. **Selección:** Una vez inicializada la interfaz, se debe seleccionar la articulación a evaluar mediante el menú desplegable (Base, Hombro, Codo, Muñeca, Pinza).
2. **Lectura en Vivo:** El monitor de estado mostrará la posición actual del motor en tiempo real.
3. **Inicio de Prueba:** Al accionar el botón "INICIAR PRUEBA DE 5 PUNTOS", el manipulador se desplazará de forma autónoma hacia 5 coordenadas articulares estratégicas predefinidas en el algoritmo.
4. **Análisis de Datos:** La tabla central será poblada con los registros correspondientes. Asimismo, en la sección de estadísticas se visualizará el Error Máximo, el Error Promedio y el Desplazamiento de Cero.
5. **Generación de Gráficas:** Al culminar el barrido, el algoritmo generará automáticamente un directorio denominado `graficas_act5` en la ruta del espacio de trabajo, donde se almacenará una imagen en formato `.png` que ilustra la curva de comportamiento "Ideal" versus "Real".

## ⚠️ Consideraciones de Seguridad
La interfaz se encuentra provista de un sistema de parada de emergencia. Su activación interrumpe de manera inmediata el torque suministrado a los servomotores sin finalizar la ejecución del programa, garantizando así la integridad física del manipulador Phantom X ante cualquier comportamiento errático.
