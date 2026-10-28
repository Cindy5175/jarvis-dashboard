with col_street:
    str_lit.markdown("### 🏙️ Explorador Urbano (Street View)")
    ciudades_mundo = {
        "Valparaíso, Chile (Cámara / Costa)": (-33.0472, -71.6127),
        "Buin, Chile (Base Local)": (-33.7331, -70.7072),
        "Santiago de Chile": (-33.4489, -70.6693),
        "Viña del Mar, Chile": (-33.0245, -71.5518),
        "Concepción, Chile": (-36.8201, -73.0444),
        "La Serena, Chile": (-29.9045, -71.2489),
        "Tokio, Japón": (35.6762, 139.6503),
        "Nueva York, EE.UU.": (40.7128, -74.0060),
        "Londres, Reino Unido": (51.5074, -0.1278),
        "París, Francia": (48.8566, 2.3522),
        "Sídney, Australia": (-33.8688, 151.2093),
        "Roma, Italia": (41.9028, 12.4964)
    }
    ciudad_seleccionada = str_lit.selectbox("Seleccione Sector Urbano:", list(ciudades_mundo.keys()), key="select_street_view")
    lat_c, lon_c = ciudades_mundo[ciudad_seleccionada]
    str_lit.markdown(f"**Navegando: {ciudad_seleccionada}**")
    renderizar_street_view(lat_c, lon_c)
