<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Gabriel+Eduardo+Bojaca+Munar">
</p>
<p>
  <img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=700&size=22&duration=2400&pause=600&color=7F5AF0&center=true&vCenter=true&width=600&lines=Maria+Fernanda+Morillo+Tovar">
</p>

## Descripcion 
Con base en los requerimientos del laboratorio, la solución debe integrar el control de las articulaciones del Phantom X Pincher X100 mediante ROS 2 Jazzy, implementando las diferentes actividades solicitadas: movimientos individuales, simultáneos y secuenciales, interpolación de trayectorias, cinemática directa e inversa, enseñanza y repetición de poses, trazado de figuras y una coreografía robótica. Todo el sistema debe respetar los límites seguros de cada articulación, validar las posiciones antes de ejecutarlas y permitir la interacción tanto en RViz como con el robot físico. La arquitectura desarrollada recibe comandos del usuario, verifica que las configuraciones sean alcanzables y seguras, calcula la trayectoria o la solución de cinemática correspondiente, ejecuta el movimiento del manipulador y retroalimenta el estado del robot para continuar con la siguiente acción hasta finalizar la tarea.

## Diagrama de flujo 

```mermaid
flowchart TD
    A([Inicio]) --> B[Inicializar nodo ROS 2]
    B --> C[Establecer comunicación con Phantom X100]
    C --> D[Verificar estado del robot]
    D --> E[Ubicar robot en posición segura]

    E --> F[Esperar instrucción del usuario]

    F --> G{Seleccionar operación}

    G -->|Movimiento articular| H[Ingresar posiciones articulares]
    G -->|Cinemática inversa| I[Ingresar posición cartesiana]
    G -->|Trayectoria/Coreografía| J[Cargar secuencia de movimientos]

    H --> K[Validar límites articulares]
    I --> L[Calcular solución de cinemática inversa]
    J --> M[Generar trayectoria]

    L --> N{¿Solución válida?}
    N -->|No| O[Notificar error]
    O --> F
    N -->|Sí| K

    K --> P[Enviar comandos a los servomotores]
    M --> P

    P --> Q[Ejecutar movimiento]
    Q --> R[Actualizar estado del robot]

    R --> S{¿Acción finalizada?}
    S -->|No| Q
    S -->|Sí| T{¿Nueva operación?}

    T -->|Sí| F
    T -->|No| U[Regresar a posición inicial]
    U --> V[Finalizar comunicación]
    V --> W([Fin])
```
## Plano de planta 

![Captura de pantalla](Captura%20de%20pantalla%202026-07-17%20165541.png)

## Cinematica directa 

![Captura de pantalla 2](Captura%20de%20pantalla%202026-07-17%20170242.png)

## Conclusiones 

Conclusión 1 
La implementación de la cinemática directa e inversa permitió comprender cómo las coordenadas cartesianas y los ángulos articulares se relacionan para controlar el movimiento del robot. Además, el uso de ROS 2 facilitó la ejecución y validación de trayectorias de forma organizada y segura.

Conclusión 2 
El desarrollo de actividades como la interpolación de trayectorias, la enseñanza de poses y el trazado de figuras evidenció la importancia de planificar correctamente los movimientos del manipulador. Esto permitió obtener desplazamientos más suaves y precisos, mejorando el desempeño del robot durante las diferentes tareas.
