import re
from .street_suffix_mapping import street_suffix_mapping, formal_street_suffix_mapping

def normalize_address(address, warningsEnabled=False):
    """
    Normalize an address by ensuring it is a string, converting to uppercase,
    removing extra spaces, unnecessary special characters, and stripping it.

    Parameters:
        address (str): The address to process.
        warningsEnabled (bool): A flag to enable warnings for common edge cases.

    Ex: 1234 Main Street, Unit 5 -> 1234 MAIN ST UNIT 5
    """
    if not isinstance(address, str):
        return None

    # Uppercase the address and strip any leading/trailing whitespace
    normalized = address.upper().strip()

    # Preserve numeric ranges (e.g., 123-125)
    normalized = re.sub(r'(\d+)\s*-\s*(\d+)', r'\1-\2', normalized)

    # Handle intersections (preserve or convert '&' to 'AND')
    normalized = re.sub(r'\s*&\s*', ' AND ', normalized)

    # Remove all leading/trailing # symbols and unnecessary special characters
    normalized = re.sub(r'[^\w\s-]', '', normalized)

    # Check for common edge cases and print warnings
    if warningsEnabled:
        edge_case_found = _check_for_edge_cases(address, normalized)

    # Define unit identifiers for extraction
    unit_identifiers = r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b'
    
    # Ensure unit identifiers with dashes are treated correctly
    normalized = re.sub(r'(' + unit_identifiers + r')(?=\d)', r'\1 ', normalized)

    # Extract and move the unit to the end of the address
    match = re.search(unit_identifiers + r'\s*\d+(-\d+)?[A-Z-]*', normalized)
    if match:
        unit_str = match.group()
        normalized = re.sub(unit_identifiers + r'\s*\d+(-\d+)?[A-Z-]*', '', normalized).strip()
        normalized = f"{normalized} {unit_str}".strip()

    # Standardize direction abbreviations using the provided direction_mapping
    normalized = _standardize_directions(normalized, _direction_mapping)

    # Replace the street suffix with the USPS standard abbreviation
    normalized, _ = _replace_street_suffix(normalized, street_suffix_mapping)

    # Remove multiple spaces and reduce them to a single space
    normalized = re.sub(r'\s+', ' ', normalized)

    # Check for common edge cases and print warnings
    if warningsEnabled and not edge_case_found:
        _check_for_edge_cases(address, normalized)

    return normalized if normalized else None



def _check_for_edge_cases(address, normalized, warningsEnabled=False):
    """
    Check for formatting issues related to unit identifiers, such as:
    - Duplicate unit identifiers in the address.
    - Unit identifier appearing before the street number and name in the normalized result.
    - Unit identifier having both a number before and after it, indicating incorrect ordering.
    """
    if not warningsEnabled:
        return False

    # Ensure the address is in uppercase for consistency
    normalized = normalized.upper()

    # Define unit identifiers
    unit_identifiers = r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b'

    # Pattern to detect consecutive units with similar numbers
    duplicate_unit_pattern = r'(\b(?:APT|UNIT|STE|SUITE|#)\s*\d+[A-Z\-]?)\s*(APT|UNIT|STE|SUITE|#)\s*(\d+[A-Z\-]?)'

    # Find duplicate unit identifier pairs
    match = re.search(duplicate_unit_pattern, normalized)
    if match:
        # Extract the units for comparison
        unit1 = match.group(1).strip()
        unit2 = match.group(2).strip() + " " + match.group(3).strip()

        # Compare the unit numbers and decide which one to keep
        if unit1.split()[-1] == unit2.split()[-1]:
            # Remove the second unit if they are identical
            normalized = normalized.replace(unit2, "").strip()
            print(f"Warning: The raw address '{address}' has duplicate unit formats. Review cleaned: '{normalized}'")

    unit_match = re.search(unit_identifiers, normalized)
    if unit_match:
        unit_identifier_position = unit_match.end()

        # Check if there's no valid number or letter following the unit identifier
        if not re.search(r'[A-Z0-9]', normalized[unit_identifier_position:].strip()):
            print(f"Warning: The raw address '{address}' contains a unit identifier but may be missing a valid unit after it. Review: '{normalized}'")
            return True

        # Check if there's a number both before and after the unit identifier
        pre_unit_number_match = re.search(r'\d+\s*(?=' + unit_match.group() + ')', normalized)
        post_unit_number_match = re.search(r'(?<=' + unit_match.group() + r')\s*\d+[A-Z]?', normalized)

        if pre_unit_number_match and post_unit_number_match:
            print(f"Warning: The raw address '{address}' has both a number before and after the unit identifier. Review: '{normalized}'")
            return True

    return False

