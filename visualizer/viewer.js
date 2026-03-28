const canvas = document.getElementById("scene");
const ctx = canvas.getContext("2d");
const legendElement = document.getElementById("legend");
const statusElement = document.getElementById("status");
const objectCountElement = document.getElementById("object-count");
const pointCountElement = document.getElementById("point-count");
const fileInput = document.getElementById("file-input");
const openFileButton = document.getElementById("open-file-button");
const fileNameElement = document.getElementById("file-name");
const resetViewButton = document.getElementById("reset-view-button");
const loadDefaultButton = document.getElementById("load-default-button");
const rotateXInput = document.getElementById("rotate-x");
const rotateYInput = document.getElementById("rotate-y");
const rotateZInput = document.getElementById("rotate-z");
const rotateXValue = document.getElementById("rotate-x-value");
const rotateYValue = document.getElementById("rotate-y-value");
const rotateZValue = document.getElementById("rotate-z-value");

const palette = [
  "#7a72e8",
  "#5fd6b6",
  "#f28f6b",
  "#5177d8",
  "#9a6ff0",
  "#76c46f",
  "#f16a8b",
  "#42b0c8"
];

const axisColors = {
  x: "#f15d5d",
  y: "#7fb518",
  z: "#4d96ff"
};

const state = {
  orientation: [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ],
  axisInputDegrees: {
    x: 0,
    y: 0,
    z: 0
  },
  panX: 0,
  panY: 0,
  zoom: 30,
  defaultZoom: 30,
  scene: null,
  hiddenObjectNames: new Set(),
  pointerActive: false,
  lastPointerX: 0,
  lastPointerY: 0
};

function isObjectVisible(name) {
  return !state.hiddenObjectNames.has(name);
}

function toggleObjectVisibility(name) {
  if (state.hiddenObjectNames.has(name)) {
    state.hiddenObjectNames.delete(name);
  } else {
    state.hiddenObjectNames.add(name);
  }
}

function dedupePoints(points) {
  const seen = new Set();
  return points.filter((point) => {
    const key = point.join(",");
    if (seen.has(key)) {
      return false;
    }
    seen.add(key);
    return true;
  });
}

function buildEdges(points) {
  const pointKeys = new Set(points.map((point) => point.join(",")));
  const directions = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ];

  const edges = [];
  points.forEach((point) => {
    directions.forEach(([dx, dy, dz]) => {
      const neighbor = [point[0] + dx, point[1] + dy, point[2] + dz];
      if (pointKeys.has(neighbor.join(","))) {
        edges.push([point, neighbor]);
      }
    });
  });

  return edges;
}

function flattenObjects(rawData) {
  const objects = Object.entries(rawData).map(([name, segments], index) => {
    const points = dedupePoints(Object.values(segments).flat());
    return {
      name,
      color: palette[index % palette.length],
      points,
      edges: buildEdges(points)
    };
  });

  if (!objects.length) {
    throw new Error("The JSON file did not contain any objects.");
  }

  const allPoints = objects.flatMap((object) => object.points);
  const xs = allPoints.map((point) => point[0]);
  const ys = allPoints.map((point) => point[1]);
  const zs = allPoints.map((point) => point[2]);

  const bounds = {
    minX: Math.min(...xs),
    maxX: Math.max(...xs),
    minY: Math.min(...ys),
    maxY: Math.max(...ys),
    minZ: Math.min(...zs),
    maxZ: Math.max(...zs)
  };

  const center = {
    x: (bounds.minX + bounds.maxX) / 2,
    y: (bounds.minY + bounds.maxY) / 2,
    z: (bounds.minZ + bounds.maxZ) / 2
  };

  return {
    objects,
    bounds,
    center,
    totalPoints: allPoints.length
  };
}

function parseHexColor(hex) {
  const numeric = Number.parseInt(hex.slice(1), 16);
  return {
    r: (numeric >> 16) & 0xff,
    g: (numeric >> 8) & 0xff,
    b: numeric & 0xff
  };
}

function withAlpha(hex, alpha) {
  const { r, g, b } = parseHexColor(hex);
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  const rect = canvas.getBoundingClientRect();
  canvas.width = rect.width * dpr;
  canvas.height = rect.height * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  render();
}

function rotatePoint(point) {
  const translatedX = point[0] - state.scene.center.x;
  const translatedY = point[1] - state.scene.center.y;
  const translatedZ = point[2] - state.scene.center.z;

  const x = state.orientation[0][0] * translatedX
    + state.orientation[0][1] * translatedY
    + state.orientation[0][2] * translatedZ;
  const y = state.orientation[1][0] * translatedX
    + state.orientation[1][1] * translatedY
    + state.orientation[1][2] * translatedZ;
  const z = state.orientation[2][0] * translatedX
    + state.orientation[2][1] * translatedY
    + state.orientation[2][2] * translatedZ;

  return {
    x,
    y,
    z
  };
}

