document.addEventListener("DOMContentLoaded", function() {
    jsPlumb.ready(function() {
        jsPlumb.setContainer("jsplumb-container")

        const spindleCards = Array.from(document.querySelectorAll('.spindle-card'))
        const gateCards = Array.from(document.querySelectorAll('.gate-card'))
        const dustCollectorCard = document.querySelector('.dust-collector-card')

        function getPrefix(id) {
            const match = id.match(/^([A-Z]+\d+)/)
            return match ? match[1] : id.substring(0, 2)
        }

        spindleCards.forEach(spindle => {
            const spindlePrefix = spindle.id

            gateCards.forEach(gate => {
                const gateId = gate.id.replace('card-', '')
                const gatePrefix = getPrefix(gateId)
                
                if (spindlePrefix === gatePrefix) {
                    jsPlumb.connect({
                        source: spindle.id,
                        target: gate.id,
                        anchors: ["Top", "Top"],
                        endpoint: "Blank",
                        connector: ["Flowchart", { stub: 20, gap: 0, cornerRadius: 5 }],
                        paintStyle: { stroke: "#222", strokeWidth: 15 },
                        overlays: [] 
                    })
                }

                jsPlumb.connect({
                        source: gate.id,
                        target: dustCollectorCard.id,
                        anchors: ["AutoDefault", "AutoDefault"],
                        endpoint: "Blank",
                        connector: ["Flowchart", { stub: 20, gap: 0, cornerRadius: 5 }],
                        paintStyle: { stroke: "#222", strokeWidth: 15 },
                        overlays: [] 
                    })
            })
        })
    })

    initializeDefaultCharts();
    initializeAirQualityCharts();
    restoreSimulationMode();
    setupEventSource();
})

function saveChartData(dataitemId, data) {
    try {
        const existingData = JSON.parse(localStorage.getItem('chartData') || '{}');
        existingData[dataitemId] = data;
        localStorage.setItem('chartData', JSON.stringify(existingData));
    } catch (e) {
        console.error('Error saving chart data:', e);
    }
}

function getStoredChartData(dataitemId) {
    try {
        const chartData = JSON.parse(localStorage.getItem('chartData') || '{}');
        return chartData[dataitemId] || null;
    } catch (e) {
        console.error('Error retrieving chart data:', e);
        return null;
    }
}

function saveDeviceStates(states) {
    try {
        localStorage.setItem('deviceStates', JSON.stringify(states));
    } catch (e) {
        console.error('Error saving device states:', e);
    }
}

function getStoredDeviceStates() {
    try {
        return JSON.parse(localStorage.getItem('deviceStates') || '{}');
    } catch (e) {
        console.error('Error retrieving device states:', e);
        return {};
    }
}

function saveParticleData() {
    try {
        const storageData = {};
        Object.keys(particleData).forEach(type => {
            storageData[type] = particleData[type].map(point => ({
                x: point.x.getTime(),
                y: point.y
            }));
        });
        
        const rawStorageData = {};
        Object.keys(rawParticleData).forEach(type => {
            rawStorageData[type] = rawParticleData[type].map(point => ({
                x: point.x.getTime(),
                y: point.y
            }));
        });
        
        localStorage.setItem('particleData', JSON.stringify(storageData));
        localStorage.setItem('rawParticleData', JSON.stringify(rawStorageData));
    } catch (e) {
        console.error('Error saving particle data:', e);
    }
}

function loadParticleData() {
    try {
        const stored = localStorage.getItem('particleData');
        if (stored) {
            const storageData = JSON.parse(stored);
            
            const cutoffTime = Date.now() - (TIME_WINDOW_MINUTES * 60 * 1000);
            
            Object.keys(storageData).forEach(type => {
                if (particleData[type]) {
                    particleData[type] = storageData[type]
                        .map(point => ({
                            x: new Date(point.x),
                            y: point.y
                        }))
                        .filter(point => point.x.getTime() >= cutoffTime);
                }
            });
            
            return true;
        }
    } catch (e) {
        console.error('Error loading particle data:', e);
    }
    return false;
}

