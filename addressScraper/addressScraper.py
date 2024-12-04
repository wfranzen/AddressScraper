import re
from .street_suffix_mapping import street_suffix_mapping, formal_street_suffix_mapping

def parse_address(address, warningsEnabled=False):
    if not isinstance(address, str) or not address.strip():
        return None

    # Preprocess the address
    address = address.upper().strip()
    address = re.sub(r'\s*&\s*', ' AND ', address)
    address = re.sub(r'[^\w\s/-]', '', address)
    original_address = address
    words = address.split()

    street_number = None
    street_number_pos = None
    street_type = None
    street_type_pos = None
    street_direction_prefix = None
    street_direction_suffix = None

    # List of directionals
    directionals = {'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW', 'NORTH', 'SOUTH', 'EAST', 'WEST', 'NORTHEAST', 'NORTHWEST', 'SOUTHEAST', 'SOUTHWEST'}

    # Step 1: Locate the street type from the right
    street_types = set(street_suffix_mapping.keys()).union(set(street_suffix_mapping.values()))
    i = len(words) - 1
    while i >= 0:
        word = words[i]
        if word in street_types:
            street_type = street_suffix_mapping.get(word, word)
            street_type_pos = i
            # Step 1a: Check for street direction suffix
            if i + 1 < len(words) and words[i + 1] in directionals:
                street_direction_suffix = words[i + 1]
                i += 1  # Include the directional suffix in the street type position
            break
        i -= 1

    if street_type_pos is None:
        # No street type found; assume the last word is the street type
        if warningsEnabled: print(f"AddressScraper Warning: No standard street type found in '{address}'")
        street_type_pos = len(words) - 1

    # Step 2: Locate the street number from the right, starting at the street type's position
    i = street_type_pos - 1
    while i >= 0:
        word = words[i]
        if re.match(r'^\d+(-[A-Z\d]+)?$', word):
            street_number = word
            street_number_pos = i
            # Handle fractional street numbers, adding the next word if it's a fraction
            if i + 1 < len(words) and re.match(r'^\d+/\d+$', words[i + 1]):
                street_number += ' ' + words[i + 1]
                i += 1
                # Pop the fraction from the list of words, and update the rest of the words positions
                words.pop(i)
                street_type_pos -= 1
                if street_direction_suffix:
                    street_type_pos -= 1
                
            break
        i -= 1

    if street_number_pos is None:
        # No street number found, set its position to the beginning of the address
        if warningsEnabled: print(f"AddressScraper Warning: No standard street type found in '{address}'")
        street_number_pos = -1

    # Step 3: Check for the presence of a directional prefix directly after the street number
    if street_number_pos + 1 < len(words) and words[street_number_pos + 1] in directionals:
        if street_number_pos + 2 < len(words) and words[street_number_pos + 2] in street_types:
            street_direction_prefix = None
        else:
            street_direction_prefix = words[street_number_pos + 1]
            if street_direction_prefix in _formal_direction_mapping.values():
                # Convert the formal direction to the USPS standard abbreviation
                street_direction_prefix = _standardize_directions(street_direction_prefix, _direction_mapping)

    # Extract street name between street number and street type, excluding directional suffix
    name_start = street_number_pos
    if street_direction_prefix:
        name_start += 1
    name_end = street_type_pos
    street_name_words = words[name_start + 1:name_end]
    street_name = ' '.join(street_name_words)

    # Handle multi-word street types (e.g., "240 HWY 441")
    multi_word_street_types = {'HWY', 'STATE RD', 'COUNTY RD', 'RTE', 'US HWY', 'US RTE'}
    if street_type in multi_word_street_types:
        # Include the next word if it's a number
        if street_type_pos + 1 < len(words) and re.match(r'^\d+$', words[street_type_pos + 1]):
            street_type += ' ' + words[street_type_pos + 1]
            street_type_pos += 1
            address_no_unit_words = words[street_number_pos:street_type_pos + 1]
            address_no_unit = ' '.join(address_no_unit_words)

    # Step 4: AddressNoUnit is the substring between street_number_pos and street_type_pos, inclusive
    if street_direction_suffix:
        address_no_unit_words = words[street_number_pos:street_type_pos + 2] 
    else:
        address_no_unit_words = words[street_number_pos:street_type_pos + 1]
    address_no_unit = ' '.join(address_no_unit_words)

    # Step 5: Remove AddressNoUnit from the original address
    remaining_address = original_address.replace(address_no_unit, '', 1).strip()
    unit_info = remaining_address if remaining_address else None

    # Extract unit identifier and number from unit_info
    if unit_info:
        unit_identifiers = r'\b(APARTMENT|APT|BASEMENT|BSMT|BUILDING|BLDG|DEPARTMENT|DEPT|' \
                           r'FLOOR|FL|HANGER|HNGR|KEY|LOBBY|LBBY|LOT|OFFICE|OFC|PENTHOUSE|PH|' \
                           r'PIER|ROOM|RM|SUITE|STE|TRAILER|TRLR|UNIT|SPACE|SPC)\b'
        match = re.search(unit_identifiers + r'\s*[A-Z\d\-]+', unit_info)
        if match:
            unit_info = match.group()
        else:
            unit_info = unit_info.strip()

    # Step 6: Reconstruct the address
    reconstructed_address_parts = [
        part for part in [
            street_number,
            street_direction_prefix,
            street_name,
            street_type,
            street_direction_suffix,
            unit_info
        ] if part not in [None, '']
    ]
    reconstructed_address = ' '.join(reconstructed_address_parts)

    # Check for formatting issues related to unit identifiers
    if warningsEnabled:
        _check_for_edge_cases(address, reconstructed_address)

    # Step 7: Reconstruction of the address without the unit number
    if unit_info:
        address_no_unit = reconstructed_address.replace((unit_info), '', 1).strip()
    else:
        address_no_unit = reconstructed_address

    # Step 8: Create 'street' variable
    if street_name and street_type:
        street = f"{street_name} {street_type}".strip()
        if street_direction_prefix:
            street = f"{street_direction_prefix} {street}".strip()
    else:
        street = None

    # Prepare the parsed address dictionary
    parsed_address = {
        'streetNumber': street_number,
        'streetDirectionPrefix': street_direction_prefix if street_direction_prefix else None,
        'streetName': street_name.strip() if street_name else None,
        'streetType': street_type if street_type else None,
        'streetDirectionSuffix': street_direction_suffix if street_direction_suffix else None,
        'unitNumber': unit_info.strip() if unit_info else None,
        'street': street.strip() if street else None,
        'address': address_no_unit if address_no_unit else None,
        'addressUnit': reconstructed_address.strip() if reconstructed_address and unit_info else None,
        'isComplete': all([street_number is not None, street_name is not None, reconstructed_address is not None or address_no_unit, street is not None])
    }

    return parsed_address

