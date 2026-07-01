#!/usr/bin/env python3
"""CLI do uruchomienia pipeline'u Listy 5 (PolEmo2.0-IN).

Przyklady:
    python run.py --task all
    python run.py --task all --max-samples 200
    python run.py --task 4 --llm Qwen/Qwen2.5-3B-Instruct --use-4bit

Wyniki w outputs/: wyniki.csv, wyniki.md, macierze pomylek (PNG).
"""

import argparse
import os

# backend bez okienka - ustawiamy przed importem pyplot
import matplotlib
matplotlib.use("Agg")

from src import data, encoder, decoder, metrics
from src.config import (
    SEED, MAX_SAMPLES, OUTPUT_DIR,
    DEFAULT_ENCODER, ENCODER_MODELS,
    DEFAULT_LLM, LLM_MODELS, USE_4BIT,
    LLM_MAX_NEW_TOKENS, LLM_JSON_MAX_NEW_TOKENS,
)
from src.utils import set_seed, free_memory, device_info
from src.decoder import PROMPTS


def parse_args():
    p = argparse.ArgumentParser(description="Lista 5 - klasyfikacja wydzwieku PolEmo2.0-IN")
    p.add_argument("--task", default="all",
                   choices=["1", "2", "3", "4", "5", "all"],
                   help="ktore zadanie odpalic (domyslnie: all)")
    p.add_argument("--max-samples", type=int, default=MAX_SAMPLES,
                   help="ile probek uzyc (domyslnie z config)")
    p.add_argument("--encoder", default=DEFAULT_ENCODER,
                   help="model encoder do zadania 2")
    p.add_argument("--llm", default=DEFAULT_LLM,
                   help="model LLM do zadania 4/5")
    p.add_argument("--use-4bit", action="store_true", default=USE_4BIT,
                   help="kwantyzacja 4-bit dla LLM (wymaga bitsandbytes)")
    return p.parse_args()


