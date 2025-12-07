# Spatial-Guide-Bot

# Mini-Rover Guía Espacial Autónomo
Este proyecto implementa el software de control y lógica principal para un robot guía diseñado para operar en entornos interiores mapeados, proporcionando a los usuarios funcionalidades de navegación asistida por voz y descripción del entorno en tiempo real.

El robot utiliza el sistema de voz a texto (Whisper), la API multimodal de Gemini para la visión, y una lógica de control PID/IMU para la ejecución autónoma de rutas.

# Funcionalidades Clave
Comandos de Voz Natural: Acepta comandos de voz para iniciar la navegación a destinos predefinidos (Sanitarios, Torre, Rampa, Servicio Médico).

Visión Asistida por IA: Captura una imagen del entorno y utiliza el modelo Gemini 2.5 Flash para generar una descripción detallada que se reproduce por voz.

Navegación Autónoma: Ejecuta rutas preprogramadas (listas de pasos) con corrección de rumbo basada en la integración de datos del Giroscopio (MPU6050).

Interfaz Flexible: Soporta interacción por voz o por un menú de consola simple.

# Estructura del Proyecto

Archivo,Descripción Principal
main_mr.py,"Núcleo del Sistema. Bucle principal, manejo de la interfaz de usuario (voz/menú) y orquestación de las llamadas a rutas_mpu_mr.py y vision_voz_mr.py."
vision_voz_mr.py,"Módulo de Visión y Voz. Captura de imagen, interacción con la API de Gemini (multimodal) y síntesis de voz (Text-to-Speech) para describir el entorno."
rutas_mpu_mr.py,"Módulo de Navegación. Lógica de control autónomo, lectura e integración del giroscopio MPU6050 y ejecución de las secuencias de movimientos (recto con corrección o giro)."
run_mr.sh,Script de Inicio. Inicializa el entorno virtual de Python (venv) y ejecuta el script principal del robot.
mic_mr.py,"Módulo de entrada de voz (no incluido, pero requerido). Contiene la función escuchar_y_transcribir() para usar Whisper o similar."
[Código ESP32/Motor],Firmware de las placas de control (no incluido). Recibe comandos de PWM por serial (/dev/ttyUSBx) para el control físico de los motores.
