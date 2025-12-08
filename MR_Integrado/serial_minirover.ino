// ====== Configuración ======
#define SIDE "LEFT"

// Motor A
const int A_AIN1 = 25;
const int A_AIN2 = 26;
const int A_PWM  = 27; // LEDC 0

// Motor B
const int B_AIN1 = 19;
const int B_AIN2 = 18;
const int B_PWM  = 23; // LEDC 1

// Encoders
const int ENC_A_A = 32;
const int ENC_A_B = 33;
const int ENC_B_A = 21;
const int ENC_B_B = 22;

volatile long cntA = 0;
volatile long cntB = 0;

const unsigned long DEBOUNCE_US = 200;
volatile unsigned long lastA = 0;
volatile unsigned long lastB = 0;

const int CH_A = 0;
const int CH_B = 1;

// Velocidad filtrada
const int WIN_SIZE = 10;
float filtA[WIN_SIZE]; int idxA = 0; float sumA = 0;
float filtB[WIN_SIZE]; int idxB = 0; float sumB = 0;

float speedA = 0, avgA = 0;
float speedB = 0, avgB = 0;

long lastCountA = 0;
long lastCountB = 0;

int pwmCommand = 0;   // valor recibido de -1023 a 1023

// ISR encoder A
void IRAM_ATTR isr_encA_A() {
  unsigned long now = micros();
  if (now - lastA < DEBOUNCE_US) return;
  lastA = now;
  if (digitalRead(ENC_A_B)) cntA++; else cntA--;
}
void IRAM_ATTR isr_encA_B() {
  unsigned long now = micros();
  if (now - lastA < DEBOUNCE_US) return;
  lastA = now;
  if (!digitalRead(ENC_A_A)) cntA++; else cntA--;
}

// ISR encoder B
void IRAM_ATTR isr_encB_A() {
  unsigned long now = micros();
  if (now - lastB < DEBOUNCE_US) return;
  lastB = now;
  if (digitalRead(ENC_B_B)) cntB++; else cntB--;
}
void IRAM_ATTR isr_encB_B() {
  unsigned long now = micros();
  if (now - lastB < DEBOUNCE_US) return;
  lastB = now;
  if (!digitalRead(ENC_B_A)) cntB++; else cntB--;
}

// ===== Mover motor =====
void setMotor(int AIN1, int AIN2, int channel, int val) {
  if (val > 0) {
    digitalWrite(AIN2, LOW);
    digitalWrite(AIN1, HIGH);
    ledcWrite(channel, val);
  } else if (val < 0) {
    digitalWrite(AIN1, HIGH);
    digitalWrite(AIN2, LOW);
    ledcWrite(channel, -val);
  } else {
    digitalWrite(AIN1, LOW);
    digitalWrite(AIN2, LOW);
    ledcWrite(channel, 0);
  }
}

// ===== SETUP =====
void setup() {
  Serial.begin(115200);
  delay(100);

  pinMode(A_AIN1, OUTPUT);
  pinMode(A_AIN2, OUTPUT);
  pinMode(B_AIN1, OUTPUT);
  pinMode(B_AIN2, OUTPUT);

  ledcSetup(CH_A, 20000, 10);
  ledcAttachPin(A_PWM, CH_A);

  ledcSetup(CH_B, 20000, 10);
  ledcAttachPin(B_PWM, CH_B);

  pinMode(ENC_A_A, INPUT_PULLUP);
  pinMode(ENC_A_B, INPUT_PULLUP);
  pinMode(ENC_B_A, INPUT_PULLUP);
  pinMode(ENC_B_B, INPUT_PULLUP);

  attachInterrupt(digitalPinToInterrupt(ENC_A_A), isr_encA_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_A_B), isr_encA_B, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B_A), isr_encB_A, CHANGE);
  attachInterrupt(digitalPinToInterrupt(ENC_B_B), isr_encB_B, CHANGE);

  Serial.println("PWM DIRECTO READY");
}

// ===== LOOP =====
unsigned long lastPID = 0;
const unsigned long PERIOD = 20;

void loop() {

  // ----- Lectura de PWM por serial -----
  if (Serial.available()) {
    String s = Serial.readStringUntil('\n');
    pwmCommand = s.toInt();
    pwmCommand = constrain(pwmCommand, -1023, 1023);
  }

  // ----- Cada 20 ms calcula velocidad -----
  if (millis() - lastPID >= PERIOD) {
    lastPID = millis();

    // ---- MOTOR A ----
    long pulsesA = cntA - lastCountA;
    lastCountA = cntA;

    speedA = pulsesA * 0.0865;

    sumA -= filtA[idxA];
    filtA[idxA] = speedA;
    sumA += speedA;
    idxA = (idxA + 1) % WIN_SIZE;
    avgA = sumA / WIN_SIZE;

    // ---- MOTOR B ----
    long pulsesB = cntB - lastCountB;
    lastCountB = cntB;

    speedB = pulsesB * 0.0865;

    sumB -= filtB[idxB];
    filtB[idxB] = speedB;
    sumB += speedB;
    idxB = (idxB + 1) % WIN_SIZE;
    avgB = sumB / WIN_SIZE;

    // ----- Mover motores directamente -----
    setMotor(A_AIN1, A_AIN2, CH_A, pwmCommand);
    setMotor(B_AIN1, B_AIN2, CH_B, pwmCommand);

    // ----- Print -----
    Serial.print("A pwm:"); Serial.print(pwmCommand);
    Serial.print(" vel:"); Serial.print(avgA);
    Serial.print("   |   B pwm:"); Serial.print(pwmCommand);
    Serial.print(" vel:"); Serial.println(avgB);
  }
}
