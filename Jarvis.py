# 4. Función del Mapa Cartográfico con Leaflet (Libre y 100% Funcional sin errores)
def renderizar_mapa_tactico(modo):
    # Capas públicas estables y gratuitas (CartoDB Positron para Día, CartoDB Dark Matter para Noche)
    if modo == "dia":
        tile_layer = "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
    else:
        tile_layer = "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
    
    mapa_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>
            body {{ margin: 0; padding: 0; }}
            #map {{ width: 100%; height: 400px; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            const map = L.map('map').setView([-33.7331, -70.7072], 12);
            
            L.tileLayer('{tile_layer}', {{
                maxZoom: 19,
                attribution: '© OpenStreetMap & CARTO'
            }}).addTo(map);

            L.marker([-33.7331, -70.7072]).addTo(map)
                .bindPopup('<b>Base Operativa Buin</b><br>Telemetría activa.')
                .openPopup();

            L.marker([-33.4489, -70.6693]).addTo(map)
                .bindPopup('<b>Santiago Centro</b><br>Grid Táctico.');
        </script>
    </body>
    </html>
    """
    components.html(mapa_html, height=410)
