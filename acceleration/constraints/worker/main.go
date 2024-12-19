package main

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"time"

	_ "github.com/lib/pq"
)

func main() {
	connStr := os.Getenv("POSTGRES_CONN")
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	// Every 4 seconds, get a random row from the users table and increase the items_bought by 1
	for {
		time.Sleep(4 * time.Second)

		var email string
		var itemsBought int64
		err := db.QueryRow("SELECT email, items_bought FROM users ORDER BY RANDOM() LIMIT 1").Scan(&email, &itemsBought)
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println("Updating user", email, "items_bought:", itemsBought, "to", itemsBought+1)

		_, err = db.Exec("UPDATE users SET items_bought = items_bought + 1 WHERE email = $1", email)
		if err != nil {
			log.Fatal(err)
		}
	}
}