function initializeDefaultCharts() {
    const toolElements = document.querySelectorAll('[id$="-pie-chart"]');
    const initialData = document.getElementById('initialChartsData')
    console.log(initialData ? initialData.value : 'No initial data element found')

    toolElements.forEach(svg => {
        const dataitemId = svg.id.replace('-pie-chart', '');
        
        let defaultData = getStoredChartData(dataitemId);

        let totalTime = 0;
        
        if (defaultData) {
            Object.keys(defaultData).forEach( state =>{
                totalTime += defaultData[state]
            })

        } else if (initialData && initialData.value) {
            try {
                const parsedData = JSON.parse(initialData.value);
                defaultData = parsedData[dataitemId] || {
                    'OFF': 100,
                    'ON': 1,
                    'UNAVAILABLE': 1
                };
                Object.keys(defaultData).forEach( state =>{
                    totalTime += defaultData[state]
                })

                saveChartData(dataitemId, defaultData);
            } catch (e) {
                console.error('Error parsing initial data:', e);
                defaultData = {
                    'OFF': 100,
                    'ON': 1,
                    'UNAVAILABLE': 1
                }
                totalTime = 102
            }
        } else {
            defaultData = {
                'OFF': 100,
                'ON': 1,
                'UNAVAILABLE': 1
            }
            totalTime = 102
        }
        
        const labels = ['ON', 'OFF', 'UNAVAILABLE'];
       
        const percentages = [];
        Object.values(defaultData).forEach(value => {
            percentages.push((value / totalTime) * 100);
        });
        
        createPieChart(dataitemId, totalTime, percentages, defaultData, labels);
    });

    const storedStates = getStoredDeviceStates();
    Object.entries(storedStates).forEach(([id, value]) => {
        const valueElem = document.getElementById(id);
        if (valueElem) {
            if (id.includes('Tool')) {
                valueElem.style.color = (value === "ON" ? "#6ed43f" : "red");
                if (valueElem.parentElement) {
                    valueElem.parentElement.style.border = (value === "ON" ? "2px solid #6ed43f" : "2px solid red");
                }
            }
            if (id.includes('Gate')) {
                valueElem.src = (value === "OPEN" ? "../static/icons/blast-gate-open.png" : "../static/icons/blast-gate-closed.png");
            }
        }
    });
}

const colors = ["#2F3061", "#ffb800", "#5BC0EB"]

function createPieChart(dataitem_id, total, percentages, data, labels) {
    const svg = document.getElementById(dataitem_id + '-pie-chart');
    
    const radius = 50;
    const centerX = 70;
    const centerY = 70;
    
    if(svg) {
        svg.innerHTML = '';
    
        let currentAngle = -Math.PI / 2;
        
        Object.values(data).forEach((value, index) => {
            const sliceAngle = (value / total) * 2 * Math.PI;
            const endAngle = currentAngle + sliceAngle;
            
            const x1 = centerX + radius * Math.cos(currentAngle);
            const y1 = centerY + radius * Math.sin(currentAngle);
            const x2 = centerX + radius * Math.cos(endAngle);
            const y2 = centerY + radius * Math.sin(endAngle);
            
            const largeArcFlag = sliceAngle > Math.PI ? 1 : 0;

            const pathData = [
                `M ${centerX} ${centerY}`,
                `L ${x1} ${y1}`,
                `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${x2} ${y2}`,
                'Z'
            ].join(' ');
            
            const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            path.setAttribute('d', pathData);
            path.setAttribute('fill', colors[index % colors.length]);
            path.setAttribute('class', 'pie-slice');
            path.setAttribute('data-value', `${percentages[index].toFixed(1)}%`);
            path.setAttribute('data-label', labels[index] || `Item ${index + 1}`);
            
            svg.appendChild(path);
            
            currentAngle = endAngle;
        });

        const powerDurationText = document.getElementById(`${dataitem_id}-power-duration`);
        if (powerDurationText) {
            if ((total/60).toFixed(2) > 2) {
                powerDurationText.innerText = `Total powered duration: ${(total/60).toFixed(2)} minutes`;
            } else {
                powerDurationText.innerText = `Total powered duration: NA minutes`;
            }
        }
    }
}

function updateDeviceChart(dataitem_id, analyticsData) {
    const labels = ['ON', 'OFF', 'UNAVAILABLE']
    let totalTime = 0

    const percentages = []
    Object.keys(analyticsData).forEach( state =>{
        totalTime += analyticsData[state]
        percentages.push(analyticsData[state]/totalTime * 100)
    })

    saveChartData(dataitem_id, analyticsData);
    
    createPieChart(dataitem_id, totalTime, percentages, analyticsData, labels);
}

function saveSimulationMode(enabled) {
    try {
        localStorage.setItem('simulationMode', JSON.stringify(enabled));
    } catch (e) {
        console.error('Error saving simulation mode:', e);
    }
}

function getStoredSimulationMode() {
    try {
        const stored = localStorage.getItem('simulationMode');
        if (stored === null) return false;
        return JSON.parse(stored);
    } catch (e) {
        console.error('Error retrieving simulation mode:', e);
        return false;
    }
}

function restoreSimulationMode() {
    const checkbox = document.querySelector('.switch input[type="checkbox"]');
    if (checkbox) {
        const stored = getStoredSimulationMode();
        checkbox.checked = !!stored;
    }
}

