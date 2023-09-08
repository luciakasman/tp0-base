import logging

MAX_BUFFER_SIZE = 1024


def receive_message(client_sock):
    message = b''
    try:
        while True:
            data = client_sock.recv(MAX_BUFFER_SIZE)
            if not data:
                logging.error("action: receive_message | result: fail | error: data is none")
                return None  # TODO: manejar esto
            message += data
            #if message[-1:] == b'|':
            if message[-1:] == b"\n":
                decoded = message.decode('utf-8').replace(" ","").split('|')
                last_msg_code = decoded[-4]
                if last_msg_code.isnumeric() and (int(last_msg_code) == 3 or int(last_msg_code) == 4):
                    break
        """ 
        addr = client_sock.getpeername()
        logging.info(f'action: receive_message | result: success | ip: {addr[0]}') """
    except OSError as e:
        logging.error(f"action: receive_message | result: fail | error: {e}")
        client_sock.close()

    return message

def send_message(client_sock, encoded_message):
    try:
        total_bytes_sent = 0
        while total_bytes_sent < len(encoded_message):
            bytes_sent = client_sock.send(encoded_message[total_bytes_sent:])
            if bytes_sent == 0:
                break
            total_bytes_sent += bytes_sent

        addr = client_sock.getpeername()
        logging.info(f'action: send_message | result: success | ip: {addr[0]}')
    except OSError as e:
        client_sock.close()
        logging.error(f"action: send_message | result: fail | error: {e}")
