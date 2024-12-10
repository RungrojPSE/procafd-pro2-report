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
    const container = document.getElementById('network');
    const networkData = { nodes, edges };
    const options = {
      edges: {
        arrows: {
          to: { enabled: true, scaleFactor: 1.2 }, // Customize arrow size
        },
        color: {
          color: '#848484', // Edge color
          highlight: '#ff0000', // Highlight color
        },
        font: {
          align: 'top', // Align edge labels
        },
      },
    };

    // Initialize the network
    new vis.Network(container, networkData, options);
  })
  .catch(error => {
    console.error('Error fetching the JSON data:', error);
  });
