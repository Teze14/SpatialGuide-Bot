import subprocess
from mic_mr import escuchar_y_transcribir


def ejecutar_ruta_destino(destino: str) -> None:
    """
    Lanza la ruta autónoma usando rutas_mpu_mr.py con el Python del sistema.
    """
    print(f"[CORE] Comando: IR A {destino.upper()}")
    print("[CORE] Llamando rutas_mpu_mr.ejecutar_ruta_mpu desde /usr/bin/python3...")
    subprocess.run(
        ["/usr/bin/python3", "/home/jesusgj/MR_Integrado/rutas_mpu_mr.py", destino],
        check=False,
    )


def describir_entorno_una_vez() -> None:
    """
    Lanza la función describir_entorno_una_vez() de vision_voz_mr.py
    """
    print("[CORE] Comando: DESCRIBIR ENTORNO")
    subprocess.run(
        [
            "/usr/bin/python3",
            "-c",
            "from vision_voz_mr import describir_entorno_una_vez; describir_entorno_una_vez()",
        ],
        check=False,
    )


def detectar_destino(texto: str) -> str | None:
    """
    Mapea texto de Whisper a un destino lógico.
    Implementados:
      - 'sanitarios' / 'baños'
      - 'torre'
      - 'servicio médico' / 'meditec'
      - 'rampa'
    """
    t = texto.lower()

    # Sanitarios / baños
    if "sanitario" in t or "sanitarios" in t or "baño" in t or "baños" in t:
        return "sanitarios"

    # Torre
    if "torre" in t:
        return "torre"

    # Servicio médico / Meditec / salud
    if (
        "meditec" in t
        or "meditek" in t
        or "servicio medico" in t
        or "servicio médico" in t
        or "servicios medicos" in t
        or "servicios médicos" in t
        or "servicios de salud" in t
        or "asistencia medica" in t
        or "asistencia médica" in t
        or "doctor" in t
        or "doctora" in t
        or "medico" in t
        or "médico" in t
    ):
        return "servicio_medico"

    # Rampa
    if "rampa" in t:
        return "rampa"

    # Futuro: laboratorios, elevadores...
    return None


def loop_principal() -> None:
    print("=== MINI-ROVER INTEGRADO (voz + rutas + visión) ===")
    print("Ejemplos de cosas que puedes decir por voz:")
    print("  - 'Quiero ir a los sanitarios'")
    print("  - 'Llévame a los baños'")
    print("  - 'Llévame a la torre'")
    print("  - 'Llévame al servicio médico'")
    print("  - 'Llévame a la rampa'")
    print("  - 'describe el entorno', 'qué ves', 'describe lo que ves'")
    print("También puedes usar el menú por teclado.")
    print("=============================================\n")

    while True:
        print("\n[MIC] Habla cuando estés listo.")

        opcion = input(
            "[MIC] Pulsa ENTER para grabar 6s...\n"
            "      O pulsa 1-Sanitarios 2-Torre 3-MediTec 4-Rampa 5-Describir el entorno: "
        ).strip()

        # =====================
        # MODO MENÚ POR TECLAS
        # =====================
        if opcion != "":
            if opcion == "1":
                ejecutar_ruta_destino("sanitarios")
                continue
            elif opcion == "2":
                ejecutar_ruta_destino("torre")
                continue
            elif opcion == "3":
                ejecutar_ruta_destino("servicio_medico")
                continue
            elif opcion == "4":
                ejecutar_ruta_destino("rampa")
                continue
            elif opcion == "5":
                describir_entorno_una_vez()
                continue
            else:
                print("[CORE] Opción de menú no válida. Usa 1, 2, 3, 4 o 5, o ENTER para voz.")
                continue

        # =====================
        # MODO VOZ (WHISPER)
        # =====================
        texto = escuchar_y_transcribir()
        if not texto:
            print("[MIC] No se reconoció nada (texto vacío).")
            continue

        t = texto.lower()
        print(f"[DEBUG] Texto reconocido: {t!r}")

        # 1) Intentar detectar destino
        destino = detectar_destino(t)
        if destino is not None:
            ejecutar_ruta_destino(destino)
            continue

        # 2) Visión + descripción del entorno
        if (
            "describe" in t
            or "que ves" in t
            or "qué ves" in t
            or "entorno" in t
            or "alrededor" in t
        ):
            describir_entorno_una_vez()
            continue

        # 3) Terminar
        if "termina" in t or "apagate" in t or "apágate" in t or "salir" in t:
            print("[CORE] Comando: TERMINAR")
            break

        # 4) Comando no reconocido
        print("[CORE] Comando no reconocido.")
        print("     Intenta algo como: 'Quiero ir a los sanitarios',")
        print("     'Llévame a la torre',")
        print("     'Llévame al servicio médico',")
        print("     'Llévame a la rampa',")
        print("     o 'describe el entorno'.")

    print("\n[CORE] Loop principal terminado.")


if __name__ == "__main__":
    loop_principal()
