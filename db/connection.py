import sqlite3
import os
import re

DB_NAME = "student_manager.db"

def remove_accents(text):
    if not isinstance(text, str): return str(text) if text else ""
    
    text = text.lower()
    text = re.sub(r'[àáạảãâầấậẩẫăằắặẳẵ]', 'a', text)
    text = re.sub(r'[èéẹẻẽêềếệểễ]', 'e', text)
    text = re.sub(r'[òóọỏõôồốộổỗơờớợởỡ]', 'o', text)
    text = re.sub(r'[ìíịỉĩ]', 'i', text)
    text = re.sub(r'[ùúụủũưừứựửữ]', 'u', text)
    text = re.sub(r'[ỳýỵỷỹ]', 'y', text)
    text = re.sub(r'[đ]', 'd', text)
    return text

def get_connection():
    if not os.path.exists(DB_NAME):
        print(f"❌ Lỗi: Không tìm thấy file cơ sở dữ liệu '{DB_NAME}'")
        return None
    
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        conn.create_function("no_accent", 1, remove_accents)
        conn.row_factory = sqlite3.Row 
        return conn
    except sqlite3.Error as e:
        print(f"❌ Lỗi kết nối CSDL: {e}")
        return None