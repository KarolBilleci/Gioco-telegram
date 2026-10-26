import os
import sys
import qrcode

# Uso: python make_qr.py NomeUtenteDelBot [numero_tappe]
# Esempio: python make_qr.py TrapaniNoirBot 4
if len(sys.argv) < 2:
    sys.exit("Uso: python make_qr.py NomeUtenteDelBot [numero_tappe]")

username = sys.argv[1].lstrip("@")
n = int(sys.argv[2]) if len(sys.argv) > 2 else 4

os.makedirs("qr", exist_ok=True)
for i in range(1, n + 1):
    url = f"https://t.me/{username}?start=tappa{i}"
    img = qrcode.make(url, box_size=14, border=4)
    img.save(f"qr/tappa{i}.png")
    print(url)
