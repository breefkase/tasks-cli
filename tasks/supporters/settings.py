from pathlib import Path
import json


class Settings:
    def __init__(self):
        self.config = {}
        self.path_settings_file = Path.home().joinpath('.breefkase')
        self.breefkase_dir = None
        self.load()

    def load(self):
        f = self.path_settings_file
        try:
            with open(f, 'r') as configfile:
                contents = json.loads(configfile.read())
                print("Settings loaded from file: ", f)
                if 'breefkaseDir' in contents:
                    self.breefkase_dir = contents["breefkaseDir"]
                    print("breefkase path set to: ", self.breefkase_dir)
                self.config = contents
        except FileNotFoundError:
            print("Settings file does not exist. Creating...")
            self.save()
            print("Settings file created at: ", f)
        except Exception as e:
            print('Something strange happened: ', e)

    def save(self):
        f = self.path_settings_file
        with open(f, 'w') as configfile:
            contents = json.dumps(self.config)
            # TODO: Must load settings from file first, to not overwrite other settings
            configfile.write(contents)
            print("Saving settings to file: ", f)
