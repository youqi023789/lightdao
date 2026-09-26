use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::Uint128;

/// Hard supply cap: 2,500,000,000 LIGHT (2.5B). Never inflated.
pub const HARD_CAP: u128 = 2_500_000_000_000_000; // 2.5B * 10^6 (6 decimals)

#[cw_serde]
pub struct InstantiateMsg {
    pub minter: String,
    pub owner: Option<String>,
    pub decimals: u8,
}

#[cw_serde]
pub enum ExecuteMsg {
    Transfer { recipient: String, amount: Uint128 },
    /// Allowance-gated transfer from `from` to `to` (spender = msg sender). Enables custodial staking/vesting.
    TransferFrom { from: String, to: String, amount: Uint128 },
    Burn { amount: Uint128 },
    BurnFrom { owner: String, amount: Uint128 },
    Mint { recipient: String, amount: Uint128 },
    UpdateMinter { new_minter: String },
    IncreaseAllowance { spender: String, amount: Uint128 },
    DecreaseAllowance { spender: String, amount: Uint128 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(cw20::TokenInfoResponse)]
    TokenInfo {},
    #[returns(cw20::BalanceResponse)]
    Balance { address: String },
    #[returns(MinterResponse)]
    Minter {},
    #[returns(cw20::AllowanceResponse)]
    Allowance { owner: String, spender: String },
}

#[cw_serde]
pub struct MinterResponse {
    pub minter: String,
    pub owner: Option<String>,
    pub total_minted: Uint128,
    pub remaining_cap: Uint128,
}
