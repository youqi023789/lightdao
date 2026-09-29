// governance v2 (native LIGHT): custodial staking with native `ulight` sent as msg funds.
// Stake locks real native LIGHT in the contract; Unstake returns it. DAO executor: a passed
// proposal can mint a sub-token, call any target contract, or migrate it (governance is admin).
//
// v2 additions (2026-10-05 migration payload):
//   * execute_proposal is permissioned: only the proposal's proposer, an owner-set executor
//     whitelist, or the DAO itself (governance calling governance via a passed proposal).
//   * proposal expiry: a passed proposal may be executed only until `end + EXPIRY_SECS`
//     (14 days); afterwards it errors "proposal expired". Expiry is exposed by query.
//   * migration-conflict guard: at most ONE pending (non-executed, non-voided, non-expired)
//     migrate proposal may exist at a time.
//   * MigrateMsg.void_ids marks proposals void; executing a voided proposal errors "voided".
//
// STORAGE COMPATIBILITY (migrate-safe, code 11 -> v2):
//   every pre-existing key AND every pre-existing value shape is byte-identical:
//     "gov_config" (Config), "proposals" (Proposal), "voted", "staked", "total_stakers".
//   All v2 state lives in NEW keys ("voided", "executors", "gov_owner") that code 11 simply
//   ignores, so a rollback migrate back to code 11 still parses 100% of the state.
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, BankMsg, Binary, Coin, Deps, DepsMut, Env, MessageInfo,
    Order, Response, StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:governance";
const CONTRACT_VERSION: &str = "2.0.0";
pub const DENOM: &str = "ulight";

/// A passed proposal stays executable for this long after its voting `end`, then expires.
pub const EXPIRY_SECS: u64 = 14 * 86400;

pub mod stfmsg {
    use cosmwasm_schema::cw_serde;
    use cosmwasm_std::Uint128;
    #[cw_serde]
    pub enum ExecuteMsg { CreateSubToken { symbol: String, investment_usd: Uint128 } }
}

#[cw_serde]
pub enum ProposalType { Micro, Acquisition, Vc, Major, Emergency }
impl ProposalType {
    pub fn min_pass(&self) -> u128 { match self { ProposalType::Micro=>55, ProposalType::Acquisition=>60, ProposalType::Vc=>60, ProposalType::Major=>66, ProposalType::Emergency=>75 } }
    pub fn default_secs(&self) -> u64 { match self { ProposalType::Emergency => 86400, _ => 7 * 86400 } }
}

#[cw_serde]
pub struct InstantiateMsg {
    pub subtoken_factory: String,
    pub proposal_min_stake: Uint128,
    pub voting_period_secs: Option<u64>,
}

/// NOTE: shape is frozen for migrate compatibility. v2 state (`voided`) lives in the separate
/// `VOIDED` map rather than as a field here, so `"proposals"` values written by code 11 and by
/// v2 are identical and both remain readable by either build (rollback-safe).
#[cw_serde]
pub struct Proposal {
    pub id: u64, pub proposer: Addr, pub ptype: ProposalType, pub title: String, pub description: String,
    pub yes_weight: Uint128, pub no_weight: Uint128, pub abstain_weight: Uint128,
    pub yes_addrs: u128, pub no_addrs: u128, pub abstain_addrs: u128,
    pub start: u64, pub end: u64, pub executed: bool,
    pub symbol: Option<String>, pub investment_usd: Option<Uint128>,
    pub target: Option<String>, pub call_msg: Option<Binary>, pub migrate_code_id: Option<u64>,
}

#[cw_serde]
pub enum VoteOption { Yes, No, Abstain }

#[cw_serde]
pub enum ExecuteMsg {
    /// Stake: attach native LIGHT as funds; amount = funds sent.
    Stake {},
    /// Unstake: return `amount` native LIGHT from custody.
    Unstake { amount: Uint128 },
    CreateProposal { ptype: ProposalType, title: String, description: String, symbol: Option<String>, investment_usd: Option<Uint128>, target: Option<String>, call_msg: Option<Binary>, migrate_code_id: Option<u64> },
    Vote { proposal_id: u64, option: VoteOption, bet: Uint128 },
    ExecuteProposal { proposal_id: u64 },
    /// Replace the executor whitelist. Callable by the configured owner, or by the DAO itself
    /// (governance calling governance as the payload of a passed proposal), so the whitelist
    /// stays governable even when no owner was set at migrate time.
    SetExecutors { executors: Vec<String> },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Proposal)] Proposal { id: u64 },
    /// Unchanged v1 semantics: every proposal with `executed == false` (voided and expired
    /// ones are still listed here so existing consumers keep working).
    #[returns(Vec<Proposal>)] ActiveProposals {},
    #[returns(Uint128)] StakedBalance { address: String },
    #[returns(Config)] Config {},
    /// v2: resolved lifecycle state of one proposal, including `expired` and `voided`.
    #[returns(ProposalState)] ProposalState { id: u64 },
    /// v2: every non-executed proposal together with its resolved lifecycle state.
    #[returns(Vec<ProposalView>)] ActiveProposalsDetailed {},
    /// v2: who may execute proposals, plus the expiry window.
    #[returns(GovPermissions)] Permissions {},
}

/// Shape frozen for migrate compatibility (see module header).
#[cw_serde]
pub struct Config { pub subtoken_factory: Addr, pub proposal_min_stake: Uint128, pub next_id: u64, pub voting_period_secs: Option<u64> }

// ---- pre-existing storage keys: names AND value shapes are unchanged ----
pub const CONFIG: Item<Config> = Item::new("gov_config");
pub const PROPOSALS: Map<u64, Proposal> = Map::new("proposals");
pub const VOTED: Map<(u64, &Addr), bool> = Map::new("voted");
pub const STAKED: Map<&Addr, Uint128> = Map::new("staked");
pub const TOTAL_STAKERS: Item<Uint128> = Item::new("total_stakers");

// ---- new v2-only keys (ignored by code 11, hence rollback-safe) ----
/// proposal id -> true when the proposal was voided (by migration `void_ids`).
pub const VOIDED: Map<u64, bool> = Map::new("voided");
/// Addresses, besides each proposal's own proposer, allowed to execute a passed proposal.
pub const EXECUTORS: Item<Vec<Addr>> = Item::new("executors");
/// Optional owner allowed to manage `EXECUTORS` directly.
pub const OWNER: Item<Addr> = Item::new("gov_owner");

