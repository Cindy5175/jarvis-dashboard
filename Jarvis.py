    st.markdown("---")
    st.markdown("#### 🛰️ Mapa Táctico Satelital")

    with st.expander("🌐 Cyber Threat Map", expanded=False):
        st.markdown(
            """<div class="cyber-radar-screen">
            <p style="color: #ff3333; font-size: 0.75rem; margin: 0;" class="radar-blip"><b>🔴 10,940,428 ATAQUES HOY</b></p>
            <p style="color: #00f3ff; font-size: 0.65rem; margin: 3px 0;">[ Rastreo Global Activo ]</p>
            <hr style="border-color: #00f3ff; opacity: 0.3; margin: 5px 0;">
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Japan ➔ Germany</b><br><span style="color:#ff3333;">[Exploit detectado]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>United States ➔ Honduras</b><br><span style="color:#bf7fff;">[Phishing activo]</span></p>
            <p style="font-size: 0.65rem; text-align: left; margin: 2px 0;"><b>Nodo Buin ➔ Seguro</b><br><span style="color:#00ff88;">[0 intrusiones]</span></p>
        </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown("👁️ **OSIRIS:** En línea")
        st.link_button(
            "🚀 Abrir OSIRIS",
            "https://osiris.mclaren.com/",
            use_container_width=True,
        )

        st.markdown("🌍 **PlanetEar:** Sincronizado")
        st.link_button(
            "🌐 Abrir PlanetEar",
            "https://www.planet.com/",
            use_container_width=True,
        )

        st.markdown("🛰️ **USGS Explorer:**")
        st.link_button(
            "🗺️ USGS Explorer",
            "https://earthexplorer.usgs.gov/",
            use_container_width=True,
        )
