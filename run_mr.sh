#!/bin/bash

# 1) Activar el entorno virtual donde está Whisper
cd /home/usr/mr_voz
source venv/bin/activate

# 2) Ir a la carpeta del Mini-Rover integrado
cd /home/usr/MR_Integrado

# 3) Ejecutar el main con ese Python del venv
python main_mr.py
