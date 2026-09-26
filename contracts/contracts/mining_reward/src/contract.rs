use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response,
    StdError, StdResult, Uint128, WasmMsg,
};
use cw2::set_contract_version;

use crate::msg::{
    Contribution, EpochInfo, ExecuteMsg, InstantiateMsg, QueryMsg, EPOCH1_TOTAL, EPOCH_DAYS,
    MAX_PROOF_LEN, MINER_SHARE_DEN, MINER_SHARE_NUM, SCORE_MAX,
};
use crate::state::{
    Config, ACTIVE_MINERS, CLAIMED, CONFIG, DAILY_ROOTS, ROOT_CAND, ROOT_VOTES, TOTAL_SCORE, ZEROED,
};
use self::tokenmsg::ExecuteMsg as TokenExec;

const CONTRACT_NAME: &str = "crates.io:mining_reward";
const CONTRACT_VERSION: &str = "0.3.0";
const SCALE: u128 = 1_000_000;

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, StdError> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let validators = msg.validators.iter().map(|v| deps.api.addr_validate(v)).collect::<StdResult<Vec<_>>>()?;
    if validators.is_empty() { return Err(StdError::generic_err("need >=1 authorized validator")); }
    if msg.root_threshold == 0 || msg.root_threshold as usize > validators.len() {
        return Err(StdError::generic_err("root_threshold must be in [1, #validators]"));
    }
    CONFIG.save(
        deps.storage,
        &Config {
            light_token: deps.api.addr_validate(&msg.light_token)?,
            anti_fraud: deps.api.addr_validate(&msg.anti_fraud)?,
            genesis_time: msg.genesis_time,
            validators,
            root_threshold: msg.root_threshold,
        },
    )?;
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

fn current_day(env: &Env, genesis: u64) -> u64 {
    env.block.time.seconds().saturating_sub(genesis) / 86_400
}

/// N-of-M multi-sig daily-root submission. A root commits only after >= root_threshold
/// distinct authorized validators submit the identical (root, active_miners, total_score) commitment.
fn submit_root(
    deps: DepsMut,
    env: Env,
    info: MessageInfo,
    day: u64,
    root: String,
    active_miners: Uint128,
    total_score: Uint128,
) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    if !cfg.validators.contains(&info.sender) {
        return Err(StdError::generic_err("unauthorized: only validator may submit daily root"));
    }
    if day >= current_day(&env, cfg.genesis_time) {
        return Err(StdError::generic_err("day not completed yet"));
    }
    if total_score.is_zero() {
        return Err(StdError::generic_err("total_score must be > 0"));
    }
    if !is_hex64(&root) {
        return Err(StdError::generic_err("root must be 64-char lowercase/uppercase hex sha256"));
    }
    if DAILY_ROOTS.has(deps.storage, day) {
        return Err(StdError::generic_err("root already committed for day"));
    }
    let commitment = sha256_hex(format!("{}|{}|{}", root, active_miners, total_score).as_bytes());
    let key = (day, commitment.as_str());
    let mut voters = ROOT_VOTES.may_load(deps.storage, key)?.unwrap_or_default();
    if voters.contains(&info.sender) {
        return Err(StdError::generic_err("validator already voted this commitment"));
    }
    voters.push(info.sender.clone());
    ROOT_VOTES.save(deps.storage, key, &voters)?;
    ROOT_CAND.save(deps.storage, key, &(root.clone(), active_miners, total_score))?;

    let mut resp = Response::new()
        .add_attribute("action", "submit_root")
        .add_attribute("day", day.to_string())
        .add_attribute("votes", voters.len().to_string())
        .add_attribute("threshold", cfg.root_threshold.to_string());
    if voters.len() as u32 >= cfg.root_threshold {
        DAILY_ROOTS.save(deps.storage, day, &root)?;
        ACTIVE_MINERS.save(deps.storage, day, &active_miners)?;
        TOTAL_SCORE.save(deps.storage, day, &total_score)?;
        resp = resp.add_attribute("committed", "true");
    }
    Ok(resp)
}

fn epoch_of(env: &Env, genesis: u64) -> (u64, u64) {
    let elapsed_days = current_day(env, genesis);
    (elapsed_days / EPOCH_DAYS + 1, elapsed_days % EPOCH_DAYS)
}

/// Daily miner pool for an absolute day index: (epoch_total/epoch_days) * miner_share.
pub fn daily_miner_pool(day: u64) -> Uint128 {
    let epoch = day / EPOCH_DAYS;
    let epoch_total = EPOCH1_TOTAL >> epoch;
    let daily = epoch_total / EPOCH_DAYS as u128;
    Uint128::from(daily * MINER_SHARE_NUM / MINER_SHARE_DEN)
}

