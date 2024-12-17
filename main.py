from operationUnits import * 
from graph import *
import openpyxl
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process an Excel report.")
    parser.add_argument("--report", type=str, required=True, help="Path to the Excel file")
    args = parser.parse_args()
    filename = args.report

    separate_script(filename)
    nodes, edges, components = parse_ctx()
    nodes = assign_level(nodes, edges)

    processes = parse_process_data(nodes)
    roles = [
        { "label": "Input Components", "value": "#63a2ff" },
        { "label": "Recycled Components", "value": "#6EC207" },
        { "label": "Released Components", "value": "#f49689" },
        { "label": "Output Components", "value": "#fdc62c" },
        { "label": "Linked Components", "value": "#f9f9f9" }
    ]
    esfiles = ["(iC)","(mABC)<1<2","[<(iAB)]","(eABC)","(reABC/ABCDE)","(eABCDE)","(flAB/ABECD)","[(prgAB/AB)[(oAB)](cAB)1]","(dlAB/CDE)","[(oAB)]","(dlD/CE)","[(eD)(oD)]","(dlC/E)","[(eE)(oE)]","(prgC/C)","[(oC)]","(pC)2"]

    nodes, edges = hypergraph_nodes_edges(nodes, edges)
    reassign_ids(nodes, edges)
    nodes, edges = hierarchical_topological_sort(nodes, edges)
    create_graph_data2(components, processes, roles, esfiles, nodes, edges, "lv3a.json")


    df = get_stream_table(filename)
    streams = get_stream_data(df)
    nodes_data = []
    for n in nodes:
        nodes_data.append({
          'id': n['id'],
          'txt': streams[n['label']]
        })

    create_graph_data(nodes_data, [], "lv3b.json")

if __name__ == "__main__":
    main()


