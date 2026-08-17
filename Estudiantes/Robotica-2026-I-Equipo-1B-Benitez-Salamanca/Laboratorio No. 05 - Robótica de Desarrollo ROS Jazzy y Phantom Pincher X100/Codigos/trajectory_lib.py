#!/usr/bin/env python3
"""Generación de trayectorias articulares por interpolación.

Implementa tres métodos clásicos de planificación de trayectoria punto a
punto (point-to-point) para una sola variable articular q(t), y una versión
vectorizada para mover varias articulaciones a la vez.

Métodos:
    - linear_trajectory:   interpolación lineal (velocidad constante).
                           Discontinuidad de velocidad en t=0 y t=tf
                           (aceleración teóricamente infinita en esos
                           instantes -> "tirones" o jerks en el robot real).
    - cubic_trajectory:    polinomio cúbico con condiciones de frontera
                           de velocidad nula en q0 y qf. Continuo en
                           posición y velocidad, pero con discontinuidad
                           en la aceleración en los extremos.
    - quintic_trajectory:  polinomio de quinto grado con velocidad Y
                           aceleración nulas en los extremos. Continuo en
                           posición, velocidad y aceleración: es el más
                           suave de los tres.

Todas las funciones devuelven (q, qd, qdd): posición, velocidad y
aceleración angular, evaluadas en los instantes de tiempo `t` (puede ser
un escalar o un arreglo de numpy).
"""

from __future__ import annotations

import numpy as np


def linear_trajectory(q0: float, qf: float, tf: float, t: np.ndarray):
    """Interpolación lineal simple: q(t) = q0 + (qf - q0) * (t / tf).

    Velocidad constante durante todo el tramo; aceleración nula excepto
    en los instantes t=0 y t=tf, donde en teoría hay un impulso infinito
    (en la práctica, un cambio brusco de velocidad).
    """
    t = np.clip(np.asarray(t, dtype=float), 0.0, tf)
    s = t / tf
    q = q0 + (qf - q0) * s
    qd = np.full_like(t, (qf - q0) / tf)
    qdd = np.zeros_like(t)
    return q, qd, qdd


def cubic_trajectory(q0: float, qf: float, tf: float, t: np.ndarray):
    """Polinomio cúbico con velocidad nula en los extremos.

    q(t) = a0 + a1*t + a2*t^2 + a3*t^3

    Condiciones de frontera: q(0)=q0, q(tf)=qf, qd(0)=0, qd(tf)=0.
    """
    t = np.clip(np.asarray(t, dtype=float), 0.0, tf)
    delta = qf - q0
    a0 = q0
    a1 = 0.0
    a2 = 3.0 * delta / tf ** 2
    a3 = -2.0 * delta / tf ** 3

    q = a0 + a1 * t + a2 * t ** 2 + a3 * t ** 3
    qd = a1 + 2 * a2 * t + 3 * a3 * t ** 2
    qdd = 2 * a2 + 6 * a3 * t
    return q, qd, qdd


def quintic_trajectory(q0: float, qf: float, tf: float, t: np.ndarray):
    """Polinomio de quinto grado con velocidad y aceleración nulas en los extremos.

    q(t) = a0 + a1*t + a2*t^2 + a3*t^3 + a4*t^4 + a5*t^5

    Condiciones de frontera: q(0)=q0, q(tf)=qf,
    qd(0)=0, qd(tf)=0, qdd(0)=0, qdd(tf)=0.
    """
    t = np.clip(np.asarray(t, dtype=float), 0.0, tf)
    delta = qf - q0
    a0 = q0
    a1 = 0.0
    a2 = 0.0
    a3 = 10.0 * delta / tf ** 3
    a4 = -15.0 * delta / tf ** 4
    a5 = 6.0 * delta / tf ** 5

    q = a0 + a3 * t ** 3 + a4 * t ** 4 + a5 * t ** 5
    qd = 3 * a3 * t ** 2 + 4 * a4 * t ** 3 + 5 * a5 * t ** 4
    qdd = 6 * a3 * t + 12 * a4 * t ** 2 + 20 * a5 * t ** 3
    return q, qd, qdd


TRAJECTORY_METHODS = {
    'linear': linear_trajectory,
    'cubic': cubic_trajectory,
    'quintic': quintic_trajectory,
}


def generate_multijoint_trajectory(
    method: str,
    q0_vec: np.ndarray,
    qf_vec: np.ndarray,
    tf: float,
    num_samples: int = 200,
):
    """Genera la trayectoria de varias articulaciones al mismo tiempo.

    Parameters
    ----------
    method: 'linear', 'cubic' o 'quintic'
    q0_vec, qf_vec: configuraciones inicial y final (radianes), un valor
        por articulación, mismo orden y longitud.
    tf: duración total del movimiento (segundos).
    num_samples: cantidad de instantes de tiempo a evaluar.

    Returns
    -------
    t: arreglo de tiempo, forma (num_samples,)
    Q, Qd, Qdd: posición/velocidad/aceleración, forma (num_samples, n_joints)
    """
    if method not in TRAJECTORY_METHODS:
        raise ValueError(f'Método desconocido: {method}. Usa uno de {list(TRAJECTORY_METHODS)}')

    q0_vec = np.asarray(q0_vec, dtype=float)
    qf_vec = np.asarray(qf_vec, dtype=float)
    if q0_vec.shape != qf_vec.shape:
        raise ValueError('q0_vec y qf_vec deben tener la misma longitud.')

    func = TRAJECTORY_METHODS[method]
    t = np.linspace(0.0, tf, num_samples)
    n_joints = q0_vec.shape[0]

    Q = np.zeros((num_samples, n_joints))
    Qd = np.zeros((num_samples, n_joints))
    Qdd = np.zeros((num_samples, n_joints))

    for j in range(n_joints):
        q, qd, qdd = func(q0_vec[j], qf_vec[j], tf, t)
        Q[:, j] = q
        Qd[:, j] = qd
        Qdd[:, j] = qdd

    return t, Q, Qd, Qdd
