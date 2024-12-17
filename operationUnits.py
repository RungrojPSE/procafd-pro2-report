import re
import json
import string
import pandas as pd
import numpy as np


def separate_script(filename='HDA-PRO2-Summary Report.xlsx'):
    # Load the Excel file
    filename = 'HDA-PRO2-Summary Report.xlsx'
    excel_file = pd.ExcelFile(filename)

    # Get the sheet names
    sheet_names = excel_file.sheet_names
    df = pd.read_excel(filename, sheet_name=sheet_names[1])

    # Extract non-null values from the 'Index' column
    text_data = df['Index'].dropna().tolist()

    # Write data to a text file starting from the first line containing "Generated"
    write_flag = False  # Flag to start writing when "Generated" is found
    with open("pro2-temp.txt", "w") as file:
        for line in text_data:
            if not write_flag:
                if "Generated" in line:  # Check if "Generated" exists in the current line
                    write_flag = True
            if write_flag:
                file.write(line + "\n")


def get_stream_table(filename='HDA-PRO2-Summary Report.xlsx'):

    # Load Excel file and sheet
    # filename = 'HDA-PRO2-Summary Report.xlsx'
    sheet_name = 3  # Specify the sheet index or name
    df = pd.read_excel(filename, sheet_name=sheet_name, header=None)  # Load without headers

    # Find the starting position of the table (cell containing "Stream (Summary)")
    start_row, start_col = None, None
    rows, columns = df.shape

    for i in range(rows):
        for j in range(columns):
            if "Stream  (Summary)" in str(df.iloc[i, j]):
                start_row, start_col = i, j
                break
        if start_row is not None:
            break

    # print(f"Start position: row {start_row}, column {start_col}")

    df = pd.read_excel(filename, sheet_name=sheet_name, skiprows=start_row)
    df = df.dropna(axis=1, how='all')

    return df

def get_stream_data(df):
    d_txt = {}
    for stream in df.columns[2:]:
        txt = []
        nan_count = 0
        for index, row in df.iterrows():
            if pd.isna(row['UOM']):
                s = f"{row['Stream  (Summary)']}: {row[stream]}"
            else:
                if pd.isna(row[stream]):
                    s = f"{row['Stream  (Summary)']} ({row['UOM']}):"
                else:
                    s = f"{row['Stream  (Summary)']} ({row['UOM']}): {row[stream]}"
            txt.append(s)

            if pd.isna(row[stream]):
                nan_count += 1  # Increment by 1
            if nan_count == 3:
                break

        txt = txt[:-1]
        d_txt[stream] = txt

    return d_txt



def parse_ctx():
    # 1. get pro2 script
    file_path = "pro2-temp.txt"
    with open(file_path, "r") as file:
        text_content = file.read()

    # 2. slice data into section {TITLE, COMPONENT DATA, ...}
    # 2.1 then parse strating stream data
    # 2.2 then parse unit operations
    sections = slice_section(text_content)
    nodes = []
    for text in sections:
        if text.startswith("COMPONENT DATA"):
            components = parse_component_data(text)
        elif text.startswith("STREAM DATA"):
            nodes.extend(parse_stream_data(text))
        elif text.startswith("UNIT OPERATIONS"):
            nodes.extend(parse_unit_operations(text))

    # 3. assign id to each node
    node_id = 0
    for node in nodes:
        node_id += 1
        node["id"] = node_id

    # create ending nodes
    streams = set()
    seen_streams = set()

    #   get all streams
    for node in nodes:
        for st in node["properties"]["in"]:
            if st not in streams:
                streams.add(st)
        for st in node["properties"]["out"]:
            if st not in streams:
                streams.add(st)

    #   get linked streams
    for node in nodes:
        for label in node["properties"]["out"]:
            for target_node in nodes:
                if label in target_node["properties"]["in"]:
                    if label not in seen_streams:
                        seen_streams.add(label)

    ending_stream = streams - seen_streams
    for st in ending_stream:
        node_id += 1
        properties = {
            "kind": "END",
            "in": [st],
            "out": [],
        }
        nodes.append(
            {"id": node_id, "label": st, "properties": properties}
        )


    # print(ending_nodes)
    # Create edges
    edges = []
    edge_id = 0
    seen_edges = set()  # To track unique edges based on 'from' and 'to'

    for node in nodes:
        for label in node["properties"]["out"]:
            for target_node in nodes:
                if label in target_node["properties"]["in"]:
                    edge = (node["id"], target_node["id"])  # Define the edge as a tuple
                    if edge not in seen_edges:  # Check if the edge already exists
                        edge_id += 1
                        edges.append({"id": edge_id, "from": edge[0], "to": edge[1], "label": label})
                        seen_edges.add(edge)  # Mark this edge as seen

    # for node in nodes:
    #     for inlet in node["properties"]["in"]:
    #         for source_node in nodes:
    #             if inlet in source_node["properties"]["out"]:
    #                 edge = (source_node["id"], node["id"])  # Define the edge as a tuple
    #                 if edge not in seen_edges:  # Check if the edge already exists
    #                     edge_id += 1
    #                     edges.append({"id": id, "from": edge[0], "to": edge[1]})
    #                     seen_edges.add(edge)  # Mark this edge as seen

    # Output edges
    # print(edges)

    # create_graph_data(nodes, edges)

    print(nodes)

    return nodes, edges, components

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



