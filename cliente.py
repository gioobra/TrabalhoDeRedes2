import socket
import os
import hashlib
import threading

HOST = '127.0.0.1'
PORT = 5001
BUFFER_SIZE = 4096 
PASTA_DOWNLOADS = "downloads_cliente"

recebendo_mensagens = False

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

def solicitarArquivo(cliente_socket, nome_arquivo):
    cliente_socket.sendall(f"ARQUIVO {nome_arquivo}".encode('utf-8'))
    resposta = cliente_socket.recv(BUFFER_SIZE).decode('utf-8')

    if resposta.startswith("OK"):
        try:
            _, tamanho_str, hash_servidor = resposta.split()
            tamanho_arquivo = int(tamanho_str)
            print(f"[INFO] Recebendo arquivo: {nome_arquivo} (Tamanho: {tamanho_arquivo} bytes, Hash: {hash_servidor})")

            caminho_arquivo_local = os.path.join(PASTA_DOWNLOADS, nome_arquivo)
            bytes_recebidos = 0
            with open(caminho_arquivo_local, 'wb') as f:
                while bytes_recebidos < tamanho_arquivo:
                    bytes_a_receber = min(BUFFER_SIZE, tamanho_arquivo - bytes_recebidos)
                    chunk = cliente_socket.recv(bytes_a_receber)
                    if not chunk:
                        raise ConnectionError("A conexão foi encerrada antes do fim do arquivo.")
                    f.write(chunk)
                    bytes_recebidos += len(chunk)
            print(f"[SUCESSO] Arquivo '{nome_arquivo}' baixado para a pasta '{PASTA_DOWNLOADS}'.")

            hash_local = calculaHashSHA256(caminho_arquivo_local)
            print(f"Hash do servidor: {hash_servidor}")
            print(f"Hash local: {hash_local}")

            if hash_servidor == hash_local:
                print("[VERIFICAÇÃO] SUCESSO! O arquivo foi baixado corretamente.")
            else:
                print("[VERIFICAÇÃO] FALHA! O arquivo pode estar corrompido.")
        except Exception as e:
            print(f"[ERRO] Falha ao processar o arquivo recebido: {e}")
    else:
        print(f"[ERRO DO SERVIDOR] {resposta}")

def iniciarChat (cliente_socket):
    global recebendo_mensagens
    try:
        cliente_socket.sendall("CHAT".encode('utf-8'))
        resposta_servidor = cliente_socket.recv(BUFFER_SIZE).decode('utf-8')
        if resposta_servidor == "OK CHAT":
            print("\n--- Modo chat Iniciado---")
            print("Digite 'sair' para voltar ao menu principal.")
            recebendo_mensagens = True
            t = threading.Thread(target=thread_receber_mensagem, args=(cliente_socket,))
            t.start()
            while recebendo_mensagens:
                mensagem = input("Você: ")
                
                if mensagem:
                    try:
                        cliente_socket.sendall(mensagem.encode('utf-8'))
                        if mensagem.upper() == 'SAIR':
                            recebendo_mensagens = False
                    except:
                        recebendo_mensagens = False
                        break
            print("--- Modo Chat Encerrado ---\n")
        else:
            print(f"[ERRO] Falha ao entrar no chat: {resposta_servidor}")
    except Exception as e:
        print(f"[ERRO]{e}")

def thread_receber_mensagem(socket_cliente):
    global recebendo_mensagens
    while recebendo_mensagens:
        try:
            msg = socket_cliente.recv(BUFFER_SIZE).decode('utf-8')

            print(f"\r{msg}\nVocê: ", end="")
        except:
            break


def main():
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente_socket.connect((HOST, PORT))
        print(f"[CONECTADO] Conexão com o servidor {HOST}:{PORT} estabelecida.")
    except ConnectionRefusedError:
        print(f"[ERRO] Conexão recusada. Verifique se o servidor está rodando.")
    except Exception as e:
        print(f"[ERRO] Ocorreu um erro ao conectar: {e}")
        return
    executando = True
    while executando:
        print("\n--- Menu Principal ---")
        print("1. Baixar arquivo")
        print("2. Iniciar Chat")
        print("3. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == '1':
            nome_arquivo = input("Digite o nome do arquivo que deseja baixar: ")
            if nome_arquivo:
                solicitarArquivo(cliente_socket, nome_arquivo)
        
        elif escolha == '2':
            iniciarChat(cliente_socket)

        elif escolha == '3':
            cliente_socket.sendall("SAIR".encode('utf-8'))
            executando = False
        
        else:
            print("[AVISO] Opção inválida. Tente novamente.")
    
    print("[DESCONECTADO] Encerrando a conexão.")
    cliente_socket.close()

if __name__ == "__main__":
    main()