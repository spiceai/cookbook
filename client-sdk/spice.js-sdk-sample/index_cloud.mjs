/* npm install @spiceai/spice --save
 * or
 * yarn add @spiceai/spice
 */
import { SpiceClient } from "@spiceai/spice";

const main = async () => {
  const spiceClient = new SpiceClient({
    api_key: "API_KEY",
    http_url: "https://data.spiceai.io",
    flight_url: "flight.spiceai.io:443",
  });
  const table = await spiceClient.query(`show tables;`);
  console.table(table.toArray());
};

main();
