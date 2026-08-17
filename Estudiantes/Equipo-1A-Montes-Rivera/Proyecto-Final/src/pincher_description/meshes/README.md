# Mallas del PhantomX Pincher X100

Descarga o copia los archivos de la carpeta `meshes` anexa al repositorio y ubícalos en esta carpeta. Deben conservar exactamente estos nombres:

- `px100_1_base.stl`
- `px100_2_shoulder.stl`
- `px100_3_upper_arm.stl`
- `px100_4_forearm.stl`
- `px100_5_gripper.stl`
- `px100_6_gripper_prop.stl`
- `px100_7_gripper_bar.stl`
- `px100_8_gripper_finger.stl`

Después de copiar las mallas, recompila el workspace para que los archivos también se instalen en el directorio `install/`.

El paquete puede iniciarse temporalmente con `use_meshes:=false` para validar TF, articulaciones y `/joint_states` mediante geometría simplificada.