async function sendSimulationMode() {
    const checkbox = document.querySelector('.switch input[type="checkbox"]');
    const simulationMode = checkbox.checked;
    const device_uuid = document.querySelector('meta[name="device-uuid"]')?.content;
    
    if (!device_uuid) {
        console.error("Device UUID not found");
        return;
    }

    try {
        const response = await fetch(`/simulation-mode/${device_uuid}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ enabled: simulationMode })
        });

        if (!response.ok) {
            throw new Error('Failed to update simulation mode');
        }

        const result = await response.json();
        console.log('Simulation mode updated:', result);
        saveSimulationMode(simulationMode);
    } catch (error) {
        console.error('Error updating simulation mode:', error);
        checkbox.checked = !simulationMode;
        alert('Failed to update simulation mode. Please try again.');
    }
}

function setupEventSource() {
    const device_uuid = document.querySelector('meta[name="device-uuid"]')?.content;
    if (!device_uuid) {
        console.error("Device UUID not found");
        return;
    }

    const eventSource = new EventSource(`/updates/${device_uuid}`);

    eventSource.onmessage = (event) => {
        try {
            const device_update = JSON.parse(event.data);
            if(device_update.event){
                if(device_update.event !== 'ping'){
                    console.log("Received update:", device_update);
                }
                if (device_update.event === "connection_established") {
                    initializeUI(device_update.data_items);
                }
                if (device_update.event === "simulation_mode_updated") {
                if (device_update.success) {
                    saveSimulationMode(device_update.value);
                } else {
                    console.error("Failed to update simulation mode:", device_update.error);
                    const checkbox = document.querySelector('.switch input[type="checkbox"]');
                    checkbox.checked = !checkbox.checked;
                }
                }
            }
            else{
                updateDeviceUI(device_update.data);
            }
        } catch (e) {
            console.error("Error processing event:", e);
        }
    };

    eventSource.onerror = (error) => {
        console.error("SSE Error:", error);
        eventSource.close();
        setTimeout(setupEventSource, 3000);
    };
}

function updateDeviceUI(updateData) {
    const id = updateData.ID;
    const value = updateData.VALUE;
    const timestamp = updateData.TIMESTAMP;
    const durations = updateData.durations;
    const valueElem = document.getElementById(id)

    if (valueElem) {
        if (id.includes('Tool')) {
            valueElem.style.color = (value === "ON" ? "#6ed43f" : "red");
            if (valueElem.parentElement) {
                valueElem.parentElement.style.border = (value === "ON" ? "2px solid #6ed43f" : "2px solid red");
            }
        } else if (id.includes('Gate')) {
            valueElem.src = (value === "OPEN" 
                ? "../static/icons/blast-gate-open.png" 
                : "../static/icons/blast-gate-closed.png");
        }
    }
    if (id.includes('concentration')) {
        updateParticleConcentration(id, convertToMg(value), timestamp);
    }

    if (durations) {
        updateDeviceChart(id, durations);
        saveChartData(id, durations);
    }
}

function initializeUI(dataItems) {
    saveDeviceStates(dataItems);
    
    Object.entries(dataItems).forEach(([id, value]) => {
        const valueElem = document.getElementById(id);
        if (!valueElem) return;

        if (id.includes('Tool')) {
            valueElem.style.color = (value === "ON" ? "#6ed43f" : "red");
            if (valueElem.parentElement) {
                valueElem.parentElement.style.border = (value === "ON" ? "2px solid #6ed43f" : "2px solid red");
            }
        } else if (id.includes('Gate')) {
            valueElem.src = (value === "OPEN" 
                ? "../static/icons/blast-gate-open.png" 
                : "../static/icons/blast-gate-closed.png");
        }
    });
}

let particleData = {
    pm1_concentration: [],
    pm2_5_concentration: [],
    pm4_concentration: [],
    pm10_concentration: []
};

let rawParticleData = {
    pm1_concentration: [],
    pm2_5_concentration: [],
    pm4_concentration: [],
    pm10_concentration: []
};

let airQualityCharts = {};
const MAX_DATA_POINTS = 50;
const TIME_WINDOW_MINUTES = 5;
const AVERAGING_INTERVAL_SECONDS = 10;

const chartConfigs = {
    pm1_concentration: {
        label: 'PM1',
        color: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.1)',
        canvasId: 'pm1Chart'
    },
    pm2_5_concentration: {
        label: 'PM2.5',
        color: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.1)',
        canvasId: 'pm25Chart'
    },
    pm4_concentration: {
        label: 'PM4',
        color: 'rgb(255, 205, 86)',
        backgroundColor: 'rgba(255, 205, 86, 0.1)',
        canvasId: 'pm4Chart'
    },
    pm10_concentration: {
        label: 'PM10',
        color: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.1)',
        canvasId: 'pm10Chart'
    }
};

function initializeAirQualityCharts() {
    const dataLoaded = loadParticleData();
    console.log('Data loaded on initialization:', dataLoaded);

    Object.keys(chartConfigs).forEach(particleType => {
        const config = chartConfigs[particleType];
        const ctx = document.getElementById(config.canvasId);
        
        if (!ctx) {
            console.warn(`Canvas element not found: ${config.canvasId}`);
            return;
        }

        airQualityCharts[particleType] = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: `${config.label} (µg/m³)`,
                    data: [],
                    borderColor: config.color,
                    backgroundColor: config.backgroundColor,
                    fill: false,
                    tension: 0.1,
                    borderWidth: 2,
                    pointRadius: 3,
                    pointHoverRadius: 5
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    intersect: false,
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second',
                            stepSize: 30,
                            displayFormats: {
                                second: 'HH:mm:ss'
                            }
                        },
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        min: function(context) {
                            const now = new Date();
                            return new Date(now.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000));
                        },
                        max: function(context) {
                            return new Date();
                        }
                    },
                    y: {
                        display: true,
                        title: {
                            display: true,
                            text: 'Concentration (µg/m³)'
                        },
                        beginAtZero: false,
                        min: function(context) {
                            const data = context.chart.data.datasets[0].data;
                            const validData = data.filter(val => val !== null && val !== undefined);
                            if (validData.length === 0) return 0;
                            const minVal = Math.min(...validData);
                            return minVal * 0.95;
                        },
                        max: function(context) {
                            const data = context.chart.data.datasets[0].data;
                            const validData = data.filter(val => val !== null && val !== undefined);
                            if (validData.length === 0) return 10;
                            const maxVal = Math.max(...validData);
                            return maxVal * 1.05;
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(3);
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                animation: {
                    duration: 200
                }
            }
        });
    });

    updateAllAirQualityCharts();
    startRealTimeUpdates();
}

function processConcentrationData(id, value, timestamp) {
    const concentrationValue = parseFloat(value) * 1000;
    
    const time = new Date(timestamp);
    const timeLabel = time.toLocaleTimeString('en-US', { 
        hour12: false, 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    
    return { value: concentrationValue, timeLabel, timestamp: time };
}

function updateParticleConcentration(id, value, timestamp) {
    if (!particleData[id]) return;
    
    const processedData = processConcentrationData(id, value, timestamp);
    
    particleData[id].push({
        x: processedData.timestamp,
        y: processedData.value 
    });

    const cutoffTime = new Date(Date.now() - (TIME_WINDOW_MINUTES * 60 * 1000));
    particleData[id] = particleData[id].filter(point => point.x >= cutoffTime);
    
    updateSingleAirQualityChart(id);
    
    updateConcentrationDisplay(id, processedData.value);
    saveParticleData();
}

function updateSingleAirQualityChart(particleType) {
    const chart = airQualityCharts[particleType];
    if (!chart) return;
    
    const dataset = chart.data.datasets[0];
    if (dataset && particleData[particleType]) {
        dataset.data = [...particleData[particleType]];
    }
    
    const now = new Date();
    chart.options.scales.x.min = new Date(now.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000));
    chart.options.scales.x.max = now;
    
    chart.update('none');
}

function updateAllAirQualityCharts() {
    Object.keys(chartConfigs).forEach(particleType => {
        updateSingleAirQualityChart(particleType);
    });
}

function startRealTimeUpdates() {
    setInterval(() => {
        const now = new Date();
        const cutoffTime = new Date(now.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000));
        
        Object.keys(airQualityCharts).forEach(particleType => {
            const chart = airQualityCharts[particleType];
            if (chart) {
                chart.options.scales.x.min = cutoffTime;
                chart.options.scales.x.max = now;
                chart.update('none');
            }
            
            if (particleData[particleType]) {
                particleData[particleType] = particleData[particleType].filter(point => point.x >= cutoffTime);
            }
        });
    }, 1000);
}

function updateConcentrationDisplay(id, value) {
    const displayElement = document.getElementById(id);
    if (displayElement) {
        displayElement.textContent = value.toFixed(3) + ' µg/m³';
    }
    
    const valueOnlyElement = document.getElementById(id + '_value');
    if (valueOnlyElement) {
        valueOnlyElement.textContent = value.toFixed(3);
    }
}

function convertToMg(percentConcentration){
    return (percentConcentration/100) * 1225000
}