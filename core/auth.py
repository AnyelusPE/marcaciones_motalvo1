import pandas as pd

def verificar_login(usuario, contraseña):
    """Verifica usuario y contraseña desde core/usuarios.csv"""
    df = pd.read_csv("core/usuarios.csv")
    fila = df[(df["usuario"].str.lower() == usuario.lower()) & (df["contraseña"] == contraseña)]

    if not fila.empty:
        return {
            "usuario": fila.iloc[0]["usuario"],
            "rol": fila.iloc[0]["rol"]
        }
    return None
