# SISMOS CSN EN TIEMPO REAL
    st.divider()
    st.subheader("🌍 Telemetría Sísmica CSN")
    if ultimo_sismo_check:
        lugar_s = ultimo_sismo_check.get('RefGeografica', 'Chile')
        mag_s = ultimo_sismo_check.get('Magnitud', 'N/A')
        fecha_s = ultimo_sismo_check.get('Fecha', 'Reciente')
        st.markdown(f"""
        <div style="
            background-color: #0b1320;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        ">
            <span style="color: #00a8b5; font-size: 12px; display: block;">📍 {lugar_s}</span>
            <span style="color: #00f3ff; font-size: 14px; font-weight: bold; display: block; margin-top: 4px;">Magnitud: {mag_s} Richter</span>
            <span style="color: #00a8b5; font-size: 11px; display: block; margin-top: 4px;">🕒 {fecha_s}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="
            background-color: #0b1320;
            border: 1px solid #00f3ff;
            border-radius: 8px;
            padding: 10px;
            font-family: monospace;
            box-shadow: 0 0 10px rgba(0, 243, 255, 0.3);
        ">
            <span style="color: #00a8b5; font-size: 12px; display: block;">📍 Red CSN Chile</span>
            <span style="color: #00f3ff; font-size: 13px; font-weight: bold; display: block; margin-top: 4px;">🟢 Perímetro Estable</span>
            <span style="color: #00a8b5; font-size: 11px; display: block; margin-top: 4px;">Sin anomalías registradas</span>
        </div>
        """, unsafe_allow_html=True)
