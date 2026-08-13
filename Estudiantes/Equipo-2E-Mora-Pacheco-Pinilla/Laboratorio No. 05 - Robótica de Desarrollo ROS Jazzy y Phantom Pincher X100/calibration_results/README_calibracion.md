# Calibración de Cero y Error Articular

## Laboratorio No. 05 — Phantom X Pincher X100 — ROS 2 Jazzy

---

## 1. Objetivo

Determinar el error sistemático de cada articulación del robot Phantom X Pincher
X100 enviando posiciones angulares conocidas y comparándolas con la posición
reportada por los servomotores DYNAMIXEL. A partir de los errores medidos se
calcula el desplazamiento de cero (offset) necesario para corregir la
calibración del manipulador.

---

## 2. Metodología

### 2.1. Posiciones de prueba

Para cada articulación se seleccionaron 5 posiciones angulares distribuidas
dentro del rango seguro, evitando colisiones con la mesa y respetando los
límites mecánicos del robot. El paso angular es de aproximadamente 45°.

| Articulación | ID  | Rango seguro (°) | Posiciones de prueba (°) |
|-------------|:---:|:----------------:|:------------------------:|
| Base         |   1 |  -150 a  150 | -60, -30, +0, +30, +60 |
| Hombro       |   2 |  -150 a  150 | +0, +15, +30, +45, +60 |
| Codo         |   3 |  -150 a  150 | -60, -30, +0, +30, +60 |
| Muñeca       |   4 |  -150 a  150 | -60, -30, +0, +30, +60 |
| Pinza        |   5 |   -90 a   90 | -30, -15, +0, +15, +30 |

### 2.2. Procedimiento

1. Se verificó que el robot esté en una posición segura y el controlador
   `pincher_controller` esté ejecutándose con `use_hardware:=true`.
2. Para cada articulación, en orden (Base → Hombro → Codo → Muñeca → Pinza):
   a. Se envía la primera posición angular vía el tópico `/pincher/command`.
   b. Se espera 1.5 segundos para que el motor alcance la posición.
   c. Se lee la posición reportada por el motor desde `/joint_states`.
   d. Se repite para las 5 posiciones.
   e. Se retorna la articulación a 0° (home).
3. Se calcula el error para cada punto: `e_q = q_deseado - q_medido`.
4. Se determina: error máximo, error promedio y desplazamiento de cero.

---

## 3. Resultados

### 3.1. Tabla de resultados

| Articulación | Error máx (°) | Error prom (°) | Offset cero (°) |
|-------------|:------------:|:--------------:|:---------------:|
| Base         |        1.64 |          0.76 |           0.76 |
| Hombro       |        1.29 |         -0.85 |          -0.85 |
| Codo         |        1.00 |         -0.29 |          -0.29 |
| Muñeca       |        0.50 |         -0.29 |          -0.29 |
| Pinza        |        0.38 |          0.29 |           0.29 |

### 3.2. Datos detallados por articulación

**Base** (`waist`)

| Prueba | Deseado (°) | Medido (°) | Error (°) |
|:-----:|:----------:|:---------:|:--------:|
|     1 |      -60.0 |    -60.70 |     0.70 |
|     2 |      -30.0 |    -31.38 |     1.38 |
|     3 |        0.0 |      0.00 |     0.00 |
|     4 |       30.0 |     29.91 |     0.09 |
|     5 |       60.0 |     58.36 |     1.64 |
|       | **Error máx:** | | **1.64°** |
|       | **Error prom:** | | **+0.76°** |
|       | **Offset cero:** | | **+0.76°** |

**Hombro** (`shoulder`)

| Prueba | Deseado (°) | Medido (°) | Error (°) |
|:-----:|:----------:|:---------:|:--------:|
|     1 |        0.0 |      0.29 |    -0.29 |
|     2 |       15.0 |     15.54 |    -0.54 |
|     3 |       30.0 |     31.09 |    -1.09 |
|     4 |       45.0 |     46.04 |    -1.04 |
|     5 |       60.0 |     61.29 |    -1.29 |
|       | **Error máx:** | | **1.29°** |
|       | **Error prom:** | | **-0.85°** |
|       | **Offset cero:** | | **-0.85°** |

**Codo** (`elbow`)

| Prueba | Deseado (°) | Medido (°) | Error (°) |
|:-----:|:----------:|:---------:|:--------:|
|     1 |      -60.0 |    -59.53 |    -0.47 |
|     2 |      -30.0 |    -30.79 |     0.79 |
|     3 |        0.0 |     -0.00 |     0.00 |
|     4 |       30.0 |     30.79 |    -0.79 |
|     5 |       60.0 |     61.00 |    -1.00 |
|       | **Error máx:** | | **1.00°** |
|       | **Error prom:** | | **-0.29°** |
|       | **Offset cero:** | | **-0.29°** |

**Muñeca** (`wrist`)

