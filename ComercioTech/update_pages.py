import os
import re

base_path = r"c:\Users\juann\OneDrive\Desktop\Sistema-ev-bd_noSql\ComercioTech\Frontend\static\src"

files_and_tags = [
    ("computadores.jsx", "computadores"),
    ("hogarOficina.jsx", "hogarOficina"),
    ("perifericos.jsx", "perifericos"),
    ("componentes.jsx", "componentes"),
    ("conectividadRedes.jsx", "conectividadRedes"),
    ("electronica.jsx", "electronica"),
    ("software.jsx", "software")
]

for filename, tag in files_and_tags:
    file_path = os.path.join(base_path, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Add the import if not present
    if "ListaProductosPorCategoria" not in content:
        content = content.replace(
            "import MainFooter from './components/footer'",
            "import MainFooter from './components/footer'\nimport ListaProductosPorCategoria from './components/ListaProductosPorCategoria'"
        )

    # Replace the paragraph with the component
    content = re.sub(
        r"<p>Contenido de.*?próximamente\.\.\.</p>",
        f'<ListaProductosPorCategoria etiqueta="{tag}" />',
        content
    )

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Pages updated successfully.")
