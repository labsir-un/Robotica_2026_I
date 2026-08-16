# keyboard.py — lectura de teclado y bucle principal
#
# Lee teclas en modo raw (sin eco, sin buffering) usando termios/tty.
# keyboard_loop() corre en el hilo principal mientras rclpy.spin
# corre en un hilo daemon separado.

import sys
import tty
import termios
import threading


KEY_UP    = '\x1b[A'
KEY_DOWN  = '\x1b[B'
KEY_LEFT  = '\x1b[D'
KEY_RIGHT = '\x1b[C'


def get_key() -> str:
    """Lee una tecla del teclado en modo raw sin bloquear el executor."""
    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        key = sys.stdin.read(1)
        if key == '\x1b':
            key += sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return key


def keyboard_loop(node) -> None:
    """
    Bucle principal de lectura de teclado.
    Recibe el nodo como argumento para desacoplar este módulo
    de la clase TurtleController.

    Las trayectorias largas se lanzan en hilos daemon para no
    bloquear este bucle ni el executor de ROS 2.
    """
    print('\n' + '=' * 58)
    print('  TURTLE CONTROLLER — Lab 04 Robótica 2026-I')
    print('=' * 58)
    print('  ↑ ↓ ← →   Movimiento manual')
    print('  s  Cuadrado     t  Triángulo')
    print('  d  Letra D      T  Letra T')
    print('  l  Letra L      m  Letra M')
    print('  r  Reiniciar    p  Lápiz ON/OFF')
    print('  a  Auto-tray.   q  Detener')
    print('  Ctrl+C  Salir')
    print('=' * 58 + '\n')

    # Teclas de flecha → acción directa (un solo publish, no bloquea)
    arrows = {
        KEY_UP:    node.move_forward,
        KEY_DOWN:  node.move_backward,
        KEY_LEFT:  node.turn_left,
        KEY_RIGHT: node.turn_right,
    }

    # Trayectorias largas → hilo daemon (pueden tardar varios segundos)
    threaded = {
        's': node.draw_square,
        't': node.draw_triangle,
        'T': node.draw_letter_T,
        'd': node.draw_letter_D,
        'l': node.draw_letter_L,
        'm': node.draw_letter_M,
    }

    # Acciones que llaman servicios → también en hilo para no bloquear
    service_actions = {
        'r': node.reset_turtle,
        'p': node.toggle_pen,
    }

    # Acciones instantáneas que no llaman servicios
    direct = {
        'a': node.auto_trajectory,
        'q': node.stop_turtle1,
    }

    while node.running:
        try:
            key = get_key()
        except Exception:
            break

        if key in arrows:
            arrows[key]()

        elif key in threaded:
            threading.Thread(target=threaded[key], daemon=True).start()

        elif key in service_actions:
            threading.Thread(target=service_actions[key], daemon=True).start()

        elif key in direct:
            direct[key]()

        elif key == '\x03':   # Ctrl+C
            node.running = False
            break

        else:
            # Tecla no reconocida → detener movimiento manual
            from geometry_msgs.msg import Twist
            node.pub1.publish(Twist())
