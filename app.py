from flask import Flask, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Servir arquivos estáticos (HTML, CSS, JS, JSON)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('.', filename)

# Página principal (index.html)
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
