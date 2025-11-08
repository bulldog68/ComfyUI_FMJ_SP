# ComfyUI/custom_nodes/ComfyUI_FMJ_SP/__init__.py

from .fmj_speed_prompt import FMJSpeedPrompt

# Mapping obligatoire pour que ComfyUI charge les nœuds
NODE_CLASS_MAPPINGS = {
    "FMJSpeedPrompt": FMJSpeedPrompt
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FMJSpeedPrompt": "FMJ-Speed-Prompt"
}

WEB_DIRECTORY = "./web"  # optionnel, si tu veux ajouter du JS/CSS plus tard
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
