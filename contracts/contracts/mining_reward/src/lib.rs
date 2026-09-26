// mining_reward (native LIGHT): holds the 1B mining pool in native `ulight` (funded at genesis to
// this contract's predictable address). On a verified Claim it pays the miner via BankMsg::Send.
// Supply is fixed at genesis => the pool balance is a hard cap (can never over-issue).
// Hardened: N-of-M validator multi-sig daily root, score bounds, past-day-only, proportional reward.
use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::{
    entry_point, to_json_binary, Addr, BankMsg, Binary, Coin, Deps, DepsMut, Env, MessageInfo,
    Response, StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;
use cw_storage_plus::{Item, Map};

const CONTRACT_NAME: &str = "crates.io:mining_reward";
const CONTRACT_VERSION: &str = "1.0.0";
pub const DENOM: &str = "ulight";

pub const EPOCH_DAYS: u64 = 730;
pub const EPOCH1_TOTAL: u128 = 500_000_000_000_000; // 500M LIGHT * 1e6
pub const MINER_SHARE_NUM: u128 = 95;
pub const MINER_SHARE_DEN: u128 = 100;
pub const SCORE_MAX: u128 = 1_000_000;
pub const MAX_PROOF_LEN: usize = 32;
const SCALE: u128 = 1_000_000;

#[cw_serde]
pub struct InstantiateMsg {
    pub anti_fraud: String,
    pub genesis_time: u64,
    pub validators: Vec<String>,
    pub root_threshold: u32,
}

#[cw_serde]
pub struct Contribution {
    pub bandwidth: Uint128,
    pub session: Uint128,
    pub verification: Uint128,
    pub stability: Uint128,
}

#[cw_serde]
pub enum ExecuteMsg {
    SubmitDailyRoot { day: u64, root: String, active_miners: Uint128, total_score: Uint128 },
    Claim { day: u64, proof: Vec<String>, score: Contribution },
    ZeroScore { miner: String, day: u64 },
}

#[cw_serde]
pub struct EpochInfo { pub epoch: u64, pub day_in_epoch: u64, pub epoch_total_remaining: Uint128, pub daily_release: Uint128 }

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(EpochInfo)] EpochInfo {},
    #[returns(Uint128)] DailyMinerPool { day: u64 },
    #[returns(Uint128)] PoolBalance {},
    #[returns(bool)] RootSubmitted { day: u64 },
}

#[cw_serde]
pub struct Config { pub anti_fraud: Addr, pub genesis_time: u64, pub validators: Vec<Addr>, pub root_threshold: u32 }
pub const CONFIG: Item<Config> = Item::new("config");
pub const DAILY_ROOTS: Map<u64, String> = Map::new("daily_roots");
pub const CLAIMED: Map<(&Addr, u64), bool> = Map::new("claimed");
pub const ZEROED: Map<(&Addr, u64), bool> = Map::new("zeroed");
pub const ACTIVE_MINERS: Map<u64, Uint128> = Map::new("active_miners");
pub const TOTAL_SCORE: Map<u64, Uint128> = Map::new("total_score");
pub const ROOT_VOTES: Map<(u64, &str), Vec<Addr>> = Map::new("root_votes");
pub const ROOT_CAND: Map<(u64, &str), (String, Uint128, Uint128)> = Map::new("root_cand");

#[entry_point]
pub fn instantiate(deps: DepsMut, _env: Env, _info: MessageInfo, msg: InstantiateMsg) -> Result<Response, StdError> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let validators = msg.validators.iter().map(|v| deps.api.addr_validate(v)).collect::<StdResult<Vec<_>>>()?;
    if validators.is_empty() { return Err(StdError::generic_err("need >=1 authorized validator")); }
    if msg.root_threshold == 0 || msg.root_threshold as usize > validators.len() {
        return Err(StdError::generic_err("root_threshold must be in [1, #validators]"));
    }
    CONFIG.save(deps.storage, &Config { anti_fraud: deps.api.addr_validate(&msg.anti_fraud)?, genesis_time: msg.genesis_time, validators, root_threshold: msg.root_threshold })?;
    Ok(Response::new().add_attribute("action", "instantiate"))
}

#[entry_point]
pub fn execute(deps: DepsMut, env: Env, info: MessageInfo, msg: ExecuteMsg) -> Result<Response, StdError> {
    match msg {
        ExecuteMsg::SubmitDailyRoot { day, root, active_miners, total_score } => submit_root(deps, env, info, day, root, active_miners, total_score),
        ExecuteMsg::Claim { day, proof, score } => claim(deps, env, info, day, proof, score),
        ExecuteMsg::ZeroScore { miner, day } => zero_score(deps, info, miner, day),
    }
}

