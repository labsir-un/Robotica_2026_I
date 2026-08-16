*
 * ============================================================================
 * CONTROL DE GRIPPER PARALELO SG90 CON ARDUINO UNO
 * Robot ABB IRB 140 "Abel" - Etapa 4: Alimentacion de PCBs a cajas
 * Proyecto Final de Robotica Industrial 2026-I
 *
 * ----------------------------------------------------------------------------
 * ENTRADAS  (IRC5 -> Arduino, a traves de optoacopladores PC817)
 *   D2 <- DO_04  do_grip     0 = abrir (10 gr)   1 = cerrar (100 gr)
 *   D4 <- DO_06  do_fault    bit de falla declarado por el programa RAPID
 *
 * SALIDAS   (Arduino -> IRC5, a traves de reles de contacto seco)
 *   D5 -> DI_04  di_gripOK   NIVEL: gripper en la posicion ordenada
 *   D6 -> DI_05  di_home     PULSO: comando remoto de ir a HOME
 *   D7 -> DI_06  di_start    PULSO: comando remoto de iniciar ciclo
 *
 * OTRAS SALIDAS
 *   D9  -> senal PWM hacia el servomotor SG90
 *   D13 -> LED de diagnostico integrado en la placa
 *
 * NO GESTIONADAS POR EL ARDUINO (cableado fijo del puesto)
 *   DO_01, DO_02, DO_03  bombillos    manejados directamente por RAPID
 *   DI_01, DI_02, DI_03  botonera     leidos directamente por RAPID
 *
 * INTERFAZ DE SUPERVISION
 *   USB / UART a 9600 baudios. Protocolo de texto.
 * ============================================================================
 *

#include <Servo.h>

// ------------------------- Asignacion de pines -------------------------
const uint8_t PIN_DO04  =  2;   // do_grip
const uint8_t PIN_DO06  =  4;   // do_fault

const uint8_t PIN_DI04  =  5;   // di_gripOK (nivel)
const uint8_t PIN_DI05  =  6;   // di_home   (pulso)
const uint8_t PIN_DI06  =  7;   // di_start  (pulso)

const uint8_t PIN_SERVO =  9;   // PWM hacia el SG90 (Timer1)
const uint8_t PIN_LED   = 13;   // LED integrado

// ------------- Polaridad del modulo de reles (VERIFICAR EN EL MONTAJE) -------------
// Muchos modulos comerciales son activos en BAJO. Si al energizar los tres
// reles quedan cerrados, invertir estas dos constantes.
const uint8_t RELE_ON  = HIGH;
const uint8_t RELE_OFF = LOW;

// ------------- Angulos de trabajo (CALIBRADOS EXPERIMENTALMENTE) -------------
int angAbierto = 10;    // apertura total: reposo, aproximacion y suelta
int angCerrado = 100;   // sujecion del PCB

// ------------------------ Parametros de operacion ------------------------
const unsigned long T_DEBOUNCE   =  30;   // ms - filtro antirrebote
const unsigned long T_DETACH     = 800;   // ms - espera antes de liberar el servo
const unsigned long T_PULSO      = 300;   // ms - duracion del pulso en DI05 y DI06
const unsigned long T_TELEMETRIA = 500;   // ms - periodo de la trama de estado
const int           PASO_GRADOS  =   2;   // grados por paso (movimiento suave)
const unsigned long T_PASO       =  15;   // ms entre pasos consecutivos

// ---------------------------- Estado interno ----------------------------
Servo gripper;

int      anguloActual   = 10;
int      anguloObjetivo = 10;
uint8_t  cmdAnterior    = 0xFF;       // fuerza la primera lectura
uint8_t  fallaAnterior  = 0xFF;       // fuerza la primera lectura
bool     servoActivo    = false;
bool     gripOK         = false;

unsigned long tCambioCmd     = 0;
unsigned long tCambioFalla   = 0;
unsigned long tUltimoPaso    = 0;
unsigned long tFinMovimiento = 0;
unsigned long tTelemetria    = 0;
unsigned long tPulso[2]      = {0, 0};
bool          pulsoActivo[2] = {false, false};

const uint8_t PIN_PULSO[2] = {PIN_DI05, PIN_DI06};

// Buffer de recepcion serie de tamano fijo. NO se emplea la clase String:
// en un microcontrolador con 2 kB de SRAM la fragmentacion del heap que
// provoca acaba colgando el programa tras algunas horas de operacion.
char    bufferSerie[24];
uint8_t idxBuffer = 0;