#[cw_serde]
pub struct ProposalState {
    pub id: u64,
    pub start: u64,
    pub end: u64,
    /// `end + EXPIRY_SECS`: the last second at which the proposal can still be executed.
    pub expires_at: u64,
    pub executed: bool,
    pub voided: bool,
    pub expired: bool,
    pub voting_open: bool,
    pub is_migrate: bool,
    /// Whether the dual-dimension tally currently passes.
    pub passed: bool,
    /// True when nothing (permission aside) blocks execution right now.
    pub executable_now: bool,
}

#[cw_serde]
pub struct ProposalView { pub proposal: Proposal, pub state: ProposalState }

#[cw_serde]
pub struct GovPermissions {
    pub owner: Option<Addr>,
    pub executors: Vec<Addr>,
    pub expiry_secs: u64,
}

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        subtoken_factory: deps.api.addr_validate(&msg.subtoken_factory)?,
        proposal_min_stake: msg.proposal_min_stake, next_id: 1, voting_period_secs: msg.voting_period_secs,
    })?;
    TOTAL_STAKERS.save(deps.storage, &Uint128::zero())?;
    EXECUTORS.save(deps.storage, &vec![])?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Stake {} => stake(deps, info),
        ExecuteMsg::Unstake { amount } => unstake(deps, info, amount),
        ExecuteMsg::CreateProposal { ptype, title, description, symbol, investment_usd, target, call_msg, migrate_code_id } => create(deps, env, info, ptype, title, description, symbol, investment_usd, target, call_msg, migrate_code_id),
        ExecuteMsg::Vote { proposal_id, option, bet } => vote(deps, env, info, proposal_id, option, bet),
        ExecuteMsg::ExecuteProposal { proposal_id } => exec(deps, env, info, proposal_id),
        ExecuteMsg::SetExecutors { executors } => set_executors(deps, env, info, executors),
    }
}

fn stake(deps: DepsMut, info: MessageInfo) -> StdResult<Response> {
    let amount = info.funds.iter().find(|c| c.denom == DENOM).map(|c| c.amount).unwrap_or_default();
    if amount.is_zero() { return Err(StdError::generic_err("no native LIGHT attached to stake")); }
    let prev = STAKED.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if prev.is_zero() {
        let ts = TOTAL_STAKERS.may_load(deps.storage)?.unwrap_or_default();
        TOTAL_STAKERS.save(deps.storage, &(ts + Uint128::one()))?;
    }
    STAKED.save(deps.storage, &info.sender, &(prev + amount))?;
    Ok(Response::new().add_attribute("action", "stake").add_attribute("staker", info.sender).add_attribute("amount", amount))
}

/// Unstake refunds the caller's own native LIGHT from custody. (Mainnet code 11 routed this
/// through light_token allowance/transfer_from, whose message shape no longer parses; v2 keeps
/// the native path already present in the repo source.)
fn unstake(deps: DepsMut, info: MessageInfo, amount: Uint128) -> StdResult<Response> {
    if amount.is_zero() { return Err(StdError::generic_err("zero unstake")); }
    let prev = STAKED.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if prev < amount { return Err(StdError::generic_err("insufficient staked")); }
    let new = prev - amount;
    STAKED.save(deps.storage, &info.sender, &new)?;
    if new.is_zero() {
        let ts = TOTAL_STAKERS.may_load(deps.storage)?.unwrap_or_default();
        if !ts.is_zero() { TOTAL_STAKERS.save(deps.storage, &(ts - Uint128::one()))?; }
    }
    let send = BankMsg::Send { to_address: info.sender.to_string(), amount: vec![Coin { denom: DENOM.to_string(), amount }] };
    Ok(Response::new().add_message(send).add_attribute("action", "unstake").add_attribute("amount", amount))
}

/// A proposal is a "migrate proposal" when it carries `migrate_code_id`. In this contract that
/// is the only way a migration is expressed: `call_msg` is then used as the migrate payload of
/// the `WasmMsg::Migrate` emitted at execution time (see `exec`), never as a standalone migrate.
pub fn is_migrate_proposal(p: &Proposal) -> bool { p.migrate_code_id.is_some() }

/// Expiry rule: still executable at exactly `end + EXPIRY_SECS`, expired strictly after it.
pub fn is_expired(p: &Proposal, now: u64) -> bool {
    now > p.end.saturating_add(EXPIRY_SECS)
}

pub fn is_voided(deps: Deps, id: u64) -> StdResult<bool> {
    Ok(VOIDED.may_load(deps.storage, id)?.unwrap_or(false))
}

/// Execution permission (F4 fix): the proposal's proposer, an owner-set executor whitelist,
/// or the DAO itself (governance calling governance from a passed proposal's payload).
pub fn is_authorized(deps: Deps, env: &Env, sender: &Addr, p: &Proposal) -> StdResult<bool> {
    if *sender == p.proposer { return Ok(true); }
    if *sender == env.contract.address { return Ok(true); }
    let execs = EXECUTORS.may_load(deps.storage)?.unwrap_or_default();
    Ok(execs.iter().any(|a| a == sender))
}

/// Id of the currently pending migrate proposal, if any. "Pending" = not executed, not voided,
/// not expired. Voting-open migrate proposals count too: the guard exists to stop the
/// id9-vs-id10 race, which would be trivially bypassable by queueing several at once while
/// voting is still open.
pub fn find_pending_migrate(deps: Deps, now: u64, skip_id: u64) -> StdResult<Option<u64>> {
    for kv in PROPOSALS.range(deps.storage, None, None, Order::Ascending) {
        let (id, p) = kv?;
        if id == skip_id || p.executed { continue; }
        if !is_migrate_proposal(&p) { continue; }
        if is_voided(deps, id)? { continue; }
        if is_expired(&p, now) { continue; }
        return Ok(Some(id));
    }
    Ok(None)
}

