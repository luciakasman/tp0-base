package common

import (
	"net"
	"time"
	"os"
	"os/signal"
	"syscall"
	"encoding/csv"
	"io"
	"fmt"

	log "github.com/sirupsen/logrus"
)

var MAX_MSGS int = 100

type Bet struct {
    Nombre     string
    Apellido   string
    Documento  string
    Nacimiento string
    Numero     string
}

// ClientConfig Configuration used by the client
type ClientConfig struct {
	ID            string
	ServerAddress string
	LoopLapse     time.Duration
	LoopPeriod    time.Duration
}

// Client Entity that encapsulates how
type Client struct {
	config ClientConfig
	conn   net.Conn
	bet	   Bet
}

// NewClient Initializes a new client receiving the configuration
// as a parameter
func NewClient(config ClientConfig, bet Bet) *Client {
	client := &Client{
		config: config,
		bet: bet,
	}
	return client
}

// CreateClientSocket Initializes client socket. In case of
// failure, error is printed in stdout/stderr and exit 1
// is returned
func (c *Client) createClientSocket() error {
	conn, err := net.Dial("tcp", c.config.ServerAddress)
	if err != nil {
		log.Fatalf(
	        "action: connect | result: fail | client_id: %v | error: %v",
			c.config.ID,
			err,
		)
	}
	c.conn = conn
	return nil
}

func (c *Client) GetLotteryResults() {
	for {
		c.createClientSocket()

		endMessage := CreateEncodedMessage(c, 4, make([][]string, 0))

		SendMessage(c, endMessage)

		receivedData := ReceiveMessage(c)

		messageCode, amount_winners := DecodeWinnerMessage(c, receivedData)

		if messageCode == 5 {
			log.Infof("action: consulta_ganadores | result: success | cant_ganadores: %d ",
				amount_winners,
			)
			break
		} else {
			log.Errorf("action: consulta_ganadores | result: fail | message_code: %v",
				messageCode,
			)
		}
		c.conn.Close()
	}
}

// StartClientLoop Send messages to the client
func (c *Client) StartClientLoop() {

	// create channel to capture SIGTERM signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGTERM)

	select {
		case <-sigChan:
			log.Infof("action: gracefully_stopping | result: success | client_id: %v",
				c.config.ID,
			)
			c.conn.Close()
			return

		default:
	}

	// Create the connection the server 
	c.createClientSocket()

	fileName := fmt.Sprintf("/config/data/agency-%s.csv", c.config.ID)
	//fileName := fmt.Sprintf("/config/data/agency-11.csv")

	file, err := os.Open(fileName)
	if err != nil {
		log.Errorf("action: opening_bet_file | result: fail | client_id: %v | error: %s",
			c.config.ID,
			err,
		)
		return
	}
	defer file.Close()

	reader := csv.NewReader(file)

	eof := false

	for !eof {
		batch := make([][]string, 0)

    	for i := 0; i < MAX_MSGS; i++ {
			record, err := reader.Read()
			if err != nil {
				if err == io.EOF {
					eof = true
					break
				}
				log.Errorf("action: reading_bet_file | result: fail | client_id: %v | data: %v",
					c.config.ID,
					record,
				)
				return
        	}

        	batch = append(batch, record)
		}

		if len(batch) != 0 {
			betMessage := CreateEncodedMessage(c, 0, batch)
			SendMessage(c, betMessage)
		}
	}

	endMessage := CreateEncodedMessage(c, 3, make([][]string, 0))

	SendMessage(c, endMessage)

	receivedData := ReceiveMessage(c)

	messageCode := DecodeMessage(c, receivedData)
	
	c.conn.Close()

	if messageCode == 1 {
		/* log.Infof("action: apuesta_enviada | result: success | client_id: %v ",
			c.config.ID,
		) */
	} else {
		/* log.Errorf("action: apuesta_enviada | result: fail | client_id: %v | message_code: %v",
			c.config.ID,
			messageCode,
		) */
	}
}


