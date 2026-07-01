"""Drobne narzedzia: powtarzalnosc (seed), sprzatanie pamieci GPU, info o sprzecie."""

import gc
import os
import random

import numpy as np


def set_seed(seed=42):
    """Ustawia ziarna RNG (powtarzalnosc wynikow)."""
    random.seed(seed)
    np.random.seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    try:
        import torch
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except ImportError:
        pass


def free_memory(*objs):
    """Zwalnia pamiec GPU/RAM po duzych obiektach.

    Uwaga: 'del' kasuje tylko lokalne referencje - najpierw `del model, tokenizer`,
    potem `free_memory()`.
    """
    for obj in objs:
        try:
            del obj
        except Exception:
            pass
    gc.collect()
    try:
        import torch
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            torch.cuda.synchronize()
    except ImportError:
        pass


def device_info():
    """Zwraca info o dostepnym urzadzeniu (GPU vs CPU)."""
    try:
        import torch
        if torch.cuda.is_available():
            name = torch.cuda.get_device_name(0)
            total = torch.cuda.get_device_properties(0).total_memory / 1024**3
            return f"GPU: {name} ({total:.1f} GB VRAM)"
        return "Brak GPU - liczymy na CPU (LLM bedzie wolny)."
    except ImportError:
        return "torch niezainstalowany."
