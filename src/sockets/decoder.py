from schema import Attack, Socket



def decode(coming_bytes: bytes, from_socket: Socket) -> Attack:
    return Attack.model_validate_json(coming_bytes)