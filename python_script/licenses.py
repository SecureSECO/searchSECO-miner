from typing import Dict

# https://opensource.org/licenses

#SPDX
LICENSE_LIST = [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSL-1.0", "MPL-2.0",
    "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "0BSD", "ECL-2.0",
    "LGPL-2.1-only", "LGPL-3.0-only", "AGPL-3.0-only", "GPL-3.0-or-later",
    "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0", "OSL-3.0", "CC-BY-4.0", "CC-BY-NC-4.0",
    "EUPL-1.1", "EUPL-1.2", "Python-2.0", "PostgreSQL", "MIT-0", "SQLite", "WTFPL"
    "CC0-1.0", "CC-BY-SA-4.0", "Artistic-2.0", "Unlicense", "UPL-1.0", "Zlib", "ISC", "MS-PL", 
    "Proprietary_Closed", "Proprietary_Unknown",
]

# Mapping various license names and aliases to SPDX standard identifiers
license_mapping = {

    # MIT variants,
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
    "MIT No Attribution": "MIT",

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

    # BSD Zero Clause License variants
    "0BSD": "0BSD",
    "BSD Zero Clause License": "0BSD",
    "BSD-0-Clause": "0BSD",
    "BSD Zero": "0BSD",
    "BSD 0-Clause": "0BSD",
    "BSD-0": "0BSD",

    # CC-BY-SA-4.0
    "CC-BY-SA-4.0":"CC-BY-SA-4.0",
    "cc-by-sa": "CC-BY-SA-4.0",
    
    "cc-by-nc": "CC-BY-NC-4.0",
    "CC-BY-NC-4.0": "CC-BY-NC-4.0",

    "EUPL-1.1":"EUPL-1.1",
    "eupl-1.1": "EUPL-1.1",

    "EUPL-1.2": "EUPL-1.2",
    "eupl-1.2": "EUPL-1.2",

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

    # ECL-2.0
    "Educational Community License v2.0": "ECL-2.0",
    "Educational Community License Version 2.0": "ECL-2.0",
    "Educational Community License 2.0": "ECL-2.0",
    "ECL-2.0": "ECL-2.0",
    "ECL v2.0": "ECL-2.0",
    "ECL Version 2.0": "ECL-2.0",
    "ECL2": "ECL-2.0",

    "Python-2.0": "Python-2.0",
    "python": "Python-2.0",

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

    # PostgreSQL
    "PostgreSQL": "PostgreSQL",
    "postgresql": "PostgreSQL",

    # MIT-0
    "MIT-0":  "MIT-0",
    "mit-0": "MIT-0",

    # SQLite
    "SQLite": "SQLite",
    "sqlite": "SQLite",

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

    # Microsoft Public License
    "MS-PL": "MS-PL",
    "Microsoft Public License": "MS-PL",
    "MSPL": "MS-PL",

    # WTFPL
    "WTFPL": "WTFPL",
    "Do What The F*ck You Want To Public License": "WTFPL",
    "Do What The Fuck You Want To Public License": "WTFPL",
    "wtfpl": "WTFPL",
    "WTF Public License": "WTFPL",
    "WTF License": "WTFPL",
    "Do WTF You Want License": "WTFPL",
    "DWTFYWTPL": "WTFPL",

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
    "Internal": "Proprietary_Closed",
    "Commercial": "Proprietary_Closed",  # Sometimes used in commercial-only packages
    "Private": "Proprietary_Closed",
    "N/A": "Proprietary_Closed",
    "n/a": "Proprietary_Closed",
    "NA": "Proprietary_Closed",
    "na": "Proprietary_Closed",
    "n/a (unknown)": "Proprietary_Closed",
    "Unlicensed": "Proprietary_Closed",

    # Universal Permissive License v1.0
    "UPL": "UPL-1.0",
    "UPL-1.0": "UPL-1.0",
    "UPL 1.0": "UPL-1.0",
    "UPL v1.0": "UPL-1.0",
    "Universal Permissive License v1.0": "UPL-1.0",
    "Universal Permissive License 1.0": "UPL-1.0",
    "Universal Permissive License Version 1.0": "UPL-1.0",

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
    "No assertion": "Proprietary_Unknown",
    "no assertion": "Proprietary_Unknown",
    "Custom": "Proprietary_Unknown",  # Often used for private/internal licenses
    "custom": "Proprietary_Unknown",
}


COMPATIBILITY_RULES = {
    "Permissive": {
        "MIT", "BSD-2-Clause", "BSD-3-Clause", "0BSD", "Apache-2.0",
        "ISC", "Zlib", "CC0-1.0", "Unlicense", "UPL-1.0", "ECL-2.0",
        "BSL-1.0", "Artistic-2.0", "MS-PL", "CC-BY-4.0", "AFL-3.0",
        "MIT-0", "PostgreSQL", "Python-2.0", "SQLite", "WTFPL",
    },
    
    "Weak Copyleft": {
        "LGPL-2.1-only", "LGPL-3.0-only", "MPL-2.0",
        "EPL-1.0", "EPL-2.0", "CDDL-1.0",
        "CC-BY-SA-4.0",
    },

    "Strong Copyleft": {
        "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only",
        "AGPL-3.0-only", "OSL-3.0", "GPL-3.0-or-later",
    },

    "Proprietary": {
        "Proprietary_Closed", "Proprietary_Unknown", "CC-BY-NC-4.0",
    }

}

# explicit incompatibility rules (pairs that should return False)
INCOMPATIBILITIES = {
("GPL-2.0-only", "GPL-3.0-only"),
("GPL-2.0-only", "GPL-3.0-or-later"),
("GPL-3.0-only", "GPL-2.0-only"),
("GPL-3.0-or-later", "GPL-2.0-only"),
("GPL-2.0-only", "LGPL-2.1-only"),
("LGPL-2.1-only", "GPL-2.0-only"),
("Apache-2.0", "GPL-2.0-only"),
("GPL-2.0-only", "Apache-2.0"),
}

# explicit compatibility rules (pairs that should return True)
EXPLICIT_COMPATIBILITIES = {
("Apache-2.0", "GPL-3.0-only"),
("GPL-3.0-only", "Apache-2.0"),
("Apache-2.0", "GPL-3.0-or-later"),
("GPL-3.0-or-later", "Apache-2.0"),
}


def check_compatibility(license_a: str, license_b: str) -> bool:
    """Determine if license_a is compatible with license_b."""
    
    license_a = license_a.strip()
    license_b = license_b.strip()
    
    # Proprietary licenses are never compatible, even with themselves
    if license_a in {"Proprietary_Closed", "Proprietary_Unknown"} or \
       license_b in {"Proprietary_Closed", "Proprietary_Unknown"}:
        return False

    if license_a == license_b:
        return True
    
    # Check explicit incompatibilities
    if (license_a, license_b) in INCOMPATIBILITIES:
        return False


    # Check explicit compatibilities
    if (license_a, license_b) in EXPLICIT_COMPATIBILITIES:
        return True

    # If both licenses belong to the same compatibility group, compatible
    for group in COMPATIBILITY_RULES.values():
        if license_a in group and license_b in group:
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