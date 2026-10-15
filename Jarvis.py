# REPRODUCTOR DE MÚSICA SPOTIFY (ANNA DAHL & SYNTHWAVE / CYBERPUNK)
with col_orbe:
    st.markdown('<div class="holo-card">', unsafe_allow_html=True)
    st.markdown('<div class="holo-title">🎵 AMBIENTE ACÚSTICO // AUDIO TÁCTICO BÚNKER 🟢 SPOTIFY</div>', unsafe_allow_html=True)
    
    # Selección de estación / artista en Spotify
    opciones_spotify = {
        "🤠 Anna Dahl (Country / Rock)": "https://open.spotify.com/embed/artist/54sB8l0wL6XhHwX3rL8mXg?utm_source=generator&theme=0",
        "⚡ Ambient Instrumental / Synthwave": "https://open.spotify.com/embed/playlist/37i9dQZF1DXdLENR312A35?utm_source=generator&theme=0"
    }
    
    estacion_sp = st.selectbox("Seleccionar Frecuencia Spotify:", list(opciones_spotify.keys()))
    url_spotify_embed = opciones_spotify[estacion_sp]

    spotify_iframe_html = f"""
    <iframe style="border-radius:12px" 
            src="{url_spotify_embed}" 
            width="100%" 
            height="152" 
            frameBorder="0" 
            allowfullscreen="" 
            allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" 
            loading="lazy">
    </iframe>
    """
    components.html(spotify_iframe_html, height=160)
