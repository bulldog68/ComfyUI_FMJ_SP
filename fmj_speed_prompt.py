import os
import random
import csv

CSV_DIR = os.path.join(os.path.dirname(__file__), "csv")

# Variable de classe pour garder l'état d'incrémentation entre les appels
# ⚠️ Attention : pas fiable dans tous les contextes (ex: rechargement du workflow)
_increment_counters = {}

class FMJSpeedPrompt:
    # Couleur de fond du nœud (bleu doux)
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

            # Ajout du mode "increment"
            choices = ["disabled", "random", "increment"] + lines
            default_choice = "disabled"

            inputs["required"][base_name] = (choices, {"default": default_choice})

        return inputs

    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "debug_info")
    FUNCTION = "generate_prompt"
    CATEGORY = "🌀FMJ"
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

            elif value == "increment":
                choices = self._load_choices(key)
                if not choices:
                    selected_prompts.append("(erreur increment)")
                    debug_lines.append(f"{key}: erreur increment")
                else:
                    # Utilise une clé unique par fichier CSV pour garder l'état
                    counter_key = f"{key}"
                    if counter_key not in _increment_counters:
                        _increment_counters[counter_key] = 0
                    index = _increment_counters[counter_key] % len(choices)
                    choice = choices[index]
                    selected_prompts.append(choice)
                    debug_lines.append(f"{key}: {choice} [increment #{index}]")
                    # Incrémente pour la prochaine fois
                    _increment_counters[counter_key] += 1

            else:
                # Valeur manuelle (choix fixe)
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