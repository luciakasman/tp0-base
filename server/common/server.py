import socket
import logging
import signal

from common.message_creator import decode_message, create_encoded_message
from common.message_protocol import receive_message, send_message
from common.utils import store_bets

MAX_BUFFER_SIZE = 1024


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.shutdown = False

        # Capture SIGTERM signal and calls the method self.__stop_gracefully
        signal.signal(signal.SIGTERM, self.__stop_gracefully)

    def __stop_gracefully(self, *args):
        self.shutdown = True
        try:
            self._server_socket.close()
            logging.info('action: gracefully_stopping | result: success ')
        except OSError:
            return

    def run(self):
        """
        Dummy Server loop

        Server that accept a new connections and establishes a
        communication with a client. After client with communucation
        finishes, servers starts to accept new connections again
        """
        # the server
        while not self.shutdown:
            client_sock = self.__accept_new_connection()
            self.__handle_client_connection(client_sock)

    def __handle_client_connection(self, client_sock):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        if client_sock is not None:
            try:
                message_received = self.__receive_message(client_sock)
                message_received_code, client_ID, bet = decode_message(message_received)
                if message_received_code == 0 and client_ID is not None and bet is not None:
                    response_encoded = create_encoded_message(response_code=1, client_ID=client_ID)
                    store_bets([bet])
                    logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}')
                else:
                    response_encoded = create_encoded_message(response_code=2, client_ID=client_ID)
                    logging.error("action: receive_message | result: fail | error: message is incorrect or is bad formatted")

                if response_encoded is not None:
                    self.__send_message(client_sock, response_encoded)
            except OSError as e:
                logging.error(f"action: receive_message | result: fail | error: {e}")
            finally:
                client_sock.close()

    def __accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info('action: accept_connections | result: in_progress')
        try:
            c, addr = self._server_socket.accept()
            logging.info(f'action: accept_connections | result: success | ip: {addr[0]}')
            return c
        except OSError as e:
            logging.info(f'action: accept_connections | result: fail | error: {e}')

    def __receive_message(self, client_sock):
        return receive_message(client_sock)

    def __send_message(self, client_sock, encoded_message):
        send_message(client_sock, encoded_message)