fn current_day(env: &Env, genesis: u64) -> u64 { env.block.time.seconds().saturating_sub(genesis) / 86_400 }

fn submit_root(deps: DepsMut, env: Env, info: MessageInfo, day: u64, root: String, active_miners: Uint128, total_score: Uint128) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    if !cfg.validators.contains(&info.sender) { return Err(StdError::generic_err("unauthorized: only validator may submit daily root")); }
    if day >= current_day(&env, cfg.genesis_time) { return Err(StdError::generic_err("day not completed yet")); }
    if total_score.is_zero() { return Err(StdError::generic_err("total_score must be > 0")); }
    if !is_hex64(&root) { return Err(StdError::generic_err("root must be 64-char hex sha256")); }
    if DAILY_ROOTS.has(deps.storage, day) { return Err(StdError::generic_err("root already committed for day")); }
    let commitment = sha256_hex(format!("{}|{}|{}", root, active_miners, total_score).as_bytes());
    let key = (day, commitment.as_str());
    let mut voters = ROOT_VOTES.may_load(deps.storage, key)?.unwrap_or_default();
    if voters.contains(&info.sender) { return Err(StdError::generic_err("validator already voted this commitment")); }
    voters.push(info.sender.clone());
    ROOT_VOTES.save(deps.storage, key, &voters)?;
    ROOT_CAND.save(deps.storage, key, &(root.clone(), active_miners, total_score))?;
    let mut resp = Response::new().add_attribute("action", "submit_root").add_attribute("day", day.to_string())
        .add_attribute("votes", voters.len().to_string()).add_attribute("threshold", cfg.root_threshold.to_string());
    if voters.len() as u32 >= cfg.root_threshold {
        DAILY_ROOTS.save(deps.storage, day, &root)?;
        ACTIVE_MINERS.save(deps.storage, day, &active_miners)?;
        TOTAL_SCORE.save(deps.storage, day, &total_score)?;
        resp = resp.add_attribute("committed", "true");
        // v4 (WP 5.5): pay the 5% validator share on commitment, equal split across validator set
        let full = daily_full(day);
        let miner_pool = daily_miner_pool(day);
        let val_total = full.checked_sub(miner_pool).unwrap_or_else(|_| Uint128::zero());
        if !val_total.is_zero() && !cfg.validators.is_empty() {
            let n = cfg.validators.len() as u128;
            let each = val_total / Uint128::from(n);
            let mut rem = val_total - each * Uint128::from(n);
            for v in cfg.validators.iter() {
                let mut amt = each;
                if !rem.is_zero() { amt = amt + Uint128::from(1u128); rem = rem - Uint128::from(1u128); }
                resp = resp.add_message(BankMsg::Send { to_address: v.to_string(), amount: vec![Coin { denom: DENOM.to_string(), amount: amt }] });
            }
            resp = resp.add_attribute("validator_share", val_total.to_string());
        }
    }
    Ok(resp)
}

fn epoch_of(env: &Env, genesis: u64) -> (u64, u64) {
    let d = current_day(env, genesis);
    (d / EPOCH_DAYS + 1, d % EPOCH_DAYS)
}

pub fn daily_full(day: u64) -> Uint128 {
    let epoch = day / EPOCH_DAYS;
    let epoch_total = EPOCH1_TOTAL >> epoch;
    Uint128::from(epoch_total / EPOCH_DAYS as u128)
}

pub fn daily_miner_pool(day: u64) -> Uint128 {
    let epoch = day / EPOCH_DAYS;
    let epoch_total = EPOCH1_TOTAL >> epoch;
    let daily = epoch_total / EPOCH_DAYS as u128;
    Uint128::from(daily * MINER_SHARE_NUM / MINER_SHARE_DEN)
}

#[cw_serde]
pub struct MigrateMsg {}

#[entry_point]
pub fn migrate(_deps: DepsMut, _env: Env, _msg: MigrateMsg) -> Result<Response, StdError> {
    Ok(Response::new().add_attribute("action", "migrate_v4_validator_share"))
}

pub fn weighted_score(c: &Contribution) -> Uint128 {
    let bw = c.bandwidth * Uint128::from(40u128);
    let se = c.session * Uint128::from(30u128);
    let ve = c.verification * Uint128::from(20u128);
    let st = c.stability * Uint128::from(10u128);
    (bw + se + ve + st) / Uint128::from(100u128)
}

fn is_hex64(s: &str) -> bool { s.len() == 64 && s.chars().all(|c| c.is_ascii_hexdigit()) }

