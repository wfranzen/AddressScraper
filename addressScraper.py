import re

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

    # Remove all leading/trailing # symbols and unnecessary special characters
    normalized = re.sub(r'[^\w\s-]', '', normalized)

    # Check for common edge cases and print warnings
    edge_case_found = False
    edge_case_found = check_for_edge_cases(address, normalized)

    # Move misplaced unit identifiers (like "STE", "UNIT") to the end of the address
    unit_identifiers = r'(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER) \d+[A-Z]?\b'
    match = re.search(unit_identifiers, normalized)
    if match:
        unit_str = match.group()
        normalized = re.sub(unit_identifiers, '', normalized).strip()  # Remove the unit part
        normalized = f"{normalized} {unit_str}"  # Add it to the end

    # Handle intersections (preserve or convert '&' to 'AND')
    normalized = re.sub(r'\s*&\s*', ' AND ', normalized)

    # Remove multiple spaces and reduce them to a single space
    normalized = re.sub(r'\s+', ' ', normalized)

    # Check for common edge cases and print warnings
    if not edge_case_found:
        check_for_edge_cases(address, normalized)

    return normalized

def check_for_edge_cases(address, normalized):
    """
    Check for formatting issues related to unit identifiers, such as:
    - Unit identifier appearing before the street number and name in the normalized result.
    - Unit identifier with no valid number or letter following it.
    - Unit identifier having both a number before and after it, indicating incorrect ordering.
    """
    # Ensure the address is in uppercase for consistency
    edge_case_found = False
    normalized = normalized.upper()
    
    # Check if a unit identifier exists
    unit_match = re.search(r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER)\b', normalized)

    if unit_match:
        unit_identifier_position = unit_match.end()

        # Check if there's no valid number or letter following the unit identifier
        if not re.search(r'[A-Z0-9]', normalized[unit_identifier_position:].strip()):
            print(f"Warning: The address '{address}' contains a unit identifier but may be missing a valid unit after it. Review: '{address}'")
            edge_case_found = True

        # Check if there's a number both before and after the unit identifier
        pre_unit_number_match = re.search(r'\d+\s*(?=' + unit_match.group() + ')', normalized)
        post_unit_number_match = re.search(r'(?<=' + unit_match.group() + r')\s*\d+[A-Z]?', normalized)

        if pre_unit_number_match and post_unit_number_match:
            print(f"Warning: The address '{address}' has both a number before and after the unit identifier. Review: '{address}'")
            edge_case_found = True

    return edge_case_found

def extract_unit_number(address):
    """
    Extract the unit number from an address if it exists.
    """
    if not isinstance(address, str):
        return None

    # Uppercase the address and strip any leading/trailing whitespace
    normalized = address.upper().strip()

    # List of patterns to ignore (Highway, State Road, County Road)
    ignore_patterns = r'(US HIGHWAY|STATE ROAD|COUNTY ROAD|PO BOX) \d+'

    # Remove highway/state/county road patterns
    normalized = re.sub(ignore_patterns, '', normalized)

    # Regex patterns to match common unit number formats with identifiers
    unit_patterns = [
        r'(UNIT|APT|STE|SUITE|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER)\s*[#\dA-Z\-]+',  # Matches unit identifier followed by number/letter
    ]

    # Check for common unit identifiers first (APT, UNIT, etc.)
    for pattern in unit_patterns:
        match = re.search(pattern, normalized)
        if match:
            return match.group().strip()

    # If no unit identifier, check if the last part of the address might be a unit number
    parts = normalized.split()

    # Ensure there are multiple parts to the address
    if len(parts) > 1:
        last_part = parts[-1]

        # Check if the last part looks like a valid unit number (e.g., '1A', 'C1', 'C-1')
        if re.match(r'^[A-Z]?\d+[A-Z]?$|^[A-Z]-\d+$|^\d+-[A-Z]$', last_part):
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
        # Remove the unit number from the address and strip any extra spaces
        address_without_unit = address.replace(unit_number, '').strip()
        
        # Ensure that multiple spaces are reduced to a single space
        address_without_unit = re.sub(r'\s+', ' ', address_without_unit)

        return address_without_unit
    
    # Return the address as is if there's no unit number
    return address

def extract_street_number(address):
    """
    Extract the street number from an address.
    """
    if not isinstance(address, str):
        return None

    # Split the address into parts
    parts = address.strip().split()

    # - Numeric street numbers (e.g., "123")
    # - Alphanumeric street numbers (e.g., "100B")
    # - Numeric ranges (e.g., "123-125")
    # - Hyphenated alphanumeric (e.g., "100-B", "450-C")
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

    # Step 1: Remove the unit number
    address_without_unit = remove_unit_number(normalized)

    # Step 2: Extract and remove the street number
    street_number = extract_street_number(address_without_unit)
    
    if street_number:
        # Remove the street number from the address and strip leading/trailing spaces
        address_without_number = address_without_unit.replace(street_number, '', 1).strip()
        
        # Remove any excess spaces that might be left
        address_without_number = re.sub(r'\s+', ' ', address_without_number)
        
        return address_without_number

    # If there's no street number, return the address as is
    return address_without_unit

def parse_address(address):
    """
    Given an address, return the normalized address, unit number, address without the unit,
    street number, and street name.
    """
    normalized = normalize_address(address)
    unit_number = extract_unit_number(normalized)
    address_without_unit = remove_unit_number(normalized)
    street_number = extract_street_number(address_without_unit)
    street_name = extract_street_name(address)
    
    return {
        "normalized_address": normalized,
        "unit_number": unit_number,
        "address_without_unit": address_without_unit,
        "street_number": street_number,
        "street_name": street_name
    }