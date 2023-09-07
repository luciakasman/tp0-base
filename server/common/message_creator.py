import logging
from common.utils import Bet


def create_encoded_message(response_code, client_ID):
    encoded_data = ""
    formatted_data = "| {} | {} | {} |".format(response_code, client_ID, encoded_data)
    formatted_data_bytes = formatted_data.encode('utf-8')
    buf = bytearray()
    buf.extend(formatted_data_bytes)
    try:
        encoded_data_big_endian = bytes(buf)

        """ logging.info("action: encode | result: success | client_id: %s | data: %s",
                     client_ID,
                     encoded_data) """

        return encoded_data_big_endian
    except Exception as e:
        logging.error(
            "action: encode | result: fail | client_id: %s | error: %s | data: %s",
            client_ID,
            str(e),
            encoded_data,
        )
        return None


def decode_message(received_data):
    try:
        parts = received_data.decode('utf-8').split('|')
        bets_data = []
        for i in range(1, len(parts), 4):
            if parts[i] != '' and parts[i] != ' ':
                message_code = int(parts[i].strip())
                client_ID = parts[i+1].strip()
                if message_code == 0:
                    bet_data = parts[i+2].split(',')
                    bet = Bet(client_ID, bet_data[0].strip(), bet_data[1].strip(), bet_data[2].strip(), bet_data[3].strip(), bet_data[4].strip())
                else:
                    bet = ""

                data = (message_code, client_ID, bet)
                bets_data.append(data)

                # logging.info("action: decode | result: success | client_id: %s", client_ID)

        return bets_data

    except Exception as e:
        logging.error(
            "action: decode | result: fail | data: %s | error: %s",
            received_data.decode('utf-8'),
            str(e),
        )
        return None, None, None