function degreesToRadians(angle) {
  return (Number(angle) * Math.PI) / 180;
}

function normalizeDegrees(angle) {
  return ((angle + 180) % 360 + 360) % 360 - 180;
}

function multiplyMatrix3x3(left, right) {
  return [
    [
      left[0][0] * right[0][0] + left[0][1] * right[1][0] + left[0][2] * right[2][0],
      left[0][0] * right[0][1] + left[0][1] * right[1][1] + left[0][2] * right[2][1],
      left[0][0] * right[0][2] + left[0][1] * right[1][2] + left[0][2] * right[2][2]
    ],
    [
      left[1][0] * right[0][0] + left[1][1] * right[1][0] + left[1][2] * right[2][0],
      left[1][0] * right[0][1] + left[1][1] * right[1][1] + left[1][2] * right[2][1],
      left[1][0] * right[0][2] + left[1][1] * right[1][2] + left[1][2] * right[2][2]
    ],
    [
      left[2][0] * right[0][0] + left[2][1] * right[1][0] + left[2][2] * right[2][0],
      left[2][0] * right[0][1] + left[2][1] * right[1][1] + left[2][2] * right[2][1],
      left[2][0] * right[0][2] + left[2][1] * right[1][2] + left[2][2] * right[2][2]
    ]
  ];
}

function getAxisRotationMatrix(axis, radians) {
  const c = Math.cos(radians);
  const s = Math.sin(radians);

  if (axis === "x") {
    return [
      [1, 0, 0],
      [0, c, -s],
      [0, s, c]
    ];
  }

  if (axis === "y") {
    return [
      [c, 0, s],
      [0, 1, 0],
      [-s, 0, c]
    ];
  }

  return [
    [c, -s, 0],
    [s, c, 0],
    [0, 0, 1]
  ];
}

function applyLocalRotation(axis, radians) {
  state.orientation = multiplyMatrix3x3(state.orientation, getAxisRotationMatrix(axis, radians));
}

function resetOrientation() {
  state.orientation = [
    [1, 0, 0],
    [0, 1, 0],
    [0, 0, 1]
  ];
  state.axisInputDegrees = {
    x: 0,
    y: 0,
    z: 0
  };
}

function syncRotationControls() {
  const xDeg = Math.round(state.axisInputDegrees.x);
  const yDeg = Math.round(state.axisInputDegrees.y);
  const zDeg = Math.round(state.axisInputDegrees.z);

  rotateXInput.value = String(xDeg);
  rotateYInput.value = String(yDeg);
  rotateZInput.value = String(zDeg);

  rotateXValue.textContent = `${xDeg}°`;
  rotateYValue.textContent = `${yDeg}°`;
  rotateZValue.textContent = `${zDeg}°`;
}

function projectRotated(rotatedPoint) {
  return {
    x: (rotatedPoint.x - rotatedPoint.z) * state.zoom * 0.86,
    y: (-rotatedPoint.y - (rotatedPoint.x + rotatedPoint.z) * 0.5) * state.zoom,
    depth: rotatedPoint.x + rotatedPoint.z - rotatedPoint.y * 0.35
  };
}

function measureScene(projectedItems) {
  if (!projectedItems.length) {
    return { minX: 0, maxX: 0, minY: 0, maxY: 0 };
  }

  return projectedItems.reduce((accumulator, item) => ({
    minX: Math.min(accumulator.minX, item.x),
    maxX: Math.max(accumulator.maxX, item.x),
    minY: Math.min(accumulator.minY, item.y),
    maxY: Math.max(accumulator.maxY, item.y)
  }), {
    minX: Number.POSITIVE_INFINITY,
    maxX: Number.NEGATIVE_INFINITY,
    minY: Number.POSITIVE_INFINITY,
    maxY: Number.NEGATIVE_INFINITY
  });
}

function getCanvasOffset(origin) {
  return {
    x: canvas.clientWidth / 2 - origin.x + state.panX,
    y: canvas.clientHeight / 2 - origin.y + state.panY
  };
}

function drawLine(start, end, color, width, dash = []) {
  ctx.beginPath();
  ctx.setLineDash(dash);
  ctx.moveTo(start.x, start.y);
  ctx.lineTo(end.x, end.y);
  ctx.strokeStyle = color;
  ctx.lineWidth = width;
  ctx.lineCap = "round";
  ctx.stroke();
  ctx.setLineDash([]);
}

function drawPoint(point, color, radius) {
  ctx.beginPath();
  ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
  ctx.fillStyle = color;
  ctx.shadowColor = withAlpha(color, 0.22);
  ctx.shadowBlur = 8;
  ctx.fill();
  ctx.shadowBlur = 0;
}

