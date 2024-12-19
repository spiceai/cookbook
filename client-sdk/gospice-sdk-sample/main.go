package main

import (
	"context"
	"fmt"

	"github.com/apache/arrow/go/v17/arrow/array"
	"github.com/spiceai/gospice/v7"
)

func main() {
	spice := gospice.NewSpiceClient()
	defer spice.Close()

	spice.Init()

	reader, err := spice.Query(
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
			fmt.Printf("VendorID: %v\n", col0.(*array.Int32).Value(i))
			fmt.Printf("tpep_pickup_datetime: %v\n", col1.(*array.Timestamp).Value(i))
			fmt.Printf("fare_amount: %v\n", col2.(*array.Float64).Value(i))
		}
	}
}
