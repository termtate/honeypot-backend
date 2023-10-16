from schema import Attack

def decode(coming_bytes: bytes) -> Attack:
    return Attack.model_validate_json(coming_bytes)