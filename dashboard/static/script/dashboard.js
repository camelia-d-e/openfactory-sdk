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

    initializeActiveTab();
    initializeDefaultCharts();
    initializeAirQualityCharts();
    restoreSimulationMode();
    setupEventSource();
})

function getStoredChartData(dataitemId) {
    const chartData = JSON.parse(sessionStorage.getItem('chartData') || '{}');
    return chartData[dataitemId] || null;
}

function saveDeviceStates(states) {
    sessionStorage.setItem('deviceStates', JSON.stringify(states));
}

function getStoredDeviceStates() {
    return JSON.parse(sessionStorage.getItem('deviceStates') || '{}');
}

function saveParticleData() {
    const storageData = {};
    Object.keys(particleData).forEach(type => {
        storageData[type] = particleData[type].map(point => ({
            x: point.x.getTime(),
            y: point.y
        }));
    });
    
    sessionStorage.setItem('particleData', JSON.stringify(storageData));
    
    const metadata = {
        lastUpdate: Date.now(),
        dataRanges: {}
    };
    
    Object.keys(particleData).forEach(type => {
        if (particleData[type].length > 0) {
            metadata.dataRanges[type] = {
                start: Math.min(...particleData[type].map(p => p.x.getTime())),
                end: Math.max(...particleData[type].map(p => p.x.getTime())),
                count: particleData[type].length
            };
        }
    });
    
    sessionStorage.setItem('particleDataMetadata', JSON.stringify(metadata));
}

