#!/usr/bin/env python3
"""
Fill in methods.csv by querying two models (Codestral-2501 & gpt-4o-mini)
using zero-shot, chain-of-thought (Prompt-Chaining), and self-consistency.
"""
import os
import time
import pandas as pd
from collections import Counter
from openai import OpenAI

# --- Configuration ----------------------------------------------------------

INPUT_CSV  = "methods.csv"
OUTPUT_CSV = "methods_filled.csv"

# Models to compare
MODELS = {
    "codestral": "Codestral-2501",
    "gpt4o":     "gpt-4o-mini",
}

# Number of samples for self-consistency
SELF_CONSISTENCY_RUNS = 5

# Per-call parameters
MAX_TOKENS   = 1024
TEMPERATURE  = 0.7
SYSTEM_MSG   = {"role": "system", "content": "You are a helpful assistant."}

# --- Setup client -----------------------------------------------------------

# Load token from env or fallback to token.txt
os.environ["GITHUB_TOKEN"] = "" // Replace with github token
token = os.getenv("GITHUB_TOKEN")
if not token:
    try:
        with open("token.txt") as f:
            token = f.read().strip()
        os.environ["GITHUB_TOKEN"] = token
    except FileNotFoundError:
        raise RuntimeError("Please set GITHUB_TOKEN or provide token.txt")

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=token
)

# --- Load CSV ---------------------------------------------------------------

df = pd.read_csv(INPUT_CSV)

# Ensure transcript columns exist and are true string dtype
string_cols = [
    "Codestral 25.01 Transcript",
    "OpenAI GPT-4o mini",
    "Codestral 25.01 Transcript.1",
    "OpenAI GPT-4o mini.1",
]

for col in string_cols:
    if col not in df.columns:
        df[col] = ""             # create as empty string column
    # replace NaN and cast entire column to Python str
    df[col] = df[col].fillna("").astype(str)

# --- Helper to call a model -----------------------------------------------

def query_model(model_name: str, user_prompt: str) -> str:
    """Send a chat completion request and return the assistant's reply."""
    resp = client.chat.completions.create(
        model=model_name,
        messages=[
            SYSTEM_MSG,
            {"role": "user", "content": user_prompt}
        ],
        max_tokens=MAX_TOKENS,
        temperature=TEMPERATURE,
    )
    return resp.choices[0].message.content

# --- Main loop -------------------------------------------------------------

for idx, row in df.iterrows():
    code = row["code"]

    # 1) Zero-Shot
    zs_prompt = row.get("Zero-shot prompt", "")
    if pd.notna(zs_prompt) and zs_prompt.strip():
        for key, model in MODELS.items():
            full_prompt = f"{zs_prompt}\n\n{code}"
            answer = query_model(model, full_prompt)
            col = (
                "Codestral 25.01 Transcript"
                if key == "codestral"
                else "OpenAI GPT-4o mini"
            )
            df.at[idx, col] = answer
            time.sleep(1)  # simple rate-limit backoff

    # 2) Second prompt type
    second_type = row.get("Second Type of Prompt", "").strip()
    sc_prompt   = row.get("Prompt (if applicable)", "")
    if second_type == "Prompt-Chaining":
        if pd.notna(sc_prompt) and sc_prompt.strip():
            for key, model in MODELS.items():
                full_prompt = f"{sc_prompt}\n\n{code}"
                answer = query_model(model, full_prompt)
                col = (
                    "Codestral 25.01 Transcript.1"
                    if key == "codestral"
                    else "OpenAI GPT-4o mini.1"
                )
                df.at[idx, col] = answer
                time.sleep(1)

    elif second_type == "Self-Consistency":
        # collect MULTIPLE answers and pick the most common
        results = { key: [] for key in MODELS }
        base_prompt = sc_prompt if pd.notna(sc_prompt) and sc_prompt.strip() else zs_prompt
        for _ in range(SELF_CONSISTENCY_RUNS):
            for key, model in MODELS.items():
                full_prompt = f"{base_prompt}\n\n{code}"
                ans = query_model(model, full_prompt)
                results[key].append(ans)
                time.sleep(1)
        for key, answers in results.items():
            most_common = Counter(answers).most_common(1)[0][0]
            col = (
                "Codestral 25.01 Transcript.1"
                if key == "codestral"
                else "OpenAI GPT-4o mini.1"
            )
            df.at[idx, col] = most_common

# --- Save -------------------------------------------------------------------

df.to_csv(OUTPUT_CSV, index=False)
print(f"Wrote filled results to {OUTPUT_CSV}")