def main():
    args = parse_args()
    set_seed(SEED)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("=" * 70)
    print(device_info())
    print(f"Zadanie: {args.task} | max_samples: {args.max_samples} | 4bit: {args.use_4bit}")
    print("=" * 70)

    run_all = args.task == "all"
    rows = []  # zbiorcza tabela wynikow

    # ZADANIE 1: zbior danych + statystyki
    print("\n[1] Laduje PolEmo2.0-IN (split test)...")
    ds = data.load_polemo_test()
    raw = data.describe_raw(ds)
    print(f"    Surowo: {raw['n_total']} probek | kolumny: {raw['columns']}")
    print(f"    Rozklad klas (surowy): {raw['class_counts_raw']}")

    texts, labels, meta = data.prepare_dataset(ds, max_samples=args.max_samples)
    print(f"    Po wyrzuceniu ambiguous: {meta['n_used']} probek "
          f"(wyrzucono {meta['n_ambiguous_dropped']})")
    print(f"    Rozklad klas (uzyty): {meta['class_counts_used']}")

    tl = data.text_length_stats(texts)
    print(f"    Dlugosc tekstu [znaki]: srednia={tl['chars']['mean']:.0f}, "
          f"mediana={tl['chars']['median']:.0f}, max={tl['chars']['max']}")
    print(f"    Dlugosc tekstu [slowa]: srednia={tl['words']['mean']:.0f}, "
          f"mediana={tl['words']['median']:.0f}, max={tl['words']['max']}")

    if args.task == "1":
        print("\nGotowe (tylko zadanie 1).")
        return

    # ZADANIE 2: encoder baseline (HerBERT)
    if run_all or args.task in ("2", "3"):
        print(f"\n[2] Encoder baseline: {args.encoder}")
        pipe, label_map = encoder.load_encoder(args.encoder)
        pred = encoder.classify_encoder(pipe, label_map, texts)
        m = metrics.compute_metrics(labels, pred)
        metrics.print_metrics(args.encoder, m)
        metrics.plot_confusion(labels, pred, args.encoder, save=True, show=False)
        rows.append({"model": args.encoder, "typ": "encoder",
                     "accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                     "f1_weighted": m["f1_weighted"]})
        free_memory(pipe)

    # ZADANIE 3: encoder - eksploracja (temperatura nie dotyczy enkodera)
    if run_all or args.task == "3":
        print("\n[3] Encoder - eksploracja (inne modele)")
        print("    (Temperatura nie ma zastosowania - encoder jest deterministyczny.)")
        for name in ENCODER_MODELS:
            if any(r["model"] == name for r in rows):
                continue  # juz policzony
            print(f"    -> {name}")
            try:
                pipe, label_map = encoder.load_encoder(name)
                pred = encoder.classify_encoder(pipe, label_map, texts)
                m = metrics.compute_metrics(labels, pred)
                metrics.print_metrics(name, m)
                metrics.plot_confusion(labels, pred, name, save=True, show=False)
                rows.append({"model": name, "typ": "encoder",
                             "accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                             "f1_weighted": m["f1_weighted"]})
                free_memory(pipe)
            except Exception as e:
                print(f"       BLAD przy {name}: {e}")

    # ZADANIE 4: decoder baseline (Qwen LLM)
    if run_all or args.task in ("4", "5"):
        print(f"\n[4] Decoder baseline: {args.llm} (prompt en_basic, temp=0.0)")
        model, tok = decoder.load_llm(args.llm, use_4bit=args.use_4bit)
        pred, n_unp = decoder.classify_llm(model, tok, texts,
                                           PROMPTS["en_basic"], temperature=0.0)
        m = metrics.compute_metrics(labels, pred, n_unparsed=n_unp)
        metrics.print_metrics(f"{args.llm} (en_basic, t=0.0)", m)
        metrics.plot_confusion(labels, pred, f"{args.llm}_en_basic", save=True, show=False)
        rows.append({"model": f"{args.llm} (en_basic, t=0.0)", "typ": "decoder",
                     "accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                     "f1_weighted": m["f1_weighted"]})

        # ZADANIE 5: decoder - eksploracja (prompt + temperatura)
        if run_all or args.task == "5":
            print("\n[5a] Decoder - eksploracja PROMPTOW (temp=0.0)")
            for prompt_name in ["en_basic", "pl_fewshot", "json"]:
                if prompt_name == "en_basic":
                    continue  # juz w baseline
                json_mode = prompt_name == "json"
                mnt = LLM_JSON_MAX_NEW_TOKENS if json_mode else LLM_MAX_NEW_TOKENS
                print(f"    -> prompt={prompt_name} (json_mode={json_mode})")
                pred, n_unp = decoder.classify_llm(
                    model, tok, texts, PROMPTS[prompt_name],
                    temperature=0.0, max_new_tokens=mnt, json_mode=json_mode)
                m = metrics.compute_metrics(labels, pred, n_unparsed=n_unp)
                metrics.print_metrics(f"{args.llm} ({prompt_name}, t=0.0)", m)
                rows.append({"model": f"{args.llm} ({prompt_name}, t=0.0)", "typ": "decoder",
                             "accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                             "f1_weighted": m["f1_weighted"]})

            print("\n[5b] Decoder - eksploracja TEMPERATURY (prompt pl_fewshot)")
            for temp in [0.0, 0.7]:
                print(f"    -> temperatura={temp}")
                pred, n_unp = decoder.classify_llm(
                    model, tok, texts, PROMPTS["pl_fewshot"], temperature=temp)
                m = metrics.compute_metrics(labels, pred, n_unparsed=n_unp)
                metrics.print_metrics(f"{args.llm} (pl_fewshot, t={temp})", m)
                rows.append({"model": f"{args.llm} (pl_fewshot, t={temp})", "typ": "decoder",
                             "accuracy": m["accuracy"], "f1_macro": m["f1_macro"],
                             "f1_weighted": m["f1_weighted"]})

        del model, tok
        free_memory()

    # ZAPIS ZBIORCZYCH WYNIKOW
    if rows:
        df = metrics.results_table(rows)
        print("\n" + "=" * 70)
        print("ZBIORCZE WYNIKI (sort po f1_macro):")
        print(df.to_string(index=False))
        csv_path = os.path.join(OUTPUT_DIR, "wyniki.csv")
        df.to_csv(csv_path, index=False)
        metrics.save_results_markdown(rows, os.path.join(OUTPUT_DIR, "wyniki.md"),
                                      title="Zbiorcze wyniki - Lista 5")
        print(f"\nZapisano: {csv_path} oraz {OUTPUT_DIR}/wyniki.md")
        print(f"Macierze pomylek (PNG): {OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
