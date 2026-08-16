"""Utilidades comunes a los scripts de analisis (rutas e import del paquete)."""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, '..', 'src', 'pincher_lab', 'pincher_lab')
IMAGES = os.path.join(HERE, '..', 'imagenes')

sys.path.insert(0, PKG)
os.makedirs(IMAGES, exist_ok=True)


DATA = os.path.join(HERE, 'datos')


def save(fig, name: str) -> str:
    path = os.path.join(IMAGES, name)
    fig.savefig(path, dpi=130, bbox_inches='tight')
    print(f'  guardado: imagenes/{name}')
    return path


def load_csv(name: str):
    """Carga un CSV grabado (cmd o state) como dict de columnas numpy.

    Celdas vacias -> NaN. Devuelve (dict columna->array, lista de nombres).
    """
    import csv

    import numpy as np
    path = os.path.join(DATA, name)
    with open(path, 'r', encoding='utf-8') as fh:
        reader = csv.reader(fh)
        header = next(reader)
        cols = {h: [] for h in header}
        for row in reader:
            for h, v in zip(header, row):
                cols[h].append(float(v) if v not in ('', None) else np.nan)
    return {h: np.array(v) for h, v in cols.items()}, header

