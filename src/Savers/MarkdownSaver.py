def save_to_markdown(customer_name, rapport):
    output_path = f"src/output/{customer_name}_rapport.md"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(rapport)
    print(f"Saved rapport to {output_path}")