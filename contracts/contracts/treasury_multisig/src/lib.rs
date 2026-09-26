use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, BankMsg, Coin, Deps, DepsMut, Env, MessageInfo,
    Response, StdResult, Uint128,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:treasury_multisig";
const CONTRACT_VERSION: &str = env!("CARGO_PKG_VERSION");
/// Timelock: 72 hours. Emergency proposals CANNOT exempt fund operations.
pub const TIMELOCK_SECS: u64 = 72 * 3600;
/// Threshold: 3 of 5.
pub const THRESHOLD: u32 = 3;

#[cw_serde]
pub struct InstantiateMsg { pub signers: Vec<String> } // exactly 5

#[cw_serde]
pub struct TxProposal {
    pub id: u64,
    pub recipient: String,
    pub amount: Uint128,
    pub denom: String,
    pub approvals: Vec<Addr>,
    pub queued_at: u64,   // when threshold reached (timelock start)
    pub executed: bool,
}

#[cw_serde]
pub enum ExecuteMsg {
    ProposeTransfer { recipient: String, amount: Uint128, denom: String },
    Approve { tx_id: u64 },
    ExecuteTransfer { tx_id: u64 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(TxProposal)] Tx { id: u64 },
    #[returns(Vec<String>)] Signers {},
}

#[cw_serde]
pub struct Config { pub signers: Vec<Addr>, pub next_id: u64 }
pub const CONFIG: Item<Config> = Item::new("ms_config");
pub const TXS: Map<u64, TxProposal> = Map::new("txs");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    if msg.signers.len() != 5 { return Err(cosmwasm_std::StdError::generic_err("need exactly 5 signers")); }
    let signers = msg.signers.iter().map(|s| deps.api.addr_validate(s)).collect::<StdResult<Vec<_>>>()?;
    CONFIG.save(deps.storage, &Config { signers, next_id: 1 })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::ProposeTransfer { recipient, amount, denom } => propose(deps, info, recipient, amount, denom),
        ExecuteMsg::Approve { tx_id } => approve(deps, env, info, tx_id),
        ExecuteMsg::ExecuteTransfer { tx_id } => exec(deps, env, tx_id),
    }
}

fn propose(deps: DepsMut, info: MessageInfo, recipient: String, amount: Uint128, denom: String) -> StdResult<Response> {
    let mut cfg = CONFIG.load(deps.storage)?;
    if !cfg.signers.contains(&info.sender) { return Err(cosmwasm_std::StdError::generic_err("not a signer")); }
    let id = cfg.next_id; cfg.next_id += 1; CONFIG.save(deps.storage, &cfg)?;
    TXS.save(deps.storage, id, &TxProposal { id, recipient, amount, denom, approvals: vec![info.sender], queued_at: 0, executed: false })?;
    Ok(Response::new().add_attribute("action", "propose").add_attribute("id", id.to_string()))
}

fn approve(deps: DepsMut, env: Env, info: MessageInfo, id: u64) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    if !cfg.signers.contains(&info.sender) { return Err(cosmwasm_std::StdError::generic_err("not a signer")); }
    let mut tx = TXS.load(deps.storage, id)?;
    if tx.approvals.contains(&info.sender) { return Err(cosmwasm_std::StdError::generic_err("already approved")); }
    tx.approvals.push(info.sender);
    if tx.approvals.len() as u32 >= THRESHOLD && tx.queued_at == 0 {
        tx.queued_at = env.block.time.seconds(); // start timelock
    }
    TXS.save(deps.storage, id, &tx)?;
    Ok(Response::new().add_attribute("action", "approve").add_attribute("id", id.to_string()))
}

fn exec(deps: DepsMut, env: Env, id: u64) -> StdResult<Response> {
    let mut tx = TXS.load(deps.storage, id)?;
    if tx.executed { return Err(cosmwasm_std::StdError::generic_err("already executed")); }
    if tx.queued_at == 0 { return Err(cosmwasm_std::StdError::generic_err("threshold not reached")); }
    // Enforce 72h timelock. NO exemption for emergency (whitepaper §6.3, §8.1).
    if env.block.time.seconds() < tx.queued_at + TIMELOCK_SECS {
        return Err(cosmwasm_std::StdError::generic_err("timelock active: wait 72h"));
    }
    tx.executed = true;
    TXS.save(deps.storage, id, &tx)?;
    let send = BankMsg::Send { to_address: tx.recipient.clone(), amount: vec![Coin { denom: tx.denom, amount: tx.amount }] };
    Ok(Response::new().add_message(send).add_attribute("action", "execute_transfer").add_attribute("id", id.to_string()))
}

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::Tx { id } => to_json_binary(&TXS.load(deps.storage, id)?),
        QueryMsg::Signers {} => to_json_binary(&CONFIG.load(deps.storage)?.signers.iter().map(|s| s.to_string()).collect::<Vec<_>>()),
    }
}
