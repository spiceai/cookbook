import { SpiceClient } from '@spiceai/spice';

const apiKey = process.env.SPICE_API_KEY;
if (!apiKey) {
  console.error('Set SPICE_API_KEY before running this sample.');
  process.exit(1);
}

const httpUrl = process.env.SPICE_HTTP_URL ?? 'https://data.spiceai.io';
const flightUrl = process.env.SPICE_FLIGHT_URL ?? 'flight.spiceai.io:443';

const main = async () => {
  const spiceClient = new SpiceClient({
    apiKey,
    httpUrl,
    flightUrl,
  });

  const table = await spiceClient.query(`show tables;`);
  console.table(table.toArray());
};

main().catch((error) => {
  console.error('Failed to run cloud query:', error);
  process.exit(1);
});
