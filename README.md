# Address Parser

The Address Parser is a Python library designed to standardize addresses and extract various address components, such as unit numbers, street numbers, and street names. This library is particularly useful for projects that require consistent and structured address data. The standardization techniques used in this library conform to USPS' standards as best as possible.

## Features

- **Normalize Addresses**: Standardize addresses by converting to uppercase, removing unnecessary spaces, and handling common edge cases.
- **Extract Components**: Extract the unit number, street number, street name, and directional affixes from an address.
- **Edge Case Detection**: Identify and warn about formatting issues in addresses.

## Field Naming Conventions

The Address Parser outputs parsed address data with the following field names:

| Field Name              | Description                                                                                   |
| ----------------------- | --------------------------------------------------------------------------------------------- |
| `addressRaw`            | The original unaltered address string.                                                        |
| `address`               | The normalized and standardized version of the address.                                       |
| `addressFormal`         | The formalized version of the address, with full forms of street types and directionals.      |
| `addressUnit`           | The normalized address including the unit information (if present).                           |
| `streetNumber`          | The number at the beginning of the address.                                                   |
| `streetDirectionPrefix` | Directional prefix (e.g., `N`, `S`, `NW`) preceding the street name.                          |
| `streetName`            | The name of the street, excluding directionals and street types.                              |
| `streetType`            | The abbreviated street type (e.g., `ST`, `RD`, `BLVD`).                                       |
| `streetDirectionSuffix` | Directional suffix (e.g., `N`, `S`, `NW`) following the street name.                          |
| `unitNumber`            | Information about the unit or apartment number (e.g., `APT 2B`, `STE 100`).                   |
| `street`                | The full street name, including the directional prefix and suffix, if applicable.             |
| `isComplete`            | Boolean indicating whether the address includes sufficient components to be considered valid. |

## Installation

You can install this library directly from GitHub:

```bash
pip install git+https://github.com/wfranzen/AddressScraper.git
```
