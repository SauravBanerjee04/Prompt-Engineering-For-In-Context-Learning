import pandas as pd

# === Configuration ===
INPUT_CSV = 'methods_filled_plus_other_manual_prompts.csv'
OUTPUT_XLSX = 'prompt_comparisons_4col_blocks.xlsx'
SETTINGS_ROW = 'Temperature: .7 Token Limit: 1024 Top-P .9'

def pretty_format(text):
    """Convert literal '\\n' and '\\t' into real newlines and indentation."""
    if pd.isna(text):
        return ''
    return text.replace('\\n', '\n').replace('\\t', '    ')

# === Load source CSV ===
df = pd.read_csv(INPUT_CSV)

records = []
for _, row in df.iterrows():
    num = str(row['Task Number'])
    # Prepare first block
    prompt1 = row['Zero-shot prompt']
    chat1 = pretty_format(prompt1) + '\n\n' + pretty_format(row['Codestral 25.01 Transcript'])
    chat2 = pretty_format(prompt1) + '\n\n' + pretty_format(row['OpenAI GPT-4o mini'])

    # Prepare second block
    prompt2 = row.get('Prompt (if applicable)', '')
    base2 = pretty_format(prompt2) + '\n\n' if pd.notna(prompt2) and prompt2.strip() else ''
    chat1_b2 = base2 + pretty_format(row.get('Codestral 25.01 Transcript.1', ''))
    chat2_b2 = base2 + pretty_format(row.get('OpenAI GPT-4o mini.1', ''))

    for block in [
        [
            ('Number', num, 'Number', num),
            ('Type', row['Type of Prompt'], 'Type', row['Type of Prompt']),
            ('Goal', row['Goal'], 'Goal', row['Goal']),
            ('Model', 'Codestral 25.01 Transcript', 'Model', 'OpenAI GPT-4o mini'),
            (SETTINGS_ROW, '', SETTINGS_ROW, ''),
            ('Chat Data', chat1, 'Chat Data', chat2)
        ],
        [
            ('Number', num, 'Number', num),
            ('Type', row['Second Type of Prompt'], 'Type', row['Second Type of Prompt']),
            ('Goal', row['Goal'], 'Goal', row['Goal']),
            ('Model', 'Codestral 25.01 Transcript', 'Model', 'OpenAI GPT-4o mini'),
            (SETTINGS_ROW, '', SETTINGS_ROW, ''),
            ('Chat Data', chat1_b2, 'Chat Data', chat2_b2)
        ]
    ]:
        for lbl1, val1, lbl2, val2 in block:
            records.append({
                'Label1': lbl1,
                'Value1': val1,
                'Label2': lbl2,
                'Value2': val2
            })

# === Convert to DataFrame ===
out_df = pd.DataFrame(records, columns=['Label1', 'Value1', 'Label2', 'Value2'])

# === Write to Excel (.xlsx) ===
with pd.ExcelWriter(OUTPUT_XLSX, engine='openpyxl') as writer:
    out_df.to_excel(writer, sheet_name='Comparisons', index=False)

print(f"Excel file saved to: {OUTPUT_XLSX}")