function drawAxisLabel(text, point, color) {
  ctx.font = "600 22px 'Avenir Next', 'Segoe UI', sans-serif";
  ctx.fillStyle = color;
  ctx.fillText(text, point.x + 8, point.y - 8);
}

function buildProjectedScene() {
  const projectedItems = [];
  const objects = state.scene.objects.map((object) => {
    const pointMap = new Map();

    object.points.forEach((point) => {
      const projected = projectRotated(rotatePoint(point));
      pointMap.set(point.join(","), projected);
      projectedItems.push(projected);
    });

    const projectedEdges = object.edges.map(([start, end]) => {
      const projectedStart = pointMap.get(start.join(","));
      const projectedEnd = pointMap.get(end.join(","));
      return {
        start: projectedStart,
        end: projectedEnd,
        depth: (projectedStart.depth + projectedEnd.depth) / 2
      };
    });

    const projectedPoints = object.points.map((point) => ({
      ...pointMap.get(point.join(",")),
      key: point.join(",")
    }));

    return {
      ...object,
      projectedEdges,
      projectedPoints
    };
  });

  const axisLength = Math.max(
    state.scene.bounds.maxX - state.scene.bounds.minX,
    state.scene.bounds.maxY - state.scene.bounds.minY,
    state.scene.bounds.maxZ - state.scene.bounds.minZ
  ) + 2;

  const axes = [
    { label: "x", color: axisColors.x, start: [0, 0, 0], end: [axisLength, 0, 0] },
    { label: "y", color: axisColors.y, start: [0, 0, 0], end: [0, axisLength, 0] },
    { label: "z", color: axisColors.z, start: [0, 0, 0], end: [0, 0, axisLength] }
  ].map((axis) => {
    const start = projectRotated(rotatePoint(axis.start));
    const end = projectRotated(rotatePoint(axis.end));
    projectedItems.push(start, end);
    return {
      ...axis,
      start,
      end
    };
  });

  return {
    objects,
    axes,
    origin: projectRotated(rotatePoint([0, 0, 0])),
    extents: measureScene(projectedItems)
  };
}

function render() {
  ctx.clearRect(0, 0, canvas.clientWidth, canvas.clientHeight);

  if (!state.scene) {
    return;
  }

  const projectedScene = buildProjectedScene();
  const offset = getCanvasOffset(projectedScene.origin);

  ctx.save();
  ctx.translate(offset.x, offset.y);

  projectedScene.axes.forEach((axis) => {
    drawLine(axis.start, axis.end, axis.color, 2.4);
    drawAxisLabel(axis.label, axis.end, axis.color);
  });

  const visibleObjects = projectedScene.objects.filter((object) => isObjectVisible(object.name));

  const edges = visibleObjects
    .flatMap((object) => object.projectedEdges.map((edge) => ({
      ...edge,
      color: withAlpha(object.color, 0.14)
    })))
    .sort((left, right) => left.depth - right.depth);

  edges.forEach((edge) => {
    drawLine(edge.start, edge.end, edge.color, 1.5);
  });

  const points = visibleObjects
    .flatMap((object) => object.projectedPoints.map((point) => ({
      ...point,
      color: object.color
    })))
    .sort((left, right) => left.depth - right.depth);

  const radius = Math.max(4.5, Math.min(7.2, state.zoom * 0.15));
  points.forEach((point) => {
    drawPoint(point, point.color, radius);
  });

  ctx.restore();
}

function renderLegend(objects) {
  legendElement.innerHTML = "";

  objects.forEach((object) => {
    const visible = isObjectVisible(object.name);
    const item = document.createElement("div");
    item.className = "legend-item";
    item.innerHTML = `
      <span class="swatch" style="background:${object.color}"></span>
      <span class="legend-name">${object.name}</span>
      <button class="legend-toggle ${visible ? "is-on" : "is-off"}" type="button" aria-pressed="${visible}" aria-label="Toggle ${object.name}">${visible ? "On" : "Off"}</button>
      <span class="legend-count">${object.points.length} pts</span>
    `;

    const toggleButton = item.querySelector(".legend-toggle");
    toggleButton.addEventListener("click", () => {
      toggleObjectVisibility(object.name);
      renderLegend(state.scene.objects);
      render();
    });

    legendElement.appendChild(item);
  });
}

function updateStats(scene) {
  objectCountElement.textContent = String(scene.objects.length);
  pointCountElement.textContent = String(scene.totalPoints);
}

