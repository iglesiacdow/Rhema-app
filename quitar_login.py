from pathlib import Path
import shutil

archivo = Path("app.py")
respaldo = Path("app.py.bak_antes_quitar_login")

shutil.copy2(archivo, respaldo)

texto = archivo.read_text(encoding="utf-8")

buscado = "\nverificar_login()\n"
nuevo = "\n# verificar_login()  # 🔓 Protección desactivada (uso personal)\n"

if buscado not in texto:
    print("❌ No se encontró la línea exacta 'verificar_login()' en app.py.")
    print("No se modificó el archivo. El respaldo fue creado igualmente.")
else:
    archivo.write_text(texto.replace(buscado, nuevo, 1), encoding="utf-8")
    print("✅ Protección de login desactivada correctamente.")
    print(f"✅ Respaldo creado: {respaldo}")
