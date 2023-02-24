# Pysimplegui
# logzero
import os
import time
import json
import base64
import sqlite3
import win32crypt
from Cryptodome.Cipher import AES
import shutil
import browserhistory as bh
import PySimpleGUI as sg

def get_master_key_edge():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Microsoft\\Edge\\User Data\\Local State', "r", encoding='UTF-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def get_master_key_chrome():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Google\\Chrome\\User Data\\Local State', "r", encoding='UTF-8') as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key

def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)

def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)

def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        return "Chrome < 80"

def send_cracked_edge () :
    try :
        master_key = get_master_key_edge()
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Microsoft\\Edge\\User Data\\default\\Login Data'
        shutil.copy2(login_db, "Loginvault.db") #making a temp copy since Login Data DB is locked while Chrome is running
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = decrypt_password(encrypted_password, master_key)
                if len(username) > 0:
                    print ("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
        except Exception as e:
            pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception as e:
            pass
    except Exception as e:
        print ("本地破解失败 ", e)

def send_cracked_chrome():
    try :
        master_key = get_master_key_chrome()
        login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\\Local\\Google\\Chrome\\User Data\\default\\Login Data'
        shutil.copy2(login_db, "Loginvault.db") #making a temp copy since Login Data DB is locked while Chrome is running
        conn = sqlite3.connect("Loginvault.db")
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT action_url, username_value, password_value FROM logins")
            for r in cursor.fetchall():
                url = r[0]
                username = r[1]
                encrypted_password = r[2]
                decrypted_password = decrypt_password(encrypted_password, master_key)
                if len(username) > 0:
                    print ("URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n")
        except Exception as e:
            pass
        cursor.close()
        conn.close()
        try:
            os.remove("Loginvault.db")
        except Exception as e:
            pass
    except Exception as e:
        print ("本地破解失败 ", e)

def get_history():
    data = bh.get_browserhistory()
    str_data = ''
    # 处理一下数据
    for i in data:
        for i_ in data[i]:
            str_data += f'{i_}\n'

    print (str_data)

def main () :

    sg.theme('DarkAmber')

    layout = [  [sg.Text('密码读取器')],
                [sg.Output(size=(80, 20))],
                [sg.Button('Chrome浏览器'), sg.Button("Edge浏览器"), sg.Button("浏览器历史记录"), sg.Button("关闭软件")] ]

    window = sg.Window('密码读取器', layout, font=("宋体", 15),default_element_size=(50,1))

    while True:
        event, values = window.read()
        if event in (None, 'Chrome浏览器'):
            send_cracked_chrome ()
        if event in (None, 'Edge浏览器'):
            send_cracked_edge ()
        if event in (None, '浏览器历史记录'):
            get_history ()
        if event in (None, '关闭软件'):
            event = WIN_CLOSED

    window.close()

try :
    main ()
except Exception as e:
    print ("Error: ", str(e))