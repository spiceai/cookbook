import { SpiceClient } from '@spiceai/spice';

const apiKey = '<YOUR_API_KEY>';
const httpUrl = 'https://data.spiceai.io';
const flightUrl = 'flight.spiceai.io:443';

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