def create_graph_data(nodes, edges, file_path="vis-plot/data.json"):
    
    # Define nodes and edges
    data = {
        "nodes": nodes,
        "edges": edges
    }

    # Write the data to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    # print("data.json created successfully!")
    

def create_graph_data2(components, processes, roles, esfiles, nodes, edges, file_path="lv3a.json"):
    
    # Define nodes and edges
    data = {
        "components": components,
        "processes": processes,
        "roles": roles,
        "esfiles": esfiles,
        "nodes": nodes,
        "edges": edges
    }

    # Write the data to a JSON file
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)

    # print("data.json created successfully!")
    

def parse_process_data(nodes):
    units = {}
    for n in nodes:
        if n['properties']['kind'] not in ['START', 'END']:
            kind = n['properties']['kind']
            # Initialize the list if the kind is not already in units
            if kind not in units:
                units[kind] = []
            units[kind].append(n['label'])

    processes = []
    for key, val in units.items(): 
        processes.append({
            'label': ", ".join(val),
            'value': key
        })

    return processes


def parse_component_data(text_content):
    # Regular expression to extract chemical names
    pattern = r"\b\d+,([A-Z]+)"

    # Find all matches
    matches = re.findall(pattern, text_content)

    # Create alphabetical labels (A, B, C...)
    labels = string.ascii_uppercase

    # Build the output JSON structure
    output = [{"label": labels[i], "value": matches[i]} for i in range(len(matches))]

    return output

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

    unit_objs = []
    for txt in unit_blocks:
        unit_objs.append(parse_unit(txt))

    return unit_objs

def parse_unit(block):
    unit_pattern = r"^\s*(\w+)\s+UID=([\w\-]+),\s+NAME=(.+)$"

    feed_pattern1 = r"\bFEED\s+([\w\-]+)"  # CONREACTOR, COMPRESSOR, FLASH, PUMP, SPLITTER, COLUMN
    feed_pattern2 = r"\bFEED=([\w\-]+)"  # HX
    feed_pattern3 = r"\bFEED\s+([\w\-,]+)"  # MIXER

    product_pattern1 = r"\bPRODUCT\s+M=([\w\-]+)"  # CONREACTOR, COMPRESSOR, FLASH, PUMP, COLUMN
    product_pattern2 = r"\bPRODUCT\s+V=([\w\-]+),\s+W=([\w\-]+)"  # FLASH
    product_pattern3 = r"\bPRODUCT\s+M=([\w\-]+),\s+M=([\w\-]+)"  # SPLITTER
    product_pattern4 = r"\bPRODUCT\s+OVHD\(M\)=([\w\-]+),.*?BTMS\(M\)=([\w\-]+),"  # COLUMN
    product_pattern5 = r"\bFEED=.*?,\s+M=([\w\-]+)"  # HX

    units = {
        "CONREACTOR": {"feed": feed_pattern1, "product": product_pattern1},
        "COMPRESSOR": {"feed": feed_pattern1, "product": product_pattern1},
        "FLASH":      {"feed": feed_pattern1, "product": product_pattern2},
        "PUMP":       {"feed": feed_pattern1, "product": product_pattern1},
        "SPLITTER":   {"feed": feed_pattern1, "product": product_pattern3},
        "COLUMN":     {"feed": feed_pattern1, "product": product_pattern4},
        "HX":         {"feed": feed_pattern2, "product": product_pattern5},
        "MIXER":      {"feed": feed_pattern3, "product": product_pattern1},
    }

    properties = {
        "kind": None,
        "in": [],
        "out": [],
        "description": None,
    }
    node = {"id": None, "label": None, "properties": properties}

    unit_match = re.search(unit_pattern, block, re.MULTILINE)
    if unit_match:
        unit = unit_match.group(1).strip()
        node["label"] = unit_match.group(2).strip()
        properties["kind"] = unit
        properties["description"] = unit_match.group(3).strip()

        # Match inlets
        feed_pattern = units[unit]["feed"]
        inlets_match = re.search(feed_pattern, block)
        if inlets_match:
            if unit == "MIXER":
                properties["in"].extend(inlets_match.group(1).split(","))
            else:
                properties["in"].append(inlets_match.group(1).strip())

        # Match outlets
        product_pattern = units[unit]["product"]
        outlets_match = re.search(product_pattern, block)
        
        # print(outlets_match)

        if outlets_match:
            # Handle multiple group matches if necessary
            for group_index in range(1, len(outlets_match.groups()) + 1):
                properties["out"].append(outlets_match.group(group_index).strip())

    return node



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
