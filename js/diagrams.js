// ===========================
// SVG Diagram Rendering & Animation
// ===========================

const SVG_NS = "http://www.w3.org/2000/svg";

// Helper functions for SVG creation
function createSVGElement(tag, attrs = {}) {
    const elem = document.createElementNS(SVG_NS, tag);
    Object.entries(attrs).forEach(([key, value]) => {
        elem.setAttribute(key, value);
    });
    return elem;
}

function createLayer(x, y, label, color = '#6366f1') {
    const g = createSVGElement('g');

    const rect = createSVGElement('rect', {
        x: x - 60,
        y: y - 20,
        width: 120,
        height: 40,
        fill: color,
        rx: 6
    });

    const text = createSVGElement('text', {
        x: x,
        y: y + 5,
        'text-anchor': 'middle',
        fill: 'white',
        'font-size': '14',
        'font-weight': '600'
    });
    text.textContent = label;

    g.appendChild(rect);
    g.appendChild(text);
    return g;
}

function createArrow(x1, y1, x2, y2, strokeWidth = 2, color = '#6366f1', opacity = 1) {
    const g = createSVGElement('g', {
        opacity: opacity
    });

    const line = createSVGElement('line', {
        x1, y1, x2, y2,
        stroke: color,
        'stroke-width': strokeWidth
    });

    // Arrow head
    const headSize = 8;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    const arrowX = x2 - headSize * Math.cos(angle - Math.PI / 6);
    const arrowY = y2 - headSize * Math.sin(angle - Math.PI / 6);
    const arrowX2 = x2 - headSize * Math.cos(angle + Math.PI / 6);
    const arrowY2 = y2 - headSize * Math.sin(angle + Math.PI / 6);

    const polygon = createSVGElement('polygon', {
        points: `${x2},${y2} ${arrowX},${arrowY} ${arrowX2},${arrowY2}`,
        fill: color
    });

    g.appendChild(line);
    g.appendChild(polygon);
    return g;
}

// ===========================
// Standard Residual Diagram
// ===========================

function renderStandardResidualDiagram() {
    const svg = document.getElementById('standard-residual-diagram');
    if (!svg) return;

    svg.innerHTML = '';

    const colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#10b981'];
    const layerY = [80, 160, 240, 320];
    const layerX = 150;
    const residualX = 400;

    // Draw layers
    layerY.forEach((y, i) => {
        const layer = createLayer(layerX, y, `Layer ${i}`, colors[i]);
        svg.appendChild(layer);
    });

    // Draw residual stream
    const residualStream = createSVGElement('rect', {
        x: residualX - 50,
        y: 40,
        width: 100,
        height: 320,
        fill: 'none',
        stroke: '#94a3b8',
        'stroke-width': 2,
        'stroke-dasharray': '5,5',
        rx: 8
    });
    svg.appendChild(residualStream);

    const streamLabel = createSVGElement('text', {
        x: residualX,
        y: 25,
        'text-anchor': 'middle',
        fill: 'var(--text-secondary)',
        'font-size': '12',
        'font-weight': '600'
    });
    streamLabel.textContent = 'Residual Stream';
    svg.appendChild(streamLabel);

    // Draw arrows from layers to residual stream (all same weight)
    layerY.forEach((y, i) => {
        const arrow = createArrow(layerX + 60, y, residualX - 50, y, 3, colors[i], 0.6);
        arrow.classList.add('arrow-animate');
        svg.appendChild(arrow);

        // Plus sign
        const plus = createSVGElement('text', {
            x: (layerX + 60 + residualX - 50) / 2,
            y: y - 10,
            'text-anchor': 'middle',
            fill: 'var(--text-secondary)',
            'font-size': '18',
            'font-weight': 'bold'
        });
        plus.textContent = '+';
        svg.appendChild(plus);
    });

    // Label: "All weights = 1"
    const label = createSVGElement('text', {
        x: residualX,
        y: 380,
        'text-anchor': 'middle',
        fill: 'var(--text-muted)',
        'font-size': '14',
        'font-style': 'italic'
    });
    label.textContent = 'All weights = 1 (fixed)';
    svg.appendChild(label);
}

// ===========================
// Comparison Diagram (Interactive)
// ===========================

