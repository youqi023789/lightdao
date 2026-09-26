use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};
use crate::xmsg::ExecuteMsg as TokenExec;

const CONTRACT_NAME: &str = "crates.io:subtoken_factory";
const CONTRACT_VERSION: &str = "0.2.0";
/// Single-address dividend cap: 15%.
pub const DIVIDEND_CAP_PCT: u128 = 15;

#[cw_serde]
pub struct InstantiateMsg { pub light_token: String, pub oracle: String, pub governance: String }

#[cw_serde]
pub struct SubToken {
    pub symbol: String,
    pub total_supply: Uint128,
    pub investment_usd: Uint128,
    pub created: u64,
    pub locked_until: u64,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// Governance creates a sub-token after an investment proposal passes. total = investment_usd.
    CreateSubToken { symbol: String, investment_usd: Uint128 },
    /// User exchanges LIGHT for sub-tokens at 30-day TWAP; exchanged LIGHT is BURNED.
    Exchange { symbol: String, light_amount: Uint128 },
    /// Record a dividend distribution (pro-rata computed off-chain; enforces 15% cap context).
    DistributeDividend { symbol: String, usdc_amount: Uint128 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(SubToken)] SubToken { symbol: String },
    #[returns(Uint128)] BalanceOf { symbol: String, address: String },
    #[returns(Vec<String>)] AllSubTokens {},
}

#[cw_serde]
pub struct Config { pub light_token: Addr, pub oracle: Addr, pub governance: Addr }
pub const CONFIG: Item<Config> = Item::new("stf_config");
pub const SUBTOKENS: Map<&str, SubToken> = Map::new("subtokens");
pub const ST_BAL: Map<(&str, &Addr), Uint128> = Map::new("st_bal");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        light_token: deps.api.addr_validate(&msg.light_token)?,
        oracle: deps.api.addr_validate(&msg.oracle)?,
        governance: deps.api.addr_validate(&msg.governance)?,
    })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::CreateSubToken { symbol, investment_usd } => create(deps, env, info, symbol, investment_usd),
        ExecuteMsg::Exchange { symbol, light_amount } => exchange(deps, env, info, symbol, light_amount),
        ExecuteMsg::DistributeDividend { symbol, usdc_amount } => dividend(deps, info, symbol, usdc_amount),
    }
}

fn create(deps: DepsMut, env: Env, info: MessageInfo, symbol: String, investment_usd: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    if info.sender != cfg.governance { return Err(StdError::generic_err("unauthorized: only governance")); }
    if investment_usd.is_zero() { return Err(StdError::generic_err("zero investment")); }
    if SUBTOKENS.has(deps.storage, &symbol) { return Err(StdError::generic_err("exists")); }
    SUBTOKENS.save(deps.storage, &symbol, &SubToken {
        symbol: symbol.clone(), total_supply: investment_usd, investment_usd,
        created: env.block.time.seconds(), locked_until: env.block.time.seconds() + 30 * 86400,
    })?;
    Ok(Response::new().add_attribute("action", "create_subtoken").add_attribute("symbol", symbol))
}

/// Exchange LIGHT -> sub-token at 30-day TWAP (from oracle). LIGHT is BURNED (deflation).
fn exchange(deps: DepsMut, env: Env, info: MessageInfo, symbol: String, light_amount: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    if light_amount.is_zero() { return Err(StdError::generic_err("zero amount")); }
    let mut st = SUBTOKENS.load(deps.storage, &symbol)?;
    if env.block.time.seconds() < st.locked_until { return Err(StdError::generic_err("transfer lock active (30d)")); }
    let vwap: Uint128 = deps.querier.query_wasm_smart(cfg.oracle.to_string(), &crate::xmsg::OQuery::Twap30d {})?;
    if vwap.is_zero() { return Err(StdError::generic_err("oracle TWAP unavailable")); }
    let sub_minted = light_amount * vwap / Uint128::from(1_000_000u128);
    let cur = ST_BAL.may_load(deps.storage, (&symbol.as_str(), &info.sender))?.unwrap_or_default();
    let new_bal = cur + sub_minted;
    // 15% single-address cap measured against the FINAL supply (post-mint).
    let final_supply = st.total_supply + sub_minted;
    if new_bal * Uint128::from(100u128) > final_supply * Uint128::from(DIVIDEND_CAP_PCT) {
        return Err(StdError::generic_err("exceeds 15% single-address cap"));
    }
    ST_BAL.save(deps.storage, (&symbol.as_str(), &info.sender), &new_bal)?;
    st.total_supply = final_supply;
    SUBTOKENS.save(deps.storage, &symbol, &st)?;
    // BURN the exchanged LIGHT (permanent deflation). Requires allowance to this factory.
    let burn = WasmMsg::Execute { contract_addr: cfg.light_token.to_string(),
        msg: to_json_binary(&TokenExec::BurnFrom { owner: info.sender.to_string(), amount: light_amount })?, funds: vec![] };
    Ok(Response::new().add_message(burn).add_attribute("action", "exchange").add_attribute("sub_minted", sub_minted))
}

fn dividend(deps: DepsMut, info: MessageInfo, symbol: String, usdc_amount: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    // Only governance may trigger a recorded dividend distribution.
    if info.sender != cfg.governance { return Err(StdError::generic_err("unauthorized: only governance")); }
    let st = SUBTOKENS.load(deps.storage, &symbol)?;
    Ok(Response::new().add_attribute("action", "distribute_dividend").add_attribute("symbol", symbol).add_attribute("amount", usdc_amount).add_attribute("total_supply", st.total_supply))
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::SubToken { symbol } => to_json_binary(&SUBTOKENS.load(deps.storage, &symbol)?),
        QueryMsg::BalanceOf { symbol, address } => {
            let a = deps.api.addr_validate(&address)?;
            to_json_binary(&ST_BAL.may_load(deps.storage, (&symbol.as_str(), &a))?.unwrap_or_default())
        }
        QueryMsg::AllSubTokens {} => {
            let mut out = vec![];
            for kv in SUBTOKENS.range(deps.storage, None, None, cosmwasm_std::Order::Ascending) { let (s, _) = kv?; out.push(s); }
            to_json_binary(&out)
        }
    }
}

pub mod xmsg { use cosmwasm_schema::cw_serde; use cosmwasm_std::Uint128; #[cw_serde] pub enum ExecuteMsg { Burn { amount: Uint128 }, BurnFrom { owner: String, amount: Uint128 } } #[cw_serde] pub enum OQuery { Twap30d {} } }
