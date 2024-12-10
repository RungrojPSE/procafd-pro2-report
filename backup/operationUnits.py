import re
import json


def parse_ctx():
    file_path = "sample_full.txt"

    with open(file_path, "r") as file:
        text_content = file.read()

    sections = slice_section(text_content)

    nodes = []
    for text in sections:
        if text.startswith("STREAM DATA"):
            nodes.extend(parse_stream_data(text))
        elif text.startswith("UNIT OPERATIONS"):
            nodes.extend(parse_unit_operations(text))

    for i, node in enumerate(nodes):
        node["id"] = i + 1

    # Create edges
    edges = []
    id = 0
    for node in nodes:
        for outlet in node["properties"]["out"]:
            for target_node in nodes:
                if outlet in target_node["properties"]["in"]:
                    id = id + 1
                    edges.append(
                        {"id": id, "from": node["id"], "to": target_node["id"]}
                    )

    return nodes, edges


def parse_stream_data(text_content):
    # Define a list to store the parsed stream data
    streams = []

    # Regular expression to match each PROPERTY STREAM block
    pattern = re.compile(
        r"STREAM=(?P<label>[^,]+),\s*"
        r"TEMPERATURE=(?P<temperature>[\d.]+),\s*"
        r"PRESSURE=(?P<pressure>[\d.]+),\s*"
        r"PHASE=[^,]+,\s*&\s*"
        r"RATE\(M\)=[\d.]+,\s*"
        r"COMPOSITION\(M\)=(?P<composition>.+)"
    )

    # Iterate over all matches
    for match in pattern.finditer(text_content):
        # Extract composition and parse into nested lists
        raw_composition = match.group("composition")
        composition = [
            [int(pair.split(",")[0]), float(pair.split(",")[1])]
            for pair in raw_composition.split("/")
        ]

        # Add the parsed data to the streams list
        properties = {
            "kind": "START",
            "in": [],
            "out": [match.group("label")],
            "temperature": int(match.group("temperature")),
            "pressure": match.group("pressure"),
            "composition": composition,
        }
        streams.append(
            {"id": None, "label": match.group("label"), "properties": properties}
        )

    return streams


def parse_unit_operations(text_content):
    # Step 1: Slice the section into individual units
    unit_blocks = slice_units(text_content)

    # Define a mapping of prefixes to their corresponding parser functions
    parser_map = {
        "CONREACTOR": parse_conreactor_block,
        "FLASH": parse_flash_block,
        "COLUMN": parse_column_block,
        "COMPRESSOR": parse_compressor_block,
        "SPLITTER": parse_splitter_block,
        "PUMP": parse_pump_block,
        "MIXER": parse_mixer_block,
        "HX": parse_hx_block,
    }

    unit_objs = []
    for txt in unit_blocks:
        # Iterate through the map to find the matching parser
        for prefix, parser_func in parser_map.items():
            if txt.startswith(prefix):
                unit_objs.append(parser_func(txt))
                break  # No need to check other prefixes once a match is found

    return unit_objs



def slice_section(section_text):
    """
    Slice the context into individual section.
    """
    # Match lines starting with section name
    unit_start_pattern = re.compile(
        r"^\s*(TITLE|COMPONENT DATA|THERMODYNAMIC DATA|STREAM DATA|RXDATA|UNIT OPERATIONS|END)\b",
        re.MULTILINE,
    )
    unit_positions = [
        match.start() for match in unit_start_pattern.finditer(section_text)
    ]
    unit_positions.append(len(section_text))

    # Slice into individual section
    units = []
    for i in range(len(unit_positions) - 1):
        units.append(section_text[unit_positions[i] : unit_positions[i + 1]].strip())

    return units


