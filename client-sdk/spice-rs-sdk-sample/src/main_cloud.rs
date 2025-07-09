use spiceai::{ClientBuilder, StreamExt};

#[tokio::main]
async fn main() {
    let mut client = ClientBuilder::new()
        .api_key("API_KEY")
        .flight_url("https://flight.spiceai.io")
        .build()
        .await
        .unwrap();

    let mut flight_data_stream = client
        .query("show tables;")
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
