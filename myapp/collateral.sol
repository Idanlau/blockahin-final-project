import "@openzeppelin/contracts/token/ERC721/IERC721.sol";

contract CollateralizedLoanNFT {
    address public lender;
    address public borrower;
    uint public loanAmount;
    uint public interestRate;
    uint public dueDate;
    bool public isRepaid;

    IERC721 public nftContract;
    uint public tokenId;

    enum LoanState { Created, Funded, Collateralized, Repaid, Defaulted }
    LoanState public state;

    constructor(uint _interestRate, uint _dueDate) {
        lender = msg.sender;
        interestRate = _interestRate;
        dueDate = _dueDate;
        state = LoanState.Created;
    }

    function fundLoan(address _borrower, uint _loanAmount) external payable {
        require(msg.sender == lender, "Only lender can fund");
        require(state == LoanState.Created, "Loan already funded");
        require(msg.value >= _loanAmount, "Insufficient funding");

        borrower = _borrower;
        loanAmount = _loanAmount;
        state = LoanState.Funded;
    }

    function depositCollateral(address _nftAddress, uint _tokenId) external {
        require(msg.sender == borrower, "Only borrower can deposit NFT");
        require(state == LoanState.Funded, "Loan not ready for NFT");

        nftContract = IERC721(_nftAddress);
        tokenId = _tokenId;

        // Transfer NFT to contract
        nftContract.transferFrom(msg.sender, address(this), _tokenId);

        // Send loan funds to borrower
        payable(borrower).transfer(loanAmount);
        state = LoanState.Collateralized;
    }

    function repay() external payable {
        require(msg.sender == borrower, "Only borrower can repay");
        require(state == LoanState.Collateralized, "Loan not active");

        uint repaymentAmount = loanAmount + ((loanAmount * interestRate) / 10000);
        require(msg.value >= repaymentAmount, "Insufficient repayment");

        isRepaid = true;
        state = LoanState.Repaid;

        // Transfer repayment to lender
        payable(lender).transfer(repaymentAmount);

        // Return NFT to borrower
        nftContract.transferFrom(address(this), borrower, tokenId);
    }

    function claimCollateral() external {
        require(msg.sender == lender, "Only lender can claim");
        require(state == LoanState.Collateralized, "Loan not active");
        require(block.timestamp > dueDate && !isRepaid, "Loan not defaulted");

        state = LoanState.Defaulted;

        // Transfer NFT to lender
        nftContract.transferFrom(address(this), lender, tokenId);
    }
}
