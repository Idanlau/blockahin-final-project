// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";

contract MyNFT is ERC721 {
    uint public nextTokenId;
    address public admin;

    constructor() ERC721("MyTestNFT", "MTNFT") {
        admin = msg.sender;
    }

    function mint() external {
        _safeMint(msg.sender, nextTokenId);
        nextTokenId++;
    }
}
