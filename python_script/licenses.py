from typing import Dict

# https://opensource.org/licenses

#SPDX
LICENSE_LIST = [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSL-1.0", "MPL-2.0",
    "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", 
    "LGPL-2.1-only", "LGPL-3.0-only", "AGPL-3.0-only", "GPL-3.0-or-later",
    "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0", "OSL-3.0", "CC-BY-4.0",
    "CC0-1.0", "Artistic-2.0", "Unlicense", "Zlib", "ISC", "MS-PL", 
    "Proprietary_Closed", "Proprietary_Unknown",
]

# Mapping various license names and aliases to SPDX standard identifiers
license_mapping = {

    # MIT variants
    "MIT": "MIT",
    "MIT License": "MIT",
    "The MIT License": "MIT",
    "MIT license": "MIT",
    "MIT license (expat)": "MIT",
    "MIT License (Expat)": "MIT",
    "Expat License": "MIT",
    "Expat": "MIT",
    "MIT-style license": "MIT",
    "MIT-style": "MIT",
    "MIT License Version": "MIT",
    "MITL": "MIT",
    "MIT-license": "MIT",
    "MIT / Expat": "MIT",
    "Expat/MIT License": "MIT",
    "MIT License (MIT)": "MIT",
    "MIT License (MIT License)": "MIT",
    "MIT OR Apache-2.0": "MIT",

    # Apache 2.0 variants
    "Apache 2.0": "Apache-2.0",
    "Apache License 2.0": "Apache-2.0",
    "The Apache License, Version 2.0": "Apache-2.0",
    "Apache License Version 2.0": "Apache-2.0",
    "Apache License, Version 2.0": "Apache-2.0",
    "Apache License v2.0": "Apache-2.0",
    "Apache v2.0": "Apache-2.0",
    "Apache v2": "Apache-2.0",
    "Apache-2": "Apache-2.0",
    "Apache License v2": "Apache-2.0",
    "Apache License": "Apache-2.0",  # Occasionally used, though ambiguous
    "Apache Software License 2.0": "Apache-2.0",
    "Apache Software Foundation License 2.0": "Apache-2.0",
    "Apache-2.0 License": "Apache-2.0",
    "Apache Version 2": "Apache-2.0",
    "Apache Version 2.0": "Apache-2.0",
    "ASF 2.0": "Apache-2.0",
    "ASF License 2.0": "Apache-2.0",

    # Academic Free License v. 3.0
    "AFL-3.0": "AFL-3.0",
    "Academic Free License v. 3.0": "AFL-3.0",
    "Academic Free License 3.0": "AFL-3.0",
    "AFL Version 3.0": "AFL-3.0",
    "Academic Free License Version 3.0": "AFL-3.0",
    "Academic Free License v3.0": "AFL-3.0",
    "Academic Free License version 3.0": "AFL-3.0",
    "Academic Free License": "AFL-3.0",

    # BSD 2 variants
    "BSD 2-Clause": "BSD-2-Clause",
    "BSD 2-Clause License": "BSD-2-Clause",
    'BSD 2-Clause "Simplified" License': "BSD-2-Clause",
    "BSD 2-Clause Simplified License": "BSD-2-Clause",
    "BSD Simplified License": "BSD-2-Clause",
    "Simplified BSD License": "BSD-2-Clause",
    "BSD License (Simplified)": "BSD-2-Clause",

    # BSD 3 variants
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
    "GNU General Public License v2.0 or later": "GPL-2.0-or-later",
    "GNU General Public License v2 or later": "GPL-2.0-or-later",
    "GPL v2 or later": "GPL-2.0-or-later",
    "GPLv2 or later": "GPL-2.0-or-later",
    "GPL-2.0+": "GPL-2.0-or-later",
    "GNU GPL v2+": "GPL-2.0-or-later",
    "GNU GPL v2 or later": "GPL-2.0-or-later",
    "GNU General Public License version 2.0 or later": "GPL-2.0-or-later",
    "GNU GPL version 2 or later": "GPL-2.0-or-later",
    "GPL version 2 or later": "GPL-2.0-or-later",
    "GNU General Public License v2+": "GPL-2.0-or-later",
    "GNU GPL v2.0+": "GPL-2.0-or-later",
    "GPL 2.0+": "GPL-2.0-or-later",

    # GPL v3 variants
    "GPL-3.0": "GPL-3.0-only",
    "GNU General Public License v3.0": "GPL-3.0-only",
    "GNU General Public License version 3.0": "GPL-3.0-only",
    "GNU GPL v3": "GPL-3.0-only",
    "GPLv3": "GPL-3.0-only",

    # If needed: add GPL-3.0-or-later
    "GPL-3.0-or-later": "GPL-3.0-or-later",
    "GPL v3 or later": "GPL-3.0-or-later",
    "GNU GPL v3 or later": "GPL-3.0-or-later",
    "GNU General Public License v3.0 or later": "GPL-3.0-or-later",
    "GPLv3+": "GPL-3.0-or-later",

    # LGPL 2.1 variants
    "LGPL-2.1-only": "LGPL-2.1-only",
    "LGPL 2.1": "LGPL-2.1-only",
    "LGPL v2.1": "LGPL-2.1-only",
    "LGPL v2.1 only": "LGPL-2.1-only",
    "GNU LGPL 2.1": "LGPL-2.1-only",
    "GNU LGPL v2.1": "LGPL-2.1-only",
    "GNU Lesser General Public License 2.1": "LGPL-2.1-only",
    "GNU Lesser General Public License v2.1": "LGPL-2.1-only",
    "GNU Lesser General Public License Version 2.1": "LGPL-2.1-only",
    "GNU Library General Public License v2.1": "LGPL-2.1-only",  # historical alias
    "GNU Library or Lesser General Public License v2.1": "LGPL-2.1-only",
    "GNU LGPL Version 2.1": "LGPL-2.1-only",
    "GNU Lesser GPL v2.1": "LGPL-2.1-only",
    "GNU LGPL v2.1 only": "LGPL-2.1-only",
    "LGPL Version 2.1": "LGPL-2.1-only",
    "LGPL v2.1 (only)": "LGPL-2.1-only",

    # LGPL variants
    "LGPL-3.0": "LGPL-3.0-only",
    "LGPL v3.0": "LGPL-3.0-only",
    "LGPL v3": "LGPL-3.0-only",
    "GNU LGPL v3.0": "LGPL-3.0-only",
    "GNU Lesser GPL v3.0": "LGPL-3.0-only",
    "LGPL Version 3.0": "LGPL-3.0-only",
    "GNU LGPL v3": "LGPL-3.0-only",
    "GNU Lesser General Public License v3": "LGPL-3.0-only",
    "GNU Lesser General Public License v3.0": "LGPL-3.0-only",

    # MPL 2.0
    "MPL 2.0": "MPL-2.0",
    "Mozilla Public License 2.0": "MPL-2.0",

    # AGPL v3 variants
    "AGPL-3.0": "AGPL-3.0-only",
    "Affero General Public License v3.0": "AGPL-3.0-only",
    "GNU Affero General Public License v3.0": "AGPL-3.0-only",
    "AGPLv3": "AGPL-3.0-only",

    # EPL variants EPL-1.0
    "EPL-1.0": "EPL-1.0",
    "Eclipse Public License 1.0": "EPL-1.0",
    "EPL 1.0": "EPL-1.0",
    "EPL Version 1.0": "EPL-1.0",
    "Eclipse License 1.0": "EPL-1.0",
    "EclipsePL 1.0": "EPL-1.0",
    "EclipsePL-1.0": "EPL-1.0",
    "Eclipse Public License v1.0": "EPL-1.0",
    "epl-1.0": "EPL-1.0",
    "EPL v1.0": "EPL-1.0",

    # EPL-2.0
    "EPL-2.0": "EPL-2.0",
    "Eclipse Public License 2.0": "EPL-2.0",
    "Eclipse Public License v2.0": "EPL-2.0",
    "Eclipse License 2.0": "EPL-2.0",
    "EPL 2.0": "EPL-2.0",
    "EPL v2.0": "EPL-2.0",
    "EPL Version 2.0": "EPL-2.0",
    "EclipsePL 2.0": "EPL-2.0",
    "EclipsePL-2.0": "EPL-2.0",
    "epl-2.0": "EPL-2.0",
    "epl2.0": "EPL-2.0",
    "EPL2": "EPL-2.0",

    # Unlicense and public domain
    "Unlicense": "Unlicense",
    "The Unlicense": "Unlicense",
    "Public Domain": "Unlicense",
    "Unlicense (Public Domain Dedication)": "Unlicense",

    # ISC variants
    "ISC": "ISC",
    "ISC License": "ISC",
    "Internet Systems Consortium License": "ISC",

    # CDDL 1.0
    "CDDL-1.0": "CDDL-1.0",
    "CDDL v1.0": "CDDL-1.0",
    "CDDL Version 1.0": "CDDL-1.0",
    "CDDL v.1.0": "CDDL-1.0",
    "CDDL License 1.0": "CDDL-1.0",
    "Common Development and Distribution License 1.0": "CDDL-1.0",
    "Common Development and Distribution License v1.0": "CDDL-1.0",
    "Common Development and Distribution License Version 1.0": "CDDL-1.0",
    "Sun CDDL": "CDDL-1.0",

    # CC-BY-4.0
    "Creative Commons Attribution 4.0 International": "CC-BY-4.0",
    "Creative Commons Attribution v4.0": "CC-BY-4.0",
    "Creative Commons Attribution License 4.0": "CC-BY-4.0",
    "CC-BY 4.0": "CC-BY-4.0",
    "CC-BY-4.0": "CC-BY-4.0",
    "CC BY 4.0": "CC-BY-4.0",
    "CC BY-4.0": "CC-BY-4.0",
    "Creative Commons BY 4.0": "CC-BY-4.0",
    "Creative Commons - Attribution 4.0": "CC-BY-4.0",
    "Creative Commons Attribution": "CC-BY-4.0",
    "Creative Commons Attribution International 4.0": "CC-BY-4.0",

    # OSL 3.0
    "OSL 3.0": "OSL-3.0",
    "Open Software License 3.0": "OSL-3.0",

    # BSL 1.0
    "BSL 1.0": "BSL-1.0",
    "Boost Software License 1.0": "BSL-1.0",

    # CC0 1.0
    "CC0": "CC0-1.0",
    "CC0 1.0": "CC0-1.0",
    "Creative Commons Zero v1.0 Universal": "CC0-1.0",

    # Artistic-2.0
    "Artistic License 2.0": "Artistic-2.0",
    "Artistic 2.0": "Artistic-2.0",

    #Microsoft Public License
    "MS-PL": "MS-PL",
    "Microsoft Public License": "MS-PL",
    "MSPL": "MS-PL",

    #Zlib variants
    "Zlib": "Zlib",
    "zlib License": "Zlib",
    "zlib license": "Zlib",
    "Zlib/libpng License": "Zlib",
    "zlib/libpng license": "Zlib",
    "zlib/libpng-style license": "Zlib",
    "ZLIB License": "Zlib",
    "The zlib License": "Zlib",
    "zlib/libpng": "Zlib",

    # Proprietary Closed
    "-": "Proprietary_Closed",
    "": "Proprietary_Closed",
    " ": "Proprietary_Closed",
    None: "Proprietary_Closed",
    "No license": "Proprietary_Closed",
    "Not licensed": "Proprietary_Closed",
    "Closed": "Proprietary_Closed",
    "Closed Source": "Proprietary_Closed",
    "Not Open Source": "Proprietary_Closed",
    "Proprietary": "Proprietary_Closed",
    "None": "Proprietary_Closed",
    "No License": "Proprietary_Closed",  # Capitalization variant
    "Not Licensed": "Proprietary_Closed",  # Capitalization variant
    "No licensing": "Proprietary_Closed",
    "Custom": "Proprietary_Closed",  # Often used for private/internal licenses
    "Internal": "Proprietary_Closed",
    "Commercial": "Proprietary_Closed",  # Sometimes used in commercial-only packages
    "Private": "Proprietary_Closed",

    # Proprietary Unknown
    "Other": "Proprietary_Unknown",
    "other": "Proprietary_Unknown",
    "NOASSERTION": "Proprietary_Unknown",
    "undefined": "Proprietary_Unknown",
    "Undefined": "Proprietary_Unknown",
    "<undefined>": "Proprietary_Unknown",
    "Unknown": "Proprietary_Unknown",
    "unknown": "Proprietary_Unknown",
    "Not specified": "Proprietary_Unknown",
    "not specified": "Proprietary_Unknown",
    "Not Provided": "Proprietary_Unknown",
    "not provided": "Proprietary_Unknown",
    "unspecified": "Proprietary_Unknown",
    "Unspecified": "Proprietary_Unknown",
    "n/a (unknown)": "Proprietary_Unknown",
    "No assertion": "Proprietary_Unknown",
    "noassertion": "Proprietary_Unknown",
    "N/A": "Proprietary_Unknown",
    "n/a": "Proprietary_Unknown",
    "NA": "Proprietary_Unknown",
    "na": "Proprietary_Unknown",
    
}


COMPATIBILITY_RULES = {
    "Permissive": {
        "MIT", "BSD-2-Clause", "BSD-3-Clause", "Apache-2.0",
        "ISC", "Zlib", "CC0-1.0", "Unlicense",
        "BSL-1.0", "Artistic-2.0", "MS-PL", "CC-BY-4.0",
    },
    "Weak Copyleft": {
        "LGPL-2.1-only", "LGPL-3.0-only", "MPL-2.0",
        "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0",
    },
    "Strong Copyleft": {
        "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only",
        "AGPL-3.0-only", "OSL-3.0", "GPL-3.0-or-later",
    },
    "Proprietary": {
        "Proprietary_Closed", "Proprietary_Unknown"
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