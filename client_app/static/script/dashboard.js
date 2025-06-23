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
})

const device_uuid = document.querySelector('meta[name="device-uuid"]').getAttribute('content')
if(device_uuid){
    const wsl_url = `ws://localhost:8000/devices/${device_uuid}/ws`
    const socket = new WebSocket(wsl_url)

    socket.onopen = () => {
        console.log("Socket opened")
    }

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.event === "device_change" && data.data) {
            const id = data.data.id;
            const value = data.data.value;

            const valueElem = document.getElementById(id);
            if (valueElem) {
                
                if (id.includes('Tool'))
                {
                    valueElem.style.color = (value === "ON"? "#6ed43f" : "red")
                    valueElem.parentElement.style.border = (value === "ON"? "2px solid #6ed43f" : "2px solid red")
                }

                if (id.includes('Gate')){
                    valueElem.src = (value === "OPEN"? "../static/icons/blast-gate-open.png": "../static/icons/blast-gate-closed.png")
                }
            }
        }

        if (data.event === "connection_established" && data.data_items) {
            Object.entries(data.data_items).forEach(([id, value]) => {
                const valueElem = document.getElementById(id);
                
                if (valueElem) {
                    if (id.includes('Tool'))
                    {
                        valueElem.style.color = (value === "ON"? "#6ed43f" : "red")
                        valueElem.parentElement.style.border = (value === "ON"? "2px solid #6ed43f" : "2px solid red")
                    }

                    if (id.includes('Gate'))
                    {
                        valueElem.src = (value === "OPEN"? "../static/icons/blast-gate-open.png": "../static/icons/blast-gate-closed.png")
                    }
                }
            });
        }
    }

    socket.onclose = () => {
        console.log("Connection closed.")
    }
}
