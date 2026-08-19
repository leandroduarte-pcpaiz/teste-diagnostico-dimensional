from app.scanner.scanner import localizar_arquivos

caminho = input("Informe a pasta: ")

arquivos = localizar_arquivos(caminho)

print(f"\nForam encontrados {len(arquivos)} arquivos.\n")

for arquivo in arquivos[:20]:
    print(arquivo)