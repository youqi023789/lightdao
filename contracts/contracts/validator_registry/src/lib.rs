use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:validator_registry";
const CONTRACT_VERSION: &str = "0.2.0";
/// Min stake 500,000 LIGHT. Max 100 validators. Double-sign slash 5% + 180d ban.
pub const MIN_STAKE: u128 = 500_000_000_000; // 500K * 1e6
pub const MAX_VALIDATORS: u32 = 100;
pub const DOUBLE_SIGN_SLASH_PCT: u128 = 5;
pub const OFFLINE_SLASH_PCT: u128 = 1;
pub const BAN_DAYS: u64 = 180;

pub mod lt {
    use cosmwasm_schema::cw_serde;
    use cosmwasm_std::Uint128;
    #[cw_serde]
    pub enum ExecuteMsg {
        Transfer { recipient: String, amount: Uint128 },
        TransferFrom { from: String, to: String, amount: Uint128 },
        Burn { amount: Uint128 },
    }
}

#[cw_serde]
pub struct InstantiateMsg { pub light_token: String, pub owner: String }

#[cw_serde]
pub struct Validator {
    pub addr: Addr,
    pub stake: Uint128,
    pub active: bool,
    pub banned_until: u64,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// Stake LIGHT (CW20) as a validator. Pulls `amount` from sender via allowance into registry custody.
    Register { amount: Uint128 },
    /// Exit: return remaining stake to sender.
    Unregister {},
    /// Owner/governance only: slash 5% + ban 180d for double-signing (slashed LIGHT is burned).
    SlashDoubleSign { validator: String },
    /// Owner/governance only: slash 1% for offline (slashed LIGHT is burned).
    SlashOffline { validator: String },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Vec<Validator>)] ActiveValidators {},
    #[returns(Validator)] Validator { address: String },
    #[returns(u32)] Count {},
    #[returns(Config)] Config {},
}

#[cw_serde]
pub struct Config { pub light_token: Addr, pub owner: Addr }
pub const CONFIG: Item<Config> = Item::new("vr_config");
pub const VALIDATORS: Map<&Addr, Validator> = Map::new("validators");
pub const COUNT: Item<u32> = Item::new("vcount");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, m: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        light_token: deps.api.addr_validate(&m.light_token)?,
        owner: deps.api.addr_validate(&m.owner)?,
    })?;
    COUNT.save(deps.storage, &0)?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Register { amount } => register(deps, env, info, amount),
        ExecuteMsg::Unregister {} => unregister(deps, env, info),
        ExecuteMsg::SlashDoubleSign { validator } => slash(deps, env, info, validator, true),
        ExecuteMsg::SlashOffline { validator } => slash(deps, env, info, validator, false),
    }
}

fn register(deps: DepsMut, env: Env, info: MessageInfo, amount: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    if amount.u128() < MIN_STAKE { return Err(StdError::generic_err("stake < 500K LIGHT")); }
    if VALIDATORS.has(deps.storage, &info.sender) { return Err(StdError::generic_err("already registered")); }
    let n = COUNT.load(deps.storage)?;
    if n >= MAX_VALIDATORS { return Err(StdError::generic_err("max 100 validators")); }
    VALIDATORS.save(deps.storage, &info.sender, &Validator { addr: info.sender.clone(), stake: amount, active: true, banned_until: 0 })?;
    COUNT.save(deps.storage, &(n + 1))?;
    // Pull LIGHT from sender into registry custody (requires allowance).
    let pull = WasmMsg::Execute {
        contract_addr: cfg.light_token.to_string(),
        msg: to_json_binary(&lt::ExecuteMsg::TransferFrom { from: info.sender.to_string(), to: env.contract.address.to_string(), amount })?,
        funds: vec![],
    };
    Ok(Response::new().add_message(pull).add_attribute("action", "register").add_attribute("stake", amount))
}

fn unregister(deps: DepsMut, env: Env, info: MessageInfo) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    let v = VALIDATORS.may_load(deps.storage, &info.sender)?.ok_or_else(|| StdError::generic_err("not registered"))?;
    let now = env.block.time.seconds();
    if v.banned_until > now { return Err(StdError::generic_err("banned: cannot unregister")); }
    VALIDATORS.remove(deps.storage, &info.sender);
    let n = COUNT.load(deps.storage)?; COUNT.save(deps.storage, &n.saturating_sub(1))?;
    let mut resp = Response::new().add_attribute("action", "unregister");
    if !v.stake.is_zero() {
        let send = WasmMsg::Execute {
            contract_addr: cfg.light_token.to_string(),
            msg: to_json_binary(&lt::ExecuteMsg::Transfer { recipient: info.sender.to_string(), amount: v.stake })?,
            funds: vec![],
        };
        resp = resp.add_message(send);
    }
    Ok(resp)
}

fn slash(deps: DepsMut, env: Env, info: MessageInfo, validator: String, double_sign: bool) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    // AUTH: only owner (governance/treasury) may slash.
    if info.sender != cfg.owner { return Err(StdError::generic_err("unauthorized: only owner may slash")); }
    let v = deps.api.addr_validate(&validator)?;
    let mut val = VALIDATORS.load(deps.storage, &v)?;
    let pct = if double_sign { DOUBLE_SIGN_SLASH_PCT } else { OFFLINE_SLASH_PCT };
    let slash_amt = val.stake * Uint128::from(pct) / Uint128::from(100u128);
    val.stake = val.stake - slash_amt;
    if double_sign {
        val.active = false;
        val.banned_until = env.block.time.seconds() + BAN_DAYS * 86400;
    }
    VALIDATORS.save(deps.storage, &v, &val)?;
    let mut resp = Response::new()
        .add_attribute("action", if double_sign { "slash_double_sign" } else { "slash_offline" })
        .add_attribute("validator", v).add_attribute("slash", slash_amt);
    // Burn the slashed LIGHT from registry custody (deflationary).
    if !slash_amt.is_zero() {
        let burn = WasmMsg::Execute {
            contract_addr: cfg.light_token.to_string(),
            msg: to_json_binary(&lt::ExecuteMsg::Burn { amount: slash_amt })?,
            funds: vec![],
        };
        resp = resp.add_message(burn);
    }
    Ok(resp)
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::ActiveValidators {} => {
            let mut out = vec![];
            for kv in VALIDATORS.range(deps.storage, None, None, cosmwasm_std::Order::Ascending) {
                let (_, v) = kv?; if v.active { out.push(v); }
            }
            to_json_binary(&out)
        }
        QueryMsg::Validator { address } => { let a = deps.api.addr_validate(&address)?; to_json_binary(&VALIDATORS.load(deps.storage, &a)?) }
        QueryMsg::Count {} => to_json_binary(&COUNT.load(deps.storage)?),
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
    }
}
