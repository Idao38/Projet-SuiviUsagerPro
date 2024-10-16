import json
import os
import customtkinter as ctk
from utils.config_utils import *

CONFIG_FILE = os.environ.get("CONFIG_FILE", "config.json")

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"conseillers": [], "current_conseiller": ""}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

def setUp(self):
    self.test_config_file = "test_config.json"
    self.original_config_file = os.environ.get("CONFIG_FILE", "config.json")
    os.environ["CONFIG_FILE"] = self.test_config_file
    
    # Réinitialiser la configuration pour chaque test
    initial_config = {"conseillers": [], "current_conseiller": ""}
    save_config(initial_config)

def tearDown(self):
    super().tearDown()
    os.environ["CONFIG_FILE"] = self.original_config_file
    if os.path.exists(self.test_config_file):
        os.remove(self.test_config_file)
    self.root.destroy()

def get_inactivity_period():
    config = load_config()
    return config.get("inactivity_period", "12")  # Par défaut 12 mois

def set_inactivity_period(period):
    config = load_config()
    config["inactivity_period"] = str(period)
    save_config(config)

def get_ateliers_entre_paiements():
    config = load_config()
    return config.get("ateliers_entre_paiements", 5)  # Par défaut 5 ateliers

def set_ateliers_entre_paiements(nombre):
    config = load_config()
    config["ateliers_entre_paiements"] = int(nombre)
    save_config(config)