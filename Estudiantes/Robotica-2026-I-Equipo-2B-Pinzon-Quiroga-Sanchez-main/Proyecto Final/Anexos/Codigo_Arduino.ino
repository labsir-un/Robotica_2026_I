const int sensorIR = 2; // Debe ser pin 2 o 3 en Arduino Uno
const int pinCapacitor = 9;
const int pinIC = 11;
const int pinResistor = 8;
const int pinConector = 10;

volatile bool ifInf = LOW; // Variable modificada dentro de la interrupción

void setup() {
  Serial.begin(115200);
  pinMode(sensorIR, INPUT_PULLUP); // O INPUT según tu circuito
  pinMode(pinCapacitor, OUTPUT);
  pinMode(pinIC, OUTPUT);
  pinMode(pinResistor, OUTPUT);
  pinMode(pinConector, OUTPUT);
  apagarTodo();
  
  // Vincular la interrupción en flanco de subida (RISING)
  attachInterrupt(digitalPinToInterrupt(sensorIR), detectarIR, RISING);
}

void loop() {
  // Si la interrupción detectó el sensor
  if (ifInf == HIGH) {
    Serial.println("IR");
    Serial.println(" ");
    // Esperar respuesta desde Python
    while (Serial.available() == 0) {
      // Esperar datos sin bloquear con delay
    }
    
    int clase = Serial.parseInt();
    apagarTodo();
    switch (clase) {
      case 1: digitalWrite(pinIC, LOW); Serial.println("Capacitor"); break;
      case 2: digitalWrite(pinCapacitor, LOW); Serial.println("IC"); break;
      case 3: digitalWrite(pinConector, LOW); Serial.println("Resistor"); break;
      case 4: digitalWrite(pinResistor, LOW); Serial.println("Transistor"); break;
      case 5: Serial.println("No se detectó nada"); break;
      default: Serial.println("Dato invalido"); break;
    }
    ifInf = LOW; // Reiniciar indicador
    Serial.print("Recibido: ");
    Serial.println(clase);
  }
}

// Rutina de Servicio de Interrupción (ISR)
void detectarIR() {
  ifInf = HIGH;
}

void apagarTodo() {
  digitalWrite(pinCapacitor, HIGH);
  digitalWrite(pinIC, HIGH);
  digitalWrite(pinResistor, HIGH);
  digitalWrite(pinConector, HIGH);
}
