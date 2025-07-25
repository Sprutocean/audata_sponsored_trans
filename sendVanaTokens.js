require('dotenv').config();
const { ethers } = require('ethers');

// Load environment variables
const {
  SPONSOR_PRIVATE_KEY,
  PROVIDER_URL,
  VANA_TOKEN_ADDRESS
} = process.env;

if (!SPONSOR_PRIVATE_KEY || !PROVIDER_URL || !VANA_TOKEN_ADDRESS) {
  throw new Error('Missing required env variables.');
}

// Minimal ERC20 ABI with balanceOf and transfer
const VANA_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function transfer(address to, uint256 amount) returns (bool)'
];

async function sendVanaTokens(toAddress, amount) {
  try {
    // Setup provider and wallet
    const provider = new ethers.JsonRpcProvider(PROVIDER_URL);
    const wallet = new ethers.Wallet(SPONSOR_PRIVATE_KEY, provider);

    // Connect to VANA token contract
    const vanaContract = new ethers.Contract(VANA_TOKEN_ADDRESS, VANA_ABI, wallet);

    // Check sponsor wallet balance (ETH) for gas
    const ethBalance = await wallet.getBalance();
    if (ethBalance.lt(ethers.parseEther('0.001'))) {  // minimum gas threshold
      throw new Error('Sponsor wallet has insufficient ETH for gas.');
    }

    // Check sponsor wallet VANA balance
    const vanaBalance = await vanaContract.balanceOf(wallet.address);
    if (vanaBalance.lt(amount)) {
      throw new Error('Sponsor wallet has insufficient VANA tokens.');
    }

    // Send VANA tokens
    const tx = await vanaContract.transfer(toAddress, amount);
    console.log(`Transaction sent. Hash: ${tx.hash}`);

    // Wait for confirmation
    const receipt = await tx.wait();
    console.log(`Transaction confirmed in block ${receipt.blockNumber}`);

    return receipt;
  } catch (error) {
    console.error('Error sending VANA tokens:', error);
    throw error;
  }
}

// Example usage (send 0.01 VANA, assuming 18 decimals)
async function main() {
  const recipient = '0xUserWalletAddressHere';
  const amount = ethers.parseUnits('0.01', 18); // Adjust decimals if VANA uses different decimals

  await sendVanaTokens(recipient, amount);
}

main();
