import serial
import time
import smbus2
import sys

# ==========================================
# 1. CLASE DEL SENSOR (MPU6050, SOLO GYRO X)
# ==========================================

class MPU_Gyro_X_Only:
    def __init__(self, bus_num=7, address=0x68):
        self.bus = smbus2.SMBus(bus_num)
        self.address = address
        self.angle_x = 0.0
        self.offset_x = 0.0
        self.prev_time = time.time()
        self.DEADZONE = 0.8  # Ajusta si hay drift estando quieto

        try:
            # Despertar el MPU6050 (quitar sleep)
            self.bus.write_byte_data(self.address, 0x6B, 0)
        except Exception as e:
            print(f"Error MPU: {e}")
            sys.exit(1)

    def read_gyro_x(self):
        try:
            high = self.bus.read_byte_data(self.address, 0x43)
            low = self.bus.read_byte_data(self.address, 0x44)
            val = (high << 8) | low
            if val > 32768:
                val -= 65536
            # Escala típica MPU6050 → 131 LSB/(°/s)
            return val / 131.0  # °/s
        except Exception:
            return 0.0

    def calibrate(self):
        print(">>> CALIBRANDO GIROSCOPIO (NO MOVER EL MR)...")
        time.sleep(1)
        suma = 0.0
        for _ in range(100):
            suma += self.read_gyro_x()
            time.sleep(0.01)
        self.offset_x = suma / 100.0
        self.prev_time = time.time()
        print(f"Calibrado. Offset X: {self.offset_x:.2f} °/s")

    def update(self):
        """
        Integra gyro X para obtener ángulo en grados.
        """
        now = time.time()
        dt = now - self.prev_time
        self.prev_time = now

        raw = self.read_gyro_x()
        corrected = raw - self.offset_x

        if abs(corrected) < self.DEADZONE:
            corrected = 0.0

        self.angle_x += corrected * dt
        return self.angle_x


# ==========================================
# 2. CONFIGURACIÓN SERIAL Y CONTROL
# ==========================================

PUERTO_LEFT = "/dev/ttyUSB0"   # Lado IZQUIERDO
PUERTO_RIGHT = "/dev/ttyUSB1"  # Lado DERECHO
BAUDRATE = 115200

# Control proporcional para mantener recta la ruta
KP = 15.0  # Si oscila mucho, bájalo; si corrige lento, súbelo.


# ==========================================
# 3. DEFINICIÓN DE RUTAS (LISTAS DE PASOS)
# Formato: [PWM_Base_L, PWM_Base_R, Tiempo_Max, ANGULO_OBJETIVO]
#   ANGULO_OBJETIVO:
#     0   -> RECTO con corrección (PID sobre ángulo)
#     !=0 -> GIRO hasta alcanzar ese ángulo relativo (o agotar tiempo_max)
# ==========================================

# Ruta SANITARIOS: la que ya probaron con IMU
SANITARIOS = [
    [1000, 1000, 19.3, 0],     # Recto
    [-1000, 1000, 6.0, 90],    # Giro Izquierda 90
    [1000, 1000, 67.46, 0],    # Recto largo
    [-1000, 1000, 6.0, 90],    # Giro Izquierda 90
    [1000, 1000, 19.3, 0],     # Recto corto
    [-1000, 1000, 10.0, 180],  # U de 180°

    # Regreso
    [1000, 1000, 19.3, 0],
    [1000, -1000, 6.0, -90],   # Giro Derecha 90
    [1000, 1000, 67.46, 0],
    [1000, -1000, 6.0, -90],   # Giro Derecha 90
    [1000, 1000, 19.3, 0],
    [-1000, 1000, 10.0, 180]   # Giro final 180
]

# Ruta TORRE (distancias ya convertidas):
#   Tramo 1: 30.4 m → 30.4 * 7 ≈ 212.8 s
#   Tramo 2:  9.5 m →  9.5 * 7 = 66.5 s
TORRE = [
    [1000, 1000, 212.8, 0],   # Tramo largo recto
    [1000, -1000, 6.0, -90],  # Giro derecha 90°
    [1000, 1000, 66.5, 0],    # Tramo corto recto (llegada a torre)

    [-1000, 1000, 10.0, 180], # Giro 180° en la torre
    [1000, 1000, 66.5, 0],    # Tramo corto de regreso
    [-1000, 1000, 6.0, 90],   # Giro izquierda 90°
    [1000, 1000, 212.8, 0],   # Tramo largo de regreso
    [-1000, 1000, 10.0, 180], # Giro final 180°
]

# Ruta SERVICIO MÉDICO:
#  40 m recto → giro izquierda → 6 m recto → giro y regreso
#  Distancias convertidas con 1 m ≈ 7 s:
#    40 m → 280 s
#     6 m →  42 s
SERVICIO_MEDICO = [
    # Ida
    [1000, 1000, 280.0, 0],    # 40 m recto
    [-1000, 1000, 6.0, 90],    # Giro izquierda 90°
    [1000, 1000, 42.0, 0],     # 6 m recto (llegada a servicio médico)

    # Giro ahí y regreso
    [-1000, 1000, 10.0, 180],  # Giro 180° en servicio médico
    [1000, 1000, 42.0, 0],     # 6 m de regreso
    [1000, -1000, 6.0, -90],   # Giro derecha 90°
    [1000, 1000, 280.0, 0],    # 40 m de regreso
    [-1000, 1000, 10.0, 180],  # Giro final 180° (misma orientación que al inicio)
]

