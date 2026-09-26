use cosmwasm_schema::cw_serde;
use cosmwasm_std::{Addr, Uint128};
use cw_storage_plus::{Item, Map};

#[cw_serde]
pub struct Config {
    pub light_token: Addr,
    pub anti_fraud: Addr,
    pub genesis_time: u64,
    pub validators: Vec<Addr>,
    pub root_threshold: u32,
}

pub const CONFIG: Item<Config> = Item::new("config");
/// day -> committed merkle root
pub const DAILY_ROOTS: Map<u64, String> = Map::new("daily_roots");
/// (miner, day) -> claimed flag
pub const CLAIMED: Map<(&Addr, u64), bool> = Map::new("claimed");
/// (miner, day) -> zeroed by anti_fraud
pub const ZEROED: Map<(&Addr, u64), bool> = Map::new("zeroed");
/// day -> total active miners (informational)
pub const ACTIVE_MINERS: Map<u64, Uint128> = Map::new("active_miners");
/// day -> sum of weighted scores of all miners (reward denominator)
pub const TOTAL_SCORE: Map<u64, Uint128> = Map::new("total_score");
/// (day, commitment) -> distinct validator voters (N-of-M multi-sig)
pub const ROOT_VOTES: Map<(u64, &str), Vec<Addr>> = Map::new("root_votes");
/// (day, commitment) -> candidate (root, active_miners, total_score)
pub const ROOT_CAND: Map<(u64, &str), (String, Uint128, Uint128)> = Map::new("root_cand");
