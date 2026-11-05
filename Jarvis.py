import os
import fitz  # PyMuPDF

def cargar_documentos_pdf(directorio):
    texto_total = ""
    for archivo in os.listdir(directorio):
        if archivo.endswith(".pdf"):
            ruta_pdf = os.path.join(directorio, archivo)
            doc = fitz.open(ruta_pdf)
            for pagina in doc:
                texto_total += pagina.get_text()
    return texto_total
