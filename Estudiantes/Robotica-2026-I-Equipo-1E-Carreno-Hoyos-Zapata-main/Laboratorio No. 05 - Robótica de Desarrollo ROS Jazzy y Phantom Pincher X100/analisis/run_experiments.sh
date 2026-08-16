#!/bin/bash
# Corre los experimentos reales: para cada uno lanza, en un dominio ROS propio,
# pincher_node + recorder + experiments, graba CSV en analisis/datos/ y termina.
# Sin RViz (solo datos). Dominio unico por corrida + teardown completo para evitar
# flakiness de descubrimiento DDS al reiniciar nodos.
#
# Uso: bash run_experiments.sh
HERE="$(cd "$(dirname "$0")" && pwd)"
DATA="$HERE/datos"
mkdir -p "$DATA"
source /opt/ros/jazzy/setup.bash
source "$(cd "$HERE/.." && pwd)/install/setup.bash"

DOMAIN=100

teardown () {
  pkill -9 -f 'pincher_lab.pincher_node' 2>/dev/null
  pkill -9 -f 'pincher_lab.recorder' 2>/dev/null
  pkill -9 -f 'pincher_lab.experiments' 2>/dev/null
  pkill -9 -f 'ros2 run pincher_lab' 2>/dev/null
  sleep 3
}

run () {
  local prefix="$1"; shift
  DOMAIN=$((DOMAIN+1))
  export ROS_DOMAIN_ID=$DOMAIN
  teardown
  setsid ros2 run pincher_lab pincher_node --ros-args \
      -p actuator_tau:=0.06 -p servo_kp:=12.0 -p max_joint_speed:=2.5 >/tmp/pn.log 2>&1 &
  sleep 3
  setsid ros2 run pincher_lab recorder --ros-args -p out_prefix:="$DATA/$prefix" >/tmp/rec.log 2>&1 &
  sleep 2.5
  setsid ros2 run pincher_lab experiments --ros-args "$@" >/tmp/exp_$prefix.log 2>&1 &
  local EX=$!
  local waited=0
  while kill -0 $EX 2>/dev/null && [ $waited -lt 70 ]; do sleep 1; waited=$((waited+1)); done
  sleep 1.5
  teardown
  local cmd_n; cmd_n=$(($(wc -l < "$DATA/${prefix}_cmd.csv" 2>/dev/null || echo 1)-1))
  local st_n;  st_n=$(($(wc -l < "$DATA/${prefix}_state.csv" 2>/dev/null || echo 1)-1))
  if [ "$cmd_n" -lt 10 ] || [ "$st_n" -lt 10 ]; then
    echo "  !! $prefix  cmd=$cmd_n state=$st_n  (POCOS DATOS, revisar)"
  else
    echo "  -> $prefix  cmd=$cmd_n state=$st_n"
  fi
}

echo "Interpolacion (codo -90 a 90, 3 metodos):"
run interp_linear  -p kind:=interp -p method:=linear  -p joint:=elbow
run interp_cubic   -p kind:=interp -p method:=cubic   -p joint:=elbow
run interp_quintic -p kind:=interp -p method:=quintic -p joint:=elbow

echo "Sinusoidal (4 pruebas A x f):"
run sinus_a20_f025 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=20.0 -p frequency:=0.25 -p cycles:=3.0
run sinus_a20_f050 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=20.0 -p frequency:=0.50 -p cycles:=3.0
run sinus_a40_f025 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=40.0 -p frequency:=0.25 -p cycles:=3.0
run sinus_a40_f050 -p kind:=sinus -p joint:=elbow -p amplitude_deg:=40.0 -p frequency:=0.50 -p cycles:=3.0

echo "Calibracion / exactitud (5 escalones por articulacion):"
run calib -p kind:=calib -p settle:=1.5

teardown
echo "LISTO. CSV en $DATA"