#[allow(clippy::too_many_arguments)]
fn create(deps: DepsMut, env: Env, info: MessageInfo, ptype: ProposalType, title: String, description: String, symbol: Option<String>, investment_usd: Option<Uint128>, target: Option<String>, call_msg: Option<Binary>, migrate_code_id: Option<u64>) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    let staked = STAKED.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if staked < cfg.proposal_min_stake { return Err(StdError::generic_err("insufficient stake")); }
    if let Some(t) = target.as_ref() { deps.api.addr_validate(t)?; }
    if migrate_code_id.is_some() && target.is_none() { return Err(StdError::generic_err("migrate requires target")); }
    let now = env.block.time.seconds();
    // migration-conflict guard: at most one pending migrate proposal at a time.
    if migrate_code_id.is_some() {
        if let Some(other) = find_pending_migrate(deps.as_ref(), now, u64::MAX)? {
            return Err(StdError::generic_err(format!("another migrate proposal is pending (id {})", other)));
        }
    }
    let id = cfg.next_id;
    let period = cfg.voting_period_secs.unwrap_or_else(|| ptype.default_secs());
    PROPOSALS.save(deps.storage, id, &Proposal {
        id, proposer: info.sender.clone(), ptype, title: title.clone(), description,
        yes_weight: Uint128::zero(), no_weight: Uint128::zero(), abstain_weight: Uint128::zero(),
        yes_addrs: 0, no_addrs: 0, abstain_addrs: 0, start: now, end: now + period,
        executed: false, symbol, investment_usd, target, call_msg, migrate_code_id,
    })?;
    // next_id is only advanced once the proposal is really stored.
    CONFIG.save(deps.storage, &Config { next_id: id + 1, ..cfg })?;
    Ok(Response::new().add_attribute("action", "create_proposal").add_attribute("id", id.to_string()).add_attribute("title", title))
}

fn set_executors(deps: DepsMut, env: Env, info: MessageInfo, executors: Vec<String>) -> StdResult<Response> {
    let owner = OWNER.may_load(deps.storage)?;
    let is_owner = owner.as_ref().map(|o| *o == info.sender).unwrap_or(false);
    let is_self = info.sender == env.contract.address;
    if !is_owner && !is_self {
        return Err(StdError::generic_err("not authorized to set executors"));
    }
    let mut addrs = Vec::with_capacity(executors.len());
    for e in executors {
        let a = deps.api.addr_validate(&e)?;
        if !addrs.contains(&a) { addrs.push(a); }
    }
    EXECUTORS.save(deps.storage, &addrs)?;
    Ok(Response::new()
        .add_attribute("action", "set_executors")
        .add_attribute("count", addrs.len().to_string()))
}

fn vote(deps: DepsMut, env: Env, info: MessageInfo, id: u64, option: VoteOption, _bet: Uint128) -> StdResult<Response> {
    let mut p = PROPOSALS.load(deps.storage, id)?;
    let now = env.block.time.seconds();
    if now < p.start || now >= p.end { return Err(StdError::generic_err("voting not open")); }
    if VOTED.may_load(deps.storage, (id, &info.sender))?.unwrap_or(false) { return Err(StdError::generic_err("already voted")); }
    let w = STAKED.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if w.is_zero() { return Err(StdError::generic_err("no stake")); }
    match option {
        VoteOption::Yes => { p.yes_weight += w; p.yes_addrs += 1; }
        VoteOption::No => { p.no_weight += w; p.no_addrs += 1; }
        VoteOption::Abstain => { p.abstain_weight += w; p.abstain_addrs += 1; }
    }
    VOTED.save(deps.storage, (id, &info.sender), &true)?;
    PROPOSALS.save(deps.storage, id, &p)?;
    Ok(Response::new().add_attribute("action", "vote").add_attribute("id", id.to_string()))
}

pub fn passes(deps: Deps, p: &Proposal) -> StdResult<bool> {
    let total_w = p.yes_weight + p.no_weight + p.abstain_weight;
    if total_w.is_zero() { return Ok(false); }
    let yes_weight_pct = p.yes_weight * Uint128::from(100u128) / total_w;
    let voted_addrs = p.yes_addrs + p.no_addrs + p.abstain_addrs;
    let total_stakers = TOTAL_STAKERS.may_load(deps.storage)?.unwrap_or(Uint128::one());
    let turnout = Uint128::from(voted_addrs) * Uint128::from(100u128) / total_stakers.max(Uint128::one());
    let dynamic_min = if turnout < Uint128::from(50u128) { Uint128::from(50u128) + (Uint128::from(50u128) - turnout) } else { Uint128::from(50u128) };
    let required = dynamic_min.max(Uint128::from(p.ptype.min_pass()));
    let addr_yes_pct = if voted_addrs == 0 { Uint128::zero() } else { Uint128::from(p.yes_addrs) * Uint128::from(100u128) / Uint128::from(voted_addrs) };
    Ok(yes_weight_pct >= required && addr_yes_pct >= required)
}

fn exec(deps: DepsMut, env: Env, info: MessageInfo, id: u64) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    let mut p = PROPOSALS.load(deps.storage, id)?;
    let now = env.block.time.seconds();
    if is_voided(deps.as_ref(), id)? { return Err(StdError::generic_err("voided")); }
    if p.executed { return Err(StdError::generic_err("already executed")); }
    if !is_authorized(deps.as_ref(), &env, &info.sender, &p)? {
        return Err(StdError::generic_err("not authorized to execute proposal"));
    }
    if now < p.end { return Err(StdError::generic_err("voting not ended")); }
    if is_expired(&p, now) { return Err(StdError::generic_err("proposal expired")); }
    if !passes(deps.as_ref(), &p)? { return Err(StdError::generic_err("proposal did not pass")); }
    p.executed = true; PROPOSALS.save(deps.storage, id, &p)?;
    let mut resp = Response::new().add_attribute("action", "execute_proposal").add_attribute("id", id.to_string());
    if let (Some(symbol), Some(investment_usd)) = (p.symbol.clone(), p.investment_usd) {
        let msg = WasmMsg::Execute { contract_addr: cfg.subtoken_factory.to_string(), msg: to_json_binary(&stfmsg::ExecuteMsg::CreateSubToken { symbol: symbol.clone(), investment_usd })?, funds: vec![] };
        resp = resp.add_message(msg).add_attribute("create_subtoken", symbol);
    }
    if let Some(target) = p.target.clone() {
        let target_addr = deps.api.addr_validate(&target)?;
        if let Some(code_id) = p.migrate_code_id {
            let m = p.call_msg.clone().unwrap_or_else(|| Binary::from(b"{}".to_vec()));
            resp = resp.add_message(WasmMsg::Migrate { contract_addr: target_addr.to_string(), new_code_id: code_id, msg: m }).add_attribute("migrate_target", target);
        } else if let Some(call) = p.call_msg.clone() {
            resp = resp.add_message(WasmMsg::Execute { contract_addr: target_addr.to_string(), msg: call, funds: vec![] }).add_attribute("call_target", target);
        }
    }
    Ok(resp)
}