function loadParticleData() {
    const stored = sessionStorage.getItem('particleData');
    const metadata = JSON.parse(sessionStorage.getItem('particleDataMetadata') || '{}');
    
    if (stored) {
        const storageData = JSON.parse(stored);
        
        const extendedCutoffTime = Date.now() - (TIME_WINDOW_MINUTES * 2 * 60 * 1000);
        
        Object.keys(storageData).forEach(type => {
            if (particleData[type]) {
                let loadedData = storageData[type]
                    .map(point => ({
                        x: new Date(point.x),
                        y: point.y
                    }))
                    .filter(point => point.x.getTime() >= extendedCutoffTime);
                
                const uniqueData = [];
                loadedData.forEach(point => {
                    const existingIndex = uniqueData.findIndex(existing => 
                        Math.abs(existing.x.getTime() - point.x.getTime()) < 1000
                    );
                    
                    if (existingIndex === -1) {
                        uniqueData.push(point);
                    } else {
                        if (point.x.getTime() > uniqueData[existingIndex].x.getTime()) {
                            uniqueData[existingIndex] = point;
                        }
                    }
                });
                
                uniqueData.sort((a, b) => a.x.getTime() - b.x.getTime());
                particleData[type] = uniqueData;
            }
        });
        
        console.log('Loaded particle data with metadata:', metadata);
        return true;
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
    sessionStorage.setItem('simulationMode', JSON.stringify(enabled));
}

function getStoredSimulationMode() {
    const stored = sessionStorage.getItem('simulationMode');
    if (stored === null) return false;
    return JSON.parse(stored);
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
    const eventSource = new EventSource('/updates/all');

    eventSource.onmessage = (event) => {
        try {
           
            const device_update = JSON.parse(event.data);
            if(device_update.event){
                if (device_update.event === "connection_established") {
                    const deviceUuid = device_update.device_uuid;
                    if (deviceUuid) {
                        initializeUI(device_update.data_items, deviceUuid);
                    }
                }
                if (device_update.event === "simulation_mode_updated") {
                    if (device_update.success) {
                        saveSimulationMode(device_update.value);
                    } else {
                        console.error("Failed to update simulation mode:", device_update.error);
                        const checkbox = document.querySelector('.switch input[type="checkbox"]');
                        if (checkbox) {
                            checkbox.checked = !checkbox.checked;
                        }
                    }
                }
            }
            else{
                const deviceUuid = device_update.device_uuid || extractDeviceUuidFromData(device_update.data);
                updateDeviceUI(device_update.data, deviceUuid);
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

function extractDeviceUuidFromData(data) {
    if (data && data.ID) {
        const match = data.ID.match(/^([^_]+)/);
        return match ? match[1] : null;
    }
    return null;
}
function updateDeviceUI(updateData, deviceUuid = null) {
    const id = updateData.ID;
    const value = updateData.VALUE;
    const avg_data = updateData.avg_value || {};
    const durations = updateData.durations;
    
    
    const valueElem = document.getElementById(id);

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
        if(JSON.stringify(avg_data) !== '{}'){
            updateParticleConcentration(id, convertToMg(avg_data.value), avg_data.timestamp, convertToMg(value));
        }else{
            const processedActualData = processConcentrationData(convertToMg(value), updateData.timestamp);
            updateConcentrationDisplay(id, processedActualData.value);
        }
    }

    if (durations) {
        updateDeviceChart(id, durations);
        saveChartData(id, durations);
    }
    
    if (deviceUuid) {
        const deviceStates = getStoredDeviceStates();
        if (!deviceStates[deviceUuid]) {
            deviceStates[deviceUuid] = {};
        }
        deviceStates[deviceUuid][id] = value;
        saveDeviceStates(deviceStates);
    }
}

function initializeUI(dataItems, deviceUuid = null) {
    if (deviceUuid) {
        const allDeviceStates = getStoredDeviceStates();
        allDeviceStates[deviceUuid] = dataItems;
        saveDeviceStates(allDeviceStates);
    } else {
        saveDeviceStates(dataItems);
    }
    
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

function saveDeviceStates(states) {
    sessionStorage.setItem('deviceStates', JSON.stringify(states));
}

function getStoredDeviceStates() {
    return JSON.parse(sessionStorage.getItem('deviceStates') || '{}');
}

function getStoredDeviceStatesForDevice(deviceUuid) {
    const allStates = getStoredDeviceStates();
    return allStates[deviceUuid] || {};
}

function saveChartData(dataitemId, data, deviceUuid = null) {
    const existingData = JSON.parse(sessionStorage.getItem('chartData') || '{}');
    
    if (deviceUuid) {
        if (!existingData[deviceUuid]) {
            existingData[deviceUuid] = {};
        }
        existingData[deviceUuid][dataitemId] = data;
    } else {
        existingData[dataitemId] = data;
    }
    
    sessionStorage.setItem('chartData', JSON.stringify(existingData));
}

function getStoredChartData(dataitemId, deviceUuid = null) {
    const chartData = JSON.parse(sessionStorage.getItem('chartData') || '{}');
    
    if (deviceUuid) {
        return chartData[deviceUuid] ? chartData[deviceUuid][dataitemId] || null : null;
    }
    
    return chartData[dataitemId] || null;
}

let particleDataByDevice = {};

function saveParticleDataForDevice(deviceUuid) {
    if (!particleDataByDevice[deviceUuid]) return;
    
    const storageData = {};
    Object.keys(particleDataByDevice[deviceUuid]).forEach(type => {
        storageData[type] = particleDataByDevice[deviceUuid][type].map(point => ({
            x: point.x.getTime(),
            y: point.y
        }));
    });
    
    const allParticleData = JSON.parse(sessionStorage.getItem('allParticleData') || '{}');
    allParticleData[deviceUuid] = storageData;
    sessionStorage.setItem('allParticleData', JSON.stringify(allParticleData));
}

function loadParticleDataForDevice(deviceUuid) {
    const allParticleData = JSON.parse(sessionStorage.getItem('allParticleData') || '{}');
    const stored = allParticleData[deviceUuid];
    
    if (stored) {
        const extendedCutoffTime = Date.now() - (TIME_WINDOW_MINUTES * 2 * 60 * 1000);
        
        if (!particleDataByDevice[deviceUuid]) {
            particleDataByDevice[deviceUuid] = {
                pm1_concentration: [],
                pm2_5_concentration: [],
                pm4_concentration: [],
                pm10_concentration: []
            };
        }
        
        Object.keys(stored).forEach(type => {
            if (particleDataByDevice[deviceUuid][type]) {
                let loadedData = stored[type]
                    .map(point => ({
                        x: new Date(point.x),
                        y: point.y
                    }))
                    .filter(point => point.x.getTime() >= extendedCutoffTime);
                
                particleDataByDevice[deviceUuid][type] = loadedData;
            }
        });
        
        return true;
    }
    return false;
}

let particleData = {
    pm1_concentration: [],
    pm2_5_concentration: [],
    pm4_concentration: [],
    pm10_concentration: []
};

let airQualityCharts = {};
const MAX_DATA_POINTS = 100;
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

function getOptimalTimeRange(particleType) {
    if (!particleData[particleType] || particleData[particleType].length === 0) {
        const now = new Date();
        return {
            min: new Date(now.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000)),
            max: now
        };
    }
    
    const now = new Date();
    const dataStart = new Date(Math.min(...particleData[particleType].map(p => p.x.getTime())));
    const dataEnd = new Date(Math.max(...particleData[particleType].map(p => p.x.getTime())));
    
    const timeSinceLastData = now.getTime() - dataEnd.getTime();
    const maxGapMinutes = 2;
    
    if (timeSinceLastData > (maxGapMinutes * 60 * 1000)) {
        return {
            min: new Date(dataEnd.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000)),
            max: dataEnd
        };
    } else {
        const idealStart = new Date(now.getTime() - (TIME_WINDOW_MINUTES * 60 * 1000));
        return {
            min: dataStart.getTime() < idealStart.getTime() ? dataStart : idealStart,
            max: now
        };
    }
}

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

        const timeRange = getOptimalTimeRange(particleType);

        airQualityCharts[particleType] = new Chart(ctx, {
            type: 'line',
            data: {
                datasets: [{
                    label: `${config.label} (µg/m³)`,
                    data: particleData[particleType] || [],
                    borderColor: config.color,
                    backgroundColor: config.backgroundColor,
                    fill: false,
                    tension: 0,
                    borderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 2,
                    spanGaps: false,
                    cubicInterpolationMode: 'monotone'
                }]
            },
            options: {
                responsive: true,
                interaction: {
                    intersect: false,
                },
                elements: {
                    line: {
                        tension: 0
                    }
                },
                scales: {
                    x: {
                        type: 'time',
                        time: {
                            unit: 'second',
                            stepSize: 10,
                            displayFormats: {
                                second: 'HH:mm:ss'
                            }
                        },
                        display: true,
                        title: {
                            display: true,
                            text: 'Time'
                        },
                        ticks: {
                            maxTicksLimit: 10,
                            source: 'auto'
                        },
                        min: timeRange.min,
                        max: timeRange.max
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
                            const validData = data.filter(val => val !== null && val !== undefined && val.y !== null);
                            if (validData.length === 0) return 0;
                            const minVal = Math.min(...validData.map(d => d.y));
                            return Math.max(0, minVal - 2);
                        },
                        max: function(context) {
                            const data = context.chart.data.datasets[0].data;
                            const validData = data.filter(val => val !== null && val !== undefined && val.y !== null);
                            if (validData.length === 0) return 10;
                            const maxVal = Math.max(...validData.map(d => d.y));
                            return maxVal + 2;
                        },
                        ticks: {
                            callback: function(value) {
                                return value.toFixed(1);
                            }
                        }
                    }
                },
                animation: {
                    duration: 0
                }
            }
        });
    });

    updateAllAirQualityCharts();
    startRealTimeUpdates();
}

