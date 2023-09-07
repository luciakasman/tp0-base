package common

import (
	log "github.com/sirupsen/logrus"
)

func SendBytes(client *Client, encodedMessage []byte) {
	_, err := client.conn.Write(encodedMessage)
	if err != nil {
		client.conn.Close()
		log.Fatalf("action: send_message | result: fail | client_id: %v | error: %v",
			client.config.ID,
			err,
		)
	}

	log.Infof("action: send_message | result: success | client_id: %v ",
		client.config.ID,
	)
}

func ReceiveBytes(client *Client) []byte {
	buffer := make([]byte, 1024) // Tamaño del búfer de lectura (ajusta según tus necesidades)

    n, err := client.conn.Read(buffer)
    if err != nil {
		client.conn.Close()
		log.Fatalf("action: receive_bytes | result: fail | client_id: %v | error: %v",
			client.config.ID,
			err,
		)
    }

    receivedData := make([]byte, n)
    copy(receivedData, buffer[:n])

	log.Infof("action: receive_bytes | result: success | client_id: %v | data: %v",
		client.config.ID,
		receivedData,
	)

    return receivedData
}