# Ruta RAMPA:
#  40 m recto → giro izquierda → 2 m recto → giro y regreso
#  Distancias convertidas con 1 m ≈ 7 s:
#    40 m → 280 s
#     2 m →  14 s
RAMPA = [
    # Ida
    [1000, 1000, 280.0, 0],    # 40 m recto
    [-1000, 1000, 6.0, 90],    # Giro izquierda 90°
    [1000, 1000, 14.0, 0],     # 2 m recto (llegada a la rampa)

    # Giro ahí y regreso
    [-1000, 1000, 10.0, 180],  # Giro 180° en la rampa
    [1000, 1000, 14.0, 0],     # 2 m de regreso
    [1000, -1000, 6.0, -90],   # Giro derecha 90°
    [1000, 1000, 280.0, 0],    # 40 m de regreso
    [-1000, 1000, 10.0, 180],  # Giro final 180°
]

RUTAS = {
    "SANITARIOS": SANITARIOS,
    "BANOS": SANITARIOS,
    "BAÑOS": SANITARIOS,
    "TORRE": TORRE,
    "SERVICIO_MEDICO": SERVICIO_MEDICO,
    "SERVICIO MÉDICO": SERVICIO_MEDICO,
    "RAMPA": RAMPA,
}


# ==========================================
# 4. EJECUCIÓN GENÉRICA DE UNA RUTA CON IMU
# ==========================================

def ejecutar_ruta_mpu(nombre_ruta: str) -> None:
    nombre_upper = nombre_ruta.upper()
    secuencia = RUTAS.get(nombre_upper)

    if secuencia is None:
        print(f"[RUTAS_MPU] Ruta '{nombre_ruta}' no definida.")
        return

    print(f"\n=== INICIANDO RUTA '{nombre_upper}' CON CORRECCIÓN DE GIROSCOPIO ===\n")

    # 1) Inicializar IMU
    mpu = MPU_Gyro_X_Only(bus_num=7)
    mpu.calibrate()

    # 2) Inicializar serial
    try:
        esp_left  = serial.Serial(port=PUERTO_LEFT,  baudrate=BAUDRATE, timeout=0.1)
        esp_right = serial.Serial(port=PUERTO_RIGHT, baudrate=BAUDRATE, timeout=0.1)
    except serial.SerialException as e:
        print(f"Error puertos: {e}")
        return

    try:
        for i, paso in enumerate(secuencia):
            pwm_base_L = paso[0]
            pwm_base_R = paso[1]
            tiempo_max = paso[2]
            target_delta_angle = paso[3]

            # Para cada paso, tomamos el ángulo actual como "cero"
            start_angle = mpu.angle_x

            es_recta = (target_delta_angle == 0)
            modo_str = "RECTA (Corrigiendo)" if es_recta else f"GIRO ({target_delta_angle}°)"
            print(f"\n>> PASO {i+1}: {modo_str} | PWM_Base: L={pwm_base_L}, R={pwm_base_R} | t_max={tiempo_max:.1f}s")

            start_time = time.time()

            while (time.time() - start_time) < tiempo_max:
                # 1. Actualizar sensor
                current_total_angle = mpu.update()
                # Ángulo relativo desde que empezó este paso
                angle_recorrido = current_total_angle - start_angle

                final_L = pwm_base_L
                final_R = pwm_base_R

                if es_recta:
                    # MODO RECTA: queremos angle_recorrido ≈ 0
                    error = angle_recorrido  # objetivo = 0°
                    correccion = error * KP

                    # Aplica corrección opuesta en cada motor
                    # Orden: IZQUIERDA (L), DERECHA (R)
                    final_L = int(pwm_base_L + correccion)
                    final_R = int(pwm_base_R - correccion)
                    # Si ves que corrige al revés, invierte los signos arriba.

                else:
                    # MODO GIRO: parar cuando lleguemos al ángulo requerido
                    if abs(angle_recorrido) >= abs(target_delta_angle):
                        print(f"   -> Giro completado a {angle_recorrido:.1f}° (target {target_delta_angle}°)")
                        break
                    print(f"   -> Girando... Actual: {angle_recorrido:.1f}° / Meta: {target_delta_angle}°", end="\r")

                # 2. Saturar PWM (asumo rango -1023 a 1023)
                final_L = max(min(final_L, 1023), -1023)
                final_R = max(min(final_R, 1023), -1023)

                # 3. Enviar a motores (orden: IZQUIERDA, DERECHA)
                esp_left.write((str(final_L) + "\n").encode("utf-8"))
                esp_right.write((str(final_R) + "\n").encode("utf-8"))

                time.sleep(0.05)  # ~20 Hz

        print("\n=== RUTA TERMINADA ===")

    except KeyboardInterrupt:
        print("\nSTOP DE EMERGENCIA (Ctrl+C)")

    finally:
        try:
            esp_left.write("0\n".encode("utf-8"))
            esp_right.write("0\n".encode("utf-8"))
        except Exception:
            pass
        try:
            esp_left.close()
            esp_right.close()
        except Exception:
            pass
        print("[RUTAS_MPU] Motores detenidos y puertos cerrados.")


# ==========================================
# 5. MODO CLI (para ser llamado desde main_mr.py)
# ==========================================

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        destino_cli = sys.argv[1]
    else:
        destino_cli = "SANITARIOS"

    print(f"[RUTAS_MPU] Ejecutando ruta desde CLI: {destino_cli}")
    ejecutar_ruta_mpu(destino_cli)
