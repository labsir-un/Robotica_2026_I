# Módulo Core - Puente de Comunicaciones (`joint_selector.py`)

## 📖 Descripción y Máxima Importancia
El archivo `joint_selector.py` no es una actividad en sí misma, sino el **corazón y sistema nervioso de todo el laboratorio**. Es un script fundamental diseñado como un Nodo de ROS 2 (`Node`) que actúa como un puente (middleware) entre las Interfases Gráficas (GUIs) construidas con Tkinter y el controlador de hardware/simulación subyacente.

Sin este archivo, las Actividades de la 4 a la 15 simplemente no podrían funcionar, ya que es el único encargado de traducir las órdenes de los botones y deslizadores a comandos matemáticos que ROS 2 y los servomotores Dynamixel puedan entender. 

### ¿Por qué es tan importante?
1. **Abstracción del Código:** Oculta toda la complejidad de los publicadores y suscriptores de ROS 2. En lugar de que cada actividad tenga que lidiar con mensajes complejos de `JointTrajectory`, las actividades simplemente llaman a funciones amigables como `node.mover_simultaneo()`.
2. **Traducción de Nombres y Unidades:** Mapea nombres humanos ("base", "hombro", "codo") a los nombres largos y técnicos del URDF (`phantomx_pincher_arm_shoulder_pan_joint`, etc.). Además, convierte automáticamente los grados de la interfaz a radianes para los motores del brazo, y a metros lineales para los dedos de la pinza.
3. **Lectura en Tiempo Real:** Mantiene un hilo de ejecución constante escuchando el tópico `/joint_states`, permitiendo que cualquier actividad sepa exactamente dónde está el robot en todo momento (vital para la Actividad 13 de Enseñanza y la Cinemática Inversa).
4. **Seguridad Integrada (Actividad 6):** El script está programado para buscar automáticamente el archivo `limites_seguros.json` creado en la Actividad 6. Si lo encuentra, sobrescribe sus límites por defecto para garantizar que ningún otro script pueda dañar el robot enviando comandos fuera de los topes mecánicos.

## ⚙️ Arquitectura de Funciones (API)
Los scripts de las actividades utilizan este módulo a través de las siguientes funciones principales:

*   `leer_posicion(nombre)` / `leer_todas()`: Extraen la posición actual del motor en grados (procesando el mensaje nativo en radianes de ROS 2).
*   `mover_articulacion(nombre, angulo_deg, espera_s)`: Envía un único motor a una posición específica en un tiempo determinado.
*   `mover_simultaneo(objetivos_deg, espera_s)`: La función más poderosa. Recibe un diccionario con múltiples articulaciones y empaqueta un mensaje de trayectoria coordinada, enviando comandos simultáneos tanto al controlador del brazo (`arm_pub`) como al de la pinza (`gripper_pub`).
*   `habilitar_torque()` / `apagar_torque_solamente()`: Controlan la rigidez de los servomotores permitiendo bloquear la postura o liberar el brazo para manipulación manual.
*   `set_velocidad(velocidad)`: Ajusta el registro de velocidad física de los Dynamixel (0 a 1023).

## 🚀 Uso
Este archivo **nunca se ejecuta directamente por consola**. En su lugar, es importado al principio del código de todas las demás actividades mediante la directiva:
```python
from joint_selector import JointSelector, JOINTS, LIMITS_DEG
```
Debe mantenerse siempre en la misma carpeta (`mis_actividades`) donde residen los scripts de las actividades de la 4 a la 15 para asegurar que Python pueda encontrarlo y compilarlo como un módulo local.