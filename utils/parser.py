import json
import zipfile
from io import BytesIO

def _extraer_nombres(entry):
    """
    Devuelve lista con un nombre (o vacío) según formato variable.
    """
    if isinstance(entry, str):
        return [entry]

    if isinstance(entry, dict):
        # followers
        sld = entry.get("string_list_data")
        if isinstance(sld, list) and sld:
            value = sld[0].get("value")
            if value:
                return [value]

        # following nuevo
        if "value" in entry:
            return [entry["value"]]

    return []

def extraer_json_desde_zip(zip_bytes):
    """
    Lee un ZIP exportado por Instagram y devuelve (followers, following)
    sin escribir nada en disco.
    """
    zf = zipfile.ZipFile(BytesIO(zip_bytes))
    followers, following = [], []
    for name in zf.namelist():
        if not name.endswith(".json"):
            continue

        # --- identifica el tipo de archivo ---
        is_following_file = name.endswith("/following.json") or name.endswith("following.json")
        is_follower_file  = (
            "followers" in name
            and not is_following_file        # evita confusión con following.json
        )

        with zf.open(name) as f:
            try:
                data = json.load(f)
            except Exception as e:
                print(f"[WARN] JSON corrupto en {name}: {e}")
                continue

            if is_follower_file:
                for entry in data:
                    followers.extend(_extraer_nombres(entry))

            elif is_following_file:
                if isinstance(data, list):
                    for entry in data:
                        following.extend(_extraer_nombres(entry))
                elif isinstance(data, dict):
                    for entry in data.get("relationships_following", []):
                        following.extend(_extraer_nombres(entry))
    return followers, following

def no_te_siguen(followers, following):
    """
    Diferencia de conjuntos, ordenada alfabéticamente.
    """
    return sorted(set(following) - set(followers))