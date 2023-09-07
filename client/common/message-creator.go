package common

import (
	"fmt"
	"bytes"
	"strings"
	"encoding/binary"
	"strconv"

	log "github.com/sirupsen/logrus"
)

//` | código | agencia | datos | `


func CreateEncodedMessage(client *Client, messageCode int) []byte {
	encodedData := ""
	
	if messageCode == 0 {
		encodedData = fmt.Sprintf(
			"%s,%s,%s,%s,%s", 
			client.bet.Nombre, 
			client.bet.Apellido,
			client.bet.Documento,
			client.bet.Nacimiento,
			client.bet.Numero,
		)
	}

    formattedData := fmt.Sprintf("| %s | %s | %s |", messageCode, client.config.ID, encodedData)

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
	buf := bytes.NewBuffer(receivedData)

	var formattedData string
    if err := binary.Read(buf, binary.BigEndian, &formattedData); err != nil {
        log.Fatalf(
			"action: decode | result: fail | client_id: %v | error: %v",
			client.config.ID,
			err,
		)
    }

    parts := strings.Split(formattedData, "|")
    if len(parts) != 3 {
        log.Fatalf(
			"action: decode | result: fail | client_id: %v | error: formato invalido",
			client.config.ID,
		)
    }

    messageCode, _ := strconv.Atoi(strings.TrimSpace(parts[0]))

	log.Infof("action: decode | result: success | client_id: %v",
		client.config.ID,
	)

    return messageCode
}