def _check_for_edge_cases(address, normalized):
    """
    Check for formatting issues related to unit identifiers, such as:
    - Duplicate unit identifiers in the address.
    - Unit identifier appearing before the street number and name in the normalized result.
    - Unit identifier having both a number before and after it, indicating incorrect ordering.
    """

    # Ensure the address is in uppercase for consistency
    normalized = normalized.upper()

    # Define unit identifiers
    unit_identifiers = r'\b(APARTMENT|APT|BASEMENT|BSMT|BUILDING|BLDG|DEPARTMENT|DEPT|' \
                           r'FLOOR|FL|HANGER|HNGR|KEY|LOBBY|LBBY|LOT|OFFICE|OFC|PENTHOUSE|PH|' \
                           r'PIER|ROOM|RM|SUITE|STE|TRAILER|TRLR|UNIT|SPACE|SPC)\b'

    duplicate_unit_pattern = (
        r'(\b(?:APT|UNIT|STE|SUITE|#)\s*\d+[A-Z\d\-]*)\s+'
        r'(APT|UNIT|STE|SUITE|#)\s*'
        r'(\d+[A-Z\d\-]*)'
    )

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
            print(f"AddressScraper Warning: The raw address '{address}' has duplicate unit formats. Review cleaned: '{normalized}'")

    unit_match = re.search(unit_identifiers, normalized)
    if unit_match:
        unit_identifier_position = unit_match.end()

        # Check if there's no valid number or letter following the unit identifier
        if not re.search(r'[A-Z0-9]', normalized[unit_identifier_position:].strip()):
            print(f"AddressScraper Warning: The raw address '{address}' contains a unit identifier but may be missing a valid unit after it. Review: '{normalized}'")
            return True

        # Check if there's a number both before and after the unit identifier
        pre_unit_number_match = re.search(r'\d+\s*(?=' + unit_match.group() + ')', normalized)
        post_unit_number_match = re.search(r'(?<=' + unit_match.group() + r')\s*\d+[A-Z]?', normalized)

        if pre_unit_number_match and post_unit_number_match:
            print(f"AddressScraper Warning: The raw address '{address}' has both a number before and after the unit identifier. Review: '{normalized}'")
            return True

    return False

def _extract_unit(address):
    """
    Extract the unit number from an address if it exists.

    Parameters:
        address (str): The address from which to extract the unit number.

    Returns:
        str or None: The extracted unit number, or None if not found.
    """
    if not isinstance(address, str):
        return None

    # Uppercase the address and strip any leading/trailing whitespace
    normalized = address.upper().strip()

    # Remove the '#' symbol as per USPS standards
    normalized = normalized.replace('#', '')

    # Updated list of USPS-compliant unit identifiers, excluding 'KEY' and 'SIDE'
    unit_identifiers_list = [
        'APARTMENT', 'APT', 'BASEMENT', 'BSMT', 'BUILDING', 'BLDG', 'DEPARTMENT', 'DEPT',
        'FLOOR', 'FL', 'HANGER', 'HNGR', 'LOBBY', 'LBBY', 'LOT', 'OFFICE', 'OFC', 'PENTHOUSE',
        'PH', 'PIER', 'ROOM', 'RM', 'SLIP', 'SPACE', 'SPC', 'STOP', 'SUITE', 'STE', 'TRAILER',
        'TRLR', 'UNIT'
    ]
    unit_identifiers = r'\b(?:' + '|'.join(unit_identifiers_list) + r')\b'

    # Regex pattern to match unit identifiers followed by unit numbers, including hyphens
    unit_pattern = r'(' + unit_identifiers + r')\s*([A-Z\d\-]+)'

    # Search for the unit pattern in the normalized address
    match = re.search(unit_pattern, normalized)
    if match:
        unit_identifier = match.group(1)
        unit_number = match.group(2)
        return f"{unit_identifier} {unit_number}".strip()

    # Directional suffixes to exclude from being misclassified as unit numbers
    directionals = {'N', 'S', 'E', 'W', 'NE', 'NW', 'SE', 'SW'}

    # List of street suffixes to exclude
    street_suffixes = set(street_suffix_mapping.values())

    # If no unit identifier is found, check if the last part might be a unit number
    parts = normalized.split()
    if len(parts) > 1:
        last_part = parts[-1]
        # Check if the last part is a potential unit number containing letters
        if re.match(r'^[A-Z\d\-]+$', last_part) and re.search(r'[A-Z]', last_part):
            # Exclude directional suffixes and street suffixes
            if last_part not in directionals and last_part not in street_suffixes:
                return last_part

    return None

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

