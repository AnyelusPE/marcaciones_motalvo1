import bcrypt
import csv

usuarios = [
    ("gabriela", "12345678", "financista", "TRUJILLO MALL,FM BARRANCO,FM BELLAVISTA,FM JAVIER PRADO"),
    ("FM_BARRANCO", "barranco", "salon", "FM BARRANCO"),
    ("FM_BELLAVISTA", "bellavista", "salon", "FM BELLAVISTA"),
    ("FM_JAVIER_PRADO", "jprado", "salon", "FM JAVIER PRADO"),
    ("TRUJILLO_MALL", "tmall", "salon", "TRUJILLO MALL"),
    ("ely", "1234", "financista", "DOS DE MAYO,ESCOBEDO,FM LA MOLINA"),
    ("efrain", "1234", "financista", "BELLAVISTA MIXTO,GARZON MIXTO,UNIVERSITARIA,PRIMAVERA"),
    ("arturo", "1234", "financista", "FM JAVIER PRADO,SJM"),
    ("admin", "admin", "admin", "todos"),
]

with open("data/usuarios.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["usuario", "hash", "rol", "salones"])

    for u, p, r, s in usuarios:
        hashed = bcrypt.hashpw(p.encode("utf-8"), bcrypt.gensalt()).decode()
        writer.writerow([u, hashed, r, s])

print("✅ Archivo usuarios.csv regenerado con éxito")