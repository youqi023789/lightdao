// governance (native LIGHT): custodial staking with native `ulight` sent as msg funds.
// Stake locks real native LIGHT in the contract; Unstake returns it. DAO executor: a passed
// proposal can mint a sub-token, call any target contract, or migrate it (governance is admin).
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, BankMsg, Binary, Coin, Deps, DepsMut, Env, MessageInfo,
    Response, StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:governance";
const CONTRACT_VERSION: &str = "1.0.0";
pub const DENOM: &str = "ulight";

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
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(Proposal)] Proposal { id: u64 },
    #[returns(Vec<Proposal>)] ActiveProposals {},
    #[returns(Uint128)] StakedBalance { address: String },
    #[returns(Config)] Config {},
}

#[cw_serde]
pub struct Config { pub subtoken_factory: Addr, pub proposal_min_stake: Uint128, pub next_id: u64, pub voting_period_secs: Option<u64> }
pub const CONFIG: Item<Config> = Item::new("gov_config");
pub const PROPOSALS: Map<u64, Proposal> = Map::new("proposals");
pub const VOTED: Map<(u64, &Addr), bool> = Map::new("voted");
pub const STAKED: Map<&Addr, Uint128> = Map::new("staked");
pub const TOTAL_STAKERS: Item<Uint128> = Item::new("total_stakers");

