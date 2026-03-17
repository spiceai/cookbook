/* npm install @spiceai/spice --save
 * or
 * yarn add @spiceai/spice
 */
import { SpiceClient } from "@spiceai/spice";

const main = async () => {
  const spiceClient = new SpiceClient({
    apiKey: "API_KEY",
    httpUrl: "https://data.spiceai.io",
    flightUrl: "flight.spiceai.io:443",
  });
  const table = await spiceClient.query(`show tables;`);
  console.table(table.toArray());
};

main();
