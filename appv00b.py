# app.py
from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Archivo para guardar los mensajes
MESSAGES_FILE = "myriota_messages.json"

def load_messages():
    """Cargar mensajes desde archivo"""
    try:
        with open(MESSAGES_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
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
    
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump(messages, f, indent=2)
    except Exception as e:
        print(f"Error guardando mensaje: {e}")
    
    return new_message

@app.route('/', methods=['GET'])
def home():
    """Página principal"""
    return '''
    <html>
        <head>
            <title>🚀 Myriota Webhook Test</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                .endpoint { background: #f0f0f0; padding: 15px; border-radius: 8px; margin: 20px 0; }
                code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            </style>
        </head>
        <body>
            <h1>📡 Servidor de Prueba Myriota</h1>
            <p>¡El servidor está funcionando correctamente! 🎉</p>
            
            <div class="endpoint">
                <h3>📋 Endpoints disponibles:</h3>
                <p><strong>POST</strong> <code>/webhook/myriota</code> - Recibir mensajes de Myriota</p>
                <p><strong>GET</strong> <code>/messages</code> - Ver todos los mensajes recibidos</p>
                <p><strong>GET</strong> <code>/clear</code> - Limpiar mensajes (solo pruebas)</p>
            </div>
            
            <h3>🔧 Para configurar en Myriota:</h3>
            <p>Usa esta URL en Myriota Device Manager:</p>
            <code id="webhookUrl"></code>
            
            <script>
                document.getElementById('webhookUrl').textContent = 
                    window.location.origin + '/webhook/myriota';
            </script>
        </body>
    </html>
    '''

@app.route('/webhook/myriota', methods=['POST', 'GET'])
def webhook_myriota():
    """Endpoint para recibir mensajes de Myriota"""
    try:
        print("📨 Solicitud recibida en /webhook/myriota")
        
        if request.method == 'GET':
            return jsonify({
                "status": "ready",
                "message": "Endpoint listo para recibir POST de Myriota"
            })
        
        # Procesar POST request
        message_data = {
            "headers": dict(request.headers),
            "json": request.get_json(silent=True),
            "args": dict(request.args),
            "form": dict(request.form),
            "raw_data": request.data.decode('utf-8') if request.data else None,
            "timestamp": datetime.now().isoformat(),
            "method": request.method
        }
        
        print(f"✅ Datos recibidos: {json.dumps(message_data, indent=2)}")
        
        # Guardar el mensaje
        saved_message = save_message(message_data)
        
        return jsonify({
            "status": "success",
            "message": "Datos recibidos correctamente",
            "message_id": saved_message['id'],
            "received_at": saved_message['received_at']
        }), 200
        
    except Exception as e:
        print(f"❌ Error en webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/messages', methods=['GET'])
def get_messages():
    """Ver todos los mensajes recibidos"""
    try:
        messages = load_messages()
        
        response = {
            "total_messages": len(messages),
            "messages": messages
        }
        
        # Si es solicitud HTML, mostrar página bonita
        if request.headers.get('Accept', '').find('text/html') >= 0:
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
                <div style="border: 1px solid #ddd; margin: 15px; padding: 15px; border-radius: 8px;">
                    <h3>Mensaje #{msg['id']} - {msg['received_at']}</h3>
                    <pre style="background: #f5f5f5; padding: 10px; border-radius: 5px;">
{json.dumps(msg['data'], indent=2, ensure_ascii=False)}
                    </pre>
                </div>
                """
            
            html += "</body></html>"
            return html
        else:
            return jsonify(response)
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/clear', methods=['GET'])
def clear_messages():
    """Limpiar todos los mensajes (solo para pruebas)"""
    try:
        with open(MESSAGES_FILE, 'w') as f:
            json.dump([], f)
        return "✅ Todos los mensajes han sido eliminados. <a href='/'>Volver al inicio</a>"
    except Exception as e:
        return f"❌ Error: {str(e)}"

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud para Render"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

# Configuración para producción
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
