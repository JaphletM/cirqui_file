class ConfigReader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = {}
        return None

    def read_config(self):
        try:
            with open(self.config_file, 'r') as file:
                self.parse_lines(file)
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found.")
        except Exception as e:
            print(f"An error occurred while reading the config file: {e}")

        return None

    def parse_lines(self, file):
        for line in file:
            self.parse_line(line)

        return None

    def parse_line(self, line):
        line = line.strip()
        if not line or line.startswith('#'):
            return None

        key, value = line.split('=', 1)
        self.config_data[key.strip()] = value.strip()
        return None

    def get_config(self, key, default=None):
        return self.config_data.get(key, default)