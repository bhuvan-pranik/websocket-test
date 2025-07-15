from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn
import ssl
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/")
async def get():
    return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket SSL Test</title>
</head>
<body>
    <h1>WebSocket SSL Test</h1>
    <div id="messages"></div>
    <input type="text" id="messageInput" placeholder="Type a message...">
    <button onclick="sendMessage()">Send</button>
    <button onclick="connect()">Connect</button>
    <button onclick="disconnect()">Disconnect</button>

    <script>
        let ws = null;
        const messages = document.getElementById('messages');
        
        function connect() {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            ws = new WebSocket(`${protocol}//${window.location.host}/ws`);
            
            ws.onopen = function(event) {
                addMessage('Connected to WebSocket');
            };
            
            ws.onmessage = function(event) {
                addMessage('Received: ' + event.data);
            };
            
            ws.onclose = function(event) {
                addMessage('WebSocket connection closed');
            };
            
            ws.onerror = function(error) {
                addMessage('WebSocket error: ' + error);
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
                ws = null;
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            if (ws && input.value) {
                ws.send(input.value);
                addMessage('Sent: ' + input.value);
                input.value = '';
            }
        }
        
        function addMessage(message) {
            const div = document.createElement('div');
            div.textContent = new Date().toLocaleTimeString() + ' - ' + message;
            messages.appendChild(div);
        }
        
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
    """)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass

if __name__ == "__main__":
    # Get SSL configuration from environment
    ssl_certfile = os.getenv("SSL_CERTFILE", "cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", "key.pem")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8443"))
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile
    )