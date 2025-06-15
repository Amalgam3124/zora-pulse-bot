// zora-sdk/getCoinMetrics.js
import dotenv from 'dotenv';
import { setApiKey, getCoin } from '@zoralabs/coins-sdk';
import { getAddress } from 'ethers';
import { base } from 'viem/chains';

dotenv.config();
setApiKey(process.env.ZORA_API_KEY || '');

async function main() {
  const raw = process.argv[2];
  if (!raw) {
    console.error('Usage: node getCoinMetrics.js <contract_address>');
    process.exit(1);
  }

  let addr;
  try {
    addr = getAddress(raw);
  } catch {
    console.error('❌ Invalid address format');
    process.exit(1);
  }

  try {
    const resp = await getCoin({
      address: addr,
      chain: base.id,
    });

    const coin = resp.data?.zora20Token;
    if (!coin) {
      console.error('❌ Coin not found');
      process.exit(1);
    }

    console.log(JSON.stringify({
      contract:             coin.address,
      symbol:               coin.symbol,
      volume_24h:           coin.volume24h    ?? null,
      market_cap:           coin.marketCap    ?? null,
      market_cap_delta_24h: coin.marketCapDelta24h ?? null,
      unique_holders:       coin.uniqueHolders      ?? null
    }));
  } catch (e) {
    console.error('❌ Error fetching coin metrics:', e.message);
    process.exit(1);
  }
}

main();