| Prueba | Deseado (°) | Medido (°) | Error (°) |
|:-----:|:----------:|:---------:|:--------:|
|     1 |      -60.0 |    -59.82 |    -0.18 |
|     2 |      -30.0 |    -29.91 |    -0.09 |
|     3 |        0.0 |      0.29 |    -0.29 |
|     4 |       30.0 |     30.50 |    -0.50 |
|     5 |       60.0 |     60.41 |    -0.41 |
|       | **Error máx:** | | **0.50°** |
|       | **Error prom:** | | **-0.29°** |
|       | **Offset cero:** | | **-0.29°** |

**Pinza** (`gripper`)

| Prueba | Deseado (°) | Medido (°) | Error (°) |
|:-----:|:----------:|:---------:|:--------:|
|     1 |      -30.0 |    -30.21 |     0.21 |
|     2 |      -15.0 |    -15.25 |     0.25 |
|     3 |        0.0 |     -0.29 |     0.29 |
|     4 |       15.0 |     14.66 |     0.34 |
|     5 |       30.0 |     29.62 |     0.38 |
|       | **Error máx:** | | **0.38°** |
|       | **Error prom:** | | **+0.29°** |
|       | **Offset cero:** | | **+0.29°** |


### 3.3. Interpretación de resultados

- **Error máximo:** La mayor desviación absoluta entre lo deseado y lo medido.
  Indica la precisión máxima del servo en todo su rango.
- **Error promedio:** El sesgo sistemático de la articulación. Si es positivo,
  el motor tiende a quedarse por debajo de la posición deseada.
- **Offset de cero:** Es el error promedio. Representa cuánto hay que desplazar
  la referencia de la articulación para que 0° real corresponda a 0° medido.

---

## 4. Gráficas

Se generaron dos tipos de gráficas:

### 4.1. Gráficas individuales

Archivo: `calibracion_{articulación}.png`

Cada gráfica contiene dos subgráficas:

1. **Posición deseada vs. medida** (superior): Compara visualmente el
   comportamiento real del servo frente a lo solicitado.
2. **Error** (inferior): Muestra la magnitud del error en cada punto.
   La línea verde punteada indica el error promedio.

### 4.2. Gráfica de resumen

Archivo: `calibracion_resumen.png`

Compara todas las articulaciones en una sola figura para facilitar la
identificación de cuáles articulaciones presentan mayor error.

---

## 5. Corrección de cero

### 5.1. Cálculo de la corrección

El offset de cero calculado debe aplicarse al parámetro `home_positions`
en el archivo de configuración del controlador. Para los servomotores
AX-12A, el rango raw es de 0 a 1023, correspondiente a 300° de giro.
La conversión de grados a unidades raw es:

    raw_offset = offset_grados × (1024 / 300)

### 5.2. Offsets recomendados

| Articulación | Offset (°) | Offset (raw) | home actual | home corregido |
|-------------|:----------:|:------------:|:----------:|:--------------:|
| Base         |       0.76 |           3 |        512 |           515 |
| Hombro       |      -0.85 |          -3 |        512 |           509 |
| Codo         |      -0.29 |          -1 |        512 |           511 |
| Muñeca       |      -0.29 |          -1 |        512 |           511 |
| Pinza        |       0.29 |           1 |        512 |           513 |

### 5.3. Aplicación de la corrección

1. Abrir el archivo `pincher_control/config/ax12a.yaml`
2. Modificar el parámetro `home_positions` con los valores de la columna
   "home corregido":

```yaml
home_positions: [515, 509, 511, 511, 513]
```

3. Guardar el archivo y reiniciar el controlador.
4. Verificar que en home (0° para todas las articulaciones) el robot esté en la
   posición de referencia definida en la Actividad 2.

### 5.4. Verificación

Después de aplicar los offsets, repetir la calibración para confirmar que el
error promedio se ha reducido (idealmente a menos de ±1°).

---

## 6. Archivos generados

| Archivo | Contenido |
|---------|----------|
| `calibracion_resultados.yaml` | Datos completos de todas las mediciones |
| `offsets_recomendados.yaml` | Offsets calculados por articulación |
| `calibracion_{articulación}.png` | Gráfica individual por articulación |
| `calibracion_resumen.png` | Gráfica comparativa de todas las articulaciones |
| `README_calibracion.md` | Este documento |

---

## 7. Conclusiones

La calibración permitió cuantificar el error sistemático de cada articulación
del Phantom X Pincher X100. Los principales hallazgos fueron:

- **Base:** error máximo de 1.64°, offset de +0.76°.
- **Hombro:** error máximo de 1.29°, offset de -0.85°.
- **Codo:** error máximo de 1.00°, offset de -0.29°.
- **Muñeca:** error máximo de 0.50°, offset de -0.29°.
- **Pinza:** error máximo de 0.38°, offset de +0.29°.

Se recomienda aplicar los offsets calculados en el archivo `ax12a.yaml`
para mejorar la precisión del robot en tareas que requieran repetibilidad.
