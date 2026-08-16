#!/bin/bash
# Repite los experimentos de las Actividades 9 y 10 sobre el ROBOT REAL.
#
# A diferencia de `run_experiments.sh`, que arranca el simulador `pincher_node`
# en cada corrida, aqui el driver de hardware YA debe estar corriendo:
#
#   ros2 launch pincher_lab robot_real.launch.py
#
# Solo se lanzan `recorder` (graba /pincher/command y /joint_states) y
# `experiments` (genera la consigna). El driver se deja intacto entre pruebas
# para no reabrir el puerto serie una y otra vez.
#
#   Uso:  bash analisis/run_experiments_hw.sh
#
# Los CSV se guardan en analisis/datos/ con el sufijo _hw, de modo que NO
# sobrescriben los de simulacion: asi se pueden comparar ambos.

AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RAIZ="$(dirname "$AQUI")"
DATOS="$AQUI/datos"
mkdir -p "$DATOS"

source /opt/ros/jazzy/setup.bash
source "$RAIZ/install/setup.bash"
set -u

VEL=100

if ! ros2 service call /pincher/torque_enable std_srvs/srv/SetBool "{data: true}" \
        >/dev/null 2>&1; then
    echo "ERROR: no responde /pincher/torque_enable."
    echo "       Lanza antes:  ros2 launch pincher_lab robot_real.launch.py"
    exit 1
fi

a_home() {
    ros2 topic pub --once /pincher/command sensor_msgs/JointState \
        "{name: ['waist','shoulder','elbow','wrist','gripper'], \
          position: [0.0, 0.0, 0.0, 0.0, 0.0]}" >/dev/null 2>&1
    sleep 6
}

# `experiments` hereda de Node, no de SamplePlayer: no declara `profile_velocity`
# ni `shutdown_when_done`, asi que pasarlos como parametros haria fallar el nodo.
# La velocidad se fija por topico (dos veces, por el emparejamiento DDS) y el
# propio nodo termina solo al agotar sus muestras.
fijar_velocidad() {
    for _ in 1 2; do
        ros2 topic pub --once /pincher/profile_velocity std_msgs/UInt32 \
            "{data: $VEL}" >/dev/null 2>&1
        sleep 0.3
    done
}

correr () {
    local prefijo="$1"; shift
    echo ">>> $prefijo"
    a_home
    fijar_velocidad
    # Sin `setsid`: con el, el recorder queda en otra sesion, la senal no le
    # llega y el guion se queda esperandolo indefinidamente. Se cierra por
    # nombre, primero con INT para que vacie los CSV y luego a la fuerza.
    # Se graba /joint_states_sim, que es donde el driver publica con los nombres
    # CORTOS del entregable. En /joint_states estan ya traducidos a los nombres
    # largos del modelo del KIT, que el recorder no reconoce (escribiria vacio).
    ros2 run pincher_lab recorder --ros-args \
        -r /joint_states:=/joint_states_sim \
        -p out_prefix:="$DATOS/${prefijo}_hw" >/tmp/rec_hw.log 2>&1 &
    sleep 2
    ros2 run pincher_lab experiments --ros-args "$@" >/tmp/exp_hw.log 2>&1
    sleep 2
    pkill -INT -f 'pincher_lab/recorder' 2>/dev/null
    sleep 2
    pkill -9 -f 'pincher_lab/recorder' 2>/dev/null
    sleep 1
    local n=$(wc -l < "$DATOS/${prefijo}_hw_state.csv" 2>/dev/null || echo 0)
    echo "    -> ${prefijo}_hw  ($n muestras)"
}

echo "Actividad 9 - Interpolacion (lineal, cubica, quintica) sobre el codo:"
correr interp_linear  -p kind:=interp -p method:=linear  -p joint:=elbow
correr interp_cubic   -p kind:=interp -p method:=cubic   -p joint:=elbow
correr interp_quintic -p kind:=interp -p method:=quintic -p joint:=elbow

echo
echo "Actividad 10 - Sinusoidal (2 amplitudes x 2 frecuencias):"
correr sinus_a20_f025 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=20.0 -p frequency:=0.25 -p cycles:=3.0
correr sinus_a20_f050 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=20.0 -p frequency:=0.50 -p cycles:=3.0
correr sinus_a40_f025 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=40.0 -p frequency:=0.25 -p cycles:=3.0
correr sinus_a40_f050 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=40.0 -p frequency:=0.50 -p cycles:=3.0

a_home
echo
echo "LISTO. CSV en analisis/datos/ con sufijo _hw."
echo "Genera las graficas con:  python3 analisis/interpolacion_real.py"
echo "                          python3 analisis/sinusoidal_real.py"
