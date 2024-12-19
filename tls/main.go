package main

import (
	"database/sql"
	"fmt"
	"os"

	"github.com/apache/arrow-adbc/go/adbc"
	"github.com/apache/arrow-adbc/go/adbc/driver/flightsql"
	"github.com/apache/arrow-adbc/go/adbc/sqldriver"
	"github.com/apache/arrow/go/v17/arrow/memory"
)

func main() {
	caBytes, err := os.ReadFile("./ca.pem")
	if err != nil {
		panic(err)
	}

	options := fmt.Sprintf("%s=grpc+tls://localhost:50051;%s=%s", adbc.OptionKeyURI, flightsql.OptionSSLRootCerts, string(caBytes))

	var drv = flightsql.NewDriver(memory.DefaultAllocator)
	sql.Register("flightsql", sqldriver.Driver{Driver: drv})
	db, err := sql.Open("flightsql", options)
	if err != nil {
		panic(err)
	}
	defer db.Close()

	row := db.QueryRow("SELECT first_name FROM customer_addresses WHERE id = 3")
	var name string
	err = row.Scan(&name)
	if err != nil {
		panic(err)
	}
	fmt.Println("Successfully found", name)
}
