#!/usr/bin/env python3
# mando_serial_bt.py
# Lee el DualSense Edge desde /dev/input/js0 (BT o cable)
# y manda PWM por serial a dos ESP32.
#
# LEFT  <- joystick izquierdo vertical (eje 1 = LY)
# RIGHT <- joystick derecho  vertical (eje 5 = A5)

import struct
import sys
import serial
import time

# ================== CONFIG: PUERTOS SERIAL ==================
LEFT_PORT  = "/dev/ttyUSB0"   # Cambia si tu LEFT es otro (ej. /dev/ttyACM0)
RIGHT_PORT = "/dev/ttyUSB1"   # Cambia si tu RIGHT es otro

BAUDRATE = 115200

# ================== CONFIG: INTERFAZ JOYSTICK ===============
JS_DEV_PATH = "/dev/input/js0"   # joystick que ya probaste

# Formato de evento de /dev/input/js0
JS_EVENT_FORMAT = "IhBB"     # time, value, type, number
JS_EVENT_SIZE   = struct.calcsize(JS_EVENT_FORMAT)

JS_EVENT_BUTTON = 0x01
JS_EVENT_AXIS   = 0x02
JS_EVENT_INIT   = 0x80

# Ejes que nos interesan en la interfaz js:
AXIS_LEFT_Y_INDEX  = 1   # LY  (stick izquierdo vertical)
AXIS_RIGHT_Y_INDEX = 5   # A5  (stick derecho vertical)

MAX_PWM = 1000   # rango deseado -1000..1000

left_pwm  = 0
right_pwm = 0

def scale_axis_to_pwm(v):
    """
    v: valor entero del joystick en /dev/input/js0
       típicamente en rango [-32768, 32767], con 0 ~ centro.

    Queremos:
       arriba  -> +MAX_PWM
       centro  -> 0
       abajo   -> -MAX_PWM

    Si ves que está invertido, basta cambiar el signo.
    """
    # normalizar a [-1, 1] aprox
    norm = v / 32767.0
    # invertir signo si quieres que "arriba" sea +PWM:
    norm = -norm

    pwm = int(norm * MAX_PWM)

    # saturar
    if pwm >  MAX_PWM: pwm =  MAX_PWM
    if pwm < -MAX_PWM: pwm = -MAX_PWM

    # SIN zona muerta por software
    return pwm

# ================== ABRIR JOYSTICK ==========================
try:
    js = open(JS_DEV_PATH, "rb")
except FileNotFoundError:
    print(f"No se encontró {JS_DEV_PATH}. ¿Está el mando conectado por BT y reconocido?")
    sys.exit(1)

print(f"Usando joystick en {JS_DEV_PATH}")
print("LEFT  <- eje 1 (LY)")
print("RIGHT <- eje 5 (A5)")

# ================== ABRIR PUERTOS SERIAL =====================
try:
    ser_left = serial.Serial(LEFT_PORT, BAUDRATE, timeout=0.05)
    ser_right = serial.Serial(RIGHT_PORT, BAUDRATE, timeout=0.05)
except Exception as e:
    print("Error abriendo puertos serial:")
    print(e)
    js.close()
    sys.exit(1)

print(f"Conectado a LEFT  en {LEFT_PORT}")
print(f"Conectado a RIGHT en {RIGHT_PORT}")
print("Ctrl+C para salir.\n")

last_print = time.time()

try:
    while True:
        evbuf = js.read(JS_EVENT_SIZE)
        if not evbuf:
            break

        time_ms, value, etype, number = struct.unpack(JS_EVENT_FORMAT, evbuf)

        # Solo nos interesan eventos de eje
        if not (etype & JS_EVENT_AXIS):
            continue

        updated = False

        if number == AXIS_LEFT_Y_INDEX:
            left_pwm = scale_axis_to_pwm(value)
            updated = True

        elif number == AXIS_RIGHT_Y_INDEX:
            right_pwm = scale_axis_to_pwm(value)
            updated = True

        if updated:
            try:
                ser_left.write((str(left_pwm) + "\n").encode())
                ser_right.write((str(right_pwm) + "\n").encode())
            except Exception as e:
                print("\nError escribiendo por serial:", e)

            now = time.time()
            if now - last_print > 0.1:
                last_print = now
                print(f"L_PWM={left_pwm:5d}   R_PWM={right_pwm:5d}", end="\r")

except KeyboardInterrupt:
    print("\nSaliendo por Ctrl+C...")

finally:
    try:
        ser_left.close()
        ser_right.close()
    except:
        pass
    js.close()
    print("\nPuertos serial cerrados.")