function renderComparisonDiagram(transitionValue = 0) {
    const svg = document.getElementById('comparison-diagram');
    if (!svg) return;

    svg.innerHTML = '';

    const colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#10b981'];
    const layerY = [80, 160, 240, 320];
    const layerX = 150;
    const outputX = 450;
    const outputY = 200;

    // Draw layers
    layerY.forEach((y, i) => {
        const layer = createLayer(layerX, y, `L${i}`, colors[i]);
        svg.appendChild(layer);
    });

    // Draw output
    const output = createLayer(outputX, outputY, 'Output', '#f59e0b');
    svg.appendChild(output);

    // Calculate weights based on transition
    // At 0: all equal (0.25, 0.25, 0.25, 0.25)
    // At 100: attention weights (example: 0.1, 0.15, 0.35, 0.4)
    const baseWeights = [0.25, 0.25, 0.25, 0.25];
    const attnWeights = [0.1, 0.15, 0.35, 0.4];

    const t = transitionValue / 100;
    const weights = baseWeights.map((base, i) =>
        base + (attnWeights[i] - base) * t
    );

    // Draw arrows with varying thickness
    layerY.forEach((y, i) => {
        const weight = weights[i];
        const strokeWidth = 1 + weight * 12; // 1-13 range
        const opacity = 0.4 + weight * 0.6; // 0.4-1.0 range

        const arrow = createArrow(layerX + 60, y, outputX - 60, outputY, strokeWidth, colors[i], opacity);
        svg.appendChild(arrow);

        // Weight label (only show when transitioning)
        if (transitionValue > 10) {
            const weightLabel = createSVGElement('text', {
                x: (layerX + 60 + outputX - 60) / 2 + 30,
                y: y - 5,
                'text-anchor': 'middle',
                fill: colors[i],
                'font-size': '12',
                'font-weight': '600',
                opacity: t
            });
            weightLabel.textContent = weight.toFixed(2);
            svg.appendChild(weightLabel);
        }
    });
}

// ===========================
// Mechanism Diagram (How It Works)
// ===========================

function renderMechanismDiagram() {
    const svg = document.getElementById('mechanism-diagram');
    if (!svg) return;

    svg.innerHTML = '';

    const layers = [
        { x: 100, y: 100, label: 'v₀', color: '#10b981' },
        { x: 100, y: 200, label: 'v₁', color: '#3b82f6' },
        { x: 100, y: 300, label: 'v₂', color: '#6366f1' }
    ];

    const queryX = 350;
    const queryY = 200;
    const outputX = 600;
    const outputY = 200;

    // Draw value layers
    layers.forEach(({ x, y, label, color }) => {
        const layer = createLayer(x, y, label, color);
        svg.appendChild(layer);
    });

    // Draw query
    const query = createLayer(queryX, queryY, 'Qₗ', '#8b5cf6');
    svg.appendChild(query);

    // Draw output
    const output = createLayer(outputX, outputY, 'hₗ', '#f59e0b');
    svg.appendChild(output);

    // Arrows from values to query (attention computation)
    layers.forEach(({ x, y, color }, i) => {
        const arrow = createArrow(x + 60, y, queryX - 60, queryY, 2, color, 0.5);
        arrow.setAttribute('data-flow-step', '1');
        svg.appendChild(arrow);
    });

    // Arrows from query to output (weighted aggregation)
    const weights = [0.1, 0.3, 0.6];
    layers.forEach(({ y, color }, i) => {
        const strokeWidth = 2 + weights[i] * 6;
        const arrow = createArrow(queryX + 60, queryY, outputX - 60, outputY, strokeWidth, color, 0.7);
        arrow.setAttribute('data-flow-step', '2');
        svg.appendChild(arrow);
    });

    // Labels
    const attnLabel = createSVGElement('text', {
        x: (queryX + 100) / 2,
        y: 150,
        'text-anchor': 'middle',
        fill: 'var(--text-secondary)',
        'font-size': '12'
    });
    attnLabel.textContent = 'Attention scores';
    svg.appendChild(attnLabel);

    const aggLabel = createSVGElement('text', {
        x: (queryX + outputX) / 2,
        y: 150,
        'text-anchor': 'middle',
        fill: 'var(--text-secondary)',
        'font-size': '12'
    });
    aggLabel.textContent = 'Weighted sum';
    svg.appendChild(aggLabel);
}

