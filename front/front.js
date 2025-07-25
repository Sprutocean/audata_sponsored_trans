const requiredFee = await teePoolContract.teeFee();
const userBalance = await vanaToken.balanceOf(userAddress);

if (userBalance.lt(requiredFee)) {
  // 1. Call sponsor backend
  await fetch('/sponsor', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ address: userAddress })
  });

  // 2. Poll until VANA is received
  await waitUntil(async () => {
    const newBalance = await vanaToken.balanceOf(userAddress);
    return newBalance.gte(requiredFee);
  }, 10000); // 10s timeout
}

// 3. Proceed with transaction
const tx = await dlpContract.requestContributionProof(fileId);
