from typing import Tuple

def parse_full_name(full_name: str) -> Tuple[str, str]:
    """
    Parse a full name into first name and last name.

    Parameters:
    full_name (str): The full name as a single string.

    Returns:
    Tuple[str, str]: A tuple containing the first name and last name.
    If the full name has only one word, it is treated as the last name and the first name is an empty string.
    """
    # Split the full name by spaces
    name_parts = full_name.split()
    
    # If the full name has only one word, treat it as the last name
    if len(name_parts) == 1:
        return "", name_parts[0]
    
    # Otherwise, join all parts except the last one as the first name
    first_name = " ".join(name_parts[:-1])
    last_name = name_parts[-1]
    
    return first_name, last_name