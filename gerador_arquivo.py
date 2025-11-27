import os

# Define o nome do arquivo
nome_arquivo = "teste_10mb.bin"

# Define o tamanho exato de 10 MB em bytes
# 10 * 1024 * 1024 = 10.485.760 bytes
tamanho_em_bytes = 10 * 1024 * 1024

print(f"Criando arquivo '{nome_arquivo}' com {tamanho_em_bytes} bytes...")

# Cria o arquivo escrevendo bytes aleatórios (os.urandom)
# Isso é melhor que escrever apenas zeros, pois testa se o Hash está realmente funcionando
with open(nome_arquivo, "wb") as f:
    f.write(os.urandom(tamanho_em_bytes))

print(f"Sucesso! O arquivo '{nome_arquivo}' foi criado no diretório atual.")