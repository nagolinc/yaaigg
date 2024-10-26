const infoDiv = document.getElementById('info');
const state = {
    counters: {}
};

function updateInfoDiv() {
    const countersText = Object.entries(state.counters)
        .map(([key, value]) => `<div><span>${key}</span>=<span>${value}</span></div>`)
        .join('');
    infoDiv.innerHTML = `${countersText}`;
}
// Function to asynchronously get the value of a counter
async function getCounter(counterName) {
    try {
        const response = await fetch(`/get_counter?name=${counterName}`);
        const data = await response.json();
        if (data.value !== undefined) {
            console.log(`Counter ${counterName}: ${data.value}`);
            state.counters[counterName] = data.value;
            updateInfoDiv();
            return data.value;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error fetching counter:', error);
    }
}

// Function to asynchronously set the value of a counter
async function setCounter(counterName, value) {
    try {
        const response = await fetch('/set_counter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: counterName, value })
        });
        const data = await response.json();
        if (data.success) {
            console.log(`Counter ${counterName} set to ${value}`);
            state.counters[counterName] = value;
            updateInfoDiv();
            return true;
        } else {
            throw new Error('Failed to set counter');
        }
    } catch (error) {
        console.error('Error setting counter:', error);
    }
}

// Function to asynchronously fetch an image
async function getImage(name) {
    try {
        const response = await fetch('/get_image', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ object: name })
        });
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        return data.image;
    } catch (error) {
        console.error('Error fetching image:', error);
    }
}

//function to get the player image (returns a url to the image like /static/player.png)
async function getPlayerImage() {
    const url = '/get_player_image';

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.error) {
            throw new Error(data.error);
        }
        return data.image;
    } catch (error) {
        console.error('Error fetching player image:', error);
    }
}

