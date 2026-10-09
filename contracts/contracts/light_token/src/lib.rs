// light_token (native LIGHT): registry + permanent burn sink.
// LIGHT is the chain's NATIVE denom `ulight` (fixed 2.5B minted at genesis). This contract holds
// no spendable logic: any `ulight` sent here is locked forever (= burned). Balance == total burned.
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult,
    Uint128,
};
use cw2::set_contract_version;
use cw_storage_plus::Item;

const CONTRACT_NAME: &str = "crates.io:light_token";
const CONTRACT_VERSION: &str = "1.0.0";
pub const DENOM: &str = "ulight";

#[cw_serde]
pub struct InstantiateMsg {
    pub decimals: u8,
    pub owner: Option<String>,
    pub total_supply: Uint128,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// No-op marker. Native LIGHT reaches the sink via BankMsg::Send from other contracts;
    /// there is intentionally NO code path that can move funds back out (permanent burn).
    NoteBurn { note: String },
}

#[cw_serde]
pub struct TokenInfo {
    pub denom: String,
    pub symbol: String,
    pub decimals: u8,
    pub total_supply: Uint128,
    pub burned: Uint128,
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(TokenInfo)]
    TokenInfo {},
    #[returns(Uint128)]
    Burned {},
    #[returns(Config)]
    Config {},
}

#[cw_serde]
pub struct Config {
    pub decimals: u8,
    pub owner: Option<Addr>,
    pub total_supply: Uint128,
}
pub const CONFIG: Item<Config> = Item::new("lt_config");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let owner = msg.owner.map(|o| deps.api.addr_validate(&o)).transpose()?;
    CONFIG.save(deps.storage, &Config { decimals: msg.decimals, owner, total_supply: msg.total_supply })?;
    Ok(Response::new().add_attribute("action", "instantiate").add_attribute("denom", DENOM))
}

#[entry_point]
pub fn execute(_deps: DepsMut, _e: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::NoteBurn { note } => Ok(Response::new()
            .add_attribute("action", "note_burn")
            .add_attribute("by", info.sender)
            .add_attribute("note", note)),
    }
}

#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::TokenInfo {} => {
            let cfg = CONFIG.load(deps.storage)?;
            let burned = deps.querier.query_balance(env.contract.address, DENOM)?.amount;
            to_json_binary(&TokenInfo {
                denom: DENOM.to_string(),
                symbol: "LIGHT".to_string(),
                decimals: cfg.decimals,
                total_supply: cfg.total_supply,
                burned,
            })
        }
        QueryMsg::Burned {} => {
            let burned = deps.querier.query_balance(env.contract.address, DENOM)?.amount;
            to_json_binary(&burned)
        }
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
    }
}
