import { SpiceClient } from "@spiceai/spice";

const main = async () => {
  const spiceClient = new SpiceClient();
  const table = await spiceClient.query(
    `SELECT "VendorID", "tpep_pickup_datetime", "fare_amount" FROM taxi_trips LIMIT 10`
  );
  console.table(table.toArray());
};

main();
