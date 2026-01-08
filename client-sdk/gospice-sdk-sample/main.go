package main

import (
	"context"
	"fmt"

	"github.com/apache/arrow-go/v18/arrow/array"
	"github.com/spiceai/gospice/v8"
)

func main() {
	spice := gospice.NewSpiceClient()
	defer spice.Close()

	if err := spice.Init(); err != nil {
		panic(fmt.Errorf("error initializing: %w", err))
	}

	fmt.Println("=== Using Sql ===")
	queryWithSql(spice)

	fmt.Println("\n=== Using SqlWithParams ===")
	queryWithSqlParams(spice, 5)
}

func queryWithSql(spice *gospice.SpiceClient) {
	reader, err := spice.Sql(
		context.Background(),
		"SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT 10",
	)
	if err != nil {
		panic(fmt.Errorf("error querying: %w", err))
	}
	defer reader.Release()

	for reader.Next() {
		record := reader.Record()
		defer record.Release()

		col0 := record.Column(0)
		defer col0.Release()

		col1 := record.Column(1)
		defer col1.Release()

		col2 := record.Column(2)
		defer col2.Release()

		numRows := int(record.NumRows())

		for i := 0; i < numRows; i++ {
			fmt.Printf("VendorID: %v, tpep_pickup_datetime: %v, fare_amount: %v\n",
				col0.(*array.Int32).Value(i),
				col1.(*array.Timestamp).Value(i),
				col2.(*array.Float64).Value(i))
		}
	}

	if err := reader.Err(); err != nil {
		panic(fmt.Errorf("error reading: %w", err))
	}
}

func queryWithSqlParams(spice *gospice.SpiceClient, limit int) {
	reader, err := spice.SqlWithParams(
		context.Background(),
		"SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT ?",
		limit,
	)
	if err != nil {
		panic(fmt.Errorf("error querying: %w", err))
	}
	defer reader.Release()

	for reader.Next() {
		record := reader.Record()
		defer record.Release()

		col0 := record.Column(0)
		defer col0.Release()

		col1 := record.Column(1)
		defer col1.Release()

		col2 := record.Column(2)
		defer col2.Release()

		numRows := int(record.NumRows())

		for i := 0; i < numRows; i++ {
			fmt.Printf("VendorID: %v, tpep_pickup_datetime: %v, fare_amount: %v\n",
				col0.(*array.Int32).Value(i),
				col1.(*array.Timestamp).Value(i),
				col2.(*array.Float64).Value(i))
		}
	}

	if err := reader.Err(); err != nil {
		panic(fmt.Errorf("error reading: %w", err))
	}
}
