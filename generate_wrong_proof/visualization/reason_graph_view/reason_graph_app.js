const GRAPH_DATA = window.GRAPH_DATA;
const EDGE_COLORS = window.EDGE_COLORS;
const FAMILY_COLORS = window.FAMILY_COLORS;


function showError(message) {
  const overview = document.getElementById("overview");
  overview.innerHTML = `<div id="error-message">${message}</div>`;
}

function edgeSource(edge) {
  return edge[0];
}


function edgeTarget(edge) {
  return edge[1];
}


function edgeSemantic(edge) {
  return edge[2] || "related";
}


function edgeKind(edge) {
  return edge[3] || edgeSemantic(edge);
}


function edgeWeight(edge) {
  return edge[4] || 1;
}


function edgeColor(semantic) {
  return EDGE_COLORS[semantic] || EDGE_COLORS.related;
}


function nodeFamily(nodeId) {
  for (const [family, nodes] of Object.entries(GRAPH_DATA.families)) {
    if (nodes.includes(nodeId)) {
      return family;
    }
  }

  return "other";
}


function makeGroupStyles() {
  const groups = {};

  Object.keys(FAMILY_COLORS).forEach(function(family) {
    groups[family] = {
      color: {
        background: FAMILY_COLORS[family],
        border: "#333333",
        highlight: {
          background: FAMILY_COLORS[family],
          border: "#000000"
        }
      },
      font: {
        color: "#111111"
      }
    };
  });

  return groups;
}


function familyLabel(family) {
  const reasonCount = GRAPH_DATA.families[family].length;
  const internalCount = GRAPH_DATA.family_edges[family].length;

  return `${family}\n${reasonCount} reasons\n${internalCount} internal`;
}


function semanticCounts(edges) {
  const counts = {};

  edges.forEach(function(edge) {
    const semantic = edgeSemantic(edge);
    counts[semantic] = (counts[semantic] || 0) + 1;
  });

  return counts;
}


function mainSemantic(edges) {
  const counts = semanticCounts(edges);
  const sortedCounts = Object.entries(counts).sort(function(a, b) {
    return b[1] - a[1];
  });

  if (sortedCounts.length === 0) {
    return "related";
  }

  return sortedCounts[0][0];
}


function semanticSummary(edges) {
  return Object.entries(semanticCounts(edges))
    .sort(function(a, b) {
      return b[1] - a[1];
    })
    .map(function(entry) {
      return `${entry[0]}: ${entry[1]}`;
    })
    .join("\n");
}


function makeOverviewNodes() {
  return Object.keys(GRAPH_DATA.families).map(function(family) {
    return {
      id: family,
      label: familyLabel(family),
      title: `Click to open internal graph for ${family}`
    };
  });
}


function makeOverviewEdges() {
  return Object.entries(GRAPH_DATA.pair_edges).map(function(entry, index) {
    const pairId = entry[0];
    const edges = entry[1];
    const pair = pairId.split("|||");

    const familyA = pair[0];
    const familyB = pair[1];
    const count = edges.length;
    const semantic = mainSemantic(edges);

    return {
      id: pairId,
      from: familyA,
      to: familyB,
      label: String(count),
      title: `${familyA} ↔ ${familyB}\n${count} exact reason connections\n${semanticSummary(edges)}`,
      color: {
        color: edgeColor(semantic)
      },
      width: 1.5 + 0.25 * count,
      smooth: {
        enabled: true,
        type: "curvedCW",
        roundness: 0.15 + 0.05 * (index % 5)
      }
    };
  });
}


function makeReasonNodes(reasonIds) {
  return reasonIds.map(function(reasonId) {
    return {
      id: reasonId,
      label: reasonId,
      group: nodeFamily(reasonId),
      title: nodeFamily(reasonId)
    };
  });
}


function makeReasonNodesFromEdges(edges) {
  const reasonIds = new Set();

  edges.forEach(function(edge) {
    reasonIds.add(edgeSource(edge));
    reasonIds.add(edgeTarget(edge));
  });

  return makeReasonNodes(Array.from(reasonIds).sort());
}


function makeDetailEdges(edges) {
  return edges.map(function(edge) {
    const source = edgeSource(edge);
    const target = edgeTarget(edge);
    const semantic = edgeSemantic(edge);
    const kind = edgeKind(edge);
    const weight = edgeWeight(edge);

    return {
      from: source,
      to: target,
      title: `${source} → ${target}\n${kind}\n${semantic}\nweight: ${weight}`,
      color: {
        color: edgeColor(semantic)
      },
      width: 1.5 + weight,
      smooth: {
        type: "dynamic"
      }
    };
  });
}


