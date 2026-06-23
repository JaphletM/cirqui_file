import os
from datetime import datetime
from pathlib import Path

class FollowUpPromptGenerator:
    def __init__(self, output_dir: str = "./follow_up_prompts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.counter = self._get_next_number()
    
    def _get_next_number(self) -> int:
        """Get the next available number for file naming."""
        existing_files = list(self.output_dir.glob("*.txt"))
        if not existing_files:
            return 1
        def get_next_number(output_dir: str = "./follow_up_prompts") -> int:
            """Get the next available number for file naming."""
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            existing_files = list(output_path.glob("*.txt"))
            
            if not existing_files:
                return 1
            
            numbers = []
            for file in existing_files:
                try:
                    num = int(file.stem.split()[0])
                    numbers.append(num)
                except ValueError:
                    continue
            
            return max(numbers, default=0) + 1

        def create_prompt_file(user_input: str, output_dir: str = "./follow_up_prompts", counter: int = None) -> tuple[str, int]:
            """Convert user input into a numbered follow-up prompt file."""
            output_path = Path(output_dir)
            output_path.mkdir(exist_ok=True)
            
            if counter is None:
                counter = get_next_number(output_dir)
            
            filename = f"{counter:03d} follow up prompts file.txt"
            filepath = output_path / filename
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Timestamp: {datetime.now().isoformat()}\n")
                f.write(f"Prompt #{counter}\n")
                f.write("-" * 50 + "\n\n")
                f.write(user_input)
            
            return str(filepath), counter + 1

        def main():
            output_dir = "./follow_up_prompts"
            counter = get_next_number(output_dir)
            
            print("Enter your follow-up prompt (press Ctrl+D or type 'END' on a new line to finish):")
            lines = []
            
            try:
                while True:
                    line = input()
                    if line.lower() == "end":
                        break
                    lines.append(line)
            except EOFError:
                pass
            
            user_input = "\n".join(lines)
            
            if user_input.strip():
                filepath, _ = create_prompt_file(user_input, output_dir, counter)
                print(f"✓ File created: {filepath}")
            else:
                print("No input provided.")

        if __name__ == "__main__":
            main()
        numbers = []
        for file in existing_files:
            try:
                num = int(file.stem.split()[0])
                numbers.append(num)
            except ValueError:
                continue
        
        return max(numbers, default=0) + 1
    
    def create_prompt_file(self, user_input: str) -> str:
        """Convert user input into a numbered follow-up prompt file."""
        filename = f"{self.counter:03d} follow up prompts file.txt"
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Prompt #{self.counter}\n")
            f.write("-" * 50 + "\n\n")
            f.write(user_input)
        
        self.counter += 1
        return str(filepath)


def main():
    generator = FollowUpPromptGenerator()
    
    print("Enter your follow-up prompt (press Ctrl+D or type 'END' on a new line to finish):")
    lines = []
    
    try:
        while True:
            line = input()
            if line.lower() == "end":
                break
            lines.append(line)
    except EOFError:
        pass
    
    user_input = "\n".join(lines)
    
    if user_input.strip():
        filepath = generator.create_prompt_file(user_input)
        print(f"✓ File created: {filepath}")
    else:
        print("No input provided.")


if __name__ == "__main__":
    main()