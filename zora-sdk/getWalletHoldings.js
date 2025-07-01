import dotenv from 'dotenv';
import { setApiKey, getProfile } from '@zoralabs/coins-sdk';

dotenv.config();
setApiKey(process.env.ZORA_API_KEY || '');

async function main() {
  const address = process.argv[2];
  if (!address) {
    console.error('Usage: node getWalletHoldings.js <wallet_address>');
    process.exit(1);
  }

  try {
    const resp = await getProfile({ address });
    const coins = resp.data?.profile?.coins || [];
    // ***REMOVED***
    const holdings = coins.filter(c => Number(c.balance) > 0).map(c => ({
      symbol: c.symbol,
      balance: c.balance,
      contract: c.address
    }));
    console.log(JSON.stringify(holdings));
  } catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
  }
}

main(); 