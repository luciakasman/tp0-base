package common

import (
	"strings"

	log "github.com/sirupsen/logrus"
)

var MAX_BUFFER_SIZE int = 1024
var MAX_MSG_SIZE int = 1024 * 8

func SendMessage(client *Client, encodedMessage []byte) {
	messageSize := len(encodedMessage)
	startIndex := 0
	for startIndex < messageSize {
		messageToSendSize := min(MAX_MSG_SIZE, messageSize-startIndex)
		messageToSend := encodedMessage[startIndex : startIndex+messageToSendSize]

		remainingData := messageToSend
		for len(remainingData) > 0 {
			n, err := client.conn.Write(remainingData)
			if err != nil {
				log.Fatalf("action: send_message | result: fail | client_id: %v | error: %v",
				client.config.ID,
				err,
				)
			}
			remainingData = remainingData[n:]
		}
		startIndex += messageToSendSize
	}

	/* log.Infof("action: send_message | result: success | client_id: %v ",
		client.config.ID,
	) */
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func ReceiveMessage(client *Client) []byte {
	buffer := make([]byte, MAX_BUFFER_SIZE)
	totalRead := 0

	for totalRead < len(buffer) {
		n, _ := client.conn.Read(buffer[totalRead:])

		totalRead += n

		data := string(buffer[:totalRead])

		parts := strings.Split(data, "|")

		if len(parts) == 5 {
			break
		}
	}

	data := buffer[:totalRead] 
    receivedData := make([]byte, len(data))
    copy(receivedData, data)

	/* log.Infof("action: receive_message | result: success | client_id: %v | data: %v",
		client.config.ID,
		receivedData,
	) */

    return receivedData
}