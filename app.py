import os
import uuid
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Ruta para subir archivos .glb
@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if not file.filename.lower().endswith('.glb'):
        return jsonify({'error': 'Only .glb files allowed'}), 400

    file_id = str(uuid.uuid4())
    filename = f"{file_id}.glb"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    viewer_url = f"{request.host_url}viewer/{file_id}"
    return jsonify({'viewer_url': viewer_url})


# Visor 3D usando Three.js
@app.route('/viewer/<file_id>')
def viewer(file_id):
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>3D Viewer</title>
        <style> body {{ margin: 0; }} canvas {{ display: block; }} </style>
    </head>
    <body>
        <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/build/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.152.2/examples/js/loaders/GLTFLoader.js"></script>
        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(75, window.innerWidth/window.innerHeight, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{antialias:true}});
            renderer.setSize(window.innerWidth, window.innerHeight);
            document.body.appendChild(renderer.domElement);

            const light = new THREE.DirectionalLight(0xffffff, 1);
            light.position.set(0, 10, 10);
            scene.add(light);

            const loader = new THREE.GLTFLoader();
            loader.load('{request.host_url}static/uploads/{file_id}.glb',
                function(gltf) {{
                    scene.add(gltf.scene);
                    animate();
                }},
                undefined,
                function(error) {{
                    alert('Error loading model');
                    console.error(error);
                }}
            );

            camera.position.z = 5;

            function animate() {{
                requestAnimationFrame(animate);
                renderer.render(scene, camera);
            }}

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth/window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
        </script>
    </body>
    </html>
    """
    return html


# Archivos estáticos
@app.route('/static/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


# 🔥 Ejecutar en Render o localmente
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