// ============================================================================
void setup() {
  // --- Entradas provenientes del IRC5 -------------------------------------
  // INPUT simple, NO INPUT_PULLUP: el nivel bajo de reposo lo garantizan las
  // pull-down externas de 10 kOhm. Activar la pull-up interna crearia un
  // divisor con ellas y el pin quedaria permanentemente en alto.
  pinMode(PIN_DO04, INPUT);
  pinMode(PIN_DO06, INPUT);

  // --- Salidas hacia el IRC5 ----------------------------------------------
  // Se fuerzan a reposo ANTES de cualquier otra operacion para evitar que un
  // transitorio de arranque genere un comando espurio hacia el robot.
  pinMode(PIN_DI04, OUTPUT);  digitalWrite(PIN_DI04, RELE_OFF);
  pinMode(PIN_DI05, OUTPUT);  digitalWrite(PIN_DI05, RELE_OFF);
  pinMode(PIN_DI06, OUTPUT);  digitalWrite(PIN_DI06, RELE_OFF);

  pinMode(PIN_LED, OUTPUT);   digitalWrite(PIN_LED, LOW);

  // --- Enlace con la interfaz de supervision ------------------------------
  Serial.begin(9600);
  Serial.println(F("EV,BOOT,Gripper Abel Etapa 4 v5.0"));

  // --- Servomotor ---------------------------------------------------------
  // attach() SIN argumentos de ancho de pulso: reproduce exactamente la
  // relacion angulo-pulso con la que se calibraron los 10 y los 100 grados.
  gripper.attach(PIN_SERVO);
  servoActivo = true;

  anguloActual   = angAbierto;
  anguloObjetivo = angAbierto;
  gripper.write(angAbierto);
  delay(500);

  tFinMovimiento = millis();
  gripOK = true;
  digitalWrite(PIN_DI04, RELE_ON);         // se arranca en posicion conocida
  Serial.println(F("EV,READY,Posicion inicial alcanzada"));
}


// ============================================================================
void loop() {
  leerEntradas();       // decodifica DO_04 y DO_06 con antirrebote
  moverServo();         // avanza el servo un paso si corresponde
  gestionarGripOK();    // actualiza DI_04 segun la posicion alcanzada
  gestionarDetach();    // libera el servo cuando esta abierto y en reposo
  gestionarPulsos();    // cierra los pulsos de DI_05 y DI_06 al vencer
  atenderSerie();       // procesa los comandos de la interfaz
  enviarTelemetria();   // publica la trama de estado periodica
}


// ---------------- Lectura de las dos entradas con antirrebote ----------------
void leerEntradas() {
  uint8_t cmd   = digitalRead(PIN_DO04);
  uint8_t falla = digitalRead(PIN_DO06);

  // --- Comando de gripper (DO_04) ------------------------------------------
  if (cmd != cmdAnterior) {
    if (millis() - tCambioCmd > T_DEBOUNCE) {
      cmdAnterior = cmd;
      tCambioCmd  = millis();
      aplicarComando(cmd);
    }
  } else {
    tCambioCmd = millis();
  }

  // --- Bit de falla (DO_06) ------------------------------------------------
  // El Arduino no actua sobre la falla: unicamente la retransmite.
  if (falla != fallaAnterior) {
    if (millis() - tCambioFalla > T_DEBOUNCE) {
      fallaAnterior = falla;
      tCambioFalla  = millis();
      Serial.print(F("EV,FALLA,"));
      Serial.println(falla);
    }
  } else {
    tCambioFalla = millis();
  }
}


// ---------------- Aplicacion del comando de gripper ----------------
void aplicarComando(uint8_t cmd) {
  if (cmd == 1) {
    anguloObjetivo = angCerrado;
    Serial.println(F("EV,CMD,CERRADO"));
  } else {
    anguloObjetivo = angAbierto;
    Serial.println(F("EV,CMD,ABIERTO"));
  }

  // El movimiento invalida la confirmacion: DI_04 cae hasta llegar a destino
  gripOK = false;
  digitalWrite(PIN_DI04, RELE_OFF);

  // Reactivar el servo si se encontraba liberado
  if (!servoActivo) {
    gripper.attach(PIN_SERVO);
    servoActivo = true;
  }
  digitalWrite(PIN_LED, HIGH);
}


// ---------------- Movimiento suave mediante pasos incrementales ----------------
void moverServo() {
  if (anguloActual == anguloObjetivo) return;
  if (millis() - tUltimoPaso < T_PASO) return;
  tUltimoPaso = millis();

  if (anguloActual < anguloObjetivo) {
    anguloActual = min(anguloActual + PASO_GRADOS, anguloObjetivo);
  } else {
    anguloActual = max(anguloActual - PASO_GRADOS, anguloObjetivo);
  }
  gripper.write(anguloActual);

  if (anguloActual == anguloObjetivo) {
    tFinMovimiento = millis();
    Serial.print(F("EV,POS,"));
    Serial.println(anguloActual);
  }
}


