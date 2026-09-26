use cosmwasm_schema::{cw_serde, QueryResponses};
use cosmwasm_std::Uint128;

/// Epoch length in days (2 years = 730 days). Halving every epoch.
pub const EPOCH_DAYS: u64 = 730;
/// Epoch 1 total release = 500,000,000 LIGHT (5e8 * 1e6 micro-units).
pub const EPOCH1_TOTAL: u128 = 500_000_000_000_000;
/// Miner pool share of daily release = 95% (5% to validators).
pub const MINER_SHARE_NUM: u128 = 95;
pub const MINER_SHARE_DEN: u128 = 100;
/// Max normalized score per dimension (0..1 scaled by 1e6).
pub const SCORE_MAX: u128 = 1_000_000;
/// Max Merkle proof depth (DoS guard).
pub const MAX_PROOF_LEN: usize = 32;

#[cw_serde]
pub struct InstantiateMsg {
    pub light_token: String,
    pub anti_fraud: String,
    pub genesis_time: u64,
    /// Authorized validator-gateway addresses allowed to submit daily Merkle roots.
    pub validators: Vec<String>,
    /// N-of-M threshold: a daily root commits only after >= root_threshold distinct validators submit the same commitment.
    pub root_threshold: u32,
}

#[cw_serde]
pub struct Contribution {
    pub bandwidth: Uint128, // scaled by 1e6, must be <= SCORE_MAX
    pub session: Uint128,
    pub verification: Uint128,
    pub stability: Uint128,
}

#[cw_serde]
pub enum ExecuteMsg {
    /// Authorized validator submits the daily Merkle root + aggregate stats (N-of-M to commit).
    SubmitDailyRoot { day: u64, root: String, active_miners: Uint128, total_score: Uint128 },
    /// Miner claims reward for a completed day, providing Merkle proof of their score.
    Claim { day: u64, proof: Vec<String>, score: Contribution },
    /// anti_fraud zeroes a miner's score for a day (penalty).
    ZeroScore { miner: String, day: u64 },
}

#[cw_serde]
#[derive(QueryResponses)]
pub enum QueryMsg {
    #[returns(EpochInfo)]
    EpochInfo {},
    #[returns(Uint128)]
    DailyMinerPool { day: u64 },
    #[returns(Uint128)]
    PendingReward { miner: String, day: u64 },
    #[returns(bool)]
    RootSubmitted { day: u64 },
    #[returns(u32)]
    RootVotes { day: u64, commitment: String },
}

#[cw_serde]
pub struct EpochInfo {
    pub epoch: u64,
    pub day_in_epoch: u64,
    pub epoch_total_remaining: Uint128,
    pub daily_release: Uint128,
}
