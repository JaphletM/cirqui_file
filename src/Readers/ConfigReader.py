class ConfigReader:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config_data = {}

    def read_config(self):
        try:
            with open(self.config_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key, value = line.split('=', 1)
                        self.config_data[key.strip()] = value.strip()
        except FileNotFoundError:
            print(f"Config file {self.config_file} not found.")
        except Exception as e:
            print(f"An error occurred while reading the config file: {e}")

    def get_config(self, key, default=None):
        return self.config_data.get(key, default)