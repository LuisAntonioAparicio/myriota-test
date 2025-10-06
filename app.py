# app.py
from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Archivo para guardar los mensajes (persistente)
MESSAGES_FILE = "myriota_messages.json"

def load_messages():
    """Cargar mensajes desde archivo"""
    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_message(data):
    """Guardar nuevo mensaje"""
    messages = load_messages()
    
    new_message = {
        "id": len(messages) + 1,
        "received_at": datetime.now().isoformat(),
        "data": data
    }
    
    messages.append(new_message)
    
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)
    
    return new_message

@app.route('/', methods=['GET'])
def home():
    """Página principal"""
    return """
    <html>
        <head>
            <title>🚀 Myriota Webhook Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f0f0f0; padding: 10px; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>📡 Servidor de Prueba Myriota</h1>
            <p>Este servidor está listo para recibir mensajes de Myriota</p>
            
            <h2>📋 Endpoints disponibles:</h2>
            <div class="endpoint">
                <strong>POST</strong> <code>/webhook/myriota</code> - Recibir mensajes<br>
                <strong>GET</strong> <code>/messages</code> - Ver todos los mensajes<br>
                <strong>GET</strong> <code>/clear</code> - Limpiar mensajes
            </div>
            
            <h2>🔧 Uso:</h2>
            <p>Configura en Myriota Device Manager la URL:</p>
            <code id="webhookUrl">https://[TU_URL_AQUI]/webhook/myriota</code>
            
            <script>
                // Mostrar la URL actual
                document.getElementById('webhookUrl').textContent = 
                    window.location.origin + '/webhook/myriota';
            </script>
        </body>
    </html>
    """

@app.route('/webhook/myriota', methods=['POST'])
def webhook_myriota():
    """Endpoint para recibir mensajes de Myriota"""
    try:
        # Log completo para debugging
        print("=" * 50)
        print("📨 NUEVO MENSAJE RECIBIDO")
        print("=" * 50)
        
        # Headers
        print("📋 HEADERS:")
        for key, value in request.headers:
            print(f"  {key}: {value}")
        
        # Datos JSON
        if request.is_json:
            json_data = request.get_json()
            print("📦 JSON DATA:")
            print(json.dumps(json_data, indent=2))
        else:
            print("📦 RAW DATA:", request.data)
        
        # Parámetros query string
        print("🔍 QUERY PARAMS:", dict(request.args))
        
        # Form data
        print("📝 FORM DATA:", dict(request.form))
        
        # Guardar el mensaje
        message_to_save = {
            "headers": dict(request.headers),
            "json": request.get_json(silent=True),
            "args": dict(request.args),
            "form": dict(request.form),
            "raw_data": request.data.decode('utf-8') if request.data else None,
            "timestamp": datetime.now().isoformat()
        }
        
        saved_message = save_message(message_to_save)
        
        print(f"✅ Mensaje guardado con ID: {saved_message['id']}")
        print("=" * 50)
        
        return jsonify({
            "status": "success",
            "message": "Datos recibidos correctamente",
            "message_id": saved_message['id'],
            "received_at": saved_message['received_at']
        }), 200
        
    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    """Ver todos los mensajes recibidos"""
    messages = load_messages()
    
    html = f"""
    <html>
        <head><title>Mensajes Recibidos</title></head>
        <body>
            <h1>📨 Mensajes Recibidos: {len(messages)}</h1>
            <a href="/">← Volver al inicio</a>
            <hr>
    """
    
    for msg in messages:
        html += f"""
        <div style="border: 1px solid #ccc; margin: 10px; padding: 15px;">
            <h3>Mensaje #{msg['id']} - {msg['received_at']}</h3>
            <pre>{json.dumps(msg['data'], indent=2)}</pre>
        </div>
        """
    
    html += "</body></html>"
    return html

@app.route('/clear', methods=['GET'])
def clear_messages():
    """Limpiar todos los mensajes"""
    with open(MESSAGES_FILE, 'w') as f:
        json.dump([], f)
    return "✅ Todos los mensajes han sido eliminados. <a href='/'>Volver</a>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
