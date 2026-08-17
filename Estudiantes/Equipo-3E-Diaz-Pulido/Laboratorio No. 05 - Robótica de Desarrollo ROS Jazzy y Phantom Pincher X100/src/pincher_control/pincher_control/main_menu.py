#!/usr/bin/env python3
"""
Interfaz unificada de consola para la ejecución cinemática y de trayectoria (Lab 5)

"""
import rclpy
import threading
from pincher_control.phantomx_sequencer import PhantomXSequencer

def main(args=None):
    rclpy.init(args=args)
    sequencer = PhantomXSequencer()
    
    # Hilo en segundo plano para leer los encoders continuamente 
    # sin que el menú (inputs) congele la comunicación con ROS 2
    executor_thread = threading.Thread(target=rclpy.spin, args=(sequencer,), daemon=True)
    executor_thread.start()
    
    print("=====================================================")
    print("   SISTEMA INTEGRADO DE CONTROL CINEMÁTICO (LAB 5)   ")
    print("=====================================================")
    
    while rclpy.ok():
        print("\n--- MENÚ PRINCIPAL DE OPERACIONES ---")
        print("1. [Análisis] Calcular Cinemática Directa")
        print("2. [Control] Mover TCP mediante Cinemática Inversa Segura")
        print("3. [Trayectoria] Ejecutar Interpolación con Evasión de Obstáculos")
        print("4. [Prueba] Actividad 4: Movimientos articulares individuales")
        print("5. [Prueba] Actividad 10: Generación de onda sinusoidal continua")
        print("6. [Análisis] Medir error de posicionamiento (Consigna vs Encoders)")
        print("7. [Enseñanza] Actividad 13: Enseñar y repetir poses (YAML)")
        print("8. [Trazado] Actividad 14: Crear, guardar y dibujar figuras (YAML)")
        print("q. Terminar secuencia y cerrar comunicación")
        
        opcion = input("Selección: ").strip().lower()
        
        if opcion == 'q':
            print("Cerrando los canales de comunicación con el robot...")
            break
        elif opcion == '1':
            sequencer.run_forward_kinematics()
        elif opcion == '2':
            sequencer.run_inverse_kinematics_move()
        elif opcion == '3':
            sequencer.run_advanced_interpolation()
        elif opcion == '4':
            sequencer.run_actividad_4()
        elif opcion == '5':
            # Ejecuta la prueba sinusoidal en el eje de la base (index 0)
            sequencer.run_actividad_10()
        elif opcion == '6':
            sequencer.run_measure_error()
        elif opcion == '7':
            sequencer.run_actividad_13()
        elif opcion == '8':
            sequencer.run_actividad_14()
        else:
            print("Opción no válida. Intente nuevamente.")
            
    sequencer.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