// ---------------- Gestion de la confirmacion hacia el IRC5 (DI_04) ----------------
void gestionarGripOK() {
  bool enPosicion = (anguloActual == anguloObjetivo);

  if (enPosicion && !gripOK) {
    gripOK = true;
    digitalWrite(PIN_DI04, RELE_ON);
    Serial.println(F("EV,ACK,GRIP_OK"));
  }
  if (!enPosicion && gripOK) {
    gripOK = false;
    digitalWrite(PIN_DI04, RELE_OFF);
  }
}


// ------- Liberacion del servo para evitar zumbido y sobrecalentamiento -------
void gestionarDetach() {
  if (!servoActivo) return;
  if (anguloActual != anguloObjetivo) return;

  // Se libera unicamente en posicion abierta, cuando no sujeta ninguna pieza.
  // DI_04 permanece activa: el gripper sigue donde el IRC5 lo ordeno.
  if (anguloObjetivo == angAbierto && millis() - tFinMovimiento > T_DETACH) {
    gripper.detach();
    servoActivo = false;
    digitalWrite(PIN_LED, LOW);
  }
}


// ---------------- Generacion de un pulso hacia una entrada del IRC5 ----------------
void lanzarPulso(uint8_t indice) {
  if (indice > 1) return;
  digitalWrite(PIN_PULSO[indice], RELE_ON);
  pulsoActivo[indice] = true;
  tPulso[indice]      = millis();
  Serial.print(F("EV,ACK,"));
  Serial.println(indice == 0 ? F("HOME") : F("START"));
}

void gestionarPulsos() {
  for (uint8_t i = 0; i < 2; i++) {
    if (pulsoActivo[i] && millis() - tPulso[i] > T_PULSO) {
      digitalWrite(PIN_PULSO[i], RELE_OFF);
      pulsoActivo[i] = false;
    }
  }
}


// ---------------- Recepcion de comandos por el puerto serie ----------------
void atenderSerie() {
  while (Serial.available()) {
    char c = Serial.read();

    if (c == '\n' || c == '\r') {
      bufferSerie[idxBuffer] = '\0';
      if (idxBuffer > 0) procesarTrama();
      idxBuffer = 0;
    }
    else if (idxBuffer < sizeof(bufferSerie) - 1) {
      bufferSerie[idxBuffer++] = toupper(c);
    }
    // Los caracteres que exceden el buffer se descartan en lugar de
    // desbordar la memoria y corromper variables adyacentes.
  }
}

void procesarTrama() {
  if (strcmp(bufferSerie, "CMD,HOME") == 0) {
    lanzarPulso(0);
  }
  else if (strcmp(bufferSerie, "CMD,START") == 0) {
    lanzarPulso(1);
  }
  else if (strcmp(bufferSerie, "CMD,PING") == 0) {
    tTelemetria = 0;                       // fuerza el envio inmediato
  }
  else if (strncmp(bufferSerie, "CMD,CAL,", 8) == 0) {
    // Formato: CMD,CAL,<n>,<angulo>   con n = 0 (abierto) o 1 (cerrado)
    char* pIndice = bufferSerie + 8;
    char* pComa   = strchr(pIndice, ',');
    if (pComa != NULL) {
      *pComa = '\0';
      int n   = atoi(pIndice);
      int ang = constrain(atoi(pComa + 1), 0, 180);
      if (n == 0)      angAbierto = ang;
      else if (n == 1) angCerrado = ang;
      else { Serial.println(F("ER,CAL_INDICE")); return; }

      Serial.print(F("EV,CAL,"));
      Serial.print(n);
      Serial.print(',');
      Serial.println(ang);
      cmdAnterior = 0xFF;                  // fuerza reevaluacion del comando
    }
  }
  else {
    Serial.println(F("ER,CMD_DESCONOCIDO"));
  }
}


// ---------------- Trama periodica de estado hacia la interfaz ----------------
void enviarTelemetria() {
  if (millis() - tTelemetria < T_TELEMETRIA) return;
  tTelemetria = millis();

  Serial.print(F("ST,"));
  Serial.print(fallaAnterior == 1 ? F("FALLA") : F("OK"));
  Serial.print(',');
  Serial.print(cmdAnterior == 1 ? F("CERRADO") : F("ABIERTO"));
  Serial.print(',');
  Serial.print(anguloActual);
  Serial.print(',');
  Serial.print(gripOK ? 1 : 0);
  Serial.print(',');
  Serial.println(millis());
}