package main

import (
	"database/sql"
	"fmt"
	"log"
	"math/rand"
	"net/http"
	"os"

	"github.com/spiceai/sample-1/pkg/flightsql"

	_ "github.com/lib/pq"
)

var PRODUCTS = []string{"the most beautiful flower", "the most delicious chocolate", "nintendo"}

func main() {
	if len(os.Args) > 1 && os.Args[1] == "setup" {
		fmt.Println("Setting up")
		setupDB()
		os.Exit(0)
	}

	connStr := os.Getenv("POSTGRES_CONN")
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	fmt.Println("Start the example application to use Spice")

	flightDb := flightsql.NewDB("flightsql://spiced:50051?timeout=20s")
	materializedFlightDb := flightsql.NewDB("flightsql://spiced-materialized:50051?timeout=20s")
	defer flightDb.Close()
	defer materializedFlightDb.Close()

	http.HandleFunc("/ranking", rankingHandler(db))
	http.HandleFunc("/ranking-accelerated", rankingHandler(flightDb))
	http.HandleFunc("/ranking-materialized", materializedRankingHandler(materializedFlightDb))
	http.HandleFunc("/orders", orderHandler(db))
	log.Println("Listening on port 8080")
	log.Fatal(http.ListenAndServe(":8080", nil))
}

func rankingHandler(db *sql.DB) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		rows, err := db.Query("with a as (SELECT products.id, sum(count) as count FROM orders INNER JOIN products ON orders.product_id = products.id GROUP BY products.id) select name, count from products left join a on products.id = a.id order by count desc limit 5")
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			return
		}
		defer rows.Close()

		fmt.Fprintf(w, "==== Leading Products ====\n")
		for rows.Next() {
			var name string
			var count int
			if err := rows.Scan(&name, &count); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(err.Error()))
				return
			}
			fmt.Fprintf(w, "%10d sold: %s\n", count, name)
		}
	}
}

func materializedRankingHandler(db *sql.DB) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		rows, err := db.Query("select name, count from rankings order by count desc limit 5")
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			return
		}
		defer rows.Close()

		fmt.Fprintf(w, "==== Leading Products ====\n")
		for rows.Next() {
			var name string
			var count int
			if err := rows.Scan(&name, &count); err != nil {
				w.WriteHeader(http.StatusInternalServerError)
				w.Write([]byte(err.Error()))
				return
			}
			fmt.Fprintf(w, "%10d sold: %s\n", count, name)
		}
	}
}

func orderHandler(db *sql.DB) func(w http.ResponseWriter, r *http.Request) {
	return func(w http.ResponseWriter, r *http.Request) {
		// get a random product id

		var productID int
		err := db.QueryRow("SELECT id FROM products ORDER BY RANDOM() LIMIT 1").Scan(&productID)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			return
		}

		count := rand.Intn(100) + 1
		_, err = db.Exec("INSERT INTO orders (product_id, count) VALUES ($1, $2)", productID, count)
		if err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(err.Error()))
			return
		}

		fmt.Fprintf(w, "Order %d for product %d", count, productID)
	}
}

func setupDB() {
	connStr := os.Getenv("POSTGRES_CONN")
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal(err)
	}
	defer db.Close()

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS products (id SERIAL PRIMARY KEY, name TEXT NOT NULL)")
	if err != nil {
		log.Fatal(err)
	}

	for _, product := range PRODUCTS {
		result, err := db.Query("SELECT id FROM products WHERE name = $1", product)
		if err != nil {
			log.Fatal(err)
		}

		defer result.Close()

		if !result.Next() {
			_, err = db.Exec("INSERT INTO products (name) VALUES ($1)", product)
			if err != nil {
				log.Fatal(err)
			}
		}
	}

	_, err = db.Exec("CREATE TABLE IF NOT EXISTS orders (id SERIAL PRIMARY KEY, product_id INT NOT NULL, count INT NOT NULL, FOREIGN KEY (product_id) REFERENCES products(id))")
	if err != nil {
		log.Fatal(err)
	}

	_, err = db.Exec("INSERT INTO orders (product_id, count) VALUES (1, 100)")
	if err != nil {
		log.Fatal(err)
	}
	_, err = db.Exec("INSERT INTO orders (product_id, count) VALUES (2, 101)")
	if err != nil {
		log.Fatal(err)
	}
	_, err = db.Exec("INSERT INTO orders (product_id, count) VALUES (3, 102)")
	if err != nil {
		log.Fatal(err)
	}
}
