def GenericNameValidator(name: str) -> bool:
    return len(name) >= 3 and len(name) <= 16
