from typing import Dict

# https://opensource.org/licenses

#SPDX
LICENSE_LIST = [
    "MIT", "Apache-2.0", "BSD-2-Clause", "BSD-3-Clause", "BSL-1.0", "MPL-2.0",
    "GPL-2.0-only", "GPL-2.0-or-later", "GPL-3.0-only", "0BSD", "ECL-2.0",
    "LGPL-2.1-only", "LGPL-3.0-only", "AGPL-3.0-only", "GPL-3.0-or-later",
    "EPL-1.0", "EPL-2.0", "CDDL-1.0", "AFL-3.0", "OSL-3.0", "CC-BY-4.0", "CC-BY-NC-4.0",
    "EUPL-1.1", "EUPL-1.2", "Python-2.0", "PostgreSQL", "MIT-0", "SQLite", "WTFPL",
    "CC0-1.0", "CC-BY-SA-4.0", "Artistic-2.0", "UPL-1.0", "Zlib", "ISC", "MS-PL", 
    "Proprietary", "Unknown", "Unlicensed", "Unlicense", "Custom"
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

    # Universal Permissive License v1.0
    "UPL": "UPL-1.0",
    "UPL-1.0": "UPL-1.0",
    "UPL 1.0": "UPL-1.0",
    "UPL v1.0": "UPL-1.0",
    "Universal Permissive License v1.0": "UPL-1.0",
    "Universal Permissive License 1.0": "UPL-1.0",
    "Universal Permissive License Version 1.0": "UPL-1.0",

    # Proprietary Closed

    "Closed": "Proprietary",
    "Closed Source": "Proprietary",
    "Not Open Source": "Proprietary",
    "Proprietary": "Proprietary",
    "Internal": "Proprietary",
    "Commercial": "Proprietary",  # Sometimes used in commercial-only packages
    "Private": "Proprietary",
    "All Rights Reserved": "Proprietary",
    
    # Unlicense and public domain
    "The Unlicense": "Unlicense",
    "Public Domain": "Unlicense",
    "Unlicense (Public Domain Dedication)": "Unlicense",

    # Unlicensed
    "None": "Unlicensed",
    "none": "Unlicensed",
    "No license": "Unlicensed",
    "Not licensed": "Unlicensed",
    "no license": "Unlicensed",
    "not licensed": "Unlicensed",
    "No licensing": "Unlicensed",
    "no licensing": "Unlicensed",
    "Unlicensed": "Unlicensed",
    "unlicensed": "Unlicensed",

    # Custom
    "Other": "Custom",
    "other": "Custom",
    "Custom": "Custom",
    "custom": "Custom",
    "Private": "Custom",
    "Internal": "Custom",

    # Unknown
    "Unknown": "Unknown",
    "unknown": "Unknown",
    "Not specified": "Unknown",
    "not specified": "Unknown",
    "Not Provided": "Unknown",
    "not provided": "Unknown",
    "unspecified": "Unknown",
    "Unspecified": "Unknown",
    "No assertion": "Unknown",
    "no assertion": "Unknown",
    "NOASSERTION": "Unknown",
    "undefined": "Unknown",
    "Undefined": "Unknown",
    "<undefined>": "Unknown",
    "n/a (unknown)": "Unknown",
    "-": "Unknown",
    "": "Unknown",
    " ": "Unknown",
    "N/A": "Unknown",
    "n/a": "Unknown",
    "NA": "Unknown",
    "na": "Unknown",
}


