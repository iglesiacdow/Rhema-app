from pathlib import Path
import shutil

archivo = Path("app.py")
respaldo = Path("app.py.bak_antes_reactivar_login")

shutil.copy2(archivo, respaldo)

texto = archivo.read_text(encoding="utf-8")

buscado = "\n# verificar_login()  # 🔓 Protección desactivada (uso personal)\n"
nuevo = "\nverificar_login()\n"

if buscado not in texto:
    print("❌ No se encontró la línea comentada. Puede que ya esté activa o el texto cambió.")
else:
    archivo.write_text(texto.replace(buscado, nuevo, 1), encoding="utf-8")
    print("✅ Login reactivado correctamente.")
    print(f"✅ Respaldo creado: {respaldo}")
