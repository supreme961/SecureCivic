// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract LandRegistry {
    
    struct Land {
        uint256 id;
        string location;
        uint256 area;
        address owner;
        bool isForSale;
    }

    // Land ID se Land ki details map karne ke liye
    mapping(uint256 => Land) public lands;

    // Land register karne ka function
    function registerLand(uint256 _id, string memory _location, uint256 _area) public {
        require(lands[_id].id == 0, "Land already registered!");
        
        lands[_id] = Land({
            id: _id,
            location: _location,
            area: _area,
            owner: msg.sender,
            isForSale: false
        });
    }
}