COMPATIBILITY_GROUPS = {
    "Permissive": {
        "MIT", "BSD-2-Clause", "BSD-3-Clause", "0BSD", "Apache-2.0",
        "ISC", "Zlib", "CC0-1.0", "UPL-1.0", "ECL-2.0",
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
    "Custom": {
        "Custom",
        },
    "Restricted": {
        "CC-BY-NC-4.0",
    },
    "Proprietary": {
        "Proprietary",
    },
    "Unknown": {
        "Unknown",
    },
    "Unlicensed": {
        "Unlicensed",
    }
}

# Define the flow hierarchy for directional compatibility
# A license can flow into a group listed in its 'can_flow_into'
FLOW_HIERARCHY = {
    "Permissive": ["Permissive", "Weak Copyleft", "Strong Copyleft", "Unlicense"],
    "Weak Copyleft": ["Weak Copyleft", "Strong Copyleft"],
    "Strong Copyleft": ["Strong Copyleft"],
    "Restricted": ["Restricted"],
    "Proprietary": ["Proprietary"],
    "Custom": ["Custom",],
    "Unknown": ["Unknown"],
    "Unlicensed": ["Unlicensed"],         
}

# explicit incompatibility rules (pairs that should return False)
# Explicit incompatibility rules (l_orig, l_sink)
# Even if they are in the same hierarchy group, these are forbidden.
INCOMPATIBILITIES = {
    # GPL Version Clashes (GPL-2.0 is NOT forward compatible with 3.0 unless "or-later" is specified)
    ("GPL-2.0-only", "GPL-3.0-only"),
    ("GPL-2.0-only", "GPL-3.0-or-later"),
    ("GPL-3.0-only", "GPL-2.0-only"),
    ("GPL-3.0-or-later", "GPL-2.0-only"),
    
    # LGPL Version Clashes
    ("LGPL-2.1-only", "LGPL-3.0-only"),
    ("LGPL-3.0-only", "LGPL-2.1-only"),

    # Apache 2.0 and GPL 2.0 (The classic "Patent Clause" conflict)
    # Note: Apache 2.0 code can go INTO GPL 3.0, but NOT into GPL 2.0.
    ("Apache-2.0", "GPL-2.0-only"),
    ("Apache-2.0", "GPL-2.0-or-later"), 
    ("GPL-2.0-only", "Apache-2.0"),
    
    # MPL and GPL Conflicts (Unless the "Incompatible with Secondary Licenses" notice is removed)
    ("MPL-2.0", "GPL-2.0-only"),
    ("MPL-2.0", "GPL-3.0-only"),
}

# Explicit compatibility rules (l_orig, l_sink)
# These allow "flow" that might otherwise be blocked by group logic.
EXPLICIT_COMPATIBILITIES = {
    # The GPL-3.0 "Peace Treaty"
    ("Apache-2.0", "GPL-3.0-only"),
    ("Apache-2.0", "GPL-3.0-or-later"),
    ("Apache-2.0", "AGPL-3.0-only"),
    
    # Library flow (LGPL is designed to be "sunk" into its GPL counterpart)
    ("LGPL-2.1-only", "GPL-2.0-only"),
    ("LGPL-2.1-only", "GPL-2.0-or-later"),
    ("LGPL-3.0-only", "GPL-3.0-only"),
    ("LGPL-3.0-only", "GPL-3.0-or-later"),

    # MPL 2.0 "Secondary License" compatibility
    ("MPL-2.0", "Apache-2.0"), # MPL allows this under certain conditions
    ("MPL-2.0", "LGPL-2.1-only"),
}


def get_license_group(license_name: str) -> str:
    """Helper to find which group a license belongs to."""
    for group_name, members in COMPATIBILITY_GROUPS.items():
        if license_name in members:
            return group_name
    return "Proprietary" # Default to Proprietary if unknown


def check_compatibility(l_orig: str, l_sink: str) -> bool:
    """
    Determine if code from l_orig can be 'sunk' into l_sink.
    This implements the Directional Sink Rule.
    """
    l_orig = l_orig.strip()
    l_sink = l_sink.strip()

    group_orig = get_license_group(l_orig)
    group_sink = get_license_group(l_sink)

    if group_orig in {"Unknown", "Unlicensed"}:
        return False

    if group_sink in {"Unknown", "Unlicensed"}:
        return False

    # 1. Identical licenses are always compatible
    if l_orig == l_sink:
        return True

    # 2. Proprietary sinks/origins are never compatible with OSS (Conservative DSR approach)
    if "Proprietary" in {l_orig, l_sink}:
        return False

    # 3. Check Explicit Incompatibilities (e.g., GPL-2.0-only vs GPL-3.0-only)
    if (l_orig, l_sink) in INCOMPATIBILITIES:
        return False

    # 4. Check Explicit Compatibilities (e.g., Apache-2.0 into GPL-3.0)
    if (l_orig, l_sink) in EXPLICIT_COMPATIBILITIES:
        return True

    # 5. Apply Directional Flow Logic

    # If the sink group is allowed for this origin group, return True
    if group_sink in FLOW_HIERARCHY.get(group_orig, []):
        return True
    
    return False



def classify_violation(l_orig, l_sink, license_list):
    """
    Orchestrates classification of License Compliance Debt (LCD).
    Returns: (Category_String, Audit_Message)
    """

    # --- 1. HIGH RISK (CATEGORY 4) ---

    if (l_orig in ["Unknown", "Unlicensed"]) and (l_sink in ["Custom", "Proprietary"]):
        return "4", f"High Risk - Unknown/Unlabeled source entering {l_sink} project (Potential Viral Ingestion): {l_sink} incompatible with {l_orig}"

    # Proprietary code leaking into unknown destination
    if l_orig == "Proprietary" and (
        l_sink not in license_list or l_sink in ["Unknown", "Unlicensed", "Custom"]
    ):
        return "4", (
            f"High Risk - IP Leak - Proprietary code in unmonitored sink: "
            f"{l_sink} incompatible with {l_orig}"
        )

    # Viral copyleft into proprietary
    if l_sink == "Proprietary" and get_license_group(l_orig) == "Strong Copyleft":
        return "4", (
            f"High-Risk-Viral Copyleft Ingestion: "
            f"{l_sink} incompatible with {l_orig}"
        )

    # Non-commercial / restricted into proprietary
    if get_license_group(l_orig) == "Restricted" and l_sink == "Proprietary":
        return "4", (
            f"High Risk - Non-commercial license used in commercial product: "
            f"{l_sink} incompatible with {l_orig}"
        )
    
    # Custom license into proprietary — possible violation
    if l_orig == "Custom" and l_sink == "Proprietary":
        return "4", (
            f"Potential license conflict - Custom license requires legal review "
            f"before proprietary use: {l_sink} with {l_orig}"
        )
    
    if l_orig == "Proprietary" and l_sink == "Custom":
        return "4", (
            f"Potential IP policy conflict - Proprietary code entering "
            f"custom-licensed system: {l_sink} with {l_orig}"
        )
    

    # --- 2. UNDETERMINED / INFORMATION GAPS (CATEGORY 5) ---

    
    if (l_orig == "Unknown" or l_sink == "Unknown" or l_orig not in license_list or l_sink not in license_list):
        return "5", f"Undetermined: {l_sink} with the {l_orig} (Provenance Debt)"
    
    if l_orig == "Custom" and l_sink == "Custom":
        return "5", f"Undetermined: {l_sink} with the {l_orig} (Provenance Debt)"
    
     # No legal permission anywhere
    if l_orig == "Unlicensed" and l_sink == "Unlicensed":
        return "5", f"Undetermined Double legal vacuum: {l_sink} with the {l_orig} (Provenance Debt)"


    # --- 3. PROPRIETARY COMPATIBILITY (CATEGORY 3) ---

    if l_orig == "Proprietary":

        if l_sink == "Proprietary":
            return "3", (
                f"Restricted Proprietary Transfer: "
                f"{l_sink} incompatible with {l_orig}"
            )

        if l_sink in LICENSE_LIST:
            return "4", f"Potential IP policy conflict - Proprietary code entering: {l_sink} incompatible with {l_orig}"

    if l_sink == "Proprietary":
        return "3", f"Proprietary Ingestion of OSS: {l_orig} incompatible with {l_sink}"

    # --- 4. STANDARD OSS COMPATIBILITY (CATEGORIES 1, 2, 3) ---

    if check_compatibility(l_orig, l_sink):

        if l_orig == l_sink:
            return "1", f"Sink is following same license {l_orig}"

        else:
            return "2", f"{l_sink} compatible with {l_orig}"

    else:
        return "3", f"{l_sink} incompatible with {l_orig}"
    