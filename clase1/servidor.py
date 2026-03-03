import socket
import threading

contador_clientes = 0 #recurso compartido
lock = threading.Lock()

def handle_client(conn, addr):
    global contador_clientes

    name = conn.recv(1024).decode()

    #seccion critica protegida
    with lock:
         contador_clientes += 1
         numero = contador_clientes


    print (f"Cliente {contador_clientes } atendido desde {addr} ")

    response = f"Hola {name} eres el numero : {contador_clientes  }"
    conn.sendall(response.encode())

    conn.close()




server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("127.0.0.1", 5000))
server.listen(1)
print("servidor esperando conexion...")

while True:
    conn, addr = server.accept()
    thread = threading.Thread(
        target=handle_client,
        args=(conn, addr)
    )
    thread.start()
