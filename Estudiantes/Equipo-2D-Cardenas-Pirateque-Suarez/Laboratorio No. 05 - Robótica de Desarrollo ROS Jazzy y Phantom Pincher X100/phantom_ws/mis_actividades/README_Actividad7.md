# Actividad 7: Movimiento Simultáneo y Validación de Límites

## 📖 Descripción
En la presente actividad se implementa una Interfaz Gráfica de Usuario (GUI) destinada al comando del desplazamiento **simultáneo** de la totalidad de las articulaciones del manipulador Phantom X Pincher X100. 

En concordancia con los requerimientos de la guía de práctica, el sistema incorpora preprogramadas las 5 configuraciones articulares solicitadas:
1. `[0, 0, 0, 0, 0]`
2. `[25, 25, 20, -20, 0]`
3. `[-35, 35, -30, 30, 0]`
4. `[85, -20, 55, 25, 0]`
5. `[80, -35, 55, -45, 0]`

El componente crítico de este desarrollo radica en su **Sistema de Validación Automática**. Previo a la ejecución de cualquier desplazamiento, el algoritmo realiza una comparación entre la configuración articular teórica solicitada y los límites experimentales seguros definidos durante la Actividad 6. En caso de detectarse una configuración fuera del rango operativo seguro, el software procede a truncar de forma automática los valores hacia los límites permitidos, imprimiendo simultáneamente una **justificación detallada** en la consola gráfica donde se exponen los riesgos asociados (p. ej., colisión inminente o sobreesfuerzo del servomotor).

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

# 3. Ejecución de la interfaz de movimiento simultáneo
python3 mis_actividades/actividad7.py
```

## 🎯 Interfaz y Guía de Uso
1. **Selección Rápida:** Mediante el menú desplegable ubicado en la sección "Configuraciones del Laboratorio", es posible seleccionar una de las 5 configuraciones articulares predefinidas.
2. **Validación y Justificación:** Al accionar el control **▶ EJECUTAR CONFIGURACIÓN**, el panel inferior (Análisis de Restricciones) desplegará de manera inmediata:
   * Los valores teóricos calculados.
   * El estado de seguridad de la configuración (ejecución sin modificaciones).
   * La necesidad de truncamiento (acompañada de la justificación técnica respectiva y la transmisión de los valores restringidos a los controladores).
3. **Control de Velocidad Dinámico:** Mediante el uso del control deslizante de Velocidad (rango de 1 a 1023), se permite el ajuste dinámico de la rapidez con la cual el manipulador ejecuta la interpolación espacial hacia el objetivo.
4. **Reporte Final:** Una vez concluida la ejecución de la trayectoria, la consola genera un reporte donde se contrasta la posición objetivo deseada frente a la posición real reportada por los encoders de los servomotores.

## ⚠️ Consideraciones de Seguridad
* **🚨 PARADA DE EMERGENCIA:** Se dispone de un control maestro de interrupción en la sección superior. Su activación suprime instantáneamente el torque suministrado a los actuadores frente a cualquier anomalía física.
* **Retorno Seguro:** Se ha implementado un control dedicado para comandar el retorno simultáneo del sistema a su configuración de inicio (HOME `[0, 0, 0, 0, 0]`).
* **Control Manual de Torque:** Se incluyen controles independientes de habilitación (Torque ON) y deshabilitación (Torque OFF) para permitir la manipulación manual del sistema robótico en caso de ser requerido.