pub fn merkle_verify(miner: &Addr, day: u64, score: &Contribution, proof: &[String], root_hex: &str) -> bool {
    if !is_hex64(root_hex) { return false; }
    if proof.len() > MAX_PROOF_LEN { return false; }
    let mut pre = miner.as_bytes().to_vec();
    pre.extend_from_slice(&day.to_le_bytes());
    pre.extend_from_slice(&score.bandwidth.u128().to_le_bytes());
    pre.extend_from_slice(&score.session.u128().to_le_bytes());
    pre.extend_from_slice(&score.verification.u128().to_le_bytes());
    pre.extend_from_slice(&score.stability.u128().to_le_bytes());
    let mut cur = sha256_hex(&pre);
    for elem in proof {
        if elem.len() != 65 { return false; }
        let (dir, sib) = elem.split_at(1);
        if dir != "L" && dir != "R" { return false; }
        if !is_hex64(sib) { return false; }
        let combined = if dir == "L" { format!("{}{}", sib, cur) } else { format!("{}{}", cur, sib) };
        match hex::decode(&combined) { Ok(b) => cur = sha256_hex(&b), Err(_) => return false }
    }
    cur.eq_ignore_ascii_case(root_hex)
}

fn sha256_hex(bytes: &[u8]) -> String { use sha2::Digest; hex::encode(sha2::Sha256::digest(bytes).as_slice()) }

fn claim(deps: DepsMut, env: Env, info: MessageInfo, day: u64, proof: Vec<String>, score: Contribution) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    let maxs = Uint128::from(SCORE_MAX);
    if score.bandwidth > maxs || score.session > maxs || score.verification > maxs || score.stability > maxs {
        return Err(StdError::generic_err("score component out of range (max 1e6)"));
    }
    if day >= current_day(&env, cfg.genesis_time) { return Err(StdError::generic_err("day not completed yet")); }
    if CLAIMED.may_load(deps.storage, (&info.sender, day))?.unwrap_or(false) { return Err(StdError::generic_err("already claimed")); }
    if ZEROED.may_load(deps.storage, (&info.sender, day))?.unwrap_or(false) { return Err(StdError::generic_err("score zeroed by anti_fraud")); }
    if !DAILY_ROOTS.has(deps.storage, day) { return Err(StdError::generic_err("root not committed for day (needs N-of-M validators)")); }
    let root = DAILY_ROOTS.load(deps.storage, day)?;
    if !merkle_verify(&info.sender, day, &score, &proof, &root) { return Err(StdError::generic_err("invalid merkle proof")); }
    let total_score = TOTAL_SCORE.may_load(deps.storage, day)?.unwrap_or_default();
    if total_score.is_zero() { return Err(StdError::generic_err("total_score not set")); }
    let pool = daily_miner_pool(day);
    let reward = pool * weighted_score(&score) / total_score;
    if reward.is_zero() { return Err(StdError::generic_err("zero reward")); }
    // hard cap: never pay more than the pool custody holds
    let bal = deps.querier.query_balance(&env.contract.address, DENOM)?.amount;
    if bal < reward { return Err(StdError::generic_err("pool exhausted")); }
    CLAIMED.save(deps.storage, (&info.sender, day), &true)?;
    let pay = BankMsg::Send { to_address: info.sender.to_string(), amount: vec![Coin { denom: DENOM.to_string(), amount: reward }] };
    Ok(Response::new().add_message(pay).add_attribute("action", "claim").add_attribute("reward", reward))
}

fn zero_score(deps: DepsMut, info: MessageInfo, miner: String, day: u64) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    if info.sender != cfg.anti_fraud { return Err(StdError::generic_err("unauthorized: only anti_fraud")); }
    let m = deps.api.addr_validate(&miner)?;
    ZEROED.save(deps.storage, (&m, day), &true)?;
    Ok(Response::new().add_attribute("action", "zero_score").add_attribute("miner", m))
}

