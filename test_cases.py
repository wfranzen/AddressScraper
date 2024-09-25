
# Test Addresses (both expected and unexpected formats)
test_addresses = [
    "123 Main St",                      # Simple, expected format
    "456 SOUTH ELM St Apt 2B",          # Mixed case direction and unit number
    "789 East Pine St. Rd",             # Two possible street types ('St.' and 'Rd')
    "321 Beach Blvd, Suite 100",        # Street type and unit type with a comma
    "2030 F ST NW",                     # Common short address format
    "350 Liberty AVE NORTHEAST",        # Full directional spelled out
    "1201 N Southport Rd SE",           # Contradictory direction prefix and suffix
    "601 N Broadway FL 15",             # Street with 'FL' (Floor) as unit type
    "402 E Maple STREET Unit #200",     # Street with mixed unit notation
    "100-200 B ST NW",                  # Address range format
    "Apt 3 250 W Main St",              # Unit indicator before street address
    "5th Avenue Apt 2C",                # Commonly used street name without a number
    "Highway 101",                      # Highway address without typical street suffix
    "1010 Downing St Building B",       # Building identifier
    "121B Baker Street",                # Alphanumeric street number
    "1 First St & Main St",             # Intersection format
    "PO Box 123",                       # PO Box format
    "55 W Wacker Drive Ste 201",        # Mixed use of 'Ste' with numeric suite
    "No address provided",              # Unexpected format (invalid address)
    "",                                 # Empty string
    " ",                                # Blank spaces
    None,                               # None as input
    "123 West-East Rd Apt 4",           # Unusual street name with hyphenated direction
    "456 OLD HIGHWAY 441",              # Older highway address format
    "Suite 201 789 Elm St",             # Unit identifier before street address
    "500 Elm Street Elm",               # Duplicate street type as a name
    "100 Baker St Ste A",               # Alphanumeric unit number
    "789 Beach Drive Blvd",             # Two street suffixes ('Drive' and 'Blvd')
    "200-B Oak Lane",                   # Hyphenated street number
    "400 Washington Blvd NW",           # Typical address with a direction suffix
    "500 Lake Shore Dr PH-2",           # Penthouse unit designation
]