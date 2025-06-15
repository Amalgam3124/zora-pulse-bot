// zora-sdk/getPulseMetrics.js
import dotenv from 'dotenv';
import { setApiKey, getCoinsTopVolume24h } from '@zoralabs/coins-sdk';
import { createPublicClient, http } from 'viem';
import { base } from 'viem/chains';

dotenv.config();
setApiKey(process.env.ZORA_API_KEY || '');


async function main() {
  try {
    const resp = await getCoinsTopVolume24h({ count: 5 });
    const coins = resp.data?.exploreList?.edges?.map(e => e.node) || [];

    for (const coin of coins) {
      console.log(JSON.stringify({
        contract:  coin.address,
        symbol: coin.symbol,
        volume_24h: coin.volume24h ?? null,
        market_cap: coin.marketCap ?? null,
        market_cap_delta_24h: coin.marketCapDelta24h ?? null,
        unique_holders: coin.uniqueHolders ?? null
      }));
    }
  } catch (err) {
    console.error('❌ Error fetching pulse metrics:', err);
    process.exit(1);
  }
}

main();
