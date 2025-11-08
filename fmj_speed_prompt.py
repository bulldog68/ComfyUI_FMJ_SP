# ComfyUI/custom_nodes/ComfyUI_FMJ_SP/fmj_speed_prompt.py

import os
import random
import csv

CSV_DIR = os.path.join(os.path.dirname(__file__), "csv")

class FMJSpeedPrompt:
    # Couleur de fond du nœud (bleu doux)
    # Format: (R, G, B)
    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)

    def __init__(self):
        self.NODE_BG_COLOR = (0.15, 0.25, 0.35)  # Bleu nuit doux

    @classmethod
    def INPUT_TYPES(cls):
        csv_files = []
        if os.path.exists(CSV_DIR):
            csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
        
        inputs = {
            "required": {
                "seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff}),
                "extra_prompt": ("STRING", {"multiline": False, "default": ""}),
            }
        }

        for filename in sorted(csv_files):
            base_name = os.path.splitext(filename)[0]
            lines = []
            file_path = os.path.join(CSV_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        if row:
                            lines.append(row[0].strip())
            except Exception as e:
                lines = [f"⚠️ Erreur: {str(e)}"]

            if not lines:
                lines = ["(vide)"]

            # Choix : disabled / random / lignes
            choices = ["disabled", "random"] + lines
            default_choice = "disabled"

            inputs["required"][base_name] = (choices, {"default": default_choice})

        return inputs

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "debug_info")
    FUNCTION = "generate_prompt"
    CATEGORY = "FMJ"
    OUTPUT_NODE = True

    def generate_prompt(self, seed, extra_prompt, **kwargs):
        random.seed(seed)
        selected_prompts = []

        debug_lines = [f"Seed: {seed}", f"Extra: {extra_prompt}"]

        for key, value in kwargs.items():
            if key in ['seed', 'extra_prompt']:
                continue

            if value == "disabled":
                debug_lines.append(f"{key}: disabled")
                continue
            elif value == "random":
                choices = self._load_choices(key)
                if choices:
                    choice = random.choice(choices)
                    selected_prompts.append(choice)
                    debug_lines.append(f"{key}: {choice} [random]")
                else:
                    selected_prompts.append("(erreur random)")
                    debug_lines.append(f"{key}: erreur random")
            else:
                selected_prompts.append(value)
                debug_lines.append(f"{key}: {value} [manual]")

        if extra_prompt.strip():
            selected_prompts.append(extra_prompt.strip())

        final_prompt = ", ".join([p for p in selected_prompts if p and not p.startswith("⚠️")])

        debug_info = "\n".join(debug_lines)

        return (final_prompt, debug_info)

    def _load_choices(self, base_name):
        file_path = os.path.join(CSV_DIR, base_name + ".csv")
        lines = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        lines.append(row[0].strip())
        except Exception:
            pass
        return lines