function animateMechanism() {
    const svg = document.getElementById('mechanism-diagram');
    if (!svg) return;

    const step1 = svg.querySelectorAll('[data-flow-step="1"]');
    const step2 = svg.querySelectorAll('[data-flow-step="2"]');

    // Reset
    step1.forEach(el => el.style.opacity = '0.2');
    step2.forEach(el => el.style.opacity = '0.2');

    // Animate step 1
    setTimeout(() => {
        step1.forEach(el => {
            el.style.transition = 'opacity 0.5s ease';
            el.style.opacity = '1';
        });
    }, 100);

    // Animate step 2
    setTimeout(() => {
        step2.forEach(el => {
            el.style.transition = 'opacity 0.5s ease';
            el.style.opacity = '1';
        });
    }, 1000);

    // Reset after animation
    setTimeout(() => {
        step1.forEach(el => el.style.opacity = '0.5');
        step2.forEach(el => el.style.opacity = '0.7');
    }, 2500);
}

// ===========================
// Block AttnRes Diagram
// ===========================

function renderBlockDiagram(numBlocks = 4) {
    const svg = document.getElementById('block-diagram');
    if (!svg) return;

    svg.innerHTML = '';

    const totalLayers = 16;
    const layersPerBlock = totalLayers / numBlocks;
    const blockHeight = 60;
    const blockWidth = 120;
    const startY = 50;
    const blockX = 150;
    const attnX = 400;

    const colors = ['#8b5cf6', '#6366f1', '#3b82f6', '#10b981'];

    // Draw blocks
    for (let i = 0; i < numBlocks; i++) {
        const y = startY + i * (blockHeight + 20);
        const color = colors[i % colors.length];

        // Block rectangle
        const block = createSVGElement('rect', {
            x: blockX - blockWidth / 2,
            y: y,
            width: blockWidth,
            height: blockHeight,
            fill: color,
            rx: 8
        });
        svg.appendChild(block);

        // Block label
        const label = createSVGElement('text', {
            x: blockX,
            y: y + 25,
            'text-anchor': 'middle',
            fill: 'white',
            'font-size': '14',
            'font-weight': '600'
        });
        label.textContent = `Block ${i}`;
        svg.appendChild(label);

        // Layers count
        const layersLabel = createSVGElement('text', {
            x: blockX,
            y: y + 45,
            'text-anchor': 'middle',
            fill: 'white',
            'font-size': '11',
            opacity: 0.8
        });
        layersLabel.textContent = `(${layersPerBlock} layers)`;
        svg.appendChild(layersLabel);
    }

    // Draw attention mechanism
    const attnY = startY + (numBlocks * (blockHeight + 20)) / 2 - 30;
    const attnRect = createSVGElement('rect', {
        x: attnX - 60,
        y: attnY,
        width: 120,
        height: 60,
        fill: '#f59e0b',
        rx: 8
    });
    svg.appendChild(attnRect);

    const attnLabel = createSVGElement('text', {
        x: attnX,
        y: attnY + 35,
        'text-anchor': 'middle',
        fill: 'white',
        'font-size': '14',
        'font-weight': '600'
    });
    attnLabel.textContent = 'Attention';
    svg.appendChild(attnLabel);

    // Draw attention arrows
    for (let i = 0; i < numBlocks; i++) {
        const y = startY + i * (blockHeight + 20) + blockHeight / 2;
        const color = colors[i % colors.length];

        const arrow = createArrow(
            blockX + blockWidth / 2,
            y,
            attnX - 60,
            attnY + 30,
            2,
            color,
            0.6
        );
        svg.appendChild(arrow);
    }

    // Memory complexity label
    const memLabel = createSVGElement('text', {
        x: 300,
        y: startY + numBlocks * (blockHeight + 20) + 20,
        'text-anchor': 'middle',
        fill: 'var(--accent-primary)',
        'font-size': '14',
        'font-weight': '600'
    });
    memLabel.textContent = `Memory: O(${numBlocks}d)`;
    svg.appendChild(memLabel);
}

// ===========================
// Initialize all diagrams
// ===========================

function initDiagrams() {
    renderStandardResidualDiagram();
    renderComparisonDiagram(0);
    renderMechanismDiagram();
    renderBlockDiagram(4);
}

// Run on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDiagrams);
} else {
    initDiagrams();
}
