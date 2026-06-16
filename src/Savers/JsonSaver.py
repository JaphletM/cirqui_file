import json
import os

def save_to_json(customer_name, followup_prompts):
    os.makedirs("src/output", exist_ok=True)
    
    output = {
        "company": customer_name,
        "results": followup_prompts
    }
    
    output_path = f"src/output/{customer_name}_analysis.json"
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"Saved analysis to {output_path}")