use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:vesting";
const CONTRACT_VERSION: &str = "0.2.0";

pub mod lt {
    use cosmwasm_schema::cw_serde;
    use cosmwasm_std::Uint128;
    #[cw_serde]
    pub enum ExecuteMsg { Transfer { recipient: String, amount: Uint128 } }
}

#[cw_serde]
pub struct InstantiateMsg { pub light_token: String, pub owner: String }

#[cw_serde]
pub struct Schedule {
    pub beneficiary: Addr,
    pub total: Uint128,
    pub cliff_secs: u64,
    pub linear_secs: u64,
    pub start: u64,
    pub claimed: Uint128,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// Owner (treasury/governance) only: create a vesting schedule. The vault must be funded with LIGHT.
    AddSchedule { beneficiary: String, total: Uint128, cliff_secs: u64, linear_secs: u64 },
    /// Beneficiary claims vested LIGHT (real transfer from vault custody).
    Claim {},
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Uint128)] Vested { address: String, at_time: u64 },
    #[returns(Schedule)] Schedule { address: String },
    #[returns(Config)] Config {},
}

#[cw_serde]
pub struct Config { pub light_token: Addr, pub owner: Addr }
pub const CONFIG: Item<Config> = Item::new("vesting_config");
pub const SCHEDULES: Map<&Addr, Schedule> = Map::new("schedules");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, m: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        light_token: deps.api.addr_validate(&m.light_token)?,
        owner: deps.api.addr_validate(&m.owner)?,
    })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::AddSchedule { beneficiary, total, cliff_secs, linear_secs } => {
            let cfg = CONFIG.load(deps.storage)?;
            // AUTH: only owner may create schedules.
            if info.sender != cfg.owner { return Err(StdError::generic_err("unauthorized: only owner")); }
            let b = deps.api.addr_validate(&beneficiary)?;
            if SCHEDULES.has(deps.storage, &b) { return Err(StdError::generic_err("schedule exists")); }
            if linear_secs == 0 { return Err(StdError::generic_err("linear_secs must be > 0")); }
            SCHEDULES.save(deps.storage, &b, &Schedule { beneficiary: b.clone(), total, cliff_secs, linear_secs, start: env.block.time.seconds(), claimed: Uint128::zero() })?;
            Ok(Response::new().add_attribute("action", "add_schedule").add_attribute("beneficiary", b).add_attribute("total", total))
        }
        ExecuteMsg::Claim {} => {
            let cfg = CONFIG.load(deps.storage)?;
            let mut s = SCHEDULES.load(deps.storage, &info.sender)?;
            let vested = vested_amount(&s, env.block.time.seconds());
            let claimable = vested.checked_sub(s.claimed).unwrap_or_default();
            if claimable.is_zero() { return Err(StdError::generic_err("nothing claimable (cliff not reached or fully claimed)")); }
            s.claimed = s.claimed + claimable;
            SCHEDULES.save(deps.storage, &info.sender, &s)?;
            // Real payout: transfer LIGHT from vault custody to beneficiary.
            let send = WasmMsg::Execute {
                contract_addr: cfg.light_token.to_string(),
                msg: to_json_binary(&lt::ExecuteMsg::Transfer { recipient: info.sender.to_string(), amount: claimable })?,
                funds: vec![],
            };
            Ok(Response::new().add_message(send).add_attribute("action", "claim").add_attribute("amount", claimable))
        }
    }
}

/// vested = 0 before cliff; after cliff, linear over linear_secs up to total.
fn vested_amount(s: &Schedule, now: u64) -> Uint128 {
    let elapsed = now.saturating_sub(s.start);
    if elapsed < s.cliff_secs { return Uint128::zero(); }
    let post_cliff = elapsed.saturating_sub(s.cliff_secs).min(s.linear_secs);
    s.total * Uint128::from(post_cliff) / Uint128::from(s.linear_secs.max(1))
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::Vested { address, at_time } => {
            let a = deps.api.addr_validate(&address)?;
            let s = SCHEDULES.load(deps.storage, &a)?;
            to_json_binary(&vested_amount(&s, at_time))
        }
        QueryMsg::Schedule { address } => { let a = deps.api.addr_validate(&address)?; to_json_binary(&SCHEDULES.load(deps.storage, &a)?) }
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
    }
}
