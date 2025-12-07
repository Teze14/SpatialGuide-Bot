'''Copyright 2025 Jesús Emiliano García Jiménez
             2025 Héctor Castillo Guerra
             2025 Andrés Méndez Cortez
             2025 Nabor Sebastían Toro García

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.'''

import subprocess
import time
import signal
import whisper

FILENAME = "grabacion_6s.wav"
DURATION = 6  # segundos

def grabar_6s_con_parec():
    print(f" Grabando {DURATION} segundos con parec... habla cerca del micrófono.")

    cmd = ["parec", "--file-format=wav", FILENAME]
    proc = subprocess.Popen(cmd)

    time.sleep(DURATION)

    proc.send_signal(signal.SIGINT)
    proc.wait()

    print(f" Archivo guardado: {FILENAME}")


print("=== Mini-Rover · Módulo de micrófono (Whisper) ===")
print("[MIC] Cargando modelo Whisper ('base')...")
model = whisper.load_model("base")
print("[MIC] Modelo Whisper cargado.\n")


def escuchar_y_transcribir() -> str:
    """
    Graba 6s de audio y devuelve el texto reconocido (puede ser cadena vacía).
    NO pide ENTER: eso ahora lo maneja main_mr.py.
    """
    grabar_6s_con_parec()

    print("[MIC] Transcribiendo con Whisper...")
    result = model.transcribe(FILENAME, language="es", fp16=False)
    texto = result.get("text", "").strip()

    print("[MIC] Texto reconocido:")
    print(f"» {texto if texto else '[vacío]'}\n")

    return texto
