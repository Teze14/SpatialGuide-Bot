import os
import sys
import cv2
import time
import pygame  # Para reproducir el audio
from gtts import gTTS  # Librería de voz (Google Text-to-Speech)

from google import genai
from google.genai import types
from google.genai.errors import APIError

# =================================================================
# ⚙️ CONFIGURACIÓN Y PARÁMETROS FIJOS
# =================================================================

# Directorio donde se guardará la imagen.
IMAGE_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "test")
IMAGE_FILENAME = "captured_image.jpg"
IMAGE_PATH = os.path.join(IMAGE_DIR, IMAGE_FILENAME)

# Configuración del modelo y la cámara
MODEL_NAME = "gemini-2.5-flash"
CAMERA_INDEX = 0

# Prompt fijo
FIXED_PROMPT = (
    "Describe detalladamente qué ves en la imagen y el entorno que está en la imagen, "
    "en menos de 50 palabras. Ten en cuenta que estás ayudando a ver y describir el "
    "entorno a una persona ciega, así que sé amigable."
)

# =================================================================
# 📢 FUNCIÓN DE SÍNTESIS DE VOZ (gTTS + PYGAME)
# =================================================================

def read_text_aloud(text_to_speak: str) -> None:
    """
    Convierte texto a audio usando Google TTS (gTTS) y lo reproduce
    con acento de México (tld='com.mx') para mayor naturalidad.
    """
    print("\n[TTS] 🗣️ Generando audio con Google TTS...")
    output_file = "temp_gtts_audio.mp3"

    try:
        # 1. Generar el objeto de audio con gTTS
        tts = gTTS(text=text_to_speak, lang='es', tld='com.mx')

        # 2. Guardar el archivo mp3
        tts.save(output_file)

        # 3. Reproducir con Pygame
        pygame.mixer.init()
        pygame.mixer.music.load(output_file)
        pygame.mixer.music.play()

        # Esperar a que termine de hablar
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.quit()

    except Exception as e:
        print(f"[ERROR TTS] No se pudo generar o reproducir el audio. Error: {e}")

    finally:
        # 4. Limpieza del archivo temporal
        if os.path.exists(output_file):
            try:
                os.remove(output_file)
            except Exception:
                pass  # Ignorar errores al borrar

# =================================================================
# 🧠 FUNCIÓN DE LLAMADA A LA API DE GEMINI
# =================================================================

def send_prompt_to_gemini_multimodal(prompt_text: str, image_path: str) -> str:
    """
    Envía texto y una imagen al modelo Gemini y devuelve el texto de respuesta.
    """
    if not os.path.exists(image_path):
        return f"Error: Archivo de imagen no encontrado en {image_path}"

    try:
        # El cliente busca automáticamente la variable GOOGLE_API_KEY
        client = genai.Client()
    except Exception as e:
        return (
            f"Error de configuración de API: {e}. "
            "Asegúrate de que GOOGLE_API_KEY esté exportada."
        )

    parts = []

    try:
        # 1. Procesar la imagen y construir la parte binaria
        with open(image_path, "rb") as f:
            image_data = f.read()
            mime_type = "image/jpeg"

        parts.append(
            types.Part.from_bytes(
                data=image_data,
                mime_type=mime_type,
            )
        )

        # 2. Construir la parte del texto
        parts.append(types.Part(text=prompt_text))

        # 3. Llamar a la API
        messages = [types.Content(role="user", parts=parts)]

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=messages,
        )
        return response.text

    except APIError as e:
        return f"Error de la API de Gemini: {e}"
    except Exception as e:
        return f"Error desconocido: {e}"

# =================================================================
# 📸 FUNCIÓN DE CAPTURA DE WEBCAM
# =================================================================

def capture_and_save_image(path: str) -> bool:
    """
    Captura una imagen de la webcam y la guarda en la ruta especificada.
    Devuelve True si salió bien, False en caso contrario.
    """
    print("\n[CAMARA] Iniciando captura...")
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"Error: No se pudo abrir la cámara en el índice {CAMERA_INDEX}.")
        return False

    time.sleep(1)  # Esperar un segundo para el ajuste automático

    ret, frame = cap.read()

    if ret:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        cv2.imwrite(path, frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
        print(f"[INFO] Imagen capturada y guardada en: {path}")
    else:
        print("Error: No se pudo leer el frame de la cámara.")

    cap.release()
    return ret

# =================================================================
# 🚀 FUNCIÓN PRINCIPAL REUTILIZABLE PARA EL MR INTEGRADO
# =================================================================

def describir_entorno_una_vez() -> None:
    """
    Captura una imagen, la manda a Gemini, imprime la descripción
    y la lee en voz alta. Esta es la función que luego llamará main_mr.py
    """
    # 0. Verificar la configuración de la API
    if not os.environ.get("GOOGLE_API_KEY"):
        print("\n--- 🛑 ERROR DE CONFIGURACIÓN ---")
        print("La clave API de Gemini no está configurada.")
        print("Por favor, ejecuta: export GOOGLE_API_KEY='TuClave'")
        return

    # 1. Capturar la imagen
    if not capture_and_save_image(IMAGE_PATH):
        print("[VISION] No se pudo capturar la imagen. Deteniendo función.")
        return

    # 2. Llamar a la API de Gemini
    print(f"[PROMPT] Enviando prompt fijo: '{FIXED_PROMPT}'")
    print("[CONSULTANDO] Esperando respuesta de Gemini...")

    response_text = send_prompt_to_gemini_multimodal(FIXED_PROMPT, IMAGE_PATH)

    # 3. Mostrar la respuesta
    print("\n=============================================")
    print("Descripción de Gemini:")
    print("=============================================")
    print(response_text)
    print("=============================================")

    # 4. Leer la respuesta en voz alta
    read_text_aloud(response_text)

# =================================================================
# 🧪 MODO PRUEBA (para usar este archivo solo)
# =================================================================

def main():
    """
    Modo prueba: permite describir múltiples imágenes seguidas.
    """
    execute_count = 0
    while True:
        if execute_count > 0:
            user_input = input("\n¿Deseas describir una nueva imagen? (SI/NO): ").strip().upper()
            if user_input != "SI":
                print("Proceso finalizado.")
                break

        describir_entorno_una_vez()
        execute_count += 1

if __name__ == "__main__":
    main()
