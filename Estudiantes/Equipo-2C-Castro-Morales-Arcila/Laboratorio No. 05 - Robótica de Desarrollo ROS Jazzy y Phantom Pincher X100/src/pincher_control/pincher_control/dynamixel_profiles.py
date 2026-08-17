"""Perfiles de registros y conversión para servomotores DYNAMIXEL compatibles."""

from dataclasses import dataclass
import math
from typing import Optional

@dataclass(frozen=True)
class MotorProfile:
    """Descripción mínima de un modelo para control de posición."""

    name: str
    protocol_version: float
    raw_min: int
    raw_center: int
    raw_max: int
    mechanical_range_rad: float
    torque_enable_addr: int
    goal_position_addr: int
    goal_position_size: int
    speed_addr: int
    speed_size: int
    present_position_addr: int
    present_position_size: int
    torque_limit_addr: Optional[int] = None
    torque_limit_size: int = 0

    def clamp_raw(self, value: int) -> int:
        return max(self.raw_min, min(self.raw_max, int(value)))

    def raw_to_radians(self, value: int) -> float:
        """Convierte una lectura absoluta a radianes alrededor del centro."""
        value = self.clamp_raw(value)
        units_per_rad = (self.raw_max - self.raw_min) / self.mechanical_range_rad
        return (value - self.raw_center) / units_per_rad

    def radians_to_raw(self, radians: float) -> int:
        """Convierte radianes alrededor del centro a unidades DYNAMIXEL."""
        units_per_rad = (self.raw_max - self.raw_min) / self.mechanical_range_rad
        return self.clamp_raw(round(self.raw_center + radians * units_per_rad))

MOTOR_PROFILES = {
    'ax12a': MotorProfile(
        name='AX-12A',
        protocol_version=1.0,
        raw_min=0,
        raw_center=512,
        raw_max=1023,
        mechanical_range_rad=math.radians(300.0),
        torque_enable_addr=24,
        goal_position_addr=30,
        goal_position_size=2,
        speed_addr=32,
        speed_size=2,
        present_position_addr=36,
        present_position_size=2,
        torque_limit_addr=34,
        torque_limit_size=2,
    ),
    'xl430': MotorProfile(
        name='XL430-W250',
        protocol_version=2.0,
        raw_min=0,
        raw_center=2048,
        raw_max=4095,
        mechanical_range_rad=2.0 * math.pi,
        torque_enable_addr=64,
        goal_position_addr=116,
        goal_position_size=4,
        speed_addr=112,
        speed_size=4,
        present_position_addr=132,
        present_position_size=4,
        torque_limit_addr=None,
        torque_limit_size=0,
    ),
}

def get_motor_profile(model: str) -> MotorProfile:
    key = model.strip().lower().replace('-', '').replace('_', '')
    aliases = {
        'ax12': 'ax12a',
        'ax12a': 'ax12a',
        'xl430': 'xl430',
        'xl430w250': 'xl430',
    }
    canonical = aliases.get(key)
    if canonical is None:
        valid = ', '.join(sorted(MOTOR_PROFILES))
        raise ValueError(f'Modelo DYNAMIXEL no soportado: {model}. Opciones: {valid}')
    return MOTOR_PROFILES[canonical]
