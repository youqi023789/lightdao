use cosmwasm_schema::cw_serde;
use cosmwasm_std::{Addr, Uint128};
use cw_storage_plus::{Item, Map};

#[cw_serde]
pub struct TokenConfig {
    pub name: String,
    pub symbol: String,
    pub decimals: u8,
    pub total_supply: Uint128,
    pub total_minted: Uint128,
    pub minter: Addr,
    pub owner: Option<Addr>,
}

pub const CONFIG: Item<TokenConfig> = Item::new("config");
/// address -> balance
pub const BALANCES: Map<&Addr, Uint128> = Map::new("balances");
/// (owner, spender) -> allowance
pub const ALLOWANCES: Map<(&Addr, &Addr), Uint128> = Map::new("allowances");