#[entry_point]
pub fn instantiate(deps: DepsMut, _e: Env, _i: MessageInfo, msg: InstantiateMsg) -> StdResult<Response> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    CONFIG.save(deps.storage, &Config {
        subtoken_factory: deps.api.addr_validate(&msg.subtoken_factory)?,
        proposal_min_stake: msg.proposal_min_stake, next_id: 1, voting_period_secs: msg.voting_period_secs,
    })?;
    TOTAL_STAKERS.save(deps.storage, &Uint128::zero())?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> StdResult<Response> {
    match msg {
        ExecuteMsg::Stake {} => stake(deps, info),
        ExecuteMsg::Unstake { amount } => unstake(deps, info, amount),
        ExecuteMsg::CreateProposal { ptype, title, description, symbol, investment_usd, target, call_msg, migrate_code_id } => create(deps, env, info, ptype, title, description, symbol, investment_usd, target, call_msg, migrate_code_id),
        ExecuteMsg::Vote { proposal_id, option, bet } => vote(deps, env, info, proposal_id, option, bet),
        ExecuteMsg::ExecuteProposal { proposal_id } => exec(deps, env, proposal_id),
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

#[allow(clippy::too_many_arguments)]
fn create(deps: DepsMut, env: Env, info: MessageInfo, ptype: ProposalType, title: String, description: String, symbol: Option<String>, investment_usd: Option<Uint128>, target: Option<String>, call_msg: Option<Binary>, migrate_code_id: Option<u64>) -> StdResult<Response> {
    let mut cfg = CONFIG.load(deps.storage)?;
    let staked = STAKED.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if staked < cfg.proposal_min_stake { return Err(StdError::generic_err("insufficient stake")); }
    if let Some(t) = target.as_ref() { deps.api.addr_validate(t)?; }
    if migrate_code_id.is_some() && target.is_none() { return Err(StdError::generic_err("migrate requires target")); }
    let id = cfg.next_id; cfg.next_id += 1; CONFIG.save(deps.storage, &cfg)?;
    let period = cfg.voting_period_secs.unwrap_or_else(|| ptype.default_secs());
    let now = env.block.time.seconds();
    PROPOSALS.save(deps.storage, id, &Proposal {
        id, proposer: info.sender.clone(), ptype, title: title.clone(), description,
        yes_weight: Uint128::zero(), no_weight: Uint128::zero(), abstain_weight: Uint128::zero(),
        yes_addrs: 0, no_addrs: 0, abstain_addrs: 0, start: now, end: now + period,
        executed: false, symbol, investment_usd, target, call_msg, migrate_code_id,
    })?;
    Ok(Response::new().add_attribute("action", "create_proposal").add_attribute("id", id.to_string()).add_attribute("title", title))
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

fn exec(deps: DepsMut, env: Env, id: u64) -> StdResult<Response> {
    let cfg = CONFIG.load(deps.storage)?;
    let mut p = PROPOSALS.load(deps.storage, id)?;
    if p.executed { return Err(StdError::generic_err("already executed")); }
    if env.block.time.seconds() < p.end { return Err(StdError::generic_err("voting not ended")); }
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

#[entry_point]
pub fn query(deps: Deps, _e: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::Proposal { id } => to_json_binary(&PROPOSALS.load(deps.storage, id)?),
        QueryMsg::ActiveProposals {} => {
            let mut out = vec![];
            for kv in PROPOSALS.range(deps.storage, None, None, cosmwasm_std::Order::Ascending) { let (_, p) = kv?; if !p.executed { out.push(p); } }
            to_json_binary(&out)
        }
        QueryMsg::StakedBalance { address } => { let a = deps.api.addr_validate(&address)?; to_json_binary(&STAKED.may_load(deps.storage, &a)?.unwrap_or_default()) }
        QueryMsg::Config {} => to_json_binary(&CONFIG.load(deps.storage)?),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::testing::mock_dependencies;
    fn prop(yes: u128, no: u128, ab: u128, ya: u128, na: u128, aa: u128, pt: ProposalType) -> Proposal {
        Proposal { id:1, proposer: Addr::unchecked("p"), ptype: pt, title:"t".into(), description:"d".into(),
            yes_weight: Uint128::new(yes), no_weight: Uint128::new(no), abstain_weight: Uint128::new(ab),
            yes_addrs: ya, no_addrs: na, abstain_addrs: aa, start:0, end:100, executed:false,
            symbol:None, investment_usd:None, target:None, call_msg:None, migrate_code_id:None }
    }
    #[test] fn no_votes_fails() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::one()).unwrap(); assert!(!passes(d.as_ref(), &prop(0,0,0,0,0,0,ProposalType::Micro)).unwrap()); }
    #[test] fn unanimous_passes() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::one()).unwrap(); assert!(passes(d.as_ref(), &prop(100,0,0,1,0,0,ProposalType::Micro)).unwrap()); }
    #[test] fn majority_no_fails() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(2)).unwrap(); assert!(!passes(d.as_ref(), &prop(40,60,0,1,1,0,ProposalType::Micro)).unwrap()); }
    #[test] fn low_turnout_raises_bar() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(10)).unwrap(); assert!(!passes(d.as_ref(), &prop(80,20,0,1,1,0,ProposalType::Micro)).unwrap()); }
    #[test] fn emergency_75() { let mut d = mock_dependencies(); TOTAL_STAKERS.save(d.as_mut().storage, &Uint128::new(4)).unwrap();
        assert!(!passes(d.as_ref(), &prop(70,30,0,1,3,0,ProposalType::Emergency)).unwrap());
        assert!(passes(d.as_ref(), &prop(80,20,0,3,1,0,ProposalType::Emergency)).unwrap()); }
}

#[cw_serde]
pub struct MigrateMsg {
    pub voting_period_secs: Option<u64>,
}

#[entry_point]
pub fn migrate(deps: DepsMut, _env: Env, msg: MigrateMsg) -> StdResult<Response> {
    let mut cfg = CONFIG.load(deps.storage)?;
    cfg.voting_period_secs = msg.voting_period_secs;
    CONFIG.save(deps.storage, &cfg)?;
    set_contract_version(deps.storage, CONTRACT_NAME, "2.0.0")?;
    Ok(Response::new()
        .add_attribute("action", "migrate")
        .add_attribute("voting_period_secs", format!("{:?}", msg.voting_period_secs)))
}
