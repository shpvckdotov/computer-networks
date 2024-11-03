import socket
import struct

def recv_all(conn, length):
    data_chunks = []
    total_received = 0
    while total_received < length:
        chunk = conn.recv(min(length - total_received, 1024))
        if not chunk:
            raise ConnectionError("Connection lost")
        data_chunks.append(chunk)
        total_received += len(chunk)
    return b''.join(data_chunks)

def recv_message(conn):
    length_bytes = recv_all(conn, 4)
    message_length = struct.unpack('!I', length_bytes)[0]
    return recv_all(conn, message_length)

def send_message(conn, message):
    message_bytes = message.encode()
    length = len(message_bytes)
    conn.sendall(struct.pack('!I', length))
    for offset in range(0, length, 1024):
        conn.sendall(message_bytes[offset:offset + 1024])

def run_tcp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen(5)
        print(f"TCP server listening on {host}:{port}")
        
        try:
            while True:
                connection, client_address = server.accept()
                print(f"Connected by {client_address}")
                with connection:
                    while True:
                        try:
                            received_data = recv_message(connection)
                        except ConnectionError:
                            print(f"Connection with {client_address} closed")
                            break
                        print(f"Received ({len(received_data)} bytes): {received_data.decode()}")
                        response = input("You: ")
                        send_message(connection, response)
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            server.close()
            print("Socket closed.")

def run_tcp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        try:
            client.connect((host, port))
            print(f"Connected to TCP server {host}:{port}")
            while True:
                user_input = input("You: ")
                send_message(client, user_input)
                received_data = recv_message(client)
                print(f"Received ({len(received_data)} bytes): {received_data.decode()}")
        except KeyboardInterrupt:
            print("\nClient shutting down.")
        finally:
            client.close()
            print("Socket closed.")

def run_udp_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server:
        server.bind((host, port))
        print(f"UDP server listening on {host}:{port}")
        try:
            while True:
                data, client_address = server.recvfrom(1024)
                print(f"Received from {client_address}: {data.decode()}")
                response = input("You: ")
                server.sendto(response.encode(), client_address)
        except KeyboardInterrupt:
            print("\nServer shutting down.")
        finally:
            server.close()

def run_udp_client(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client:
        print(f"Connected to UDP server {host}:{port}")
        try:
            while True:
                user_input = input("You: ")
                client.sendto(user_input.encode(), (host, port))
                data, _ = client.recvfrom(1024)
                print(f"Received: {data.decode()}")
        except KeyboardInterrupt:
            print("\nClient shutting down.")
        finally:
            client.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="TCP and UDP Chat Client-Server")
    parser.add_argument("mode", choices=["tcp_server", "tcp_client", "udp_server", "udp_client"], help="Mode to run the program")
    parser.add_argument("--host", default="127.0.0.1", help="Host IP address")
    parser.add_argument("--port", type=int, default=12345, help="Port number")
    args = parser.parse_args()

    try:
        if args.mode == "tcp_server":
            run_tcp_server(args.host, args.port)
        elif args.mode == "tcp_client":
            run_tcp_client(args.host, args.port)
        elif args.mode == "udp_server":
            run_udp_server(args.host, args.port)
        elif args.mode == "udp_client":
            run_udp_client(args.host, args.port)
    except KeyboardInterrupt:
        print("\nProgram interrupted.")
