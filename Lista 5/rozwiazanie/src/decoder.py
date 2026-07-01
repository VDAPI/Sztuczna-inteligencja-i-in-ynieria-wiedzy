"""Klasyfikacja modelem decoder-only / LLM (Zadania 4-5), np. Qwen2.5-Instruct."""
import json
import re

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from tqdm.auto import tqdm

from .config import (DEFAULT_LLM, LLM_MAX_NEW_TOKENS, LLM_BATCH,
                     LLM_MAX_INPUT_TOKENS, USE_4BIT, LABEL2ID, NEUTRAL_ID)
from .labels import parse_generated_label, _normalize_to_canon


# --- Ladowanie modelu ---
def load_llm(model_name=DEFAULT_LLM, use_4bit=USE_4BIT):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    tokenizer.padding_side = "left"  # przy generacji padujemy z lewej

    kwargs = {"device_map": "auto"}
    if use_4bit:
        from transformers import BitsAndBytesConfig
        kwargs["quantization_config"] = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )
    else:
        kwargs["torch_dtype"] = torch.float16

    model = AutoModelForCausalLM.from_pretrained(model_name, **kwargs)
    model.eval()
    return model, tokenizer


# --- Warianty promptow ---
def build_messages_en(text):
    return [
        {"role": "system",
         "content": "You are a sentiment classifier for Polish online reviews."},
        {"role": "user",
         "content": ("Classify the sentiment of the following review into exactly one "
                     "class: positive, negative, or neutral. Answer with a single word "
                     f"only.\n\nReview: {text}\nClass:")},
    ]


def build_messages_pl(text):
    return [
        {"role": "system",
         "content": "Jestes klasyfikatorem wydzwieku polskich recenzji."},
        {"role": "user",
         "content": ("Sklasyfikuj wydzwiek ponizszej recenzji do dokladnie jednej klasy: "
                     "positive, negative albo neutral. Odpowiedz wylacznie jednym slowem."
                     f"\n\nRecenzja: {text}\nKlasa:")},
    ]


def build_messages_fewshot(text):
    examples = (
        "Recenzja: Swietny hotel, obsluga na najwyzszym poziomie, na pewno wroce.\n"
        "Klasa: positive\n\n"
        "Recenzja: Tragiczna wizyta, lekarz opryskliwy, ogromne kolejki, nie polecam.\n"
        "Klasa: negative\n\n"
        "Recenzja: Gabinet znajduje sie na drugim pietrze, przyjmuje od poniedzialku do piatku.\n"
        "Klasa: neutral\n\n"
    )
    return [
        {"role": "system",
         "content": ("Jestes klasyfikatorem wydzwieku polskich recenzji. Odpowiadasz "
                     "jednym slowem: positive, negative albo neutral.")},
        {"role": "user", "content": examples + f"Recenzja: {text}\nKlasa:"},
    ]


def build_messages_json(text):
    instruction = (
        'Sklasyfikuj wydzwiek recenzji. Zwroc WYLACZNIE obiekt JSON w formacie '
        '{"sentiment": "positive|negative|neutral"} bez zadnego dodatkowego tekstu.\n\n'
    )
    return [
        {"role": "system",
         "content": "Jestes klasyfikatorem wydzwieku. Zwracasz wylacznie obiekt JSON."},
        {"role": "user", "content": instruction + f"Recenzja: {text}"},
    ]


PROMPTS = {
    "en_basic": build_messages_en,
    "pl_basic": build_messages_pl,
    "pl_fewshot": build_messages_fewshot,
    "json": build_messages_json,
}


# --- Parsowanie wyjscia ---
def parse_json_label(text):
    """Wyciaga pierwszy obiekt JSON i czyta pole 'sentiment' (z fallbackiem)."""
    if text:
        m = re.search(r"\{.*?\}", text, re.DOTALL)
        if m:
            try:
                obj = json.loads(m.group(0))
                canon = _normalize_to_canon(obj.get("sentiment", ""))
                if canon:
                    return LABEL2ID[canon], True
            except Exception:
                pass
    return parse_generated_label(text)  # fallback: slowo kluczowe