def _standardize_directions(address, direction_mapping):
    """
    Standardize the directional components in an address to USPS standard abbreviations.

    Handles standalone directions without modifying embedded words.

    Parameters:
        address (str): The address to process.
        direction_mapping (dict): A dictionary mapping direction names and abbreviations to USPS standards.

    Returns:
        str: The address with standardized directional abbreviations.
    """
    if not isinstance(address, str):
        return address

    # Regex to match standalone directional components (prefix/suffix)
    direction_pattern = r'\b({})\b'.format('|'.join(direction_mapping.keys()))

    def replace_direction(match):
        # Replace using the mapping
        return direction_mapping.get(match.group(0).upper(), match.group(0))

    # Apply regex replacement for standalone directions
    return re.sub(direction_pattern, replace_direction, address)


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
    address_info = parse_address(address)
    if not address_info:
        return None

    street_num = address_info.get('streetNumber')
    street_direction_prefix = address_info.get('streetDirectionPrefix')
    street_name = address_info.get('streetName')
    street_type = address_info.get('streetType')
    street_direction_suffix = address_info.get('streetDirectionSuffix')
    unit_info = address_info.get('unitNumber')

    # Convert directional affixes and street type to full form
    if street_direction_prefix:
        street_direction_prefix = _standardize_directions(street_direction_prefix, _formal_direction_mapping)
    if street_direction_suffix:
        street_direction_suffix = _standardize_directions(street_direction_suffix, _formal_direction_mapping)
    if street_type:
        street_type = formal_street_suffix_mapping.get(street_type, street_type)

    # Reconstruct the formalized address
    formalized_address_parts = [
        part for part in [
            street_num,
            street_direction_prefix,
            street_name,
            street_type,
            street_direction_suffix,
            unit_info
        ] if part
    ]
    formalized_address = ' '.join(formalized_address_parts)

    return formalized_address

def normalize_address(address):
    """
    Normalize an address according to USPS standards.

    Ex: 1234 Main Street, Unit 5 -> 1234 MAIN ST UNIT 5
    """

    return parse_address(address).get('address')

def get_unit_info(address):
    """
    Extract the unit number from an address if it exists.

    Ex: 1234 Main Street, Unit 5 -> Unit 5
    """
    return _extract_unit(parse_address(address))

def get_street_number(address):
    """
    Extract the street number from an address.

    Ex: 1234 Main Street, Unit 5 -> 1234
    """
    return parse_address(address).get('streetNumber')

def get_street_name(address):
    """
    Extract the street from an address.

    Ex: 1234 Main St, Unit 5 -> Main St
    """
    return parse_address(address).get('streetName')

def get_street_type(address):
    """
    Extract the street type from an address.

    Ex: 1234 Main St, Unit 5 -> St
    """
    return parse_address(address).get('streetType')

def get_address_with_unit(address):
    """
    Remove the unit number from an address if it exists.

    Ex: 1234 Main Street, Unit 5 -> 1234 Main Street
    """
    return parse_address(address).get('addressUnit')

def get_street_prefix(address):
    """
    Extract the street prefix from an address.

    Ex: 1234 North Main St, Unit 5 -> N
    """
    return parse_address(address).get('streetDirectionPrefix')

def get_street_suffix(address):
    """
    Extract the street suffix from an address.

    Ex: 1234 Main St Northwest, Unit 5 -> NW
    """
    return parse_address(address).get('streetDirectionSuffix')

def is_complete(address, warningsEnabled=False):
    """
    Check if the address is complete by ensuring it has a street number, street name, and normalized address.

    Ex: 1234 Main Street, Unit 5 -> True
    """
    normalized = parse_address(address, warningsEnabled)
    
    # Ensure the address has a valid street number, street name, and normalized address
    street_number_exists = get_street_number(normalized) is not None
    street_name_exists = get_street_name(normalized) is not None
    
    # An address is considered complete if it has a street number, street name, and normalized address
    return all([normalized, street_number_exists, street_name_exists])