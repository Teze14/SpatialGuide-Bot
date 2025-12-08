# Spatial-Guide-Bot
<img width="585" height="339" alt="image" src="https://github.com/user-attachments/assets/e2988c9f-0316-418e-aba4-b17850892f41" />

# Mini-Rover Guía Espacial Autónomo
Este proyecto implementa el software de control y lógica principal para un robot guía diseñado para operar en entornos interiores mapeados, proporcionando a los usuarios funcionalidades de navegación asistida por voz y descripción del entorno en tiempo real.

El robot utiliza el sistema de voz a texto (Whisper), la API multimodal de Gemini para la visión, y una lógica de control P/IMU para la ejecución autónoma de rutas.

# Funcionalidades Clave
Comandos de Voz Natural: Acepta comandos de voz para iniciar la navegación a destinos predefinidos (Sanitarios, Torre, Rampa, Servicio Médico).

Visión Asistida por IA: Captura una imagen del entorno y utiliza el modelo Gemini 2.5 Flash para generar una descripción detallada que se reproduce por voz.

Navegación Autónoma: Ejecuta rutas preprogramadas (listas de pasos) con corrección de rumbo basada en la integración de datos del Giroscopio (MPU6050).

Interfaz Flexible: Soporta interacción por voz o por un menú de consola simple.

# Estructura del Proyecto

main_mr.py - Núcleo del Sistema. Bucle principal, manejo de la interfaz de usuario (voz/menú) y orquestación de las llamadas a rutas_mpu_mr.py y vision_voz_mr.py.

vision_voz_mr.py - Módulo de Visión y Voz. Captura de imagen, interacción con la API de Gemini (multimodal) y síntesis de voz (Text-to-Speech) para describir el entorno.

rutas_mpu_mr.py - Módulo de Navegación. Lógica de control autónomo, lectura e integración del giroscopio MPU6050 y ejecución de las secuencias de movimientos (recto con corrección o giro).

run_mr.sh - Script de Inicio. Inicializa el entorno virtual de Python (venv) y ejecuta el script principal del robot.

mic_mr.py - Módulo de entrada de voz (no incluido, pero requerido). Contiene la función escuchar_y_transcribir() para usar Whisper o similar.

serial_minirover.ino - Firmware de las placas de control . Recibe comandos de PWM por serial (/dev/ttyUSBx) para el control físico de los motores. 
Nota: invertir el sentido de los motores en un lado, de lo contrario, en vez de avanzar, girará. Los archivos .ino deben estar en sus carpetas correspondientes para evitar problemas con ArduinoIDE

# Instalación y Configuración

-Clonar el Repositorio:

Bash

git clone https://github.com/Teze14/SpatialGuide-Bot.git

cd Autonomous-Spatial-Guide-Bot

-Variables de Entorno: Es OBLIGATORIO configurar tu clave API de Google Gemini:

Bash

export GOOGLE_API_KEY='TU_CLAVE_AQUI'

-Configuración de Hardware:

Asegúrate de que la Webcam esté disponible en el índice 0.
Verifica que los puertos Serial para los controladores de motor ESP32 sean /dev/ttyUSB0 (Izquierda) y /dev/ttyUSB1 (Derecha).

Configura el bus I2C para el MPU6050 (el código asume bus 7 y dirección 0x68).

-Ejecución
Usa el script de inicio para asegurar que el entorno virtual esté activo:

Bash

./run_mr.sh

# Copyright

2025 Héctor Castillo Guerra

2025 Jesús Emiliano García Jiménez  

2025 Andrés Méndez Cortez  

2025 Nabor Sebastían Toro García