# --- Glowna klasyfikacja (batchowana) ---
@torch.no_grad()
def classify_llm(model, tokenizer, texts, prompt_fn, temperature=0.0,
                 max_new_tokens=LLM_MAX_NEW_TOKENS, batch_size=LLM_BATCH,
                 json_mode=False, return_raw=False, show_progress=True):
    """Zwraca (preds, n_unparsed) albo (preds, n_unparsed, raw_outputs)."""
    preds, raws, n_unparsed = [], [], 0
    do_sample = temperature is not None and temperature > 0

    gen_kwargs = {"max_new_tokens": max_new_tokens,
                  "pad_token_id": tokenizer.pad_token_id}
    if do_sample:
        gen_kwargs.update(do_sample=True, temperature=float(temperature), top_p=0.9)
    else:
        gen_kwargs.update(do_sample=False)

    rng = range(0, len(texts), batch_size)
    if show_progress:
        rng = tqdm(rng, desc="LLM")

    for i in rng:
        batch = texts[i:i + batch_size]
        prompts = [tokenizer.apply_chat_template(prompt_fn(t), tokenize=False,
                                                 add_generation_prompt=True)
                   for t in batch]
        enc = tokenizer(prompts, return_tensors="pt", padding=True,
                        truncation=True, max_length=LLM_MAX_INPUT_TOKENS).to(model.device)
        out = model.generate(**enc, **gen_kwargs)
        gen = out[:, enc["input_ids"].shape[1]:]  # tylko nowe tokeny
        decoded = tokenizer.batch_decode(gen, skip_special_tokens=True)
        for d in decoded:
            raws.append(d)
            pid, ok = parse_json_label(d) if json_mode else parse_generated_label(d)
            if not ok or pid is None:
                pid = NEUTRAL_ID  # nieparsowalne -> neutral
                n_unparsed += 1
            preds.append(pid)

    if return_raw:
        return preds, n_unparsed, raws
    return preds, n_unparsed


# --- Demonstracja LangChain (wolne, one-by-one) ---
def langchain_json_demo(model_name, texts, temperature=0.0, max_new_tokens=40):
    """Zwraca (preds, n_unparsed) uzywajac stosu LangChain."""
    from transformers import pipeline
    from langchain_huggingface import HuggingFacePipeline
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import JsonOutputParser
    from pydantic import BaseModel, Field

    class SentimentResult(BaseModel):
        sentiment: str = Field(description="jedna z klas: positive, negative, neutral")

    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    mdl = AutoModelForCausalLM.from_pretrained(model_name, torch_dtype=torch.float16,
                                               device_map="auto")

    gen_args = {"max_new_tokens": max_new_tokens, "return_full_text": False,
                "pad_token_id": tok.pad_token_id}
    if temperature and temperature > 0:
        gen_args.update(do_sample=True, temperature=float(temperature), top_p=0.9)
    else:
        gen_args.update(do_sample=False)

    hf = pipeline("text-generation", model=mdl, tokenizer=tok, **gen_args)
    llm = HuggingFacePipeline(pipeline=hf)
    parser = JsonOutputParser(pydantic_object=SentimentResult)

    template = ("Sklasyfikuj wydzwiek recenzji do jednej z klas: positive, negative, "
                "neutral.\n{format_instructions}\nRecenzja: {text}\n")
    prompt = PromptTemplate(
        template=template,
        input_variables=["text"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | llm | parser

    preds, n_unparsed = [], 0
    for t in tqdm(texts, desc="LangChain"):
        try:
            res = chain.invoke({"text": t})
            canon = _normalize_to_canon(res.get("sentiment", ""))
            if canon:
                preds.append(LABEL2ID[canon])
            else:
                preds.append(NEUTRAL_ID); n_unparsed += 1
        except Exception:
            preds.append(NEUTRAL_ID); n_unparsed += 1
    return preds, n_unparsed
