# GenAI Prompt Comparison Assignment Automation

This repository contains scripts and data to automate the evaluation of different prompting strategies (zero-shot, chain‑of‑thought, self‑consistency, etc.) on two language models (Codestral‑2501 and GPT‑4o‑mini) for a set of code generation and understanding tasks.

## Repository Structure

```
.
├── main.py
│   Script to query the models and fill `methods.csv` with responses.
├── data_to_word_doc.py
│   Converts the filled CSV into an Excel workbook (`prompt_comparisons_4col_blocks.xlsx`)
│   with side‑by‑side comparisons.
├── methods.csv
│   Input CSV listing the 22 problems and their prompts.
├── methods_filled.csv
│   Output CSV containing model responses.
├── prompt_comparisons_4col_blocks.xlsx
│   Generated Excel file for visual comparison.
├── Report.pdf
│   Final PDF report template or output.
├── 03-Prompting.pdf
│   Assignment specification and instructions.
└── requirements.txt
    Python dependencies for running the scripts.
```

## Requirements

- Python 3.8 or higher
- See [requirements.txt](requirements.txt) for Python package dependencies.

## Installation

1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd <repo_directory>
   ```

2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Ensure you have your API token set:
   - For OpenAI/Azure usage, set the `GITHUB_TOKEN` environment variable:
     ```bash
     export GITHUB_TOKEN="your_openai_or_azure_api_key"
     ```
   - Or create a `token.txt` file containing the key in the project root.

## Usage

1. Populate model responses:
   ```bash
   python main.py
   ```
   This will read `methods.csv`, query each model, and write `methods_filled.csv`.

2. Generate Excel comparisons:
   ```bash
   python data_to_word_doc.py
   ```
   This reads `methods_filled_plus_other_manual_prompts.csv` (or your CSV)
   and outputs `prompt_comparisons_4col_blocks.xlsx`.

3. Review outputs:
   - `methods_filled.csv` for raw CSV results.
   - `prompt_comparisons_4col_blocks.xlsx` for a formatted side‑by‑side view.
