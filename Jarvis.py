def renderizar_globo_terraqueo(hex_color):
    try:
        glogo_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <style>
                body { margin: 0; overflow: hidden; background: transparent; display: flex; flex-direction: column; align-items: center; justify-content: center; }
                #canvas-container { width: 100%; height: 230px; display: flex; justify-content: center; align-items: center; position: relative; }
                #orbit-hud { font-family: monospace; color: HEX_COLOR_REPLACE; font-size: 11px; background: rgba(0,0,0,0.85); padding: 4px 12px; border-radius: 4px; border: 1px solid HEX_COLOR_REPLACE; box-shadow: 0 0 10px HEX_COLOR_REPLACE; text-align: center; margin-top: 6px; letter-spacing: 1px; }
            </style>
        </head>
        <body>
            <div id="canvas-container"></div>
            <div id="orbit-hud">OJO DE DIOS // MAPA MUNDIAL SATELITAL</div>
            <script>
                const container = document.getElementById('canvas-container');
                const scene = new THREE.Scene();
                const camera = new THREE.PerspectiveCamera(45, container.clientWidth / 230, 0.1, 1000);
                const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
                renderer.setSize(container.clientWidth, 230);
                container.appendChild(renderer.domElement);
                
                const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
                scene.add(ambientLight);
                
                const earthGroup = new THREE.Group();
                scene.add(earthGroup);

                // Esfera base de referencia sutil
                const geometry = new THREE.SphereGeometry(1.6, 24, 24);
                const material = new THREE.MeshBasicMaterial({ 
                    color: 'HEX_COLOR_REPLACE', 
                    wireframe: true, 
                    transparent: true, 
                    opacity: 0.12 
                });
                const earth = new THREE.Mesh(geometry, material);
                earthGroup.add(earth);

                // Malla densa de puntos simulando continentes y red global activa
                const dotsGeometry = new THREE.BufferGeometry();
                const count = 1200;
                const positions = [];
                
                for (let i = 0; i < count; i++) {
                    const u = Math.random();
                    const v = Math.random();
                    const theta = u * 2.0 * Math.PI;
                    const phi = Math.acos(2.0 * v - 1.0);
                    
                    // Filtrado matemático para simular masas continentales y meridianos
                    const xCoord = Math.sin(phi) * Math.cos(theta);
                    const yCoord = Math.cos(phi);
                    const zCoord = Math.sin(phi) * Math.sin(theta);
                    
                    // Patrón de continentes y anillos de radar
                    if ((Math.abs(xCoord * 3) % 1.5 < 0.8) && (Math.abs(yCoord * 2) % 1.2 < 0.9) || Math.abs(zCoord) > 0.5) {
                        const r = 1.65;
                        positions.push(r * xCoord, r * yCoord, r * zCoord);
                    }
                }
                
                dotsGeometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
                const dotsMaterial = new THREE.PointsMaterial({ color: 'HEX_COLOR_REPLACE', size: 0.055 });
                const continents = new THREE.Points(dotsGeometry, dotsMaterial);
                earthGroup.add(continents);
                
                // Anillo orbital satelital principal
                const ringGeometry = new THREE.RingGeometry(2.05, 2.08, 64);
                const ringMaterial = new THREE.MeshBasicMaterial({ color: 'HEX_COLOR_REPLACE', side: THREE.DoubleSide, transparent: true, opacity: 0.7 });
                const orbitRing = new THREE.Mesh(ringGeometry, ringMaterial);
                orbitRing.rotation.x = Math.PI / 3;
                scene.add(orbitRing);
                
                camera.position.z = 4.8;
                
                function animate() {
                    requestAnimationFrame(animate);
                    earthGroup.rotation.y += 0.0035;
                    orbitRing.rotation.z += 0.0025;
                    renderer.render(scene, camera);
                }
                animate();
            </script>
        </body>
        </html>
        """.replace("HEX_COLOR_REPLACE", hex_color)
        
        components.html(glogo_html, height=280, scrolling=False)
    except Exception as e:
        str_lit.error(f"Error en Globo Terráqueo: {e}")
