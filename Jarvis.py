import streamlit.components.v1 as components

def renderizar_gods_eye_view(color_hud="#00d2ff"):
    gods_eye_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            body {{ margin: 0; overflow: hidden; background: transparent; }}
            #canvas-container {{ width: 100%; height: 350px; position: relative; }}
            #hud-label {{
                position: absolute; top: 10px; left: 10px; 
                font-family: monospace; color: {color_hud}; 
                font-size: 11px; letter-spacing: 1px;
                background: rgba(0,0,0,0.6); padding: 4px 8px; border-radius: 4px;
            }}
        </style>
    </head>
    <body>
        <div id="canvas-container">
            <div id="hud-label">GOD's EYE VIEW // COORD: BUIN - SANTIAGO CHILE</div>
        </div>
        <script>
            const container = document.getElementById('canvas-container');
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 350, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ alpha: true, antialias: true }});
            renderer.setSize(container.clientWidth, 350);
            container.appendChild(renderer.domElement);

            // Esfera holográfica táctica
            const geometry = new THREE.SphereGeometry(2, 24, 24);
            const wireframe = new THREE.WireframeGeometry(geometry);
            const line = new THREE.LineSegments(wireframe);
            line.material.color.set('{color_hud}');
            line.material.opacity = 0.4;
            line.material.transparent = true;
            scene.add(line);

            // Anillos orbitales
            const ringGeo = new THREE.RingGeometry(2.5, 2.55, 64);
            const ringMat = new THREE.MeshBasicMaterial({{ color: '{color_hud}', side: THREE.DoubleSide, transparent: true, opacity: 0.6 }});
            const ring = new THREE.Mesh(ringGeo, ringMat);
            ring.rotation.x = Math.PI / 3;
            scene.add(ring);

            camera.position.z = 6;

            function animate() {{
                requestAnimationFrame(animate);
                line.rotation.y += 0.005;
                ring.rotation.z += 0.003;
                renderer.render(scene, camera);
            }}
            animate();
        </script>
    </body>
    </html>
    """
    components.html(gods_eye_html, height=360)
