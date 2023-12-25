import { task  } from "hardhat/config";
import { utils, Contract } from "ethers";
import * as fs from "fs";

task("track_metrics", "Updates the metrics in the Data lab")
  .setAction(async ({}, { ethers, network }) => {
    if (network.name === "hardhat") {
      console.warn(
        "You are running the faucet task with Hardhat network, which" +
          "gets automatically created and destroyed every time. Use the Hardhat" +
          " option '--network localhost'"
      );
    }

    const artifactFile =
      __dirname + `/../deployments/contracts.${network.name}.json`;

    if (!fs.existsSync(artifactFile)) {
      console.error("You need to deploy your contract first");
      return;
    }

    const artifactJson = fs.readFileSync(artifactFile);
    const artifacts = JSON.parse(artifactJson.toString());

    if ((await ethers.provider.getCode(artifacts.malt.address)) === "0x") {
      console.error("You need to deploy your contract first");
      return;
    }

    const [sender] = await ethers.getSigners();
    const senderAddress = await sender.getAddress();

    const maltDataLab = await ethers.getContractAt("MaltDataLab", artifacts.maltDataLab.address);
    const pair = new Contract(
      artifacts.maltPair.address,
      artifacts.maltPair.artifacts.abi,
      sender,
    );

    let tx = await maltDataLab.trackMaltPrice();
    let tx2 = await maltDataLab.trackPoolReserves();
    let tx3 = await maltDataLab.trackReserveRatio();
    await tx.wait();
    await tx2.wait();
    await tx3.wait();

    const malt = await ethers.getContractAt("Malt", artifacts.malt.address);
    const dai = await ethers.getContractAt("Malt", artifacts.rewardToken.address);

    const maltPrice = await maltDataLab.smoothedMaltPrice();
    const [maltReserves, collateralReserves] = await maltDataLab.smoothedReserves();
    const reserveRatio = await maltDataLab.smoothedReserveRatio();

    console.log(`Malt price: ${utils.formatEther(maltPrice)}.`);
    console.log(`Pool reserves:\nMalt: ${utils.formatEther(maltReserves)}. DAI: ${utils.formatEther(collateralReserves)}`);
    console.log(`Reserve ratio: ${utils.formatEther(reserveRatio)}.`);
  });
