import os

class Config:
    def __init__(self):
        self.script_path = os.path.dirname(os.path.abspath(__file__))
        self.config = {'script_path': self.script_path}

    def retrieveConfig(self, desired_var):
        config_file_path = os.path.join(self.script_path, 'config/config.cfg')
        with open(config_file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    key, value = line.split('=')
                    key = key.strip()
                    value = value.strip()

                    if '.' in value:
                        self.config[key] = float(value)
                    else:
                        self.config[key] = int(value)
        return self.config[desired_var]
    
if __name__ == "__main__":
    c = Config()
    print(c.retrieveConfig('script_path'))