def _extract_unit(address):
    """
    Extract the unit number from an address if it exists.
    """
    if not isinstance(address, str):
        return None

    # Uppercase the address and strip any leading/trailing whitespace
    normalized = address.upper().strip()

    # List of patterns to ignore (Highway, State Road, County Road)
    ignore_patterns = r'(US HIGHWAY|STATE ROAD|COUNTY ROAD|PO BOX|STATE ROUTE|HWY) \d+'
    normalized = re.sub(ignore_patterns, '', normalized)

    # Regex patterns to match common unit number formats with exact identifiers
    unit_patterns = [
        r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b\s*[#A-Z\d\-]+\b',
    ]

    # Check for common unit identifiers first (APT, UNIT, etc.)
    for pattern in unit_patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group().strip()

    # If no unit identifier, check if the last part of the address might be a unit number
    parts = normalized.split()
    if len(parts) > 1:
        last_part = parts[-1]
        if re.match(r'^[A-Z]?\d+(-\d+)?[A-Z]?$|^[A-Z]-\d+$|^\d+-[A-Z]$', last_part):
            return last_part

    return None


def _remove_unit_number(address):
    """
    Remove the unit number from a normalized address if it exists.
    """
    if not isinstance(address, str):
        return address

    # Extract the unit number using the previously defined function
    unit_number = _extract_unit(address)

    if unit_number:
        address_without_unit = address.replace(unit_number, '').strip()
        address_without_unit = re.sub(r'\s+', ' ', address_without_unit)
        return address_without_unit
    
    return address

def _extract_street_number(address):
    """
    Extract the street number from an address.
    """
    if not isinstance(address, str):
        return None

    parts = address.strip().split()
    street_number_pattern = r'^\d+[A-Z]?$|^\d+-\d+$|^\d+-[A-Z]$'
    
    if parts and re.match(street_number_pattern, parts[0]):
        return parts[0]

    return None

def _extract_street_name(address):
    """
    Extract the street name from a normalized address.
    """
    if not isinstance(address, str):
        return None

    address_without_unit = _remove_unit_number(address)
    street_number = _extract_street_number(address_without_unit)
    
    if street_number:
        address_without_number = address_without_unit.replace(street_number, '', 1).strip()
        address_without_number = re.sub(r'\s+', ' ', address_without_number)
        return address_without_number

    return address_without_unit

_direction_mapping = {
    "NORTH": "N",
    "SOUTH": "S",
    "EAST": "E",
    "WEST": "W",
    "NORTHEAST": "NE",
    "NORTHWEST": "NW",
    "SOUTHEAST": "SE",
    "SOUTHWEST": "SW",
    "N": "N",
    "S": "S",
    "E": "E",
    "W": "W",
    "NE": "NE",
    "NW": "NW",
    "SE": "SE",
    "SW": "SW"
}

def _standardize_directions(address, _direction_mapping):
    """
    Given an address, standardize the directional components to USPS standard abbreviations.
    
    Parameters:
        address (str): The address to process.
        direction_mapping (dict): A dictionary mapping direction names and abbreviations to USPS standards.
    
    Returns:
        str: The address with standardized direction abbreviations.
    """
    if not isinstance(address, str):
        return address

    # Split the address into components
    address_parts = address.strip().upper().split()

    # Iterate over the address components to replace any directions
    standardized_parts = [_direction_mapping.get(part, part) for part in address_parts]

    return ' '.join(standardized_parts)

def _replace_street_suffix(address, suffix_mapping):
    """
    Given an address, replace the street suffix or abbreviation with the USPS standard abbreviation.
    """
    if not isinstance(address, str):
        return address, None

    address_parts = address.strip().upper().split()
    for i in range(len(address_parts) - 1, -1, -1):
        part = address_parts[i]
        if part in suffix_mapping:
            address_parts[i] = suffix_mapping[part]
            return ' '.join(address_parts), suffix_mapping[part]

    return address, None

_formal_direction_mapping = {
    "N": "NORTH",
    "S": "SOUTH",
    "E": "EAST",
    "W": "WEST",
    "NE": "NORTHEAST",
    "NW": "NORTHWEST",
    "SE": "SOUTHEAST",
    "SW": "SOUTHWEST",
}

def formalize_address(address):
    """
    Formalize an address by first normalizing it, then converting 
    street suffixes and direction abbreviations back to their full forms.

    Ex: 123 R ST NE 130 -> 123 R STREET NORTHEAST 130
    """
    normalized_address = normalize_address(address)
    
    if not normalized_address:
        return None

    # Formalize street suffix
    formalized_address, _ = _replace_street_suffix(normalized_address, formal_street_suffix_mapping)

    # Formalize direction abbreviations
    formalized_address = _standardize_directions(formalized_address, _formal_direction_mapping)

    return formalized_address

def parse_address(address, warningsEnabled=False):
    """
    Given an address, return its key components (normalized address, unit number, etc.).
    """
    normalized = normalize_address(address, warningsEnabled)
    
    return {
        "address": normalized,
        "unitNumber": unit_number(normalized),
        "addressNoUnit": remove_unit(normalized),
        "streetNumber": street_number(normalized),
        "streetName": street_name(normalized),
        "streetType": street_type(normalized),
        "isComplete": is_complete(normalized)
    }

def unit_number(address):
    """
    Extract the unit number from an address if it exists.

    Ex: 1234 Main Street, Unit 5 -> Unit 5
    """
    return _extract_unit(normalize_address(address))

def street_number(address):
    """
    Extract the street number from an address.

    Ex: 1234 Main Street, Unit 5 -> 1234
    """
    return _extract_street_number(normalize_address(address))

def street_name(address):
    """
    Extract the street from an address.

    Ex: 1234 Main St, Unit 5 -> Main St
    """
    return _extract_street_name(normalize_address(address))

def street_type(address):
    """
    Extract the street type from an address.

    Ex: 1234 Main St, Unit 5 -> St
    """
    normalized_address = normalize_address(address)
    return _replace_street_suffix(normalized_address, street_suffix_mapping)[1]

def remove_unit(address):
    """
    Remove the unit number from an address if it exists.

    Ex: 1234 Main Street, Unit 5 -> 1234 Main Street
    """
    return _remove_unit_number(normalize_address(address))

def is_complete(address, warningsEnabled=False):
    """
    Check if the address is complete by ensuring it has a street number, street name, and normalized address.

    Ex: 1234 Main Street, Unit 5 -> True
    """
    normalized = normalize_address(address, warningsEnabled)
    
    # Ensure the address has a valid street number, street name, and normalized address
    street_number_exists = street_number(normalized) is not None
    street_name_exists = street_name(normalized) is not None
    
    # An address is considered complete if it has a street number, street name, and normalized address
    return all([normalized, street_number_exists, street_name_exists])