function makeFamilyDetail(family) {
  const edges = GRAPH_DATA.family_edges[family] || [];

  return {
    title: `Internal graph: ${family}`,
    nodes: makeReasonNodes(GRAPH_DATA.families[family]),
    edges: makeDetailEdges(edges)
  };
}


function makePairDetail(pairId) {
  const edges = GRAPH_DATA.pair_edges[pairId] || [];
  const pair = pairId.split("|||");

  return {
    title: `Cross-family graph: ${pair[0]} - ${pair[1]}`,
    nodes: makeReasonNodesFromEdges(edges),
    edges: makeDetailEdges(edges)
  };
}


function openModal(title) {
  document.getElementById("modal-title").innerText = title;
  document.getElementById("modal").style.display = "block";
}


function closeModal() {
  document.getElementById("modal").style.display = "none";
}


function renderDetailGraph(detail) {
  openModal(detail.title);

  const container = document.getElementById("detail-network");
  container.innerHTML = "";

  const data = {
    nodes: new vis.DataSet(detail.nodes),
    edges: new vis.DataSet(detail.edges)
  };

  const options = {
    autoResize: true,

    nodes: {
      shape: "box",
      margin: 10,
      widthConstraint: {
        minimum: 80,
        maximum: 180
      },
      font: {
        size: 15,
        face: "Arial"
      },
      borderWidth: 1.5,
      shadow: false
    },

    edges: {
      width: 2,
      smooth: {
        enabled: true,
        type: "dynamic"
      }
    },

    groups: makeGroupStyles(),

    physics: {
      enabled: true,
      solver: "forceAtlas2Based",
      forceAtlas2Based: {
        gravitationalConstant: -70,
        centralGravity: 0.012,
        springLength: 170,
        springConstant: 0.055,
        damping: 0.6,
        avoidOverlap: 1.0
      },
      stabilization: {
        enabled: true,
        iterations: 700
      }
    },

    interaction: {
      hover: true,
      tooltipDelay: 80
    }
  };

  const network = new vis.Network(container, data, options);

  network.once("stabilizationIterationsDone", function() {
    network.setOptions({
      physics: false
    });

    network.fit({
      animation: true
    });
  });
}


function renderOverview() {
  const container = document.getElementById("overview");

  const data = {
    nodes: new vis.DataSet(makeOverviewNodes()),
    edges: new vis.DataSet(makeOverviewEdges())
  };

  const options = {
    autoResize: true,

    nodes: {
      shape: "box",
      margin: 10,
      widthConstraint: {
        minimum: 110,
        maximum: 190
      },
      font: {
        size: 15,
        face: "Arial"
      },
      color: {
        background: "#ffffff",
        border: "#333333",
        highlight: {
          background: "#f7f7f7",
          border: "#000000"
        }
      },
      borderWidth: 1.5,
      shadow: false
    },

    edges: {
      font: {
        size: 13,
        align: "middle",
        strokeWidth: 5,
        strokeColor: "#ffffff"
      },
      smooth: {
        enabled: true,
        type: "dynamic"
      },
      selectionWidth: 3
    },

    physics: {
      enabled: true,
      solver: "forceAtlas2Based",
      forceAtlas2Based: {
        gravitationalConstant: -180,
        centralGravity: 0.015,
        springLength: 300,
        springConstant: 0.035,
        damping: 0.7,
        avoidOverlap: 1.2
      },
      stabilization: {
        enabled: true,
        iterations: 1000
      }
    },

    interaction: {
      hover: true,
      tooltipDelay: 80
    }
  };

  const network = new vis.Network(container, data, options);

  network.once("stabilizationIterationsDone", function() {
    network.setOptions({
      physics: false
    });

    network.fit({
      animation: true
    });
  });

  network.on("click", function(params) {
    if (params.nodes.length > 0) {
      const family = params.nodes[0];
      renderDetailGraph(makeFamilyDetail(family));
      return;
    }

    if (params.edges.length > 0) {
      const pairId = params.edges[0];
      renderDetailGraph(makePairDetail(pairId));
      return;
    }
  });
}


function initializeReasonGraph() {
  document.getElementById("close").onclick = closeModal;

  window.onclick = function(event) {
    const modal = document.getElementById("modal");

    if (event.target === modal) {
      closeModal();
    }
  };

  renderOverview();
}


initializeReasonGraph();
