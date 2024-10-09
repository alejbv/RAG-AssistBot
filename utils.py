import tomli
import os

def load_data():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path,'conf.toml'), "rb") as f:
        data = tomli.load(f)
    return data