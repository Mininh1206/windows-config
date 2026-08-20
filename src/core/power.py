"""
power.py — Módulo de gestión energética y prevención de suspensión (Keep-Awake).
Mantiene el equipo despierto y la pantalla encendida durante la ejecución del instalador.
"""

import sys
from contextlib import contextmanager
from src.core.logger import get_logger

logger = get_logger()

# Constantes de la API de Windows para SetThreadExecutionState
ES_CONTINUOUS       = 0x80000000
ES_SYSTEM_REQUIRED  = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002
ES_AWAYMODE_REQUIRED = 0x00000040

@contextmanager
def keep_awake():
    """
    Context manager que previene la suspensión del sistema y el apagado de la pantalla
    durante la ejecución de tareas prolongadas en Windows.
    Restaura el estado original del sistema al salir.
    """
    is_windows = (sys.platform == "win32")
    if not is_windows:
        yield
        return

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # Solicitar que el sistema permanezca encendido y la pantalla activa
        res = kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED)
        if res != 0:
            logger.log("Modo Keep-Awake activado: la pantalla y el sistema no se suspenderán durante la instalación.", "DEBUG")
    except Exception as e:
        logger.log(f"Aviso al activar modo Keep-Awake: {e}", "DEBUG")

    try:
        yield
    finally:
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            # Restaurar el comportamiento estándar de energía
            kernel32.SetThreadExecutionState(ES_CONTINUOUS)
            logger.log("Modo Keep-Awake desactivado: restaurado comportamiento energético estándar.", "DEBUG")
        except Exception:
            pass
