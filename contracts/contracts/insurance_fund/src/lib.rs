use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdError,
    StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:insurance_fund";
const CONTRACT_VERSION: &str = "0.2.0";
/// Accrual: 10% of each successful investment profit. Single payout <=20% of pool. Claim needs 66% DAO approval.
pub const ACCRUAL_PCT: u128 = 10;
pub const MAX_PAYOUT_PCT: u128 = 20;
pub const APPROVAL_PCT: u128 = 66;

pub mod lt {
    use cosmwasm_schema::cw_serde;
    use cosmwasm_std::Uint128;
    #[cw_serde]
    pub enum ExecuteMsg {
        Transfer { recipient: String, amount: Uint128 },
        TransferFrom { from: String, to: String, amount: Uint128 },
    }
}

#[cw_serde]
pub struct InstantiateMsg {
    pub light_token: String,
    /// Governance contract: the only address that may relay DAO claim votes.
    pub governance: String,
    /// Authorized accrual source (subtoken_factory) that funds the pool from realized profit.
    pub accrue_source: String,
}

#[cw_serde]
pub struct Claim {
    pub id: u64,
    pub claimant: String,
    pub amount: Uint128,
    pub yes: Uint128,
    pub no: Uint128,
    pub resolved: bool,
    pub paid: bool,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// Accrue 10% of a realized profit into the fund. Only accrue_source/governance. Pulls real LIGHT.
    Accrue { profit: Uint128 },
    /// Anyone may file a claim (needs an off-chain adjuster report).
    FileClaim { amount: Uint128 },
    /// DAO vote relay: only governance may submit aggregated vote weight.
    VoteClaim { claim_id: u64, approve: bool, weight: Uint128 },
    /// Resolve; if approved (>=66%) and amount <=20% of pool, pay claimant in real LIGHT.
    ResolveClaim { claim_id: u64 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Uint128)] PoolBalance {},
    #[returns(Claim)] Claim { id: u64 },
    #[returns(Config)] Config {},
}

#[cw_serde]
pub struct Config { pub light_token: Addr, pub governance: Addr, pub accrue_source: Addr }
pub const CONFIG: Item<Config> = Item::new("if_config");
/// Real LIGHT custodied by the fund.
pub const POOL: Item<Uint128> = Item::new("pool");
pub const CLAIMS: Map<u64, Claim> = Map::new("claims");
pub const NEXT_ID: Item<u64> = Item::new("claim_next");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, m: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        light_token: deps.api.addr_validate(&m.light_token)?,
        governance: deps.api.addr_validate(&m.governance)?,
        accrue_source: deps.api.addr_validate(&m.accrue_source)?,
    })?;
    POOL.save(deps.storage, &Uint128::zero())?;
    NEXT_ID.save(deps.storage, &1)?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Accrue { profit } => accrue(deps, env, info, profit),
        ExecuteMsg::FileClaim { amount } => file_claim(deps, info, amount),
        ExecuteMsg::VoteClaim { claim_id, approve, weight } => vote_claim(deps, info, claim_id, approve, weight),
        ExecuteMsg::ResolveClaim { claim_id } => resolve_claim(deps, info, claim_id),
    }
}

fn accrue(deps: DepsMut, env: Env, info: MessageInfo, profit: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    // AUTH: only the realized-profit source or governance may accrue.
    if info.sender != cfg.accrue_source && info.sender != cfg.governance {
        return Err(StdError::generic_err("unauthorized: only accrue_source/governance"));
    }
    let add = profit * Uint128::from(ACCRUAL_PCT) / Uint128::from(100u128);
    if add.is_zero() { return Err(StdError::generic_err("zero accrual")); }
    let mut pool = POOL.load(deps.storage)?;
    pool = pool + add;
    POOL.save(deps.storage, &pool)?;
    // Pull the real LIGHT into fund custody (sender must hold + allow).
    let pull = WasmMsg::Execute {
        contract_addr: cfg.light_token.to_string(),
        msg: to_json_binary(&lt::ExecuteMsg::TransferFrom { from: info.sender.to_string(), to: env.contract.address.to_string(), amount: add })?,
        funds: vec![],
    };
    Ok(Response::new().add_message(pull).add_attribute("action", "accrue").add_attribute("add", add))
}

fn file_claim(deps: DepsMut, info: MessageInfo, amount: Uint128) -> StdResult<Response> {
    if amount.is_zero() { return Err(StdError::generic_err("zero claim")); }
    let id = NEXT_ID.load(deps.storage)?;
    CLAIMS.save(deps.storage, id, &Claim { id, claimant: info.sender.to_string(), amount, yes: Uint128::zero(), no: Uint128::zero(), resolved: false, paid: false })?;
    NEXT_ID.save(deps.storage, &(id + 1))?;
    Ok(Response::new().add_attribute("action", "file_claim").add_attribute("id", id.to_string()))
}

fn vote_claim(deps: DepsMut, info: MessageInfo, claim_id: u64, approve: bool, weight: Uint128) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    // AUTH: only governance relays the DAO's aggregated vote weight (prevents self-approval).
    if info.sender != cfg.governance { return Err(StdError::generic_err("unauthorized: only governance")); }
    let mut c = CLAIMS.load(deps.storage, claim_id)?;
    if c.resolved { return Err(StdError::generic_err("already resolved")); }
    if approve { c.yes = c.yes + weight } else { c.no = c.no + weight };
    CLAIMS.save(deps.storage, claim_id, &c)?;
    Ok(Response::new().add_attribute("action", "vote_claim").add_attribute("id", claim_id.to_string()))
}

fn resolve_claim(deps: DepsMut, info: MessageInfo, claim_id: u64) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    let mut c = CLAIMS.load(deps.storage, claim_id)?;
    if c.resolved { return Err(StdError::generic_err("resolved")); }
    let total = c.yes + c.no;
    if total.is_zero() { return Err(StdError::generic_err("no DAO vote yet")); }
    let approved = (c.yes * Uint128::from(100u128) / total) >= Uint128::from(APPROVAL_PCT);
    c.resolved = true;
    let pool = POOL.load(deps.storage)?;
    let max_pay = pool * Uint128::from(MAX_PAYOUT_PCT) / Uint128::from(100u128);
    let mut resp = Response::new().add_attribute("action", "resolve_claim").add_attribute("approved", approved.to_string());
    if approved && c.amount <= max_pay {
        c.paid = true;
        POOL.save(deps.storage, &(pool - c.amount))?;
        // Real payout to claimant.
        let pay = WasmMsg::Execute {
            contract_addr: cfg.light_token.to_string(),
            msg: to_json_binary(&lt::ExecuteMsg::Transfer { recipient: c.claimant.clone(), amount: c.amount })?,
            funds: vec![],
        };
        resp = resp.add_message(pay).add_attribute("paid", c.amount);
    } else {
        CLAIMS.save(deps.storage, claim_id, &c)?;
        return Ok(resp.add_attribute("paid", "0"));
    }
    CLAIMS.save(deps.storage, claim_id, &c)?;
    let _ = info;
    Ok(resp)
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::PoolBalance {} => to_json_binary(&POOL.load(deps.storage)?),
        QueryMsg::Claim { id } => to_json_binary(&CLAIMS.load(deps.storage, id)?),
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
    }
}
