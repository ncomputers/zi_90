#config.py
#version 81.1
# Global configuration object to share across modules
config = {}

def set_config(cfg: dict) -> None:
    config.clear()
    config.update(cfg)
