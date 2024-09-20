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
    check_for_edge_cases(address, normalized)

    return normalized

def check_for_edge_cases(address, normalized):
    """
    Check for formatting issues related to unit identifiers, such as:
    - Unit identifier appearing before the street number and name in the normalized result.
    - Unit identifier with no valid number or letter following it.
    """
    # Check if the unit identifier comes before any street number in the normalized result
    unit_match = re.search(r'\b(UNIT|STE|SUITE|APT|FL|FLOOR|BLDG|BUILDING|HNGR|HANGER)\b', normalized)

    # Check if a unit identifier exists but has no valid number or letter following it
    if unit_match:
        unit_identifier_position = unit_match.end()
        if not re.search(r'[A-Z0-9]', normalized[unit_identifier_position:].strip()):
            print(f"Warning: The address '{address}' contains a unit identifier but may be missing a valid identifier (number or letter) after it. Review: '{normalized}'")

def extract_unit_number(address):
    """
    Extract the unit number from an address if it exists.
    Prioritize extracting unit numbers with identifiers like APT, UNIT, STE, etc.
    If no identifier exists, check if the last part of the address is a valid unit number.
    """
    if not isinstance(address, str):
        return None

    # Uppercase the address and strip any leading/trailing whitespace
    normalized = address.upper().strip()

    # List of patterns to ignore (Highway, State Road, County Road)
    ignore_patterns = r'(US HIGHWAY|STATE ROAD|COUNTY ROAD) \d+'

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

        # Check if the last part looks like a valid unit number (e.g., '1A', 'C1', or just a number '10')
        if re.match(r'^\d+[A-Z]?$', last_part):
            return last_part

    return None


# Expanded test cases
addresses = [
    "123 Main St",  # simple address
    " 45 Elm Street #101  ",  # address with extra spaces and unit number
    "100-B Oak St.",  # address with a hyphen
    "500  First    Ave",  # multiple spaces between street name
    "350 Liberty Ave # Apt 14",  # unnecessary # symbol before "Apt"
    "123-125 N Gleeb road #3 UNIT",  # incorrectly formatted range and unit
    "456 US HIGHWAY 27",  # address with highway pattern
    "789 COUNTY ROAD 561 UNIT A",  # county road with unit number
    "601 N McDonald St Apt 502",  # address with directional prefix and unit number
    "789B Park Blvd",  # address with an alphanumeric street number
    "#123 Oak St",  # incorrect leading # before street number
    "P.O. Box 123",  # address with a PO Box
    "123 North St, Apt B-4",  # correctly formatted unit number with hyphen
    "123     South Blvd",  # excessive spaces
    "   ",  # empty string (just spaces)
    "Main St Apt #10",  # missing street number
    "APT 12, 200 W 1st St",  # unit number in front of address
    "400-W Elm Street",  # street number with hyphen
    None,  # non-string input
    "Ste 102 1 South St",  # incorrectly placed "Ste" in address
    "Unit 101 456 Broadway",  # unit number first in address
    "200B West St & Main St",  # corner lot format
    "APT 2, STE 100, 550 N 10th St",  # mixed unit and suite number
    "10 North Street Apt C-1",  # normal address with complex unit number
    "US Highway 90",  # address with just a highway
    "1234 ",  # missing street name
    "1000  Main STREET SUITE # 201",  # mixed formatting with suite
    "3 #UNIT 450 10th AVE",  # unit number before street number
    "1234 Elm St C1",  # normal address with unit number but no unit identifier
    "1234 Elm St Unit 1",  # normal address with unit identifier
    "1234 Elm St 1A",  # normal address with unit identifier and letter but no unit identifier
    "MAIN ST 10",  # address with just a street and unit number
]

# Normalize addresses and print results
# for address in addresses:
#     print(f"Original: {address} -> Normalized: {normalize_address(address) or "NONE"}")

# Extract unit numbers and print results
for address in addresses:
    normalized = normalize_address(address)
    print(f"Normalized: {normalized} -> Unit Number: {extract_unit_number(normalized) or 'NO UNIT NUMBER'}")