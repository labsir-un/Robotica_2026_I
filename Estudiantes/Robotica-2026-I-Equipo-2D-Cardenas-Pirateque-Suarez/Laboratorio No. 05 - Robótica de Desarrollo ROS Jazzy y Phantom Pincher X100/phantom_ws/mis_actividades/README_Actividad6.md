# Actividad 6: Determinación de Límites Seguros

## 📖 Descripción
En la presente actividad se implementa un **Asistente Visual Interactivo** destinado a la calibración y determinación experimental de los límites seguros de operación para el manipulador Phantom X Pincher X100. 

En estricto apego a las directrices de la práctica, el algoritmo permite el registro manual de las posiciones extremas de cada actuador para el cálculo del rango operativo seguro. Se genera de forma automática una tabla de parámetros (*Articulación, Límite inferior, Límite superior y Margen de seguridad*) procediendo a su respectiva exportación. En etapas posteriores del desarrollo, dichos datos son empleados para restringir a nivel de software cualquier comando de posición que exceda estos umbrales, previniendo colisiones contra los topes mecánicos del sistema.

## 🛠️ Requisitos
Dado el uso del sistema operativo Ubuntu bajo el marco de ROS 2 Jazzy, se requiere la instalación de las dependencias gráficas a través del gestor de paquetes del sistema (`apt`) con el objetivo de preservar la integridad del entorno global.

```bash
sudo apt update
sudo apt install python3-tk
```

## 🚀 Instrucciones de Ejecución
Para la ejecución de la interfaz gráfica, se debe ingresar al espacio de trabajo, cargar el entorno y ejecutar el script correspondiente mediante las siguientes instrucciones:

```bash
# 1. Navegación al espacio de trabajo
cd ~/Laboratorio5/phantom_ws

# 2. Carga del entorno de ROS 2 y del workspace compilado
source /opt/ros/jazzy/setup.bash
source install/setup.bash

# 3. Ejecución de la interfaz de límites seguros
python3 mis_actividades/actividad6.py
```

## 🎯 Interfaz y Flujo de Trabajo
1. **Desactivación Automática del Torque:** Al inicializarse la interfaz, el sistema interrumpe de forma automática el torque de los servomotores Dynamixel, permitiendo el posicionamiento manual y libre del manipulador.
2. **Configuración del Margen de Seguridad:** Desde el panel global es posible definir el parámetro "Margen de seguridad" expresado en grados (por defecto, configurado en $5.0^\circ$). Este valor es compensado matemáticamente (sumado o restado) a los extremos registrados con el fin de establecer una franja de resguardo.
3. **Calibración Manual por Articulación:**
   * Se debe seleccionar la articulación a calibrar mediante el menú desplegable (Base, Hombro, Codo, Muñeca, Pinza).
   * El eslabón correspondiente debe ser desplazado físicamente hacia las proximidades de su primer tope mecánico, procediendo a registrar el punto mediante el botón **📸 REGISTRAR EXTREMO 1**.
   * Acto seguido, el eslabón debe ser desplazado hacia la frontera opuesta para su registro mediante el botón **📸 REGISTRAR EXTREMO 2**.
4. **Actualización de Tabla Dinámica:** Tras la captura de ambos extremos articulares, la tabla de Límites Seguros es actualizada de manera instantánea con los valores computados.
5. **Exportación de Datos:** Una vez registradas las 5 articulaciones, el sistema habilita el control de exportación. Su activación genera automáticamente el directorio `limites_act6` en la ruta del espacio de trabajo, almacenando los resultados consolidados en los formatos `limites_seguros.csv` y `limites_seguros.json`.

## ⚠️ Consideraciones de Seguridad
* **Liberación de Actuadores:** En caso de detectarse resistencia mecánica en las articulaciones, se dispone del comando "🔄 REINICIAR MOTORES (Torque OFF)" para forzar la liberación de los mismos.
* **Monitorización en Tiempo Real:** Se recomienda inspeccionar continuamente el indicador numérico "Posición:", garantizando de esta manera que el encoder del actuador se encuentre registrando el desplazamiento manual previo a la captura definitiva del punto.
