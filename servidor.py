import socket
import threading
import os 
import hashlib

HOST = '127.0.0.1'
PORT = 5051
BUFFER_SIZE = 4096

def calculaHashMD5(nome_arquivo):
    h = hashlib.md5()
    try:
        tamanho_total = os.path.getsize(nome_arquivo)
        
        with open (nome_arquivo, "rb") as f:
            for i in range (0, tamanho_total, BUFFER_SIZE):
                chunk = f.read(BUFFER_SIZE)
                if chunk:
                    h.update(chunk)
    except FileNotFoundError:
        return None
    
    return h.hexdigest()

def lidarCliente (conexao, endereco):

def iniciarServidor():