import re
from .street_suffix_mapping import street_suffix_mapping

def normalize_address(address):
    """
    Normalize an address by ensuring it is a string, converting to uppercase,
    removing extra spaces, unnecessary special characters, and stripping it.
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
    edge_case_found = check_for_edge_cases(address, normalized)

    # Define unit identifiers for checking
    unit_identifiers = r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b'
    
    # Add a space between unit identifiers and the following numbers if missing (e.g., 'PH2-20' -> 'PH 2-20')
    normalized = re.sub(r'(' + unit_identifiers + r')(?=\d)', r'\1 ', normalized)

    # Search for the first occurrence of a unit identifier with its unit number
    match = re.search(unit_identifiers + r'\s*\d+[A-Z-]*', normalized)
    if match:
        unit_str = match.group()
        # Remove the unit string from the current position
        normalized = re.sub(unit_identifiers + r'\s*\d+[A-Z-]*', '', normalized).strip()
        # Add the unit string to the end of the address
        normalized = f"{normalized} {unit_str}".strip()

    # Standardize direction abbreviations using the provided direction_mapping
    normalized = standardize_directions(normalized, direction_mapping)

    # Replace the street suffix with the USPS standard abbreviation
    normalized, _ = replace_street_suffix(normalized, street_suffix_mapping)

    # Remove multiple spaces and reduce them to a single space
    normalized = re.sub(r'\s+', ' ', normalized)

    # Check for common edge cases and print warnings
    if not edge_case_found:
        check_for_edge_cases(address, normalized)

    return normalized if normalized else None



def check_for_edge_cases(address, normalized):
    """
    Check for formatting issues related to unit identifiers, such as:
    - Duplicate unit identifiers in the address.
    - Unit identifier appearing before the street number and name in the normalized result.
    - Unit identifier with no valid number or letter following it.
    - Unit identifier having both a number before and after it, indicating incorrect ordering.
    """
    # Ensure the address is in uppercase for consistency
    normalized = normalized.upper()
    
    # Define unit identifiers
    unit_identifiers = r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b'

    # Check for duplicate unit identifiers
    all_matches = re.findall(unit_identifiers, normalized)
    if len(all_matches) > 1:
        print(f"Warning: The address '{address}' contains duplicate unit identifiers. Review: '{normalized}'")
        return True

    # Check if a unit identifier exists
    unit_match = re.search(unit_identifiers, normalized)
    if unit_match:
        unit_identifier_position = unit_match.end()

        # Check if there's no valid number or letter following the unit identifier
        if not re.search(r'[A-Z0-9]', normalized[unit_identifier_position:].strip()):
            print(f"Warning: The address '{address}' contains a unit identifier but may be missing a valid unit after it. Review: '{address}'")
            return True

        # Check if there's a number both before and after the unit identifier
        pre_unit_number_match = re.search(r'\d+\s*(?=' + unit_match.group() + ')', normalized)
        post_unit_number_match = re.search(r'(?<=' + unit_match.group() + r')\s*\d+[A-Z]?', normalized)

        if pre_unit_number_match and post_unit_number_match:
            print(f"Warning: The address '{address}' has both a number before and after the unit identifier. Review: '{address}'")
            return True

    return False

def extract_unit_number(address):
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
        r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER|LOT|PMB|SPC|PH)\b\s*[#A-Z\d\-]+\b',  # Added word boundaries for precision
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
        # Updated regex to handle simple cases (e.g., 'P-5') and complex cases (e.g., 'G1-205')
        if re.match(r'^[A-Z]?\d+(-\d+)?[A-Z]?$|^[A-Z]-\d+$|^\d+-[A-Z]$', last_part):
            return last_part

    return None


def remove_unit_number(address):
    """
    Remove the unit number from a normalized address if it exists.
    """
    if not isinstance(address, str):
        return address

    # Extract the unit number using the previously defined function
    unit_number = extract_unit_number(address)

    if unit_number:
        address_without_unit = address.replace(unit_number, '').strip()
        address_without_unit = re.sub(r'\s+', ' ', address_without_unit)
        return address_without_unit
    
    return address

def extract_street_number(address):
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

def extract_street_name(address):
    """
    Extract the street name from a normalized address.
    """
    if not isinstance(address, str):
        return None

    address_without_unit = remove_unit_number(address)
    street_number = extract_street_number(address_without_unit)
    
    if street_number:
        address_without_number = address_without_unit.replace(street_number, '', 1).strip()
        address_without_number = re.sub(r'\s+', ' ', address_without_number)
        return address_without_number

    return address_without_unit

direction_mapping = {
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

def standardize_directions(address, direction_mapping):
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
    standardized_parts = [direction_mapping.get(part, part) for part in address_parts]

    # Reconstruct the address
    return ' '.join(standardized_parts)

def replace_street_suffix(address, suffix_mapping):
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

def parse_address(address):
    """
    Given an address, return the raw address, normalized address, unit number, address without the unit,
    street number, street without the number, street type, and a flag indicating if the address is complete.
    """
    normalized = normalize_address(address)
    unit_number = extract_unit_number(normalized)
    address_without_unit = remove_unit_number(normalized)
    street_number = extract_street_number(address_without_unit)
    street_name = extract_street_name(address_without_unit)
    street_type = replace_street_suffix(address_without_unit, street_suffix_mapping)
    
    return {
        "address": normalized,
        "unitNumber": unit_number,
        "addressNoUnit": address_without_unit,
        "streetNumber": street_number,
        "streetName": street_name,
        "streetType": street_type[1],
        "isComplete": all([normalized, street_number, street_name])
    }