function processConcentrationData(value, timestamp) {
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

function updateParticleConcentration(id, avg_value, timestamp, true_value) {
    if (!particleData[id]) return;
    
    const processedAvgData = processConcentrationData(avg_value, timestamp);
    const processedActualData = processConcentrationData(true_value, timestamp);
    
    const existingIndex = particleData[id].findIndex(point => 
        Math.abs(point.x.getTime() - processedAvgData.timestamp.getTime()) < 1000
    );
    
    if (existingIndex !== -1) {
        particleData[id][existingIndex] = {
            x: processedAvgData.timestamp,
            y: processedAvgData.value 
        };
    } else {
        particleData[id].push({
            x: processedAvgData.timestamp,
            y: processedAvgData.value 
        });
    }
    
    particleData[id].sort((a, b) => a.x.getTime() - b.x.getTime());
    
    if (particleData[id].length > MAX_DATA_POINTS) {
        particleData[id] = particleData[id].slice(-MAX_DATA_POINTS);
    }
    
    updateSingleAirQualityChart(id);
    updateConcentrationDisplay(id, processedActualData.value);
    saveParticleData();
}

function updateSingleAirQualityChart(particleType) {
    const chart = airQualityCharts[particleType];
    if (!chart) return;
    
    const dataset = chart.data.datasets[0];
    if (dataset && particleData[particleType]) {
        const cleanData = [...particleData[particleType]]
            .filter(point => point && point.x && point.y !== null && point.y !== undefined)
            .sort((a, b) => a.x.getTime() - b.x.getTime());
        
        dataset.data = cleanData;
    }
    
    const timeRange = getOptimalTimeRange(particleType);
    chart.options.scales.x.min = timeRange.min;
    chart.options.scales.x.max = timeRange.max;
    
    chart.update('none');
}

function updateAllAirQualityCharts() {
    Object.keys(chartConfigs).forEach(particleType => {
        updateSingleAirQualityChart(particleType);
    });
}

let updateThrottle = {};
let lastDataCleanup = 0;

function startRealTimeUpdates() {
    setInterval(() => {
        const now = new Date();
        
        Object.keys(airQualityCharts).forEach(particleType => {
            if (updateThrottle[particleType] && (now.getTime() - updateThrottle[particleType]) < 500) {
                return;
            }
            updateThrottle[particleType] = now.getTime();
            
            const chart = airQualityCharts[particleType];
            if (chart) {
                const timeRange = getOptimalTimeRange(particleType);
                chart.options.scales.x.min = timeRange.min;
                chart.options.scales.x.max = timeRange.max;
                chart.update('none');
            }
        });
        
        if (now.getTime() - lastDataCleanup > 30000) {
            const extendedCutoffTime = new Date(now.getTime() - (TIME_WINDOW_MINUTES * 2 * 60 * 1000));
            let dataChanged = false;
            
            Object.keys(particleData).forEach(particleType => {
                if (particleData[particleType]) {
                    const originalLength = particleData[particleType].length;
                    particleData[particleType] = particleData[particleType]
                        .filter(point => point.x >= extendedCutoffTime)
                        .sort((a, b) => a.x.getTime() - b.x.getTime());
                    
                    if (particleData[particleType].length !== originalLength) {
                        dataChanged = true;
                    }
                }
            });
            
            if (dataChanged) {
                saveParticleData();
            }
            
            lastDataCleanup = now.getTime();
        }
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

function tabSelected(device_uuid){
    console.log("Tab selected for device:", device_uuid);
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.getElementById(device_uuid + '_tab').classList.add('active');
}


function initializeActiveTab() { 
    const path = window.location.pathname;
    const matches = path.match(/\/devices\/([^\/]+)/);
    if (matches && matches[1]) {
        tabSelected(matches[1]);
    }
}