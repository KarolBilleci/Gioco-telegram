import os
import sys
import qrcode

# Uso: python make_qr.py NomeUtenteDelBot
if len(sys.argv) < 2:
    sys.exit("Uso: python make_qr.py NomeUtenteDelBot")

username = sys.argv[1].lstrip("@")

os.makedirs("QRCode", exist_ok=True)

# 1. QR code di inizio / punto 0
url_inizio = f"https://t.me/{username}?start=0"
img = qrcode.make(url_inizio, box_size=14, border=4)
img.save("QRCode/inizio.png")
print(f"Generato: {url_inizio}")

# 2. I 4 QR code per le tappe (da 1 a 4)
for i in range(1, 5):
    url = f"https://t.me/{username}?start={i}"
    img = qrcode.make(url, box_size=14, border=4)
    img.save(f"QRCode/tappa{i}.png")
    print(f"Generato: {url}")
