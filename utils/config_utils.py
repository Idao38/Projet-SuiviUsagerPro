import json
import os

CONFIG_FILE = os.environ.get("CONFIG_FILE", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"conseillers": [], "current_conseiller": ""}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def get_conseillers():
    config = load_config()
    return config["conseillers"]

def add_conseiller(name):
    config = load_config()
    if name and name not in config["conseillers"]:
        config["conseillers"].append(name)
        save_config(config)

def remove_conseiller(name):
    config = load_config()
    if name in config["conseillers"]:
        config["conseillers"].remove(name)
    if config["current_conseiller"] == name:
        config["current_conseiller"] = ""
    save_config(config)

def get_current_conseiller():
    config = load_config()
    return config.get("current_conseiller", "")

def set_current_conseiller(conseiller):
    config = load_config()
    config["current_conseiller"] = conseiller
    save_config(config)

def get_dark_mode():
    config = load_config()
    return config.get("dark_mode", False)

def set_dark_mode(is_dark):
    config = load_config()
    config["dark_mode"] = is_dark
    save_config(config)