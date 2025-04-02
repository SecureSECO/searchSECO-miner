from typing import Dict

LICENSE_LIST = [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSL-1.0", "MPL-2.0", "GPL-2.0-only",
    "GPL-2.0-or-later", "GPL-3.0-only", "LGPL-2.1-only", "LGPL-3.0-only", "AGPL-3.0-only", "EPL-1.0",
    "EPL-2.0", "CDDL-1.0", "AFL-3.0", "OSL-3.0", "CC0-1.0", "WTFPL", "Artistic-2.0", "Unlicense",
    "Zlib", "ISC"
]


# Mapping different representations to a standard license name
license_mapping = {
    "MIT": "MIT",
    "MIT License": "MIT",
    "MIT License (Expat)": "MIT",
    "Apache 2.0": "Apache-2.0",
    "Apache License 2.0": "Apache-2.0",
    "BSD 2-Clause": "BSD-2-Clause",  # Updated for BSD-2-Clause
    "BSD 3-Clause": "BSD-3-Clause",
    "BSD 3-Clause \"New\" or \"Revised\"": "BSD-3-Clause",
    'BSD 3-Clause "New" or "Revised" License': "BSD-3-Clause",
    "BSD License": "BSD-3-Clause",
    "GPL-2.0": "GPL-2.0-only",  # Updated for GPL-2.0-only
    "GNU General Public License v2.0": "GPL-2.0-only",
    "GNU General Public License v2.0-only": "GPL-2.0-only",  # Adding an explicit GPL-2.0-only entry
    "GPL-2.0-or-later": "GPL-2.0-or-later",  # Explicit entry for GPL-2.0-or-later
    "GPL-3.0": "GPL-3.0-only",  # Updated for GPL-3.0-only
    "GNU General Public License v3.0": "GPL-3.0-only",
    "GNU General Public License version 3.0": "GPL-3.0-only",
    "GNU GPL v3": "GPL-3.0-only",
    "GPLv3": "GPL-3.0-only",  # Updated to GPL-3.0-only
    "LGPL-2.1-only": "LGPL-2.1-only",
    "LGPL-3.0": "LGPL-3.0-only",  # Updated to LGPL-3.0-only
    "GNU Lesser General Public License v3.0": "LGPL-3.0-only",
    "GNU LGPL v3": "LGPL-3.0-only",
    "Mozilla Public License 2.0": "MPL-2.0",
    "MPL 2.0": "MPL-2.0",
    "AGPL-3.0": "AGPL-3.0-only",  # Updated to AGPL-3.0-only
    "Affero General Public License v3.0": "AGPL-3.0-only",
    "GNU Affero General Public License v3.0": "AGPL-3.0-only",
    "AGPLv3": "AGPL-3.0-only",  # Updated to AGPL-3.0-only
    "EPL-2.0": "EPL-2.0",
    "Eclipse Public License 2.0": "EPL-2.0",
    "Unlicense": "Unlicense",
    "Public Domain": "Unlicense",
    "Unlicense (Public Domain Dedication)": "Unlicense",
    "ISC": "ISC",
    "Internet Systems Consortium License": "ISC",
    "-": "Undefined",
    "Other": "Undefined",
    "other": "Undefined",
    "": "Undefined",
}


COMPATIBILITY_RULES = {
    "Permissive": {"MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "Zlib", "CC0-1.0", "WTFPL", "Unlicense"},
    "Weak Copyleft": {"LGPL-2.1-only", "LGPL-3.0-only", "MPL-2.0", "EPL-1.0", "EPL-2.0", "CDDL-1.0"},
    "Strong Copyleft": {"GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "AGPL-3.0-only", "OSL-3.0"}
}

def check_compatibility(license_a: str, license_b: str) -> bool:
    """Determine if license_a is compatible with license_b."""
    if license_a == license_b:
        return True

    for group in COMPATIBILITY_RULES.values():
        if license_a in group and license_b in group:
            return True

    # Special case: Apache-2.0 is compatible with GPL-3.0-only (with conditions)
    if license_a == "Apache-2.0" and license_b in {"GPL-3.0-only", "GPL-2.0-or-later"}:
        return False

    return False

# Create compatibility matrix
compatibility_matrix: Dict[str, Dict[str, bool]] = {}
for lic_a in LICENSE_LIST:
    compatibility_matrix[lic_a] = {lic_b: check_compatibility(lic_a, lic_b) for lic_b in LICENSE_LIST}

# This line ensures that the matrix is available for imports but not executed on its own
if __name__ == "__main__":
    print(compatibility_matrix)

#print(compatibility_matrix)

"""
# Compatibility matrix
compatibility_matrix: Dict[str, Dict[str, bool]] = {
    "MIT": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": True,
        "ISC": True,
    },
    "Apache-2.0": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": False,
        "ISC": True,
    },
    "BSD-3-Clause": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": True,
        "ISC": True,
    },
    "MPL-2.0": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": False,
        "ISC": True,
    },
    "GPLv3": {
        "MIT": False, 
        "Apache-2.0": False, 
        "BSD-3-Clause": False, 
        "MPL-2.0": False, 
        "GPLv3": True, 
        "LGPL-3.0": True, 
        "AGPL-3.0": True, 
        "EPL-2.0": False, 
        "Unlicense": False,
        "ISC": False,
    },
    "LGPL-3.0": {
        "MIT": False, 
        "Apache-2.0": False, 
        "BSD-3-Clause": False, 
        "MPL-2.0": False, 
        "GPLv3": True, 
        "LGPL-3.0": True, 
        "AGPL-3.0": False, 
        "EPL-2.0": False, 
        "Unlicense": False,
        "ISC": False,
    },
    "AGPL-3.0": {
        "MIT": False, 
        "Apache-2.0": False, 
        "BSD-3-Clause": False, 
        "MPL-2.0": False, 
        "GPLv3": True, 
        "LGPL-3.0": False, 
        "AGPL-3.0": True, 
        "EPL-2.0": False, 
        "Unlicense": False,
        "ISC": False,
    },
    "EPL-2.0": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": False,
        "ISC": True,
    },
    "Unlicense": {
        "MIT": True, 
        "Apache-2.0": False, 
        "BSD-3-Clause": True, 
        "MPL-2.0": False, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": False, 
        "Unlicense": True,
        "ISC": True,
    },
    "ISC": {
        "MIT": True, 
        "Apache-2.0": True, 
        "BSD-3-Clause": True, 
        "MPL-2.0": True, 
        "GPLv3": False, 
        "LGPL-3.0": False, 
        "AGPL-3.0": False, 
        "EPL-2.0": True, 
        "Unlicense": True,
        "ISC": True,
    },
}
"""