package flightsql

import (
	"database/sql"

	_ "github.com/apache/arrow/go/v16/arrow/flight/flightsql/driver"
)

func NewDB(connection string) *sql.DB {
	db, err := sql.Open("flightsql", connection)
	if err != nil {
		panic(err)
	}

	return db
}
