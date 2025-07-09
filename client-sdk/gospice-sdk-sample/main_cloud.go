package main

import (
	"context"
	"fmt"

	"github.com/spiceai/gospice/v7"
)

func main() {
	spice := gospice.NewSpiceClient()
	defer spice.Close()

	err := spice.Init(
		gospice.WithApiKey("API_KEY"),
		gospice.WithHttpAddress("https://data.spiceai.io"),
		gospice.WithFlightAddress("flight.spiceai.io:443"),
	)
	if err != nil {
		panic(fmt.Errorf("Error initializing client: %s", err))
	}

	reader, err := spice.Query(context.Background(), "show tables;")
	if err != nil {
		panic(fmt.Errorf("error querying: %w", err))
	}
	defer reader.Release()

	for reader.Next() {
		record := reader.Record()
		defer record.Release()

		fmt.Printf("%v\n", record)
	}
}