/// Resolved lifecycle state used by the v2 queries.
pub fn proposal_state(deps: Deps, env: &Env, p: &Proposal) -> StdResult<ProposalState> {
    let now = env.block.time.seconds();
    let voided = is_voided(deps, p.id)?;
    let expired = is_expired(p, now);
    let voting_open = now >= p.start && now < p.end;
    let passed = passes(deps, p)?;
    Ok(ProposalState {
        id: p.id,
        start: p.start,
        end: p.end,
        expires_at: p.end.saturating_add(EXPIRY_SECS),
        executed: p.executed,
        voided,
        expired,
        voting_open,
        is_migrate: is_migrate_proposal(p),
        passed,
        executable_now: !p.executed && !voided && !expired && !voting_open && passed,
    })
}

#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::Proposal { id } => to_json_binary(&PROPOSALS.load(deps.storage, id)?),
        QueryMsg::ActiveProposals {} => {
            let mut out = vec![];
            for kv in PROPOSALS.range(deps.storage, None, None, Order::Ascending) { let (_, p) = kv?; if !p.executed { out.push(p); } }
            to_json_binary(&out)
        }
        QueryMsg::StakedBalance { address } => { let a = deps.api.addr_validate(&address)?; to_json_binary(&STAKED.may_load(deps.storage, &a)?.unwrap_or_default()) }
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
        QueryMsg::ProposalState { id } => {
            let p = PROPOSALS.load(deps.storage, id)?;
            to_json_binary(&proposal_state(deps, &env, &p)?)
        }
        QueryMsg::ActiveProposalsDetailed {} => {
            let mut out = vec![];
            for kv in PROPOSALS.range(deps.storage, None, None, Order::Ascending) {
                let (_, p) = kv?;
                if p.executed { continue; }
                let state = proposal_state(deps, &env, &p)?;
                out.push(ProposalView { proposal: p, state });
            }
            to_json_binary(&out)
        }
        QueryMsg::Permissions {} => to_json_binary(&GovPermissions {
            owner: OWNER.may_load(deps.storage)?,
            executors: EXECUTORS.may_load(deps.storage)?.unwrap_or_default(),
            expiry_secs: EXPIRY_SECS,
        }),
    }
}

#[cw_serde]
pub struct MigrateMsg {
    /// Proposal ids to mark void as part of this migration. The mainnet 2026-10-05 list
    /// `[2,5,6,7,9]` is supplied by the x/gov proposal payload, NOT hardcoded here.
    /// Ids that do not exist are skipped, so a stale id can never fail the migration tx.
    #[serde(default)]
    pub void_ids: Vec<u64>,
    /// Optional override of the voting period. Omitted/`None` PRESERVES the current value
    /// (the previous build blindly overwrote it with `None`).
    #[serde(default)]
    pub voting_period_secs: Option<u64>,
    /// Optional owner permitted to manage the executor whitelist directly.
    #[serde(default)]
    pub owner: Option<String>,
    /// Optional initial executor whitelist (always in addition to each proposal's proposer).
    #[serde(default)]
    pub executors: Option<Vec<String>>,
}

#[entry_point]
pub fn migrate(deps: DepsMut, _env: Env, msg: MigrateMsg) -> StdResult<Response> {
    // CONFIG.load fails loudly if this code is pointed at a foreign contract's state.
    let cfg = CONFIG.load(deps.storage)?;
    let vps = msg.voting_period_secs; // Option<u64> is Copy: no partial move of `msg`
    if vps.is_some() {
        CONFIG.save(deps.storage, &Config { voting_period_secs: vps, ..cfg })?;
    }

    let mut voided_n: u64 = 0;
    let mut skipped_n: u64 = 0;
    for id in msg.void_ids.iter() {
        if PROPOSALS.may_load(deps.storage, *id)?.is_some() {
            VOIDED.save(deps.storage, *id, &true)?;
            voided_n += 1;
        } else {
            skipped_n += 1;
        }
    }

    if let Some(o) = msg.owner.as_ref() {
        OWNER.save(deps.storage, &deps.api.addr_validate(o)?)?;
    }
    if let Some(list) = msg.executors.as_ref() {
        let mut addrs = Vec::with_capacity(list.len());
        for e in list {
            let a = deps.api.addr_validate(e)?;
            if !addrs.contains(&a) { addrs.push(a); }
        }
        EXECUTORS.save(deps.storage, &addrs)?;
    } else if EXECUTORS.may_load(deps.storage)?.is_none() {
        // upgrading from code 11, which never wrote this key
        EXECUTORS.save(deps.storage, &vec![])?;
    }

    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    Ok(Response::new()
        .add_attribute("action", "migrate")
        .add_attribute("voided", voided_n.to_string())
        .add_attribute("void_ids_skipped", skipped_n.to_string())
        .add_attribute("voting_period_secs", format!("{:?}", vps)))
}

#[cfg(test)]
#[allow(deprecated)] // cosmwasm-std 2.x deprecates testing::mock_info in favour of message_info
mod tests {
    use super::*;
    use cosmwasm_std::testing::{mock_dependencies, mock_env, mock_info, MockApi, MockQuerier};
    use cosmwasm_std::{coins, from_json, CosmosMsg, MemoryStorage, OwnedDeps, Storage, Timestamp};

    type TestDeps = OwnedDeps<MemoryStorage, MockApi, MockQuerier>;

