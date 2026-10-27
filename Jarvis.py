def renderizar_gods_eye(hex_color):
    gods_eye_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; background: transparent; }}
            #canvas-container {{ width: 100%; height: 320px; position: relative; }}
            #hud-text {{
                position: absolute; top: 10px; left: 10px; 
                font-family: monospace; color: {hex_color}; font-size: 11px;
                background: rgba(0,0,0,0.8); padding: 4px 8px; border-radius: 4px;
                border: 1px solid {hex_color};
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="hud-text">GOD's EYE VIEW // ESTACIÓN ACTIVA: BUIN - SANTIAGO</div>
        </div>
        <script>
            try {{
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 320, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
                renderer.setSize(container.clientWidth, 320);
                container.appendChild(renderer.domElement);

                const geometry = new THREE.SphereGeometry(2, 24, 24);
                const wireframe = new THREE.WireframeGeometry(geometry);
                const line = new THREE.LineSegments(wireframe);
                line.material.color.set('{hex_color}');
                line.material.opacity = 0.8;
                line.material.transparent = true;
                scene.add(line);

                const ringGeo = new THREE.RingGeometry(2.4, 2.45, 64);
                const ringMat = new THREE.MeshBasicMaterial({{ color: '{hex_color}', side: THREE.DoubleSide, transparent: true, opacity: 0.9 }});
                const ring = new THREE.Mesh(ringGeo, ringMat);
                ring.rotation.x = Math.PI / 3;
                scene.add(ring);

                camera.position.z = 5.5;

                function animate() {{
                    requestAnimationFrame(animate);
                    line.rotation.y += 0.004;
                    ring.rotation.z += 0.002;
                    renderer.render(scene, camera);
                }}
                animate();
            } catch (err) {{
                console.error("Error al renderizar el visor 3D:", err);
            }}
        </script>
    </body>
    </html>
    """
    components.html(gods_eye_html, height=330)
