use spiceai::{ClientBuilder, StreamExt};

#[tokio::main]
async fn main() {
    let mut client = ClientBuilder::new().build().await.unwrap();

    let mut flight_data_stream = client
        .query("SELECT \"VendorID\", \"tpep_pickup_datetime\", \"fare_amount\" FROM taxi_trips LIMIT 10")
        .await
        .expect("Error executing query");

    while let Some(batch) = flight_data_stream.next().await {
        match batch {
            Ok(batch) => {
                /* process batch */
                println!("{:?}", batch)
            }
            Err(_) => { /* handle error */ }
        };
    }
}