function loadScene(rawData, label) {
  state.scene = flattenObjects(rawData);
  state.hiddenObjectNames = new Set();
  renderLegend(state.scene.objects);
  updateStats(state.scene);
  statusElement.textContent = `Loaded ${label}.`;

  const spanX = state.scene.bounds.maxX - state.scene.bounds.minX + 1;
  const spanY = state.scene.bounds.maxY - state.scene.bounds.minY + 1;
  const spanZ = state.scene.bounds.maxZ - state.scene.bounds.minZ + 1;
  const isoWidthUnits = (spanX + spanZ) * 0.86;
  const isoHeightUnits = spanY + (spanX + spanZ) * 0.5;
  const widthScale = (canvas.clientWidth - 120) / Math.max(1, isoWidthUnits);
  const heightScale = (canvas.clientHeight - 120) / Math.max(1, isoHeightUnits);

  state.defaultZoom = Math.max(14, Math.min(widthScale, heightScale));
  state.zoom = state.defaultZoom;
  state.panX = 0;
  state.panY = 0;
  resetOrientation();

  syncRotationControls();

  render();
}

async function loadDefaultScene() {
  statusElement.textContent = "Loading objects.json…";
  fileNameElement.textContent = "objects.json";

  try {
    const response = await fetch("objects.json", { cache: "no-store" });
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const rawData = await response.json();
    loadScene(rawData, "objects.json");
  } catch (error) {
    fileNameElement.textContent = "No file selected";
    statusElement.textContent = "Could not load objects.json automatically. Use Open JSON File instead.";
  }
}

function readUserFile(file) {
  const reader = new FileReader();
  statusElement.textContent = `Loading ${file.name}…`;
  fileNameElement.textContent = file.name;

  reader.onload = () => {
    try {
      const rawData = JSON.parse(String(reader.result));
      loadScene(rawData, file.name);
    } catch (error) {
      fileNameElement.textContent = "No file selected";
      statusElement.textContent = "That file is not valid object JSON.";
    }
    fileInput.value = "";
  };

  reader.onerror = () => {
    fileNameElement.textContent = "No file selected";
    statusElement.textContent = "The selected file could not be read.";
    fileInput.value = "";
  };

  reader.readAsText(file);
}

function resetView() {
  resetOrientation();
  state.zoom = state.defaultZoom;
  state.panX = 0;
  state.panY = 0;
  syncRotationControls();
  render();
}

canvas.addEventListener("pointerdown", (event) => {
  state.pointerActive = true;
  state.lastPointerX = event.clientX;
  state.lastPointerY = event.clientY;
  canvas.classList.add("dragging");
  canvas.setPointerCapture(event.pointerId);
});

canvas.addEventListener("pointermove", (event) => {
  if (!state.pointerActive) {
    return;
  }

  const deltaX = event.clientX - state.lastPointerX;
  const deltaY = event.clientY - state.lastPointerY;
  state.lastPointerX = event.clientX;
  state.lastPointerY = event.clientY;

  state.panX += deltaX;
  state.panY += deltaY;
  render();
});

function releasePointer(event) {
  state.pointerActive = false;
  canvas.classList.remove("dragging");
  if (event.pointerId !== undefined && canvas.hasPointerCapture(event.pointerId)) {
    canvas.releasePointerCapture(event.pointerId);
  }
}

canvas.addEventListener("pointerup", releasePointer);
canvas.addEventListener("pointerleave", releasePointer);
canvas.addEventListener("pointercancel", releasePointer);

canvas.addEventListener("wheel", (event) => {
  event.preventDefault();
  state.zoom = Math.max(10, Math.min(120, state.zoom - event.deltaY * 0.02));
  render();
}, { passive: false });

fileInput.addEventListener("change", (event) => {
  const file = event.target.files?.[0];
  if (file) {
    readUserFile(file);
  }
});

openFileButton.addEventListener("click", () => {
  fileInput.click();
});

resetViewButton.addEventListener("click", resetView);
loadDefaultButton.addEventListener("click", loadDefaultScene);

rotateXInput.addEventListener("input", (event) => {
  const next = Number(event.target.value);
  const delta = degreesToRadians(next - state.axisInputDegrees.x);
  applyLocalRotation("x", delta);
  state.axisInputDegrees.x = next;
  syncRotationControls();
  render();
});

rotateYInput.addEventListener("input", (event) => {
  const next = Number(event.target.value);
  const delta = degreesToRadians(next - state.axisInputDegrees.y);
  applyLocalRotation("y", delta);
  state.axisInputDegrees.y = next;
  syncRotationControls();
  render();
});

rotateZInput.addEventListener("input", (event) => {
  const next = Number(event.target.value);
  const delta = degreesToRadians(next - state.axisInputDegrees.z);
  applyLocalRotation("z", delta);
  state.axisInputDegrees.z = next;
  syncRotationControls();
  render();
});

syncRotationControls();
window.addEventListener("resize", resizeCanvas);

resizeCanvas();
loadDefaultScene();
