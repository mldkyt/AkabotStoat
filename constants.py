import os

REVOLT_TOKEN = os.getenv("REVOLT_TOKEN")

def validate_values(l: dict[str, str | None]):
    for k, v in l.items():
        if v is None:
            print(f"CONSTANTS: The constant value for {k} is NOT set!")

validate_values({
    'REVOLT_TOKEN': REVOLT_TOKEN
})
