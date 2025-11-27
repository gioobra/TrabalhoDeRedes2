import socket
import threading
import os 
import hashlib

HOST = '127.0.0.1'
PORT = 5001
BUFFER_SIZE = 4096

clientes_conectados = []

def calculaHashSHA256(nome_arquivo):
    h = hashlib.sha256()
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
    print(f"[NOVA CONEXÃO] {endereco} conectado.")
    clientes_conectados.append(conexao)
    conexao_ativa = True
    
    try:
        while conexao_ativa:
            comando_raw = conexao.recv(BUFFER_SIZE).decode('utf-8')

            if not comando_raw:
                conexao_ativa = False
            else:
                partes_comando = comando_raw.split()
                comando = partes_comando[0].upper()

                print(f"[{endereco}] Comando recebido: {comando_raw}")

                if comando == "ARQUIVO" and len(partes_comando) > 1:
                    nome_arquivo = partes_comando[1]
                    
                    if os.path.exists(nome_arquivo):
                        tamanho_arquivo = os.path.getsize(nome_arquivo)
                        hash_arquivo = calculaHashSHA256(nome_arquivo)

                        conexao.sendall(f"OK {tamanho_arquivo} {hash_arquivo}".encode('utf-8'))
                        with open (nome_arquivo, 'rb') as f:
                            bytes_lidos = f.read(BUFFER_SIZE)
                            while bytes_lidos:
                                conexao.sendall(bytes_lidos)
                                bytes_lidos = f.read(BUFFER_SIZE)
                        print(f"[{endereco}] Arquivo '{nome_arquivo}' enviado com sucesso.")
                    else:
                        conexao.sendall("ERRO Arquivo não encontrado.".encode("utf-8"))
                        print(f"[{endereco}] Tentativa de acesso a arquivo inexistente: {nome_arquivo}")
                elif comando == "CHAT":
                    conexao.sendall("OK CHAT".encode('utf-8'))
                    chat_ativo =  True
                    broadcast_mensagem(f"[SISTEMA] {endereco[0]} entrou no chat.", remetente=conexao)
                    while chat_ativo:
                        mensagem_cliente = conexao.recv(BUFFER_SIZE).decode('utf-8')
                        if mensagem_cliente and mensagem_cliente.upper() != 'SAIR':
                            print(f"[{endereco} - CHAT] Mensagem: {mensagem_cliente}")
                            mensagem_formatada = f"[{endereco[0]}]: {mensagem_cliente}"
                            broadcast_mensagem(mensagem_formatada, remetente=conexao)
                        else:
                            chat_ativo = False
                            print(f"[{endereco}] Fim do modo CHAT.")
                elif comando == "SAIR":
                    print(f"[{endereco}] Cliente solicitou desconexão.")
                    conexao_ativa = False
    except ConnectionResetError:
        print(f"[AVISO] Conexão com {endereco} foi perdida inesperadamente.")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro com o cliente {endereco}: {e}")
    finally:
        print(f"[CONEXÃO FECHADA] Conexão com {endereco} encerrada.")
        conexao.close()

def broadcast_mensagem(mensagem, remetente=None):
    for cliente in clientes_conectados:
        if cliente != remetente:
            try:
                cliente.sendall(f"SERVIDOR {mensagem}".encode('utf-8'))
            except:
                if cliente in clientes_conectados:
                    clientes_conectados.remove(cliente)

def lidarConsoleServidor():
    while True:
        mensagem = input("")
        if mensagem:
            print(f"[SERVIDOR] Enviando para todos: {mensagem}")
            broadcast_mensagem(f"ADMIN: {mensagem}")

def iniciarServidor():
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((HOST, PORT))
    servidor.listen(5)
    print(f"[*] Servidor TCP escutando em {HOST}:{PORT}")
    thread_console = threading.Thread(target=lidarConsoleServidor)
    thread_console.start()

    while True:
        conexao, endereco = servidor.accept()
        thread_cliente = threading.Thread(target=lidarCliente, args=(conexao, endereco))
        thread_cliente.start()
        print(f"[CONEXÕES ATIVAS] {len(clientes_conectados)}")

if __name__ == "__main__":
    iniciarServidor()