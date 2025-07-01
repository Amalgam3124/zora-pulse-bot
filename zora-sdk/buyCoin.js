import dotenv from 'dotenv';
import { setApiKey, tradeCoin } from '@zoralabs/coins-sdk';
import { createWalletClient, createPublicClient, http, parseEther, Hex } from 'viem';
import { zora } from 'viem/chains';

dotenv.config();
setApiKey(process.env.ZORA_API_KEY || '');

async function main() {
  const [privateKey, coinAddress, ethAmount] = process.argv.slice(2);
  if (!privateKey || !coinAddress || !ethAmount) {
    console.error('Usage: node buyCoin.js <private_key> <coin_address> <eth_amount>');
    process.exit(1);
  }

  try {
    const publicClient = createPublicClient({
      chain: zora,
      transport: http('https://rpc.zora.energy'),
    });
    const walletClient = createWalletClient({
      account: privateKey as Hex,
      chain: zora,
      transport: http('https://rpc.zora.energy'),
    });
    const buyParams = {
      direction: 'buy',
      target: coinAddress,
      args: {
        recipient: walletClient.account.address,
        orderSize: parseEther(ethAmount),
        minAmountOut: 0n,
      },
    };
    const result = await tradeCoin(buyParams, walletClient, publicClient);
    console.log(JSON.stringify({ hash: result.hash, trade: result.trade }));
  } catch (e) {
    console.error('Error:', e.message || e);
    process.exit(1);
  }
}

main(); 