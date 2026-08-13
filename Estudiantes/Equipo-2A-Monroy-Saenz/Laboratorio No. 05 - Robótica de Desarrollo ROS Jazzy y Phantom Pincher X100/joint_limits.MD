```python
from dataclasses import dataclass

# Límite mecánico "de fábrica" (el que ya impone el xacro/GUI del repo)
FACTORY_LIMITS_DEG = {
    "waist": (-150.0, 150.0),
    "shoulder": (-150.0, 150.0),
    "elbow": (-150.0, 150.0),
    "wrist": (-150.0, 150.0),
    "gripper": (-90.0, 90.0),
}

# Margen de seguridad que se resta de cada lado del límite de fábrica
MARGIN_DEG = {
    "waist": 5.0,
    "shoulder": 5.0,
    "elbow": 5.0,
    "wrist": 5.0,
    "gripper": 5.0,
}


@dataclass(frozen=True)
class SafeLimit:
    lower_deg: float
    upper_deg: float
    margin_deg: float


def build_safe_limits():
    safe = {}
    for joint, (lo, hi) in FACTORY_LIMITS_DEG.items():
        m = MARGIN_DEG[joint]
        safe[joint] = SafeLimit(lower_deg=lo + m, upper_deg=hi - m, margin_deg=m)
    return safe


SAFE_LIMITS = build_safe_limits()

JOINT_ORDER = ["waist", "shoulder", "elbow", "wrist", "gripper"]
JOINT_LABELS_ES = {
    "waist": "Base",
    "shoulder": "Hombro",
    "elbow": "Codo",
    "wrist": "Muñeca",
    "gripper": "Pinza",
}


class OutOfSafeRangeError(ValueError):
    pass


def check_safe(joint: str, angle_deg: float) -> float:
    if joint not in SAFE_LIMITS:
        raise KeyError(f"Articulación desconocida: {joint}")
    limit = SAFE_LIMITS[joint]
    if not (limit.lower_deg <= angle_deg <= limit.upper_deg):
        raise OutOfSafeRangeError(
            f"{JOINT_LABELS_ES[joint]} ({joint}): {angle_deg}° fuera del "
            f"rango seguro [{limit.lower_deg}°, {limit.upper_deg}°] "
            f"(margen {limit.margin_deg}° respecto al tope mecánico "
            f"{FACTORY_LIMITS_DEG[joint]})."
        )
    return angle_deg


def print_table():
    print(f"{'Articulación':<12}{'Límite inf.':>14}{'Límite sup.':>14}{'Margen':>10}")
    for joint in JOINT_ORDER:
        limit = SAFE_LIMITS[joint]
        print(
            f"{JOINT_LABELS_ES[joint]:<12}"
            f"{limit.lower_deg:>13.1f}°"
            f"{limit.upper_deg:>13.1f}°"
            f"{limit.margin_deg:>9.1f}°"
        )


if __name__ == "__main__":
    print_table()
```
