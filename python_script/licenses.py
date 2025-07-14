from typing import Dict

# https://opensource.org/licenses

#SPDX
LICENSE_LIST = [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSL-1.0", "MPL-2.0",
    "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only",
    "LGPL-2.1-only", "LGPL-3.0-only", "AGPL-3.0-only",
    "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0", "OSL-3.0",
    "CC0-1.0", "Artistic-2.0", "Unlicense", "Zlib", "ISC", 
    "Proprietary_Closed", "Proprietary_Unknown",
]

# Mapping various license names and aliases to SPDX standard identifiers
license_mapping = {
    # MIT variants
    "MIT": "MIT",
    "MIT License": "MIT",
    "MIT License (Expat)": "MIT",

    # Apache 2.0 variants
    "Apache 2.0": "Apache-2.0",
    "Apache License 2.0": "Apache-2.0",

    # Academic Free License v. 3.0
    "Academic Free License v. 3.0": "AFL-3.0",
    "Academic Free License 3.0": "AFL-3.0",
    "AFL-3.0": "AFL-3.0",
    "AFL 3.0": "AFL-3.0",
    "AFL Version 3.0": "AFL-3.0",
    "Academic Free License Version 3.0": "AFL-3.0",
    "Academic Free License v3.0": "AFL-3.0",
    "Academic Free License version 3.0": "AFL-3.0",
    "Academic Free License": "AFL-3.0",

    # BSD variants
    "BSD 2-Clause": "BSD-2-Clause",
    "BSD 3-Clause": "BSD-3-Clause",
    "BSD 3-Clause \"New\" or \"Revised\"": "BSD-3-Clause",
    'BSD 3-Clause "New" or "Revised" License': "BSD-3-Clause",
    "BSD License": "BSD-3-Clause",

    # GPL v2 variants
    "GPL-2.0": "GPL-2.0-only",
    "GNU General Public License v2.0": "GPL-2.0-only",
    "GNU General Public License v2.0-only": "GPL-2.0-only",

    # GPL v2 or later
    "GPL-2.0-or-later": "GPL-2.0-or-later",

    # GPL v3 variants
    "GPL-3.0": "GPL-3.0-only",
    "GNU General Public License v3.0": "GPL-3.0-only",
    "GNU General Public License version 3.0": "GPL-3.0-only",
    "GNU GPL v3": "GPL-3.0-only",
    "GPLv3": "GPL-3.0-only",

    # LGPL variants
    "LGPL-2.1-only": "LGPL-2.1-only",
    "LGPL-3.0": "LGPL-3.0-only",
    "GNU Lesser General Public License v3.0": "LGPL-3.0-only",
    "GNU LGPL v3": "LGPL-3.0-only",

    # MPL 2.0
    "Mozilla Public License 2.0": "MPL-2.0",
    "MPL 2.0": "MPL-2.0",

    # AGPL v3 variants
    "AGPL-3.0": "AGPL-3.0-only",
    "Affero General Public License v3.0": "AGPL-3.0-only",
    "GNU Affero General Public License v3.0": "AGPL-3.0-only",
    "AGPLv3": "AGPL-3.0-only",

    # EPL variants
    "EPL-1.0": "EPL-1.0",
    "EPL-2.0": "EPL-2.0",
    "Eclipse Public License 2.0": "EPL-2.0",

    # Unlicense and public domain
    "Unlicense": "Unlicense",
    "The Unlicense": "Unlicense",
    "Public Domain": "Unlicense",
    "Unlicense (Public Domain Dedication)": "Unlicense",

    # ISC variants
    "ISC": "ISC",
    "ISC License": "ISC",
    "Internet Systems Consortium License": "ISC",

    # Proprietary Closed
    "-": "Proprietary_Closed",
    "": "Proprietary_Closed",
    " ": "Proprietary_Closed",
    None: "Proprietary_Closed",
    "No license": "Proprietary_Closed",
    "Not licensed": "Proprietary_Closed",
    "Closed": "Proprietary_Closed",
    "Closed Source": "Proprietary_Closed",

    # Proprietary Unknown
    "Other": "Proprietary_Unknown",
    "other": "Proprietary_Unknown",
    "NOASSERTION": "Proprietary_Unknown",
    "undefined": "Proprietary_Unknown",
    "Undefined": "Proprietary_Unknown",
    
}

COMPATIBILITY_RULES = {
    "Permissive": {
        "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0", "ISC", "Zlib", "CC0-1.0", "Unlicense", "BSL-1.0", "Artistic-2.0"
    },
    "Weak Copyleft": {
        "LGPL-2.1-only", "LGPL-3.0-only", "MPL-2.0", "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0"
    },
    "Strong Copyleft": {
        "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "AGPL-3.0-only", "OSL-3.0"
    }
}

def check_compatibility(license_a: str, license_b: str) -> bool:
    """Determine if license_a is compatible with license_b."""
    
    license_a = license_a.strip()
    license_b = license_b.strip()
    # Treat None and Proprietary as incompatible with all except themselves
    if "Proprietary_Closed" in {license_a, license_b}:
        return False
    
    if "Proprietary_Unknown" in {license_a, license_b}:
        return False

    if license_a == license_b:
        return True

    # If both licenses belong to the same compatibility group, compatible
    for group in COMPATIBILITY_RULES.values():
        if license_a in group and license_b in group:
            return True

    # Apache-2.0 compatibility is complex:
    # Apache-2.0 is NOT compatible with GPL-2.0-only, but IS with GPL-3.0-only and later.
    if license_a == "Apache-2.0" and license_b == "GPL-2.0-only":
        return False
    if license_b == "Apache-2.0" and license_a == "GPL-2.0-only":
        return False

    # Apache-2.0 and GPL-3.0-only are compatible (with conditions), so return True for them
    if (license_a == "Apache-2.0" and license_b == "GPL-3.0-only") or \
       (license_b == "Apache-2.0" and license_a == "GPL-3.0-only"):
        return True

    # Default fallback: incompatible
    return False

# Build compatibility matrix
compatibility_matrix: Dict[str, Dict[str, bool]] = {}
for lic_a in LICENSE_LIST:
    compatibility_matrix[lic_a] = {lic_b: check_compatibility(lic_a, lic_b) for lic_b in LICENSE_LIST}

if __name__ == "__main__":
    import pprint
    pprint.pprint(compatibility_matrix)

#print(compatibility_matrix)