def slice_units(section_text):
    """
    Slice the UNIT OPERATIONS section into individual units.
    """
    # Match lines starting with unit type (e.g., COLUMN, SPLITTER, PUMP, etc.)
    unit_start_pattern = re.compile(
        r"^\s*(CONREACTOR|FLASH|COLUMN|COMPRESSOR|SPLITTER|PUMP|MIXER|HX)\b",
        re.MULTILINE,
    )
    unit_positions = [
        match.start() for match in unit_start_pattern.finditer(section_text)
    ]
    unit_positions.append(len(section_text))  # Add end position to slice the last unit

    # Slice into individual units
    units = []
    for i in range(len(unit_positions) - 1):
        units.append(section_text[unit_positions[i] : unit_positions[i + 1]].strip())

    return units


def parse_conreactor_block(block):
    # Dictionary to store parsed values
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Extract UNIT, UID, and NAME
    unit_match = re.search(r"CONREACTOR UID=([\w\-]+), NAME=(.+)", block)
    if unit_match:
        properties["kind"] = "CONREACTOR"
        node["label"] = unit_match.group(1).strip()
        properties["description"] = unit_match.group(2).strip()

    # Extract inlets
    inlets_match = re.search(r"FEED\s+([\w\-]+)", block)
    if inlets_match:
        properties["in"].append(inlets_match.group(1).strip())

    # Extract outlet
    outlet_match = re.search(r"PRODUCT\s+M=([\w\-]+)", block)
    if outlet_match:
        properties["out"].append(outlet_match.group(1).strip())

    return node


def parse_compressor_block(block):
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Extract UNIT, UID, and NAME
    unit_match = re.search(r"COMPRESSOR UID=([\w\-]+), NAME=(.+)", block)
    if unit_match:
        properties["kind"] = "COMPRESSOR"
        node["label"] = unit_match.group(1).strip()
        properties["description"] = unit_match.group(2).strip()

    # Extract inlets
    inlets_match = re.search(r"FEED\s+([\w\-]+)", block)
    if inlets_match:
        properties["in"].append(inlets_match.group(1).strip())

    # Extract outlets
    outlets_match = re.search(r"PRODUCT\s+M=([\w\-]+)", block)
    if outlets_match:
        properties["out"].append(outlets_match.group(1).strip())

    return node


def parse_flash_block(block):
    # Dictionary to store parsed values
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "outT": [],
        "outB": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Extract UNIT, UID, and NAME
    unit_match = re.search(r"FLASH UID=([\w\-]+), NAME=(.+)", block)
    if unit_match:
        properties["kind"] = "FLASH"
        node["label"] = unit_match.group(1).strip()
        properties["description"] = unit_match.group(2).strip()

    # Extract inlets
    inlets_match = re.search(r"FEED\s+([\w\-]+)", block)
    if inlets_match:
        properties["in"].append(inlets_match.group(1).strip())

    # Extract outlets
    outlets_match = re.search(r"PRODUCT\s+V=([\w\-]+), W=([\w\-]+)", block)
    if outlets_match:
        properties["out"].extend(
            [outlets_match.group(1).strip(), outlets_match.group(2).strip()]
        )
        properties["outT"].append(outlets_match.group(1).strip())  # Top outlet (V)
        properties["outB"].append(outlets_match.group(2).strip())  # Bottom outlet (W)

    return node


def parse_mixer_block(block):
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Regular expressions to extract required components
    unit_pattern = r"^\s*(\w+)\s+UID=([\w-]+),\s+NAME=(.+)$"
    feed_pattern = r"\bFEED\s+([A-Z,]+)"
    product_pattern = r"\bPRODUCT\s+M=([A-Z]+)"

    # Match and extract the components
    unit_match = re.search(unit_pattern, block, re.MULTILINE)
    feed_match = re.search(feed_pattern, block)
    product_match = re.search(product_pattern, block)

    if not unit_match or not feed_match or not product_match:
        raise ValueError("Invalid MIXER block format")

    # Extract values
    properties["kind"] = unit_match.group(1).strip()
    node["label"] = unit_match.group(2).strip()
    properties["description"] = unit_match.group(3).strip()
    properties["in"] = feed_match.group(1).split(",")
    properties["out"] = [product_match.group(1).strip()]

    return node


