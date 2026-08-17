# Mallas del PhantomX Pincher Robot Arm

Coloca en esta carpeta los archivos STL de los componentes del robot.
Deben conservar exactamente estos nombres:

| Archivo | Componente |
|---------|-----------|
| `servo_ax12a.stl` | Servomotor Dynamixel AX-12A |
| `bracket_shoulder_F3.stl` | Bracket Bioloid F3 (hombro y conexiones) |
| `bracket_upper_arm_F4.stl` | Bracket Bioloid F4 (brazo superior y codo) |
| `bracket_wrist_F2.stl` | Bracket Bioloid F2 (muñeca) |
| `gripper_base_plate.stl` | Placa base del gripper |
| `gripper_finger.stl` | Dedo del gripper |

## Notas

- Si las mallas están en milímetros, el Xacro aplica `scale="0.001 0.001 0.001"`.
- Después de copiar las mallas, recompila con `colcon build --symlink-install`.
- El paquete puede usarse con `use_meshes:=false` para validar el modelo
  usando geometría simplificada (cajas) sin necesidad de las mallas.
