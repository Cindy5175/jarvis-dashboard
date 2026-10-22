# 5. Generador de Planos / Holo-Taller
    elif (
        "plano" in prompt_lower
        or "diseña" in prompt_lower
        or "genera" in prompt_lower
        or "prototipo" in prompt_lower
        or "holograma" in prompt_lower
    ):
      response = f"🔵 **J.A.R.V.I.S.:** Renderizando proyecciones holográficas para la directiva: *'{prompt}'*. Eche un vistazo al plano antes de que explote el taller, Jefa."

      # Limpiamos el texto del prompt para la URL de la imagen
      import urllib.parse

      prompt_url = urllib.parse.quote(prompt)
      # Generador libre por URL sin necesidad de API Keys
      widget_html = f"""
            <div style="text-align: center; border: 1px solid #00f0ff; padding: 10px; border-radius: 10px; background-color: #050505;">
                <p style="color: #00f0ff; font-family: monospace; margin-bottom: 5px;">HOLO-TALLER // PROTOTIPO ACTIVO</p>
                <img src="https://image.pollinations.ai/prompt/{prompt_url}%20futuristic%20blueprint%20cyberpunk%20stark%20tech" width="100%" style="border-radius: 5px;">
            </div>
            """