def parse_hx_block(block):
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Extract UNIT, UID, and NAME
    unit_match = re.search(r"HX\s+UID=([\w\-]+), NAME=(.+)", block)
    if unit_match:
        properties["kind"] = "HX"
        node["label"] = unit_match.group(1).strip()
        properties["description"] = unit_match.group(2).strip()

    # Extract inlets
    inlets_match = re.search(r"FEED=([\w\-]+)", block)
    if inlets_match:
        properties["in"].append(inlets_match.group(1).strip())

    # Extract outlets
    outlets_match = re.search(r"M=([\w\-]+)", block)
    if outlets_match:
        properties["out"].append(outlets_match.group(1).strip())

    return node


def parse_pump_block(block):
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Regular expressions to extract required components
    unit_pattern = r"^\s*(\w+)\s+UID=([\w-]+),\s+NAME=(.+)$"
    feed_pattern = r"\bFEED\s+([\w-]+)"
    product_pattern = r"\bPRODUCT\s+M=([\w-]+)"

    # Match and extract the components
    unit_match = re.search(unit_pattern, block, re.MULTILINE)
    feed_match = re.search(feed_pattern, block)
    product_match = re.search(product_pattern, block)

    if not unit_match or not feed_match or not product_match:
        raise ValueError("Invalid PUMP block format")

    # Extract values
    properties["kind"] = unit_match.group(1).strip()
    node["label"] = unit_match.group(2).strip()
    properties["description"] = unit_match.group(3).strip()
    properties["in"] = feed_match.group(1).strip()
    properties["out"] = product_match.group(1).strip()

    return node


def parse_splitter_block(block):
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Regular expressions to extract components
    unit_pattern = r"^\s*(\w+)\s+UID=([\w-]+),\s+NAME=(.+)$"
    feed_pattern = r"\bFEED\s+([\w-]+)"
    product_pattern = r"\bPRODUCT\s+(?:M=([\w-]+),\s+)*M=([\w-]+)"

    # Match and extract components
    unit_match = re.search(unit_pattern, block, re.MULTILINE)
    feed_match = re.search(feed_pattern, block)
    product_matches = re.findall(product_pattern, block)

    if not unit_match or not feed_match or not product_matches:
        raise ValueError("Invalid SPLITTER block format")

    # Extract values
    properties["kind"] = unit_match.group(1).strip()
    node["label"] = unit_match.group(2).strip()
    properties["description"] = unit_match.group(3).strip()
    properties["in"] = [feed_match.group(1).strip()]

    # Flatten and collect all product streams
    properties["out"] = [
        match for sublist in product_matches for match in sublist if match
    ]

    return node


def parse_column_block(block):
    # Dictionary to store parsed values
    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "outT": [],
        "outB": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    # Extract UNIT, UID, and NAME
    unit_match = re.search(r"COLUMN UID=([\w\-]+), NAME=(.+)", block)
    if unit_match:
        properties["kind"] = "COLUMN"
        node["label"] = unit_match.group(1).strip()
        properties["description"] = unit_match.group(2).strip()

    # Extract inlets
    inlets_match = re.search(r"FEED\s+([\w\-]+)", block)
    if inlets_match:
        properties["in"].append(inlets_match.group(1).strip())

    # Extract outlets (OVHD and BTMS)
    outlets_match = re.search(r"OVHD\(M\)=(.*?),.*?BTMS\(M\)=(.*?),", block)
    if outlets_match:
        properties["outT"].append(outlets_match.group(1).strip())  # Top outlet
        properties["outB"].append(outlets_match.group(2).strip())  # Bottom outlet
        properties["out"].extend(properties["outT"] + properties["outB"])

    return node
