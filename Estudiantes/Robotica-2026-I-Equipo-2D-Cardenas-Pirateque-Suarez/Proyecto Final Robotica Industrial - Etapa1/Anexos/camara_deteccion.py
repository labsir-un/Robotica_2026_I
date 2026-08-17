from ultralytics import YOLO
import cv2
import serial
import time

# -------------------------
# Puerto serial (Arduino)
# -------------------------

arduino = serial.Serial(
    port="COM3",
    baudrate=115200,
    timeout=0.1
)

time.sleep(2)

# -------------------------
# Modelo YOLO
# -------------------------

model = YOLO(
    r"C:\Users\david\Desktop\ROBOTICA\Proyecto\YOLO\runs\detect\runs\Detector_prefinal\weights\best.pt"
)

# -------------------------
# Cámara
# -------------------------

cap = cv2.VideoCapture(0)

print("Esperando señal del Arduino...")

while True:

    # ¿Llegó un mensaje desde Arduino?
    if arduino.in_waiting > 0:

        mensaje = arduino.readline().decode().strip()
        if mensaje == "IR":
            print(mensaje)
            print("Pieza detectada")

            # Capturar una fotografía
            ret, frame = cap.read()

            if not ret:
                continue

            # Ejecutar YOLO
            results = model(frame, conf=0.5)

            # Imagen con anotaciones
            annotated = results[0].plot()

            if len(results[0].boxes) > 0:

                # Detección con mayor confianza
                mejor = results[0].boxes.conf.argmax()

                box = results[0].boxes[mejor]

                clase_yolo = int(box.cls[0])
                confianza = float(box.conf[0])

                nombre = results[0].names[clase_yolo]

                # Conversión de clases
                # YOLO: 0,1,2,3
                # Arduino: 1,2,3,4

                clase_arduino = clase_yolo + 1

                print(f"Clase: {nombre}")
                print(f"Confianza: {confianza:.2f}")
                print(f"Enviando: {clase_arduino}")

                arduino.write(f"{clase_arduino}\n".encode())
                while True:
                    if arduino.in_waiting:
                        respuesta = arduino.readline().decode().strip()

                        if respuesta.startswith("Recibido"):
                            break

            else:

                print("No se detectó ningún objeto")

                # 5 = No se detectó nada
                arduino.write(b"5\n")

            cv2.imshow("Resultado", annotated)
            

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()