    fn prop(yes: u128, no: u128, ab: u128, ya: u128, na: u128, aa: u128, pt: ProposalType) -> Proposal {
        Proposal { id:1, proposer: Addr::unchecked("p"), ptype: pt, title:"t".into(), description:"d".into(),
            yes_weight: Uint128::new(yes), no_weight: Uint128::new(no), abstain_weight: Uint128::new(ab),
            yes_addrs: ya, no_addrs: na, abstain_addrs: aa, start:0, end:100, executed:false,
            symbol:None, investment_usd:None, target:None, call_msg:None, migrate_code_id:None }
    }

    // ---------------- pre-existing tally tests (unchanged) ----------------
    #[test] fn no_votes_fails() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::one()).unwrap(); assert!(!passes(d.as_ref(), &prop(0,0,0,0,0,0,ProposalType::Micro)).unwrap()); }
    #[test] fn unanimous_passes() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::one()).unwrap(); assert!(passes(d.as_ref(), &prop(100,0,0,1,0,0,ProposalType::Micro)).unwrap()); }
    #[test] fn majority_no_fails() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(2)).unwrap(); assert!(!passes(d.as_ref(), &prop(40,60,0,1,1,0,ProposalType::Micro)).unwrap()); }
    #[test] fn low_turnout_raises_bar() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(10)).unwrap(); assert!(!passes(d.as_ref(), &prop(80,20,0,1,1,0,ProposalType::Micro)).unwrap()); }
    #[test] fn emergency_75() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(4)).unwrap();
        assert!(!passes(d.as_ref(), &prop(70,30,0,1,3,0,ProposalType::Emergency)).unwrap());
        assert!(passes(d.as_ref(), &prop(80,20,0,3,1,0,ProposalType::Emergency)).unwrap()); }

    // ---------------- harness ----------------
    const T0: u64 = 1_790_000_000;
    const PERIOD: u64 = 7 * 86400;
    const SELF: &str = "gov_self";

    fn env_at(secs: u64) -> Env {
        let mut e = mock_env();
        e.block.time = Timestamp::from_seconds(secs);
        e
    }

    /// instantiate with a 7-day voting period and zero proposal threshold.
    fn setup() -> (TestDeps, Env, Addr, Addr, Addr) {
        let mut deps = mock_dependencies();
        // addresses from the SAME MockApi instance so addr_validate() accepts them
        let factory = deps.api.addr_make("factory");
        let proposer = deps.api.addr_make("proposer");
        let outsider = deps.api.addr_make("outsider");
        let env = env_at(T0);
        instantiate(deps.as_mut(), env.clone(), mock_info(proposer.as_str(), &[]), InstantiateMsg {
            subtoken_factory: factory.to_string(),
            proposal_min_stake: Uint128::zero(),
            voting_period_secs: Some(PERIOD),
        }).unwrap();
        (deps, env, proposer, outsider, factory)
    }

    fn info_of(who: &Addr, funds: &[Coin]) -> MessageInfo { mock_info(who.as_str(), funds) }

    fn do_stake(deps: &mut TestDeps, env: &Env, who: &Addr, amount: u128) -> StdResult<Response> {
        execute(deps.as_mut(), env.clone(), info_of(who, &coins(amount, DENOM)), ExecuteMsg::Stake {})
    }

    fn do_create(deps: &mut TestDeps, env: &Env, who: &Addr, ptype: ProposalType, migrate_code_id: Option<u64>, target: Option<&Addr>) -> StdResult<Response> {
        execute(deps.as_mut(), env.clone(), info_of(who, &[]), ExecuteMsg::CreateProposal {
            ptype, title: "t".into(), description: "d".into(),
            symbol: None, investment_usd: None,
            target: target.map(|t| t.to_string()),
            call_msg: migrate_code_id.map(|_| Binary::from(b"{}".to_vec())),
            migrate_code_id,
        })
    }

    fn id_of(r: &Response) -> u64 {
        r.attributes.iter().find(|a| a.key == "id").unwrap().value.parse().unwrap()
    }

    fn create_prop(deps: &mut TestDeps, env: &Env, who: &Addr, migrate_code_id: Option<u64>, target: Option<&Addr>) -> u64 {
        id_of(&do_create(deps, env, who, ProposalType::Micro, migrate_code_id, target).unwrap())
    }

    fn create_migrate(deps: &mut TestDeps, env: &Env, who: &Addr, code: Option<u64>, target: Option<&Addr>) -> StdResult<Response> {
        do_create(deps, env, who, ProposalType::Major, code, target)
    }

    /// Cast a single yes vote and assert the tally now passes.
    fn pass_it(deps: &mut TestDeps, env: &Env, who: &Addr, id: u64) {
        execute(deps.as_mut(), env.clone(), info_of(who, &[]), ExecuteMsg::Vote { proposal_id: id, option: VoteOption::Yes, bet: Uint128::zero() }).unwrap();
        let p = PROPOSALS.load(&deps.storage, id).unwrap();
        assert!(passes(deps.as_ref(), &p).unwrap(), "test setup: proposal {} should pass", id);
    }

    fn do_exec(deps: &mut TestDeps, env: &Env, who: &Addr, id: u64) -> StdResult<Response> {
        execute(deps.as_mut(), env.clone(), info_of(who, &[]), ExecuteMsg::ExecuteProposal { proposal_id: id })
    }

    fn q_state(deps: &TestDeps, env: &Env, id: u64) -> ProposalState {
        from_json(&query(deps.as_ref(), env.clone(), QueryMsg::ProposalState { id }).unwrap()).unwrap()
    }

    fn err_of(res: StdResult<Response>) -> String { res.unwrap_err().to_string() }

    // ---------------- (1) native stake / unstake round-trip ----------------
    #[test]
    fn native_stake_unstake_roundtrip() {
        let (mut deps, env, who, _outsider, _f) = setup();

        // stake with native funds attached to the message
        do_stake(&mut deps, &env, &who, 5_000).unwrap();
        assert_eq!(STAKED.load(&deps.storage, &who).unwrap(), Uint128::new(5_000));
        assert_eq!(TOTAL_STAKERS.load(&deps.storage).unwrap(), Uint128::one());

        // topping up must not double-count the staker
        do_stake(&mut deps, &env, &who, 2_500).unwrap();
        assert_eq!(STAKED.load(&deps.storage, &who).unwrap(), Uint128::new(7_500));
        assert_eq!(TOTAL_STAKERS.load(&deps.storage).unwrap(), Uint128::one());

        // unstake refunds native LIGHT of the right denom to the right address
        let r = execute(deps.as_mut(), env.clone(), info_of(&who, &[]), ExecuteMsg::Unstake { amount: Uint128::new(3_000) }).unwrap();
        assert_eq!(r.messages.len(), 1, "unstake must emit exactly one bank send");
        match &r.messages[0].msg {
            CosmosMsg::Bank(BankMsg::Send { to_address, amount }) => {
                assert_eq!(to_address, who.as_str());
                assert_eq!(amount.len(), 1);
                assert_eq!(amount[0].denom, DENOM);
                assert_eq!(amount[0].amount, Uint128::new(3_000));
            }
            other => panic!("expected BankMsg::Send, got {:?}", other),
        }
        assert_eq!(STAKED.load(&deps.storage, &who).unwrap(), Uint128::new(4_500));
        assert_eq!(TOTAL_STAKERS.load(&deps.storage).unwrap(), Uint128::one());

        // full unstake decrements the staker count
        execute(deps.as_mut(), env.clone(), info_of(&who, &[]), ExecuteMsg::Unstake { amount: Uint128::new(4_500) }).unwrap();
        assert_eq!(STAKED.load(&deps.storage, &who).unwrap(), Uint128::zero());
        assert_eq!(TOTAL_STAKERS.load(&deps.storage).unwrap(), Uint128::zero());

        // guards
        assert!(err_of(execute(deps.as_mut(), env.clone(), info_of(&who, &[]), ExecuteMsg::Unstake { amount: Uint128::new(1) })).contains("insufficient staked"));
        assert!(err_of(execute(deps.as_mut(), env.clone(), info_of(&who, &[]), ExecuteMsg::Unstake { amount: Uint128::zero() })).contains("zero unstake"));
        assert!(err_of(do_stake(&mut deps, &env, &who, 0)).contains("no native LIGHT attached to stake"));
        // wrong denom is not credited
        assert!(err_of(execute(deps.as_mut(), env.clone(), info_of(&who, &coins(999, "stake")), ExecuteMsg::Stake {})).contains("no native LIGHT attached to stake"));
        assert_eq!(STAKED.load(&deps.storage, &who).unwrap(), Uint128::zero());

        // query round-trip
        let bal: Uint128 = from_json(&query(deps.as_ref(), env.clone(), QueryMsg::StakedBalance { address: who.to_string() }).unwrap()).unwrap();
        assert_eq!(bal, Uint128::zero());
    }

    // ---------------- (2) execute_proposal permission ----------------
    #[test]
    fn execute_restricted_to_proposer_or_whitelisted_executor() {
        let (mut deps, env, proposer, outsider, factory) = setup();
        do_stake(&mut deps, &env, &outsider, 1_000).unwrap();
        do_stake(&mut deps, &env, &proposer, 1_000).unwrap();
        let id = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        pass_it(&mut deps, &env, &proposer, id);
        let after = env_at(T0 + PERIOD + 1);

        // a) a random address is rejected and nothing is marked executed
        let e = err_of(do_exec(&mut deps, &after, &outsider, id));
        assert!(e.contains("not authorized to execute proposal"), "got: {}", e);
        assert!(!PROPOSALS.load(&deps.storage, id).unwrap().executed, "rejected call must not mark executed");

        // b) the whitelist itself is not publicly writable
        let e = err_of(execute(deps.as_mut(), after.clone(), info_of(&outsider, &[]), ExecuteMsg::SetExecutors { executors: vec![outsider.to_string()] }));
        assert!(e.contains("not authorized to set executors"), "got: {}", e);

        // c) the proposer may execute; a second attempt is "already executed"
        do_exec(&mut deps, &after, &proposer, id).unwrap();
        assert!(PROPOSALS.load(&deps.storage, id).unwrap().executed);
        assert!(err_of(do_exec(&mut deps, &after, &proposer, id)).contains("already executed"));

        // d) the DAO can whitelist an executor by calling itself
        let mut self_env = after.clone();
        self_env.contract.address = Addr::unchecked(SELF);
        execute(deps.as_mut(), self_env.clone(), mock_info(SELF, &[]), ExecuteMsg::SetExecutors { executors: vec![outsider.to_string()] }).unwrap();
        let perms: GovPermissions = from_json(&query(deps.as_ref(), after.clone(), QueryMsg::Permissions {}).unwrap()).unwrap();
        assert_eq!(perms.executors, vec![outsider.clone()]);
        assert_eq!(perms.expiry_secs, EXPIRY_SECS);
        assert_eq!(perms.owner, None);

        // e) the whitelisted executor may now execute a proposal it did not propose
        let id2 = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        pass_it(&mut deps, &env, &proposer, id2);
        do_exec(&mut deps, &after, &outsider, id2).unwrap();
        assert!(PROPOSALS.load(&deps.storage, id2).unwrap().executed);

        // f) clearing the whitelist re-locks execution
        execute(deps.as_mut(), self_env, mock_info(SELF, &[]), ExecuteMsg::SetExecutors { executors: vec![] }).unwrap();
        let id3 = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        pass_it(&mut deps, &env, &proposer, id3);
        assert!(err_of(do_exec(&mut deps, &after, &outsider, id3)).contains("not authorized"));
    }

    // ---------------- (3) proposal expiry ----------------
    #[test]
    fn proposal_expires_after_end_plus_14_days() {
        let (mut deps, env, proposer, _outsider, factory) = setup();
        do_stake(&mut deps, &env, &proposer, 1_000).unwrap();
        let id = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        pass_it(&mut deps, &env, &proposer, id);
        let p = PROPOSALS.load(&deps.storage, id).unwrap();
        assert_eq!(p.end, T0 + PERIOD);
        let deadline = p.end + EXPIRY_SECS;
        assert_eq!(deadline, T0 + 21 * 86400);

        // before the deadline: not expired
        assert!(!q_state(&deps, &env_at(deadline - 1), id).expired);
        // boundary: still executable AT end + 14 days
        assert!(!q_state(&deps, &env_at(deadline), id).expired);
        // strictly after: expired, and the query says so
        let st = q_state(&deps, &env_at(deadline + 1), id);
        assert!(st.expired, "query must expose expired state");
        assert!(!st.executable_now);
        assert_eq!(st.expires_at, deadline);

        let e = err_of(do_exec(&mut deps, &env_at(deadline + 1), &proposer, id));
        assert!(e.contains("proposal expired"), "got: {}", e);
        assert!(!PROPOSALS.load(&deps.storage, id).unwrap().executed);

        // the very same proposal succeeds inside the window -> the error is purely time-based
        do_exec(&mut deps, &env_at(deadline), &proposer, id).unwrap();
        assert!(PROPOSALS.load(&deps.storage, id).unwrap().executed);
    }

    #[test]
    fn expired_migrate_proposal_frees_the_conflict_guard() {
        let (mut deps, env, proposer, _outsider, factory) = setup();
        do_stake(&mut deps, &env, &proposer, 1_000).unwrap();
        let m1 = create_prop(&mut deps, &env, &proposer, Some(9), Some(&factory));
        assert!(err_of(create_migrate(&mut deps, &env, &proposer, Some(12), Some(&factory))).contains("another migrate proposal is pending"));

        let far = env_at(T0 + 21 * 86400 + 10);
        assert!(q_state(&deps, &far, m1).expired);
        let m2 = id_of(&create_migrate(&mut deps, &far, &proposer, Some(12), Some(&factory)).unwrap());
        assert!(m2 > m1, "an expired migrate proposal must free the guard");
    }

    // ---------------- (4) migration-conflict guard ----------------
    #[test]
    fn migration_conflict_guard_allows_only_one_pending_migrate() {
        let (mut deps, env, proposer, _outsider, factory) = setup();
        do_stake(&mut deps, &env, &proposer, 1_000).unwrap();

        // first migrate proposal is accepted
        let a = create_migrate(&mut deps, &env, &proposer, Some(9), Some(&factory)).unwrap();
        let a_id = id_of(&a);
        assert_eq!(a_id, 1);

        // a second concurrent migrate proposal is rejected and names the blocker
        let e = err_of(create_migrate(&mut deps, &env, &proposer, Some(12), Some(&factory)));
        assert!(e.contains("another migrate proposal is pending"), "got: {}", e);
        assert!(e.contains(&format!("id {}", a_id)), "error should name the blocking proposal: {}", e);
        // the rejection must not consume an id nor write a proposal
        assert_eq!(CONFIG.load(&deps.storage).unwrap().next_id, 2);
        assert!(PROPOSALS.may_load(&deps.storage, 2).unwrap().is_none());

        // non-migrate proposals are unaffected by the guard
        let b = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        assert_eq!(b, 2);
        // the pre-existing "migrate requires target" rule still fires first
        assert!(err_of(create_migrate(&mut deps, &env, &proposer, Some(12), None)).contains("migrate requires target"));

        // executing the pending migrate proposal frees the guard
        pass_it(&mut deps, &env, &proposer, a_id);
        let after = env_at(T0 + PERIOD + 1);
        let r = do_exec(&mut deps, &after, &proposer, a_id).unwrap();
        assert!(matches!(r.messages[0].msg, CosmosMsg::Wasm(WasmMsg::Migrate { new_code_id: 9, .. })));
        assert_eq!(id_of(&create_migrate(&mut deps, &env, &proposer, Some(12), Some(&factory)).unwrap()), 3);

        // voiding the pending one frees the guard too
        VOIDED.save(deps.as_mut().storage, 3, &true).unwrap();
        assert_eq!(id_of(&create_migrate(&mut deps, &env, &proposer, Some(13), Some(&factory)).unwrap()), 4);
    }

    // ---------------- (5) MigrateMsg.void_ids ----------------
    #[test]
    fn migrate_voids_listed_ids_and_blocks_execution() {
        let (mut deps, env, proposer, _outsider, factory) = setup();
        do_stake(&mut deps, &env, &proposer, 1_000).unwrap();
        let mut ids = vec![];
        for _ in 0..5u64 { ids.push(create_prop(&mut deps, &env, &proposer, None, Some(&factory))); }
        assert_eq!(ids, vec![1, 2, 3, 4, 5]);
        pass_it(&mut deps, &env, &proposer, 1);
        pass_it(&mut deps, &env, &proposer, 2);
        pass_it(&mut deps, &env, &proposer, 5);

        // mainnet-shaped payload: {"void_ids":[2,5,6,7,9]}
        let msg: MigrateMsg = from_json(br#"{"void_ids":[2,5,6,7,9]}"#).unwrap();
        assert_eq!(msg.void_ids, vec![2, 5, 6, 7, 9]);
        assert_eq!(msg.voting_period_secs, None);
        let r = migrate(deps.as_mut(), env.clone(), msg).unwrap();
        let attr = |k: &str| r.attributes.iter().find(|a| a.key == k).unwrap().value.clone();
        // 2,5,6,7,9 -> 2 and 5 exist here, 6/7/9 do not => skipped, not fatal
        assert_eq!(attr("voided"), "2");
        assert_eq!(attr("void_ids_skipped"), "3");
        assert!(VOIDED.load(&deps.storage, 2).unwrap());
        assert!(VOIDED.load(&deps.storage, 5).unwrap());
        assert!(VOIDED.may_load(&deps.storage, 1).unwrap().is_none());

        // a voided proposal can no longer be executed, not even by its proposer
        let after = env_at(T0 + PERIOD + 1);
        let e = err_of(do_exec(&mut deps, &after, &proposer, 2));
        assert!(e.contains("voided"), "got: {}", e);
        assert!(!PROPOSALS.load(&deps.storage, 2).unwrap().executed);

        // query exposes the voided flag; untouched proposals stay executable
        let st = q_state(&deps, &after, 2);
        assert!(st.voided && !st.executable_now);
        assert!(!q_state(&deps, &after, 1).voided);
        do_exec(&mut deps, &after, &proposer, 1).unwrap();

        // stale/unknown ids are skipped
        let r = migrate(deps.as_mut(), env.clone(), from_json(br#"{"void_ids":[999,1000]}"#).unwrap()).unwrap();
        assert_eq!(r.attributes.iter().find(|a| a.key == "voided").unwrap().value, "0");
        assert_eq!(r.attributes.iter().find(|a| a.key == "void_ids_skipped").unwrap().value, "2");
        // idempotent: re-voiding is a no-op, not an error
        migrate(deps.as_mut(), env, from_json(br#"{"void_ids":[2]}"#).unwrap()).unwrap();
        assert!(VOIDED.load(&deps.storage, 2).unwrap());
    }

    // ---------------- migrate compatibility: keys, shapes and state survive ----------------
    #[test]
    fn migrate_preserves_storage_keys_and_state() {
        let (mut deps, env, proposer, outsider, factory) = setup();
        do_stake(&mut deps, &env, &proposer, 5_000_000_000_000u128).unwrap();
        do_stake(&mut deps, &env, &outsider, 1_234).unwrap();
        let id = create_prop(&mut deps, &env, &proposer, Some(9), Some(&factory));
        pass_it(&mut deps, &env, &proposer, id);

        // every pre-existing storage namespace must be present BEFORE the migration
        let before_keys: Vec<String> = deps.storage
            .range(None, None, Order::Ascending)
            .map(|(k, _)| String::from_utf8_lossy(&k).to_string())
            .collect();
        for needle in ["gov_config", "proposals", "staked", "total_stakers", "voted"] {
            assert!(before_keys.iter().any(|k| k.contains(needle)), "missing storage namespace {}", needle);
        }
        // and the "proposals" value bytes must be byte-identical after the migration
        let raw_before: Vec<u8> = deps.storage
            .range(None, None, Order::Ascending)
            .find(|(k, _)| k.windows(9).any(|w| w == b"proposals"))
            .map(|(_, v)| v.to_vec())
            .expect("a proposals record must exist");

        let cfg_before = CONFIG.load(&deps.storage).unwrap();
        migrate(deps.as_mut(), env.clone(), from_json(br#"{"void_ids":[2,5,6,7,9]}"#).unwrap()).unwrap();

        // staked balances unchanged, address by address
        assert_eq!(STAKED.load(&deps.storage, &proposer).unwrap(), Uint128::new(5_000_000_000_000u128));
        assert_eq!(STAKED.load(&deps.storage, &outsider).unwrap(), Uint128::new(1_234));
        assert_eq!(TOTAL_STAKERS.load(&deps.storage).unwrap(), Uint128::new(2));

        // proposal payload untouched (frozen struct shape => code 11 can still parse it)
        let p_after = PROPOSALS.load(&deps.storage, id).unwrap();
        assert_eq!(p_after.yes_weight, Uint128::new(5_000_000_000_000u128));
        assert!(!p_after.executed);
        assert_eq!(p_after.migrate_code_id, Some(9));
        let raw_after: Vec<u8> = deps.storage
            .range(None, None, Order::Ascending)
            .find(|(k, _)| k.windows(9).any(|w| w == b"proposals"))
            .map(|(_, v)| v.to_vec())
            .expect("a proposals record must exist");
        assert_eq!(raw_before, raw_after, "\"proposals\" value bytes must be unchanged by migrate");

        // config preserved, including voting_period_secs (NOT clobbered to null)
        let cfg_after = CONFIG.load(&deps.storage).unwrap();
        assert_eq!(cfg_after.subtoken_factory, cfg_before.subtoken_factory);
        assert_eq!(cfg_after.proposal_min_stake, cfg_before.proposal_min_stake);
        assert_eq!(cfg_after.next_id, cfg_before.next_id);
        assert_eq!(cfg_after.voting_period_secs, Some(PERIOD));
        // an explicit override still works
        migrate(deps.as_mut(), env.clone(), from_json(br#"{"void_ids":[],"voting_period_secs":30}"#).unwrap()).unwrap();
        assert_eq!(CONFIG.load(&deps.storage).unwrap().voting_period_secs, Some(30));

        // ActiveProposals semantics unchanged: still lists non-executed proposals
        let active: Vec<Proposal> = from_json(&query(deps.as_ref(), env.clone(), QueryMsg::ActiveProposals {}).unwrap()).unwrap();
        assert!(active.iter().any(|p| p.id == id));
        // the detailed view carries the v2 flags
        let detailed: Vec<ProposalView> = from_json(&query(deps.as_ref(), env, QueryMsg::ActiveProposalsDetailed {}).unwrap()).unwrap();
        let v = detailed.iter().find(|d| d.proposal.id == id).unwrap();
        assert!(!v.state.voided && !v.state.expired);
    }

    #[test]
    fn migrate_sets_owner_and_executors() {
        let (mut deps, env, proposer, outsider, factory) = setup();
        let _ = create_prop(&mut deps, &env, &proposer, None, Some(&factory));
        let payload = format!(r#"{{"void_ids":[],"owner":"{}","executors":["{}","{}"]}}"#, proposer, outsider, outsider);
        migrate(deps.as_mut(), env.clone(), from_json(payload.as_bytes()).unwrap()).unwrap();
        assert_eq!(OWNER.load(&deps.storage).unwrap(), proposer);
        // duplicate executors collapse
        let perms: GovPermissions = from_json(&query(deps.as_ref(), env.clone(), QueryMsg::Permissions {}).unwrap()).unwrap();
        assert_eq!(perms.executors, vec![outsider.clone()]);
        assert_eq!(perms.owner, Some(proposer.clone()));
        // the owner may now manage the whitelist
        execute(deps.as_mut(), env.clone(), info_of(&proposer, &[]), ExecuteMsg::SetExecutors { executors: vec![] }).unwrap();
        let perms: GovPermissions = from_json(&query(deps.as_ref(), env.clone(), QueryMsg::Permissions {}).unwrap()).unwrap();
        assert!(perms.executors.is_empty());
        // an invalid address is rejected rather than silently whitelisted
        assert!(migrate(deps.as_mut(), env, from_json(br#"{"void_ids":[],"executors":["not a valid address"]}"#).unwrap()).is_err());
    }
}