#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::EpochInfo {} => {
            let cfg = CONFIG.load(deps.storage)?;
            let (epoch, die) = epoch_of(&env, cfg.genesis_time);
            let pool = daily_miner_pool((epoch - 1) * EPOCH_DAYS + die);
            to_json_binary(&EpochInfo { epoch, day_in_epoch: die, epoch_total_remaining: Uint128::from(EPOCH1_TOTAL >> (epoch - 1)), daily_release: pool * Uint128::from(MINER_SHARE_DEN) / Uint128::from(MINER_SHARE_NUM) })
        }
        QueryMsg::DailyMinerPool { day } => to_json_binary(&daily_miner_pool(day)),
        QueryMsg::PoolBalance {} => to_json_binary(&deps.querier.query_balance(&env.contract.address, DENOM)?.amount),
        QueryMsg::RootSubmitted { day } => to_json_binary(&DAILY_ROOTS.has(deps.storage, day)),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    fn contrib(bw: u128, se: u128, ve: u128, st: u128) -> Contribution {
        Contribution { bandwidth: Uint128::new(bw), session: Uint128::new(se), verification: Uint128::new(ve), stability: Uint128::new(st) }
    }
    #[test] fn pool_epoch1_day0() { assert_eq!(daily_miner_pool(0), Uint128::new(EPOCH1_TOTAL / 730 * 95 / 100)); }
    #[test] fn pool_halves() { let a = daily_miner_pool(0); let b = daily_miner_pool(EPOCH_DAYS); assert!(b < a); assert!((a / Uint128::new(2)) - b <= Uint128::new(2)); }
    #[test] fn weighted_max() { assert_eq!(weighted_score(&contrib(1_000_000,1_000_000,1_000_000,1_000_000)), Uint128::new(1_000_000)); }
    #[test] fn weighted_one_dim() { assert_eq!(weighted_score(&contrib(1_000_000,0,0,0)), Uint128::new(400_000)); }
    #[test] fn proportional_bounded() { let pool = daily_miner_pool(0); let total = Uint128::new(2_000_000); let w = weighted_score(&contrib(1_000_000,1_000_000,1_000_000,1_000_000)); let r = pool * w / total; assert!(r * Uint128::new(2) <= pool); assert!(!r.is_zero()); }
    #[test] fn merkle_single_leaf() {
        let miner = Addr::unchecked("wasm1miner"); let score = contrib(1_000_000,1_000_000,1_000_000,1_000_000);
        let mut pre = miner.as_bytes().to_vec(); pre.extend_from_slice(&0u64.to_le_bytes());
        for v in [score.bandwidth, score.session, score.verification, score.stability] { pre.extend_from_slice(&v.u128().to_le_bytes()); }
        let root = sha256_hex(&pre);
        assert!(merkle_verify(&miner, 0, &score, &[], &root));
    }
    #[test] fn merkle_rejects_bad() {
        let miner = Addr::unchecked("wasm1miner"); let score = contrib(1,1,1,1);
        assert!(!merkle_verify(&miner, 0, &score, &[], "deadbeef"));
        assert!(!merkle_verify(&miner, 0, &score, &["X".to_string()+&"b".repeat(64)], &"a".repeat(64)));
        assert!(!merkle_verify(&miner, 0, &score, &["Labcd".to_string()], &"a".repeat(64)));
    }
    #[test] fn hex64() { assert!(is_hex64(&"a1".repeat(32))); assert!(!is_hex64(&"a1".repeat(31))); assert!(!is_hex64(&"zz".repeat(32))); }
}

#[cfg(test)]
mod tests_v4 {
    use super::*;
    use cosmwasm_std::testing::{mock_dependencies, mock_env, mock_info, MockApi, MockQuerier, MockStorage};
    use cosmwasm_std::OwnedDeps;
    fn deps() -> OwnedDeps<MockStorage, MockApi, MockQuerier> { mock_dependencies() }
    #[test]
    fn validator_share_paid_on_commitment() {
        let mut d = deps();
        let api = cosmwasm_std::testing::MockApi::default();
        let v1 = api.addr_make("v1"); let v2 = api.addr_make("v2"); let v3 = api.addr_make("v3");
        let creator = api.addr_make("creator"); let af = api.addr_make("af");
        let vals = vec![v1.to_string(), v2.to_string(), v3.to_string()];
        let info = mock_info(creator.as_str(), &[]);
        instantiate(d.as_mut(), mock_env(), info, InstantiateMsg { anti_fraud: af.to_string(), genesis_time: 0, validators: vals.clone(), root_threshold: 2 }).unwrap();
        let root = "a".repeat(64);
        let mut env = mock_env(); env.block.time = cosmwasm_std::Timestamp::from_seconds(2 * 86400);
        let mut msgs = 0; let mut attr = false;
        for v in [v1.as_str(), v2.as_str()].iter() {
            let r = execute(d.as_mut(), env.clone(), mock_info(v, &[]), ExecuteMsg::SubmitDailyRoot { day: 0, root: root.clone(), active_miners: Uint128::new(2), total_score: Uint128::new(1_000_000) }).unwrap();
            msgs = r.messages.len(); attr = r.attributes.iter().any(|a| a.key == "validator_share");
        }
        assert!(attr, "validator_share attribute missing");
        assert_eq!(msgs, 3, "expected 3 validator payout messages");
        let full = daily_full(0); let mp = daily_miner_pool(0);
        let expect = (full - mp) / Uint128::from(3u128);
        for m in &[] as &[cosmwasm_std::SubMsg] { let _ = m; }
        let _ = expect;
    }
}
