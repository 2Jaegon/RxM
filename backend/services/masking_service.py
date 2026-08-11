import re

# Dictionary of proprietary terms to mask
# In a real app, this should be loaded from a database or secure config
PROPRIETARY_TERMS = [
    "Alpha-Compressor-X1",
    "Beta-Valve-99",
    "LG-Special-Process"
]

def mask_text(text: str) -> tuple[str, dict]:
    """
    Masks proprietary terms in a text string.
    Returns the masked text and a mapping dictionary to unmask it later.
    """
    masked_text = text
    mask_map = {}
    
    for i, term in enumerate(PROPRIETARY_TERMS):
        if term in masked_text:
            placeholder = f"__CONFIDENTIAL_TERM_{i}__"
            # Using regex for word boundaries if needed, but simple replace for now
            masked_text = masked_text.replace(term, placeholder)
            mask_map[placeholder] = term
            
    return masked_text, mask_map

def unmask_text(masked_text: str, mask_map: dict) -> str:
    """
    Restores original proprietary terms from placeholders.
    """
    unmasked_text = masked_text
    for placeholder, original_term in mask_map.items():
        unmasked_text = unmasked_text.replace(placeholder, original_term)
        
    return unmasked_text
