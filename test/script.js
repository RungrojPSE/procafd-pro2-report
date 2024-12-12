// Path to the JSON file or API URL
const jsonUrl = 'data.json';

// Fetch the JSON data
fetch(jsonUrl)
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    // Create a vis.js DataSet for nodes and edges
    const nodes = new vis.DataSet(data.nodes);
    const edges = new vis.DataSet(data.edges);

    // Create a network
    // const nodes = new vis.DataSet([
    //   { id: 1, label: 'Node 1', level: 0 },
    //   { id: 2, label: 'Node 2', level: 1 },
    //   { id: 3, label: 'Node 3', level: 1 },
    //   { id: 4, label: 'Node 4', level: 2 },
    //   { id: 5, label: 'Node 5', level: 2 },
    // ]);
    
    // const edges = new vis.DataSet([
    //   { from: 1, to: 2 },
    //   { from: 1, to: 3 },
    //   { from: 2, to: 4 },
    //   { from: 3, to: 5 },
    // ]);
    
    // Create a network
    const container = document.getElementById('network');
    const networkData = { nodes, edges };
    const options = {
      nodes: {
        color: {
          background: "#f9f9f9",
          border: "#666",
        },
      },
      edges: {
        arrows: {
          to: {
            enabled: true,
            scaleFactor: 0.7,
          },
        },
        // color: {
        //   color: '#848484', // Edge color
        //   highlight: '#ff0000', // Highlight color
        // },
        // font: {
        //   align: 'top', // Align edge labels
        // },
        smooth: {
          enabled: true,
          type: "cubicBezier", // 'continuous', 'cubicBezier'
          forceDirection: "horizontal",
          roundness: 0.4,
        },
      },
      layout: {
        hierarchical: {
          direction: "LR",
          // sortMethod: 'directed', // Organizes nodes based on directed edges
          // levelSeparation: 100, // Distance between levels
          // nodeSpacing: 150, // Distance between nodes
        },
      },
      //   physics: {
      //     stabilization: true,
      //     barnesHut: {
      //       gravitationalConstant: -10000,
      //       springConstant: 0.001,
      //       springLength: 200,
      //     },
      //   },
      physics: {
        enabled: false, // Disable physics to prevent nodes from bouncing back
      },
      interaction: {
        hover: false,
        // dragNodes: true, // Allow dragging nodes without them bouncing back
      },
    };

    // Initialize the network
    new vis.Network(container, networkData, options);
  })
  .catch(error => {
    console.error('Error fetching the JSON data:', error);
  });
