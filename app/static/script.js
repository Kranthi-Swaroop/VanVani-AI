// Elements
const micButton = document.getElementById('micButton');
const voiceWaves = document.getElementById('voiceWaves');
const connectionStatus = document.getElementById('connectionStatus');
const languageSelect = document.getElementById('languageSelect');
const chatArea = document.getElementById('chatArea');

// State
let isListening = false;
let recognition = null;
let synthesis = window.speechSynthesis;

// Initialize Speech Recognition
function initSpeechRecognition() {
    if (!('webkitSpeechRecognition' in window)) {
        alert("Web Speech API is not supported in this browser. Please use Chrome.");
        return;
    }

    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => {
        isListening = true;
        updateUIState('listening');
    };

    recognition.onend = () => {
        isListening = false;
        updateUIState('idle');
    };

    recognition.onresult = async (event) => {
        const transcript = event.results[0][0].transcript;
        console.log("Heard:", transcript);
        addMessage(transcript, 'user');
        await processQuery(transcript);
    };

    recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        updateUIState('error');
    };
}

// Process Query with Backend
async function processQuery(text) {
    updateUIState('processing');

    try {
        const response = await fetch('/api/web-chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: text,
                language: languageSelect.options[languageSelect.selectedIndex].getAttribute('data-lang') || (languageSelect.value.startsWith('hi') ? 'hi' : 'en'),
                sessionId: 'web-' + Date.now()
            })
        });

        const data = await response.json();

        if (data.status === 'success') {
            addMessage(data.response, 'assistant');
            speakResponse(data.response, data.language);
        } else {
            addMessage("Sorry, something went wrong.", 'assistant');
        }

    } catch (error) {
        console.error("API Error:", error);
        addMessage("Error connecting to server.", 'assistant');
    } finally {
        updateUIState('idle');
    }
}

// Speak Response
function speakResponse(text, langCode) {
    if (synthesis.speaking) {
        synthesis.cancel();
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = langCode;
    utterance.volume = 1;
    utterance.rate = 1;
    utterance.pitch = 1;

    // Try to find a matching voice
    const voices = synthesis.getVoices();
    // Prefer Google voices if available
    const preferredVoice = voices.find(voice =>
        voice.lang.includes(langCode.split('-')[0]) && voice.name.includes('Google')
    );

    if (preferredVoice) {
        utterance.voice = preferredVoice;
    }

    utterance.onstart = () => {
        voiceWaves.classList.add('active');
    };

    utterance.onend = () => {
        voiceWaves.classList.remove('active');
    };

    synthesis.speak(utterance);
}

// UI Helpers
function updateUIState(state) {
    micButton.classList.remove('listening');
    voiceWaves.classList.remove('active');

    switch (state) {
        case 'listening':
            micButton.classList.add('listening');
            connectionStatus.innerHTML = '<span class="dot" style="background:#ef4444;box-shadow:0 0 8px #ef4444"></span> Listening...';
            break;
        case 'processing':
            connectionStatus.innerHTML = '<span class="dot" style="background:#eab308;box-shadow:0 0 8px #eab308"></span> Thinking...';
            voiceWaves.classList.add('active'); // Simulate thinking activity
            break;
        case 'error':
            connectionStatus.innerHTML = '<span class="dot" style="background:#ef4444"></span> Error';
            break;
        case 'idle':
        default:
            connectionStatus.innerHTML = '<span class="dot"></span> Ready';
            voiceWaves.classList.remove('active');
            break;
    }
}

function addMessage(text, sender) {
    const div = document.createElement('div');
    div.className = `message ${sender}`;
    div.innerHTML = `<p>${text}</p>`;
    chatArea.appendChild(div);
    chatArea.scrollTop = chatArea.scrollHeight;
}

// Event Listeners
micButton.addEventListener('click', () => {
    if (!recognition) initSpeechRecognition();

    if (isListening) {
        recognition.stop();
    } else {
        recognition.lang = languageSelect.value;
        recognition.start();
    }
});

// Initialize
initSpeechRecognition();
// Load voices
window.speechSynthesis.onvoiceschanged = () => {
    console.log("Voices loaded:", window.speechSynthesis.getVoices().length);
};
