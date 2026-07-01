"""Konfiguracja projektu: definicje kolumn, typy, stałe, ścieżki.

Cała wiedza domenowa o zbiorze (które kolumny są czym, co jest wyciekiem)
mieszka tutaj, żeby reszta kodu była czysta.
"""
from __future__ import annotations

from pathlib import Path

# --- ścieżki ---
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RESULTS_DIR = ROOT / "results"
LOCAL_CSV = DATA_DIR / "cirrhosis.csv"  # opcjonalny lokalny zbiór (wariant z C/CL/D)

UCI_DATASET_ID = 878

# --- reprodukowalność ---
RANDOM_STATE = 42

# --- target ---
TARGET = "Status"
# Etykiety w wersji surowej (CSV) to napisy; w wersji ucimlrepo id=878 bywają 0/1/2.
CLASS_LABELS = ["C", "CL", "D"]
# Mapowanie liczbowe -> napis (gdy zbiór przyjdzie zakodowany jak na stronie UCI).
NUMERIC_TO_LABEL = {0: "D", 1: "C", 2: "CL"}

# --- kolumny do usunięcia ---
# ID  -> czysty identyfikator, brak wartości predykcyjnej
# N_Days -> czas od rejestracji do śmierci/przeszczepu/końca badania:
#           BEZPOŚREDNI WYCIEK targetu. Nie jest na liście 17 cech w treści zadania.
LEAKAGE_COLS = ["ID", "N_Days"]

# --- 17 cech (zgodnie z treścią zadania) ---
# Kategoryczne (7). Uwaga: Stage (1-4) i Edema (N<S<Y) są porządkowe — można je
# potraktować ordinalnie albo one-hot; decyzję opisz w raporcie.
CATEGORICAL_FEATURES = [
    "Drug",          # D-penicillamine / placebo; NA dla 106 pacjentów spoza trialu
    "Sex",
    "Ascites",
    "Hepatomegaly",
    "Spiders",
    "Edema",         # N / S / Y  (porządkowa)
    "Stage",         # 1 / 2 / 3 / 4  (porządkowa)
]

# Liczbowe (10). UWAGA: 'Tryglicerides' z błędem ortograficznym — tak jest w oryginale.
NUMERIC_FEATURES = [
    "Age",           # w DNIACH -> w EDA przelicz na lata (/365.25)
    "Bilirubin",     # mocno skośna (klinicznie istotna)
    "Cholesterol",
    "Albumin",
    "Copper",
    "Alk_Phos",
    "SGOT",
    "Tryglicerides",
    "Platelets",
    "Prothrombin",
]

ALL_FEATURES = CATEGORICAL_FEATURES + NUMERIC_FEATURES

# Kolumny, które potrafią mieć dużo braków (głównie 106 pacjentów spoza trialu).
KNOWN_NA_HEAVY = ["Drug", "Cholesterol", "Copper", "Alk_Phos", "SGOT", "Tryglicerides", "Platelets"]
