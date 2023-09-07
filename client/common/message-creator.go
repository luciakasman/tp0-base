package common

import (
	"bytes"
	"encoding/binary"
	"fmt"
	"strconv"
	"strings"

	log "github.com/sirupsen/logrus"
)

// El mensaje tiene la forma: ` | código | agencia | datos | `

func CreateEncodedMessage(client *Client, messageCode int, batch [][]string) []byte {
	encodedData := ""
	formattedData := ""

	for i := 0; i < len(batch); i++ {
		encodedData = fmt.Sprintf(
			"%s,%s,%s,%s,%s",
			batch[i][0],
			batch[i][1],
			batch[i][2],
			batch[i][3],
			batch[i][4],
		)
		formattedData += fmt.Sprintf("| %s | %s | %s |", strconv.Itoa(messageCode), client.config.ID, encodedData)
	}

	if messageCode == 3 {
		formattedData += fmt.Sprintf("| %s | %s | %s |", strconv.Itoa(messageCode), client.config.ID, encodedData)
	}

	formattedDataBytes := []byte(formattedData)

	buf := new(bytes.Buffer)
	err := binary.Write(buf, binary.BigEndian, formattedDataBytes)

	if err != nil {
		log.Fatalf(
			"action: encode | result: fail | client_id: %v | error: %v | data: %v",
			client.config.ID,
			err,
			encodedData,
		)
	}

	formattedDataBigEndian := buf.Bytes()

	log.Infof("action: encode | result: success | client_id: %v | data: %v",
		client.config.ID,
		encodedData,
	)

	return formattedDataBigEndian
}

func DecodeMessage(client *Client, receivedData []byte) int {
	formattedData := string(receivedData)

	log.Infof("action: decode | result: success | client_id: %v | data: %v",
		client.config.ID,
		formattedData,
	)

	parts := strings.Split(formattedData, "|")
	if len(parts) != 5 {
		log.Fatalf(
			"action: decode | result: fail | client_id: %v | error: formato invalido",
			client.config.ID,
		)
	}

	messageCode, _ := strconv.Atoi(strings.TrimSpace(parts[1]))

	log.Infof("action: decode | result: success | client_id: %v | messageCode: %d",
		client.config.ID,
		messageCode,
	)

	return messageCode
}
