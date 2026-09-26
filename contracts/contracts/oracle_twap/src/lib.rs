pub mod msg {
    use cosmwasm_schema::{cw_serde, QueryResponses};
    use cosmwasm_std::Uint128;
    /// Single-source deviation >5% excluded; cross-source deviation >15% triggers anomaly pause.
    pub const BLOCK_DEVIATION_CAP_PCT: u128 = 5;
    pub const CROSS_DEVIATION_CAP_PCT: u128 = 15;

    #[cw_serde]
    pub struct InstantiateMsg { pub validators: Vec<String>, pub feeders: Vec<String> }

    #[cw_serde]
    pub enum ExecuteMsg {
        /// Validator submits an external price observation (USD per LIGHT, scaled 1e6).
        SubmitPrice { price: Uint128 },
        /// Feed the DEX spot price; accumulated into the current day's bucket for a 30-day TWAP.
        Accumulate { spot: Uint128 },
    }

    #[cw_serde]
    #[derive(QueryResponses)]
    pub enum QueryMsg {
        #[returns(Uint128)] Twap30d {},
        #[returns(Uint128)] ExternalMedian {},
        #[returns(bool)] Anomaly {},
    }
}

use cosmwasm_schema::cw_serde;
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdError, StdResult, Uint128,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

use crate::msg::{ExecuteMsg, InstantiateMsg, QueryMsg, BLOCK_DEVIATION_CAP_PCT, CROSS_DEVIATION_CAP_PCT};

const CONTRACT_NAME: &str = "crates.io:oracle_twap";
const CONTRACT_VERSION: &str = "0.2.0";
const WINDOW_DAYS: u64 = 30;
const DAY_SECS: u64 = 86_400;

#[cw_serde]
pub struct Config { pub validators: Vec<Addr>, pub feeders: Vec<Addr> }
/// Per-day accumulation bucket: (sum of spots, count).
#[cw_serde]
pub struct Bucket { pub sum: Uint128, pub count: Uint128 }
pub const CONFIG: Item<Config> = Item::new("oracle_config");
pub const EXT: Map<&Addr, Uint128> = Map::new("ext");
/// day index -> bucket
pub const DAILY: Map<u64, Bucket> = Map::new("daily");
/// last block height that fed (per-block dedup)
pub const LAST_BLOCK: Item<u64> = Item::new("last_block");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let validators = msg.validators.iter().map(|v| deps.api.addr_validate(v)).collect::<StdResult<Vec<_>>>()?;
    let feeders = msg.feeders.iter().map(|v| deps.api.addr_validate(v)).collect::<StdResult<Vec<_>>>()?;
    CONFIG.save(deps.storage, &Config { validators, feeders })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::SubmitPrice { price } => {
            let cfg = CONFIG.load(deps.storage)?;
            if !cfg.validators.contains(&info.sender) { return Err(StdError::generic_err("not a validator")); }
            let prev = EXT.may_load(deps.storage, &info.sender)?.unwrap_or(price);
            let diff = if price > prev { price - prev } else { prev - price };
            if prev > Uint128::zero() && diff * Uint128::from(100u128) > prev * Uint128::from(BLOCK_DEVIATION_CAP_PCT) {
                return Err(StdError::generic_err("block deviation >5%: rejected"));
            }
            EXT.save(deps.storage, &info.sender, &price)?;
            Ok(Response::new().add_attribute("action", "submit_price"))
        }
        ExecuteMsg::Accumulate { spot } => {
            let cfg = CONFIG.load(deps.storage)?;
            let authorized = cfg.validators.contains(&info.sender) || cfg.feeders.contains(&info.sender);
            if !authorized { return Err(StdError::generic_err("unauthorized feeder")); }
            if spot.is_zero() { return Err(StdError::generic_err("zero spot")); }
            // One accumulation per block (prevents intra-block spam skew).
            let last = LAST_BLOCK.may_load(deps.storage)?.unwrap_or(0);
            if last == env.block.height && last != 0 { return Err(StdError::generic_err("already accumulated this block")); }
            LAST_BLOCK.save(deps.storage, &env.block.height)?;
            let day = env.block.time.seconds() / DAY_SECS;
            let mut b = DAILY.may_load(deps.storage, day)?.unwrap_or(Bucket { sum: Uint128::zero(), count: Uint128::zero() });
            b.sum = b.sum + spot;
            b.count = b.count + Uint128::one();
            DAILY.save(deps.storage, day, &b)?;
            Ok(Response::new().add_attribute("action", "accumulate").add_attribute("day", day.to_string()))
        }
    }
}

/// 30-day time-weighted average: equal weight per day that has data within the last 30 days,
/// each day's value = average of that day's spot samples.
fn twap30d(deps: Deps, env: &Env) -> StdResult<Uint128> {
    let today = env.block.time.seconds() / DAY_SECS;
    let start = today.saturating_sub(WINDOW_DAYS - 1);
    let mut acc = Uint128::zero();
    let mut days = Uint128::zero();
    for d in start..=today {
        if let Some(b) = DAILY.may_load(deps.storage, d)? {
            if !b.count.is_zero() {
                acc = acc + (b.sum / b.count);
                days = days + Uint128::one();
            }
        }
    }
    if days.is_zero() { return Ok(Uint128::zero()); }
    Ok(acc / days)
}

fn external_median(deps: Deps) -> StdResult<Uint128> {
    let cfg = CONFIG.load(deps.storage)?;
    let mut vals: Vec<Uint128> = vec![];
    for v in cfg.validators { if let Some(p) = EXT.may_load(deps.storage, &v)? { vals.push(p); } }
    if vals.is_empty() { return Ok(Uint128::zero()); }
    vals.sort();
    Ok(vals[vals.len() / 2])
}

#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::Twap30d {} => to_json_binary(&twap30d(deps, &env)?),
        QueryMsg::ExternalMedian {} => to_json_binary(&external_median(deps)?),
        QueryMsg::Anomaly {} => {
            let twap = twap30d(deps, &env)?;
            let med = external_median(deps)?;
            let anom = if twap.is_zero() || med.is_zero() { false } else {
                let diff = if twap > med { twap - med } else { med - twap };
                diff * Uint128::from(100u128) > twap * Uint128::from(CROSS_DEVIATION_CAP_PCT)
            };
            to_json_binary(&anom)
        }
    }
}
