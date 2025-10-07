import pandas as pd
import bcrypt
import os

def cargar_usuarios():
    path = os.path.join("data", "usuarios.csv")
    if not os.path.exists(path):
        return []

    df = pd.read_csv(path)
    usuarios = []
    for _, row in df.iterrows():
        try:
            usuario = str(row["usuario"]).strip()
            hash_pw = str(row["hash"]).strip()
            rol = str(row["rol"]).strip().lower()
            salones_raw = str(row["salones"]).strip()
            salones = [s.strip(' "\'') for s in salones_raw.replace("[", "").replace("]", "").split(",") if s.strip()]
            usuarios.append({"usuario": usuario, "hash": hash_pw, "rol": rol, "salones": salones})
        except Exception as e:
            print(f"[AUTH] Error leyendo fila: {e}")
    return usuarios


def verificar_login(username, password):
    usuarios = cargar_usuarios()
    for u in usuarios:
        if u["usuario"].lower() == username.lower():
            try:
                if bcrypt.checkpw(password.encode("utf-8"), u["hash"].encode("utf-8")):
                    return u
            except ValueError:
                print("[AUTH] Hash inválido para usuario:", username)
                return None
    return None