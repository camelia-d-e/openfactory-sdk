async function sendSimulationMode() {
    const checkbox = document.querySelector('.switch input[type="checkbox"]');
    const simulationMode = checkbox.checked;
    
    try {
        const response = await fetch('/simulationMode', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ enabled: simulationMode })
        });
        
        if (!response.ok) {
            throw new Error('Failed to update simulation mode');
        }
        
        const result = await response.json();
        console.log('Simulation mode updated:', result);
        
    } catch (error) {
        console.error('Error updating simulation mode:', error);
        checkbox.checked = !simulationMode;
        alert('Failed to update simulation mode. Please try again.');
    }
}