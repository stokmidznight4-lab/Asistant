import json
import os
from config import DATA_DIR

USERS_FILE = os.path.join(DATA_DIR, "users.json")


def _load():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def _save(data):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _get_user(data, user_id):
    uid = str(user_id)
    if uid not in data:
        data[uid] = {
            "model": None,          # provider aktif, None = pakai default
            "history": [],          # riwayat percakapan [{role, content}, ...]
            "jadwal": [],           # [{hari, jam, matkul}]
            "tugas": [],            # [{judul, deadline, selesai}]
            "catatan": [],          # [{judul, isi}]
        }
    return data[uid]


# ---------- MODEL AKTIF ----------
def get_active_model(user_id, default_model):
    data = _load()
    user = _get_user(data, user_id)
    return user["model"] or default_model


def set_active_model(user_id, provider):
    data = _load()
    user = _get_user(data, user_id)
    user["model"] = provider
    _save(data)


# ---------- HISTORY PERCAKAPAN ----------
MAX_HISTORY = 20  # jumlah pesan (user+ai) yang disimpan per user, biar hemat token

def get_history(user_id):
    data = _load()
    user = _get_user(data, user_id)
    return user["history"]


def add_to_history(user_id, role, content):
    data = _load()
    user = _get_user(data, user_id)
    user["history"].append({"role": role, "content": content})
    user["history"] = user["history"][-MAX_HISTORY:]
    _save(data)


def clear_history(user_id):
    data = _load()
    user = _get_user(data, user_id)
    user["history"] = []
    _save(data)


# ---------- JADWAL KULIAH ----------
def add_jadwal(user_id, hari, jam, matkul):
    data = _load()
    user = _get_user(data, user_id)
    user["jadwal"].append({"hari": hari, "jam": jam, "matkul": matkul})
    _save(data)


def get_jadwal(user_id):
    data = _load()
    return _get_user(data, user_id)["jadwal"]


def clear_jadwal(user_id):
    data = _load()
    user = _get_user(data, user_id)
    user["jadwal"] = []
    _save(data)


# ---------- TUGAS / DEADLINE ----------
def add_tugas(user_id, judul, deadline):
    data = _load()
    user = _get_user(data, user_id)
    user["tugas"].append({"judul": judul, "deadline": deadline, "selesai": False})
    _save(data)


def get_tugas(user_id, hanya_belum_selesai=True):
    data = _load()
    tugas = _get_user(data, user_id)["tugas"]
    if hanya_belum_selesai:
        return [t for t in tugas if not t["selesai"]]
    return tugas


def selesaikan_tugas(user_id, index):
    data = _load()
    user = _get_user(data, user_id)
    belum = [t for t in user["tugas"] if not t["selesai"]]
    if 0 <= index < len(belum):
        target = belum[index]
        for t in user["tugas"]:
            if t is target:
                t["selesai"] = True
        _save(data)
        return True
    return False


# ---------- CATATAN ----------
def add_catatan(user_id, judul, isi):
    data = _load()
    user = _get_user(data, user_id)
    user["catatan"].append({"judul": judul, "isi": isi})
    _save(data)


def get_catatan(user_id):
    data = _load()
    return _get_user(data, user_id)["catatan"]
