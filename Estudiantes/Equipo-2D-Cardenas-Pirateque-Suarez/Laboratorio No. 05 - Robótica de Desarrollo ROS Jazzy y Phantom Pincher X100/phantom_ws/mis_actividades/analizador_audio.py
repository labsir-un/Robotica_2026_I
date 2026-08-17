#!/usr/bin/env python3
"""
Analizador de Espectro y Ritmo para Coreografía Robótica
Extrae Energía (Volumen), Frecuencia y Beats a 10Hz y lo guarda en CSV para ambas canciones.
"""

import os
import csv
import librosa
import numpy as np

# Rutas de archivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Canción 1
ARCHIVO_MP3_1 = os.path.join(BASE_DIR, "dubidubidu.mp3")
ARCHIVO_CSV_1 = os.path.join(BASE_DIR, "datos_dubidubidu.csv")

# Canción 2
ARCHIVO_MP3_2 = os.path.join(BASE_DIR, "pedro.mp3")
ARCHIVO_CSV_2 = os.path.join(BASE_DIR, "datos_pedro.csv")

def procesar_cancion(ruta_in, ruta_out, fps=10):
    if not os.path.exists(ruta_in):
        print(f"❌ Error: No se encontró {ruta_in}")
        return

    print(f"\n🎧 Cargando audio: {os.path.basename(ruta_in)} (Esto puede tardar unos segundos)...")
    y, sr = librosa.load(ruta_in, sr=None)

    print("📊 Extrayendo Energía (Volumen/RMS)...")
    rms = librosa.feature.rms(y=y)[0]

    print("🌊 Extrayendo Frecuencias (Centroide Espectral)...")
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]

    print("🥁 Detectando Golpes (Beats)...")
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    beats = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)[1]
    beat_times = librosa.frames_to_time(beats, sr=sr)

    # Crear una base de tiempo absoluta a nuestra frecuencia objetivo (10 Hz = 0.1s)
    duracion = librosa.get_duration(y=y, sr=sr)
    tiempos_10hz = np.arange(0, duracion, 1.0 / fps)

    # Interpolar los datos de librosa para que encajen exactamente en nuestros tiempos de 10Hz
    frames_librosa = librosa.times_like(rms, sr=sr)
    energia_10hz = np.interp(tiempos_10hz, frames_librosa, rms)
    freq_10hz = np.interp(tiempos_10hz, frames_librosa, cent)

    # Normalizar los datos entre 0.0 y 1.0 para que sean fáciles de multiplicar por los ángulos de las articulaciones
    energia_norm = energia_10hz / np.max(energia_10hz)
    freq_norm = freq_10hz / np.max(freq_10hz)

    print(f"💾 Guardando datos sincronizados en: {os.path.basename(ruta_out)}")
    with open(ruta_out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Tiempo_s", "Energia", "Frecuencia", "Es_Beat"])
        
        # Margen para considerar que un tiempo de 10Hz "cae" en un beat
        margen = (1.0 / fps) / 2.0 
        
        for t, e, f_val in zip(tiempos_10hz, energia_norm, freq_norm):
            # Verificar si en este frame de 0.1s hubo un golpe de percusión
            es_beat = 1 if any(abs(t - bt) <= margen for bt in beat_times) else 0
            
            # Guardamos a 3 decimales
            writer.writerow([round(t, 2), round(e, 3), round(f_val, 3), es_beat])
            
    print(f"✅ ¡Análisis de {os.path.basename(ruta_in)} completado exitosamente!")

if __name__ == "__main__":
    print("INICIANDO EXTRACCIÓN DE CARACTERÍSTICAS MUSICALES (FFT)")
    procesar_cancion(ARCHIVO_MP3_1, ARCHIVO_CSV_1, fps=10)
    procesar_cancion(ARCHIVO_MP3_2, ARCHIVO_CSV_2, fps=10)
    print("\n✅ TODO EL PROCESAMIENTO HA FINALIZADO.")