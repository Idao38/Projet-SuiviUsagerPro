import json
import os
import customtkinter as ctk
from utils.config_utils import *
from ui.settings import Settings

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

    self.root = ctk.CTk()
    self.root.update_appearance = lambda: None
    self.root.update_conseiller_dropdown = self.mock_update_conseiller_dropdown
    self.settings = Settings(self.root, self.db_manager, self.root)

def tearDown(self):
    super().tearDown()
    os.environ["CONFIG_FILE"] = self.original_config_file
    if os.path.exists(self.test_config_file):
        os.remove(self.test_config_file)
    self.root.destroy()
