# app_myriota_labview.py
from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

app = Flask(__name__)

# Archivo para almacenar mensajes en formato simple
MESSAGES_FILE = "myriota_messages.json"

@app.route('/myriota-webhook', methods=['POST'])
def myriota_webhook():
    """
    Endpoint ESPECÍFICO para Myriota
    Formato limpio para fácil procesamiento en LabVIEW
    """
    try:
        # Obtener timestamp actual
        received_time = datetime.now().isoformat()
        
        # Preparar datos en formato estructurado
        message_data = {
            "labview_id": f"msg_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "received_at": received_time,
            "raw_payload": request.get_json(silent=True) or request.data.decode() if request.data else None,
            "device_info": {
                "headers": dict(request.headers),
                "query_params": dict(request.args)
            }
        }
        
        # Guardar mensaje
        save_message(message_data)
        
        print(f"✅ Myriota → LabVIEW: {message_data['labview_id']}")
        
        # Respuesta MUY SIMPLE que Myriota espera
        return jsonify({
            "status": "success",
            "id": message_data["labview_id"],
            "received_at": received_time
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

def save_message(message):
    """Guardar mensaje en formato simple para LabVIEW"""
    try:
        # Cargar mensajes existentes
        try:
            with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            messages = []
        
        # Agregar nuevo mensaje
        messages.append(message)
        
        # Mantener solo los últimos 100 mensajes (opcional)
        if len(messages) > 100:
            messages = messages[-100:]
        
        # Guardar
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        print(f"Error guardando: {e}")

@app.route('/labview-data', methods=['GET'])
def get_labview_data():
    """
    Endpoint para que LabVIEW consulte los mensajes
    Formato OPTIMIZADO para LabVIEW
    """
    try:
        with open(MESSAGES_FILE, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        # Formato optimizado para LabVIEW
        response = {
            "success": True,
            "total_messages": len(messages),
            "timestamp": datetime.now().isoformat(),
            "messages": messages
        }
        
        return jsonify(response)
        
    except FileNotFoundError:
        return jsonify({
            "success": True,
            "total_messages": 0,
            "timestamp": datetime.now().isoformat(),
            "messages": []
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/clear-data', methods=['POST'])
def clear_data():
    """Limpiar todos los mensajes (útil para testing)"""
    try:
        with open(MESSAGES_FILE, 'w', encoding='utf-8') as f:
            json.dump([], f)
        return jsonify({"success": True, "message": "Data cleared"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    """Simple health check"""
    return jsonify({"status": "healthy", "service": "myriota-labview-bridge"})

# Solo 4 endpoints específicos, nada de HTML
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🚀 Myriota-LabVIEW Bridge running on port {port}")
    app.run(host='0.0.0.0', port=port)
