use arrow::array::{Array, Float64Array, Int32Array, Int64Array, TimestampMicrosecondArray};
use arrow::datatypes::{DataType, Field, Schema};
use arrow::record_batch::RecordBatch;
use spiceai::{ClientBuilder, StreamExt};
use std::sync::Arc;

#[tokio::main]
async fn main() {
    let client = ClientBuilder::new().build().await.unwrap();

    println!("=== Using query ===");
    query(&client).await;

    println!("\n=== Using query_with_params ===");
    query_with_params(&client, 5).await;
}

async fn query(client: &spiceai::Client) {
    let mut flight_data_stream = client
        .query("SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT 10")
        .await
        .expect("Error executing query");

    while let Some(batch) = flight_data_stream.next().await {
        match batch {
            Ok(batch) => {
                print_batch(&batch);
            }
            Err(e) => {
                eprintln!("Error reading batch: {:?}", e)
            }
        };
    }
}

async fn query_with_params(client: &spiceai::Client, limit: i64) {
    // Build a RecordBatch with the parameter
    // The column name must match the placeholder name ($1, $2, etc.)
    let schema = Arc::new(Schema::new(vec![Field::new("$1", DataType::Int64, false)]));
    let limit_array = Arc::new(Int64Array::from(vec![limit]));
    let params = RecordBatch::try_new(schema, vec![limit_array]).expect("Failed to create params");

    let mut flight_data_stream = client
        .query_with_params(
            "SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT $1",
            Some(params),
        )
        .await
        .expect("Error executing query");

    while let Some(batch) = flight_data_stream.next().await {
        match batch {
            Ok(batch) => {
                print_batch(&batch);
            }
            Err(e) => {
                eprintln!("Error reading batch: {:?}", e)
            }
        };
    }
}

fn print_batch(batch: &RecordBatch) {
    let vendor_id = batch
        .column(0)
        .as_any()
        .downcast_ref::<Int32Array>()
        .expect("Expected Int32Array for VendorID");

    let pickup_datetime = batch
        .column(1)
        .as_any()
        .downcast_ref::<TimestampMicrosecondArray>()
        .expect("Expected TimestampMicrosecondArray for tpep_pickup_datetime");

    let fare_amount = batch
        .column(2)
        .as_any()
        .downcast_ref::<Float64Array>()
        .expect("Expected Float64Array for fare_amount");

    let num_rows = batch.num_rows();

    for i in 0..num_rows {
        let vendor = if vendor_id.is_null(i) {
            "NULL".to_string()
        } else {
            vendor_id.value(i).to_string()
        };

        let datetime = if pickup_datetime.is_null(i) {
            "NULL".to_string()
        } else {
            // Convert microseconds to a readable format
            let micros = pickup_datetime.value(i);
            let secs = micros / 1_000_000;
            let nanos = ((micros % 1_000_000) * 1000) as u32;
            let datetime = chrono::DateTime::from_timestamp(secs, nanos)
                .map(|dt| dt.format("%Y-%m-%d %H:%M:%S").to_string())
                .unwrap_or_else(|| micros.to_string());
            datetime
        };

        let fare = if fare_amount.is_null(i) {
            "NULL".to_string()
        } else {
            format!("{:.2}", fare_amount.value(i))
        };

        println!(
            "VendorID: {}, tpep_pickup_datetime: {}, fare_amount: {}",
            vendor, datetime, fare
        );
    }
}
