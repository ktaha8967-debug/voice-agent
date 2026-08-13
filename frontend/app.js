const chatContainer = document.getElementById('chatContainer');
const recordBtn = document.getElementById('recordBtn');
const statusText = document.getElementById('status');

let ws;
let mediaRecorder;
let audioChunks = [];

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/audio`);

    ws.onopen = () => {
        statusText.innerText = "Status: Connected";
        statusText.style.color = "#22c55e"; // green
    };

    ws.onmessage = async (event) => {
        if (typeof event.data === 'string') {
            const data = JSON.parse(event.data);
            if (data.type === 'transcript') {
                addMessage(data.role, data.text);
            } else if (data.type === 'processing_llm') {
                statusText.innerText = "Status: AI Thinking...";
                statusText.style.color = "#8b5cf6"; // purple
            } else if (data.type === 'audio_start') {
                statusText.innerText = "Status: AI Speaking...";
                statusText.style.color = "#3b82f6"; // blue
            }
        } else if (event.data instanceof Blob) {
            // Received audio blob from server
            playAudio(event.data);
        }
    };

    ws.onclose = () => {
        statusText.innerText = "Status: Disconnected. Reconnecting...";
        statusText.style.color = "#ef4444"; // red
        setTimeout(initWebSocket, 3000);
    };
}

function addMessage(role, text) {
    const msgDiv = document.createElement('div');
    msgDiv.classList.add('message', role);
    msgDiv.innerText = text;
    chatContainer.appendChild(msgDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function initAudio() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        // Use webm for broad browser support
        mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });

        mediaRecorder.ondataavailable = (event) => {
            if (event.data.size > 0) {
                audioChunks.push(event.data);
            }
        };

        mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(audioBlob);
                statusText.innerText = "Status: Processing...";
                statusText.style.color = "#eab308"; // yellow
            }
            audioChunks = [];
        };

    } catch (err) {
        console.error("Error accessing microphone:", err);
        statusText.innerText = "Microphone access denied.";
        statusText.style.color = "#ef4444";
    }
}

async function playAudio(blob) {
    const url = URL.createObjectURL(blob);
    const audio = new Audio(url);
    
    audio.onended = () => {
        URL.revokeObjectURL(url);
        statusText.innerText = "Status: Connected";
        statusText.style.color = "#22c55e";
    };

    try {
        await audio.play();
    } catch (e) {
        console.error("Audio playback error:", e);
    }
}

// Push to talk handlers
recordBtn.addEventListener('mousedown', startRecording);
recordBtn.addEventListener('mouseup', stopRecording);
recordBtn.addEventListener('mouseleave', stopRecording);

// Touch device support
recordBtn.addEventListener('touchstart', (e) => {
    e.preventDefault();
    startRecording();
});
recordBtn.addEventListener('touchend', (e) => {
    e.preventDefault();
    stopRecording();
});

function startRecording() {
    if (!mediaRecorder || mediaRecorder.state === "recording") return;
    audioChunks = [];
    mediaRecorder.start();
    recordBtn.classList.add('recording');
    recordBtn.innerText = "Listening...";
}

function stopRecording() {
    if (!mediaRecorder || mediaRecorder.state !== "recording") return;
    mediaRecorder.stop();
    recordBtn.classList.remove('recording');
    recordBtn.innerText = "Push to Talk";
}

// Initialize
initWebSocket();
initAudio();
