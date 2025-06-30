from flask import Flask, request, jsonify
from datetime import datetime
import json
import os


app = Flask(__name__)



@app.route('/recolectar', methods=['POST'])
def recolectar_datos():
    """
    Este endpoint recibe los datos del sistema en formato JSON,
    los valida y los guarda en un archivo JSON en la misma carpeta que app.py.
    """
    
    if not request.is_json:
        return jsonify({"mensaje": "La solicitud debe ser en formato JSON"}), 400

    
    data = request.get_json()

    
    if not isinstance(data, dict) or 'CPU Info' not in data or 'Operating System' not in data:
        return jsonify({"mensaje": "Estructura de datos inválida. Faltan campos requeridos."}), 400

    
    data['timestamp'] = datetime.now().isoformat()

   
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"system_info_{timestamp_str}.json"
    
    
   
    file_path = os.path.join(os.path.dirname(__file__), filename)
    
    try:
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
       
        print(f"Datos guardados exitosamente en: {file_path}")
        return jsonify({
            "mensaje": "Datos recolectados y guardados exitosamente", 
            "ruta_archivo": file_path
        }), 201 
        
    except IOError as e:
        
        print(f"Error al guardar el archivo: {e}")
        return jsonify({"mensaje": f"Error del servidor al guardar los datos: {e}"}), 500


@app.route('/status', methods=['GET'])
def get_status():
    """
    Endpoint para verificar el estado de la API.
    """
    return jsonify({"status": "API de recolección de datos funcionando"}), 200


if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=True)