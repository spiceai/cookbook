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

	// Every 5 seconds, insert a new user record into the users table
	for {
		time.Sleep(5 * time.Second)

		newEmail := fmt.Sprintf("user_%d@example.com", time.Now().UnixNano())
		newUsername := fmt.Sprintf("user_%d", time.Now().UnixNano())
		_, err := db.Exec("INSERT INTO users (email, username, last_login) VALUES ($1, $2, $3)", newEmail, newUsername, time.Now())
		if err != nil {
			log.Fatal(err)
		}

		fmt.Println("Inserted new user", newEmail, "with username", newUsername)
	}
}
