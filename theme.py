import customtkinter as ctk

def set_dark_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")  # Vous pouvez choisir un autre thème de couleur si vous préférez

    # Définir les couleurs personnalisées
    ctk.ThemeManager.theme["CTk"]["fg_color"] = ["#2B2B2B", "#2B2B2B"]
    ctk.ThemeManager.theme["CTk"]["text"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = ["#383838", "#383838"]
    ctk.ThemeManager.theme["CTkButton"]["fg_color"] = ["#1F6AA5", "#1F6AA5"]
    ctk.ThemeManager.theme["CTkButton"]["hover_color"] = ["#144870", "#144870"]
    ctk.ThemeManager.theme["CTkButton"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkLabel"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = ["#4A4A4A", "#4A4A4A"]
    ctk.ThemeManager.theme["CTkEntry"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkEntry"]["placeholder_text_color"] = ["#AAAAAA", "#AAAAAA"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["fg_color"] = ["#1F6AA5", "#1F6AA5"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_color"] = ["#144870", "#144870"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["button_hover_color"] = ["#0D2F4B", "#0D2F4B"]
    ctk.ThemeManager.theme["CTkOptionMenu"]["text_color"] = ["#FFFFFF", "#FFFFFF"]
    ctk.ThemeManager.theme["CTkSwitch"]["progress_color"] = ["#1F6AA5", "#1F6AA5"]
    ctk.ThemeManager.theme["CTkSwitch"]["button_hover_color"] = ["#144870", "#144870"]

def set_light_theme():
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")