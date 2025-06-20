document.addEventListener("DOMContentLoaded", function() {
    jsPlumb.ready(function() {
        jsPlumb.setContainer("jsplumb-container")

        const toolCards = Array.from(document.querySelectorAll('.tool-card'))
        const gateCards = Array.from(document.querySelectorAll('.gate-card'))

        function getPrefix(id) {
            const match = id.match(/^([A-Z]+\d+)/)
            return match ? match[1] : id.substring(0, 2)
        }

        toolCards.forEach(tool => {
            const toolId = tool.id.replace('card-', '')
            const toolPrefix = getPrefix(toolId)

            gateCards.forEach(gate => {
                const gateId = gate.id.replace('card-', '')
                const gatePrefix = getPrefix(gateId)
                
                if (toolPrefix === gatePrefix) {
                    jsPlumb.connect({
                        source: tool.id,
                        target: gate.id,
                        anchors: ["Right", "Left"],
                        endpoint: "Blank",
                        connector: ["Flowchart", { stub: 20, gap: 2, cornerRadius: 5 }],
                        paintStyle: { stroke: "#222", strokeWidth: 2 },
                        overlays: [] 
                    })
                }
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
        console.log(data)

        if (data.event === "device_change" && data.data) {
            const id = data.data.id;
            const value = data.data.value;

            const valueElem = document.getElementById(id);
            if (valueElem) {
                valueElem.textContent = value;
            }
        }

        if (data.event === "connection_established" && data.data_items) {
            Object.entries(data.data_items).forEach(([id, value]) => {
                const valueElem = document.getElementById(id);
                if (valueElem) {
                    valueElem.textContent = value;
                }
            });
        }
    }

    socket.onclose = () => {
        console.log("Connection closed.")
    }
}
