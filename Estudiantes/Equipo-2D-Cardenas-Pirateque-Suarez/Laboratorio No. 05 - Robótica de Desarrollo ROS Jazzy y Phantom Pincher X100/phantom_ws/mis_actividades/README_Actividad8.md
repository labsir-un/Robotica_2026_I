# Actividad 8: Movimiento Secuencial y Comparación Cinemática

## 📖 Descripción
En esta actividad se implementa una Interfaz Gráfica de Usuario (GUI) diseñada para la ejecución de las mismas 5 configuraciones articulares analizadas en la Actividad 7, modificando el paradigma de control hacia un esquema de **movimiento secuencial**.

En cumplimiento con los requerimientos de la guía de práctica, el algoritmo comanda el posicionamiento final del manipulador desplazando una única articulación a la vez, rigiéndose estrictamente por el siguiente orden cinemático:
1. Base
2. Hombro
3. Codo
4. Muñeca
5. Pinza

El objetivo principal de esta herramienta radica en proveer los instrumentos de medición (cronometraje exacto mediante consola) para permitir el análisis comparativo entre el movimiento secuencial y el simultáneo (Actividad 7) en términos de **tiempo de ejecución, trayectoria del TCP (Tool Center Point) y suavidad**. De manera análoga a la actividad previa, se integra un sistema de validación automática encargado de truncar y justificar cualquier comando escalar que exceda los límites mecánicos seguros.

## 🛠️ Requisitos
El despliegue del entorno gráfico bajo ROS 2 en Ubuntu requiere la disponibilidad de la librería `tkinter`. Se debe asegurar su instalación mediante el gestor de paquetes del sistema (`apt`):

```bash
sudo apt update
sudo apt install python3-tk
```

## 🚀 Instrucciones de Ejecución
En una terminal independiente, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de movimiento secuencial
python3 mis_actividades/actividad8.py
```

## 🎯 Interfaz y Guía de Uso
1. **Configuraciones:** Mediante el menú desplegable, es posible seleccionar una de las 5 configuraciones articulares predefinidas.
2. **Control de Tiempo Secuencial:** A diferencia del esquema simultáneo, el sistema permite definir el parámetro "Tiempo por articulación (s)". Si este es configurado, por ejemplo, en 1.5 segundos, la secuencia completa requerirá exactamente 7.5 segundos ($1.5 \text{ s} \times 5 \text{ articulaciones}$) para su culminación.
3. **Validación:** Tras accionar el comando **▶ EJECUTAR SECUENCIAL**, el módulo de seguridad verificará la viabilidad espacial de la postura. En caso de detectarse riesgo de colisión, los parámetros angulares serán truncados a los límites experimentales (Actividad 6), desplegando la justificación técnica respectiva.
4. **Ejecución y Comparación:** El sistema iniciará el desplazamiento secuencial, eslabón por eslabón. Al concluir la trayectoria, la consola generará un reporte donde se detalla el tiempo total exacto de la operación, proporcionando así el dato empírico necesario para el análisis comparativo posterior.

## ⚠️ Consideraciones de Seguridad
* **🚨 PARADA DE EMERGENCIA:** Su activación interrumpe el flujo lógico de la secuencia en cualquier instante y suprime de manera inmediata el torque suministrado a los actuadores.
* **Control de Torque:** Se dispone de controles dedicados para la habilitación (Torque ON) o deshabilitación (Torque OFF) manual de la rigidez articular de los servomotores.
