import socket
import logging
import signal
from multiprocessing import Value, Lock, Process

from common.message_creator import decode_message, create_encoded_message
from common.message_protocol import receive_message, send_message
from common.utils import store_bets, load_bets, has_won

MAX_BUFFER_SIZE = 1024

AMOUNT_CLIENTS = 5


class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)
        self.shutdown = False
        self.amount_agencies = Value('i', 0)
        self.processes = []

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

        lock = Lock()

        # the server
        while not self.shutdown:
            client_sock = self.__accept_new_connection()
            p = Process(target=self.__handle_client_connection, args=(client_sock, lock, self.amount_agencies))
            p.start()
            self.processes.append(p)

        for p in self.processes:
            p.join()

    def __handle_client_connection(self, client_sock, lock, amount_agencies):
        """
        Read message from a specific client socket and closes the socket

        If a problem arises in the communication with the client, the
        client socket will also be closed
        """
        keep_receiving = True
        response_encoded = None
        response_code = 1
        response_data = ""
        # TODO: pasar response codes a un archivo.

        if client_sock is not None:
            try:
                while keep_receiving:
                    message_received = self.__receive_message(client_sock)
                    bets_data = decode_message(message_received)
                    for bet_data in bets_data:
                        if bet_data is not None:
                            message_code = bet_data[0]
                            client_ID = bet_data[1]
                            bet = bet_data[2]
                            if message_code == 0 and client_ID is not None and bet is not None:
                                lock.acquire()
                                store_bets([bet])
                                lock.release()
                                """ logging.info(f'action: apuesta_almacenada | result: success | dni: {bet.document} | numero: {bet.number}') """
                            elif message_code == 3 and client_ID is not None and bet is not None:
                                """ logging.info('action: apuestas_recibidas | result: success | client_id: %s', client_ID) """
                                keep_receiving = False
                                amount_agencies.value += 1
                            elif message_code == 4:
                                if amount_agencies.value >= AMOUNT_CLIENTS:
                                    logging.info('action: sorteo | result: success')
                                    response_data = self.get_lottery_results(client_ID, lock)
                                    response_code = 5
                                else:
                                    response_code = 6
                                keep_receiving = False
                            else:
                                response_code = 2
                                logging.error("action: receive_message | result: fail | client_id: %s | error: message is incorrect or bad formatted", client_ID)
                                keep_receiving = False
            except OSError as e:
                keep_receiving = False
                response_code = 2
                logging.error(f"action: receive_message | result: fail | client_id: %s | error: {e}", client_ID)

            response_encoded = create_encoded_message(response_code, client_ID, response_data)
            if response_encoded is not None:
                self.__send_message(client_sock, response_encoded)

    def get_lottery_results(self, client_ID, lock):
        winners = []
        lock.acquire()
        all_bets = load_bets()
        lock.release()
        for bet in all_bets:
            if bet.agency == client_ID and has_won(bet):
                winners.append(bet.document)
        return winners


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


