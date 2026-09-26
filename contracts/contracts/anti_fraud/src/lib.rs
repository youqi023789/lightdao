use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdResult, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:anti_fraud";
const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");
/// 3 consecutive challenge failures => zero that day's score. 5 in 7 days => review.
pub const FAIL_ZERO: u32 = 3;
pub const FAIL_REVIEW: u32 = 5;

#[cw_serde]
pub struct InstantiateMsg { pub mining_reward: String, pub validators: Vec<String> }

#[cw_serde]
pub enum ExecuteMsg {
    /// Validator issues a challenge to a light node (off-chain response window 30s).
    IssueChallenge { miner: String, day: u64 },
    /// Validator records a failed challenge response.
    RecordFailure { miner: String, day: u64 },
    /// Validator records a passed challenge.
    RecordSuccess { miner: String, day: u64 },
    /// After FAIL_ZERO, zero the miner's score for that day via mining_reward.
    ApplyPenalty { miner: String, day: u64 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(u32)] FailCount { miner: String, day: u64 },
    #[returns(bool)] Zeroed { miner: String, day: u64 },
}

#[cw_serde]
pub struct Config { pub mining_reward: Addr, pub validators: Vec<Addr> }
pub const CONFIG: Item<Config> = Item::new("af_config");
/// (miner, day) -> consecutive fail count
pub const FAILS: Map<(&Addr, u64), u32> = Map::new("fails");
/// (miner, day) -> zeroed flag
pub const ZEROED: Map<(&Addr, u64), bool> = Map::new("af_zeroed");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let validators = msg.validators.iter().map(|v| deps.api.addr_validate(v)).collect::<StdResult<Vec<_>>>()?;
    CONFIG.save(deps.storage, &Config { mining_reward: deps.api.addr_validate(&msg.mining_reward)?, validators })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, _env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    if !cfg.validators.contains(&info.sender) { return Err(cosmwasm_std::StdError::generic_err("not a validator")); }
    match msg {
        ExecuteMsg::IssueChallenge { miner, day } => {
            Ok(Response::new().add_attribute("action", "issue_challenge").add_attribute("miner", miner).add_attribute("day", day.to_string()))
        }
        ExecuteMsg::RecordFailure { miner, day } => {
            let m = deps.api.addr_validate(&miner)?;
            let f = FAILS.may_load(deps.storage, (&m, day))?.unwrap_or(0) + 1;
            FAILS.save(deps.storage, (&m, day), &f)?;
            Ok(Response::new().add_attribute("action", "record_failure").add_attribute("count", f.to_string()))
        }
        ExecuteMsg::RecordSuccess { miner, day } => {
            let m = deps.api.addr_validate(&miner)?;
            FAILS.save(deps.storage, (&m, day), &0)?;
            Ok(Response::new().add_attribute("action", "record_success"))
        }
        ExecuteMsg::ApplyPenalty { miner, day } => {
            let m = deps.api.addr_validate(&miner)?;
            let f = FAILS.may_load(deps.storage, (&m, day))?.unwrap_or(0);
            if f < FAIL_ZERO { return Err(cosmwasm_std::StdError::generic_err("below fail threshold")); }
            ZEROED.save(deps.storage, (&m, day), &true)?;
            // Call mining_reward.ZeroScore
            let zero = WasmMsg::Execute { contract_addr: cfg.mining_reward.to_string(),
                msg: to_json_binary(&crate::mmsg::ExecuteMsg::ZeroScore { miner: m.to_string(), day })?, funds: vec![] };
            Ok(Response::new().add_message(zero).add_attribute("action", "apply_penalty"))
        }
    }
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::FailCount { miner, day } => {
            let m = deps.api.addr_validate(&miner)?;
            to_json_binary(&FAILS.may_load(deps.storage, (&m, day))?.unwrap_or(0))
        }
        QueryMsg::Zeroed { miner, day } => {
            let m = deps.api.addr_validate(&miner)?;
            to_json_binary(&ZEROED.may_load(deps.storage, (&m, day))?.unwrap_or(false))
        }
    }
}

pub mod mmsg { use cosmwasm_schema::cw_serde; #[cw_serde] pub enum ExecuteMsg { ZeroScore { miner: String, day: u64 } } }