/// Weighted contribution score = bw*0.40 + session*0.30 + verif*0.20 + stab*0.10 (scaled 0..1e6).
pub fn weighted_score(c: &Contribution) -> Uint128 {
    let bw = c.bandwidth * Uint128::from(40u128);
    let se = c.session * Uint128::from(30u128);
    let ve = c.verification * Uint128::from(20u128);
    let st = c.stability * Uint128::from(10u128);
    (bw + se + ve + st) / Uint128::from(100u128)
}

/// Strict hex validation: exactly 64 hex chars (sha256).
fn is_hex64(s: &str) -> bool {
    s.len() == 64 && s.chars().all(|c| c.is_ascii_hexdigit())
}

/// Hardened Merkle verification.
/// leaf = sha256( miner_bech32_bytes || day_le64 || bw_le128 || se_le128 || ve_le128 || st_le128 )
/// each proof element = 'L'|'R' + 64-hex sibling. Proof length capped. Root must be 64-hex.
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
        if elem.len() != 65 { return false; }              // 1 dir char + 64 hex
        let (dir, sib) = elem.split_at(1);
        if dir != "L" && dir != "R" { return false; }
        if !is_hex64(sib) { return false; }
        let combined = if dir == "L" { format!("{}{}", sib, cur) } else { format!("{}{}", cur, sib) };
        match hex_to_bytes(&combined) {
            Some(b) => cur = sha256_hex(&b),
            None => return false,
        }
    }
    // case-insensitive compare of hex digests
    cur.eq_ignore_ascii_case(root_hex)
}

fn sha256_hex(bytes: &[u8]) -> String {
    use sha2::Digest;
    hex::encode(sha2::Sha256::digest(bytes).as_slice())
}
fn hex_to_bytes(h: &str) -> Option<Vec<u8>> { hex::decode(h).ok() }

fn claim(
    deps: DepsMut,
    env: Env,
    info: MessageInfo,
    day: u64,
    proof: Vec<String>,
    score: Contribution,
) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    let maxs = Uint128::from(SCORE_MAX);
    if score.bandwidth > maxs || score.session > maxs || score.verification > maxs || score.stability > maxs {
        return Err(StdError::generic_err("score component out of range (max 1e6)"));
    }
    if day >= current_day(&env, cfg.genesis_time) {
        return Err(StdError::generic_err("day not completed yet"));
    }
    if CLAIMED.may_load(deps.storage, (&info.sender, day))?.unwrap_or(false) {
        return Err(StdError::generic_err("already claimed"));
    }
    if ZEROED.may_load(deps.storage, (&info.sender, day))?.unwrap_or(false) {
        return Err(StdError::generic_err("score zeroed by anti_fraud"));
    }
    if !DAILY_ROOTS.has(deps.storage, day) {
        return Err(StdError::generic_err("root not committed for day (needs N-of-M validators)"));
    }
    let root = DAILY_ROOTS.load(deps.storage, day)?;
    if !merkle_verify(&info.sender, day, &score, &proof, &root) {
        return Err(StdError::generic_err("invalid merkle proof: score not in daily root"));
    }
    let total_score = TOTAL_SCORE.may_load(deps.storage, day)?.unwrap_or_default();
    if total_score.is_zero() {
        return Err(StdError::generic_err("total_score not set"));
    }
    let pool = daily_miner_pool(day);
    let w = weighted_score(&score);
    let reward = pool * w / total_score;
    if reward.is_zero() {
        return Err(StdError::generic_err("zero reward"));
    }
    CLAIMED.save(deps.storage, (&info.sender, day), &true)?;
    let mint_msg = WasmMsg::Execute {
        contract_addr: cfg.light_token.to_string(),
        msg: to_json_binary(&TokenExec::Mint { recipient: info.sender.to_string(), amount: reward })?,
        funds: vec![],
    };
    Ok(Response::new().add_message(mint_msg).add_attribute("action", "claim").add_attribute("reward", reward))
}

fn zero_score(deps: DepsMut, info: MessageInfo, miner: String, day: u64) -> Result<Response, StdError> {
    let cfg = CONFIG.load(deps.storage)?;
    if info.sender != cfg.anti_fraud {
        return Err(StdError::generic_err("unauthorized: only anti_fraud"));
    }
    let m = deps.api.addr_validate(&miner)?;
    ZEROED.save(deps.storage, (&m, day), &true)?;
    Ok(Response::new().add_attribute("action", "zero_score").add_attribute("miner", m))
}

