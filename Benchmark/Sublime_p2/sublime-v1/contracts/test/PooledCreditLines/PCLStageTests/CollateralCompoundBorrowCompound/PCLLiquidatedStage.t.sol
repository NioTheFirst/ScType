// SPDX-License-Identifier: MIT
pragma solidity 0.7.6;
pragma abicoder v2;

import '../PCLLiquidatedStage.t.sol';

contract PCLLiquidatedStageCollateralCompoundBorrowCompound is PCLLiquidatedStage {
    using SafeMath for uint256;
    using SafeMath for uint128;
    using SafeERC20 for IERC20;

    function setUp() public override {
        PCLParent.setUp();

        lp = LenderPool(lenderPoolAddress);
        pcl = PooledCreditLine(pooledCreditLineAddress);

        request.borrowLimit = uint128(1_000_000 * (10**ERC20(address(borrowAsset)).decimals()));
        request.borrowRate = uint128((5 * pcl.SCALING_FACTOR()) / 1e2);
        request.collateralRatio = pcl.SCALING_FACTOR();
        request.borrowAsset = address(borrowAsset);
        request.collateralAsset = address(collateralAsset);
        request.duration = 5000 days;
        request.lenderVerifier = mockAdminVerifier1;
        request.defaultGracePeriod = 1 days;
        request.gracePenaltyRate = (10 * pcl.SCALING_FACTOR()) / 1e2;
        request.collectionPeriod = 5 days;
        request.minBorrowAmount = 90_000 * 10**(ERC20(address(borrowAsset)).decimals());
        request.borrowAssetStrategy = compoundYieldAddress;
        request.collateralAssetStrategy = compoundYieldAddress;
        request.borrowerVerifier = mockAdminVerifier2;
        request.areTokensTransferable = true;

        requestId = borrower.createRequest(request);
        assertEq(uint256(pcl.getStatusAndUpdate(requestId)), uint256(1));

        (requestId, numLenders) = goToActiveStage(10, request.borrowLimit);
        lender_0 = lenders[0].lenderAddress;

        assertTrue(pcl.getStatusAndUpdate(requestId) == PooledCreditLineStatus.ACTIVE, '!Active');

        // Now the borrower finds out the collateral he is required to deposit
        uint256 _requiredCollateral = borrower.getRequiredCollateral(requestId, request.borrowLimit);
        // & deposits the required collateral (this involves getting the collateral from the admin and giving allowance to the PCL)
        admin.transferToken(request.collateralAsset, address(borrower), _requiredCollateral);
        borrower.setAllowance(address(pcl), request.collateralAsset, type(uint256).max);
        borrower.depositCollateral(requestId, _requiredCollateral, false);

        // Now the borrower calculates the borrowable amount
        uint256 borrowableAmount = borrower.calculateBorrowableAmount(requestId);
        // and borrows the borrowable amount
        borrower.borrow(requestId, borrowableAmount);

        // Time travel to mid-duration
        vm.warp(block.timestamp + request.duration / 10);
        // Current Debt on the borrower
        uint256 currentDebt = borrower.calculateCurrentDebt(requestId);
        // Borrower decides to repay partial debt
        admin.transferToken(address(borrowAsset), address(borrower), currentDebt);
        borrower.setAllowance(address(pooledCreditLineAddress), address(borrowAsset), type(uint256).max);
        borrower.repay(requestId, currentDebt / 200);

        // Now we travel past the expiration date
        vm.warp(block.timestamp + request.duration + request.defaultGracePeriod);
        assertTrue(pcl.getStatusAndUpdate(requestId) == PooledCreditLineStatus.EXPIRED, '!Expired');

        // Now the PCL should be in the LIQUIDATED state
        PCLUser(lender_0).liquidate(requestId, false);
        assertTrue(pcl.getStatusAndUpdate(requestId) == PooledCreditLineStatus.LIQUIDATED);
    }
}
