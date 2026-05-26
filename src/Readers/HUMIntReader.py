from pathlib import Path


class HumintReader:
    def __init__(self, file_path: str):
        self.file_path = Path(file_path)

    def read_humint(self) -> str:
        if not self.file_path.exists():
            print(
                f"HUMINT file not found: {self.file_path}"
            )
            return ""

        content = self.file_path.read_text(
            encoding="utf-8"
        )

        return content