#[entry_point]
pub fn query(deps: Deps, env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::EpochInfo {} => {
            let cfg = CONFIG.load(deps.storage)?;
            let (epoch, day_in_epoch) = epoch_of(&env, cfg.genesis_time);
            let pool = daily_miner_pool((epoch - 1) * EPOCH_DAYS + day_in_epoch);
            to_json_binary(&EpochInfo {
                epoch,
                day_in_epoch,
                epoch_total_remaining: Uint128::from(EPOCH1_TOTAL >> (epoch - 1)),
                daily_release: pool * Uint128::from(MINER_SHARE_DEN) / Uint128::from(MINER_SHARE_NUM),
            })
        }
        QueryMsg::DailyMinerPool { day } => to_json_binary(&daily_miner_pool(day)),
        QueryMsg::PendingReward { miner, day } => {
            let _m = deps.api.addr_validate(&miner)?;
            to_json_binary(&daily_miner_pool(day))
        }
        QueryMsg::RootSubmitted { day } => to_json_binary(&DAILY_ROOTS.has(deps.storage, day)),
        QueryMsg::RootVotes { day, commitment } => {
            let n = ROOT_VOTES.may_load(deps.storage, (day, commitment.as_str()))?.unwrap_or_default().len() as u32;
            to_json_binary(&n)
        }
    }
}

pub mod tokenmsg { use cosmwasm_schema::cw_serde; use cosmwasm_std::Uint128; #[cw_serde] pub enum ExecuteMsg { Mint { recipient: String, amount: Uint128 }, Burn { amount: Uint128 }, BurnFrom { owner: String, amount: Uint128 } } }

#[cfg(test)]
mod tests {
    use super::*;
    use cosmwasm_std::{Addr, Uint128};

    fn contrib(bw: u128, se: u128, ve: u128, st: u128) -> Contribution {
        Contribution { bandwidth: Uint128::new(bw), session: Uint128::new(se), verification: Uint128::new(ve), stability: Uint128::new(st) }
    }

    #[test]
    fn pool_epoch1_day0() {
        // 500e12 / 730 * 95 / 100
        let p = daily_miner_pool(0);
        assert_eq!(p, Uint128::new(500_000_000_000_000u128 / 730 * 95 / 100));
    }

    #[test]
    fn pool_halves_each_epoch() {
        let e0 = daily_miner_pool(0);
        let e1 = daily_miner_pool(EPOCH_DAYS); // first day of epoch 2 (0-indexed epoch 1)
        // halving: e1 ~= e0 / 2 (integer shifts)
        assert!(e1 < e0);
        assert!((e0 / Uint128::new(2)) - e1 <= Uint128::new(2));
    }

    #[test]
    fn weighted_score_max_is_scale() {
        assert_eq!(weighted_score(&contrib(1_000_000, 1_000_000, 1_000_000, 1_000_000)), Uint128::new(1_000_000));
    }

    #[test]
    fn weighted_score_weights() {
        // only bandwidth maxed -> 40% of scale
        assert_eq!(weighted_score(&contrib(1_000_000, 0, 0, 0)), Uint128::new(400_000));
    }

    #[test]
    fn reward_is_proportional_and_bounded_by_pool() {
        let pool = daily_miner_pool(0);
        let total = Uint128::new(2_000_000); // two max miners
        let w = weighted_score(&contrib(1_000_000, 1_000_000, 1_000_000, 1_000_000)); // 1e6
        let reward = pool * w / total;
        // two such miners sum to <= pool
        assert!(reward * Uint128::new(2) <= pool);
        assert!(reward > Uint128::zero());
    }

    #[test]
    fn merkle_single_leaf_matches() {
        let miner = Addr::unchecked("wasm1testminer");
        let day = 0u64;
        let score = contrib(1_000_000, 1_000_000, 1_000_000, 1_000_000);
        // build the same leaf the contract builds
        let mut pre = miner.as_bytes().to_vec();
        pre.extend_from_slice(&day.to_le_bytes());
        pre.extend_from_slice(&score.bandwidth.u128().to_le_bytes());
        pre.extend_from_slice(&score.session.u128().to_le_bytes());
        pre.extend_from_slice(&score.verification.u128().to_le_bytes());
        pre.extend_from_slice(&score.stability.u128().to_le_bytes());
        let root = sha256_hex(&pre);
        assert!(merkle_verify(&miner, day, &score, &[], &root));
    }

    #[test]
    fn merkle_rejects_bad_root_and_proof() {
        let miner = Addr::unchecked("wasm1testminer");
        let score = contrib(1, 1, 1, 1);
        // wrong root length
        assert!(!merkle_verify(&miner, 0, &score, &[], "deadbeef"));
        // malformed proof element (bad direction char)
        let good_root = "a".repeat(64);
        assert!(!merkle_verify(&miner, 0, &score, &["X".to_string() + &"b".repeat(64)], &good_root));
        // proof element wrong length
        assert!(!merkle_verify(&miner, 0, &score, &["Labcd".to_string()], &good_root));
    }

    #[test]
    fn hex64_validation() {
        assert!(is_hex64(&"a1".repeat(32)));
        assert!(!is_hex64(&"a1".repeat(31)));
        assert!(!is_hex64(&"zz".repeat(32)));
    }
}
