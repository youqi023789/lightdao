use cosmwasm_std::{
    entry_point, to_json_binary, Addr, Binary, Deps, DepsMut, Env, MessageInfo, Response, StdResult,
    Uint128,
};
use cw2::set_contract_version;
use cw20::{AllowanceResponse, BalanceResponse, TokenInfoResponse};

use crate::error::ContractError;
use crate::msg::{ExecuteMsg, InstantiateMsg, MinterResponse, QueryMsg, HARD_CAP};
use crate::state::{TokenConfig, ALLOWANCES, BALANCES, CONFIG};

const CONTRACT_NAME: &str = "crates.io:light_token";
const CONTRACT_VERSION: &str = "0.2.0";

#[entry_point]
pub fn instantiate(
    deps: DepsMut,
    _env: Env,
    _info: MessageInfo,
    msg: InstantiateMsg,
) -> Result<Response, ContractError> {
    set_contract_version(deps.storage, CONTRACT_NAME, CONTRACT_VERSION)?;
    let minter = deps.api.addr_validate(&msg.minter)?;
    let owner = msg.owner.map(|o| deps.api.addr_validate(&o)).transpose()?;
    CONFIG.save(
        deps.storage,
        &TokenConfig {
            name: "LightDAO".to_string(),
            symbol: "LIGHT".to_string(),
            decimals: msg.decimals,
            total_supply: Uint128::zero(),
            total_minted: Uint128::zero(),
            minter,
            owner,
        },
    )?;
    Ok(Response::new().add_attribute("action", "instantiate").add_attribute("symbol", "LIGHT"))
}

#[entry_point]
pub fn execute(
    deps: DepsMut,
    _env: Env,
    info: MessageInfo,
    msg: ExecuteMsg,
) -> Result<Response, ContractError> {
    match msg {
        ExecuteMsg::Transfer { recipient, amount } => execute_transfer(deps, info, recipient, amount),
        ExecuteMsg::TransferFrom { from, to, amount } => execute_transfer_from(deps, info, from, to, amount),
        ExecuteMsg::Burn { amount } => execute_burn(deps, info, amount),
        ExecuteMsg::BurnFrom { owner, amount } => execute_burn_from(deps, info, owner, amount),
        ExecuteMsg::Mint { recipient, amount } => execute_mint(deps, info, recipient, amount),
        ExecuteMsg::UpdateMinter { new_minter } => execute_update_minter(deps, info, new_minter),
        ExecuteMsg::IncreaseAllowance { spender, amount } => {
            execute_change_allowance(deps, info, spender, amount, true)
        }
        ExecuteMsg::DecreaseAllowance { spender, amount } => {
            execute_change_allowance(deps, info, spender, amount, false)
        }
    }
}

fn execute_transfer(
    deps: DepsMut,
    info: MessageInfo,
    recipient: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    if amount.is_zero() {
        return Err(ContractError::InvalidZeroAmount {});
    }
    let rcpt = deps.api.addr_validate(&recipient)?;
    let sender_bal = BALANCES.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if sender_bal < amount {
        return Err(ContractError::InsufficientBalance {});
    }
    BALANCES.save(deps.storage, &info.sender, &(sender_bal - amount))?;
    let rcpt_bal = BALANCES.may_load(deps.storage, &rcpt)?.unwrap_or_default();
    BALANCES.save(deps.storage, &rcpt, &(rcpt_bal + amount))?;
    Ok(Response::new()
        .add_attribute("action", "transfer")
        .add_attribute("from", info.sender)
        .add_attribute("to", rcpt)
        .add_attribute("amount", amount))
}

/// Move `amount` from `from` to `to`, consuming allowance[from][sender]. Standard CW20 TransferFrom.
fn execute_transfer_from(
    deps: DepsMut,
    info: MessageInfo,
    from: String,
    to: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    if amount.is_zero() {
        return Err(ContractError::InvalidZeroAmount {});
    }
    let from_addr = deps.api.addr_validate(&from)?;
    let to_addr = deps.api.addr_validate(&to)?;
    let allowance = ALLOWANCES
        .may_load(deps.storage, (&from_addr, &info.sender))?
        .unwrap_or_default();
    if allowance < amount {
        return Err(ContractError::InsufficientAllowance {});
    }
    let from_bal = BALANCES.may_load(deps.storage, &from_addr)?.unwrap_or_default();
    if from_bal < amount {
        return Err(ContractError::InsufficientBalance {});
    }
    ALLOWANCES.save(deps.storage, (&from_addr, &info.sender), &(allowance - amount))?;
    BALANCES.save(deps.storage, &from_addr, &(from_bal - amount))?;
    let to_bal = BALANCES.may_load(deps.storage, &to_addr)?.unwrap_or_default();
    BALANCES.save(deps.storage, &to_addr, &(to_bal + amount))?;
    Ok(Response::new()
        .add_attribute("action", "transfer_from")
        .add_attribute("from", from_addr)
        .add_attribute("to", to_addr)
        .add_attribute("by", info.sender)
        .add_attribute("amount", amount))
}

fn execute_burn(
    deps: DepsMut,
    info: MessageInfo,
    amount: Uint128,
) -> Result<Response, ContractError> {
    if amount.is_zero() {
        return Err(ContractError::InvalidZeroAmount {});
    }
    let bal = BALANCES.may_load(deps.storage, &info.sender)?.unwrap_or_default();
    if bal < amount {
        return Err(ContractError::InsufficientBalance {});
    }
    BALANCES.save(deps.storage, &info.sender, &(bal - amount))?;
    let mut cfg = CONFIG.load(deps.storage)?;
    cfg.total_supply = cfg.total_supply.checked_sub(amount)?;
    CONFIG.save(deps.storage, &cfg)?;
    Ok(Response::new()
        .add_attribute("action", "burn")
        .add_attribute("from", info.sender)
        .add_attribute("amount", amount))
}

fn execute_burn_from(
    deps: DepsMut,
    info: MessageInfo,
    owner: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    if amount.is_zero() {
        return Err(ContractError::InvalidZeroAmount {});
    }
    let owner_addr = deps.api.addr_validate(&owner)?;
    let allowance = ALLOWANCES
        .may_load(deps.storage, (&owner_addr, &info.sender))?
        .unwrap_or_default();
    if allowance < amount {
        return Err(ContractError::InsufficientAllowance {});
    }
    let bal = BALANCES.may_load(deps.storage, &owner_addr)?.unwrap_or_default();
    if bal < amount {
        return Err(ContractError::InsufficientBalance {});
    }
    ALLOWANCES.save(deps.storage, (&owner_addr, &info.sender), &(allowance - amount))?;
    BALANCES.save(deps.storage, &owner_addr, &(bal - amount))?;
    let mut cfg = CONFIG.load(deps.storage)?;
    cfg.total_supply = cfg.total_supply.checked_sub(amount)?;
    CONFIG.save(deps.storage, &cfg)?;
    Ok(Response::new()
        .add_attribute("action", "burn_from")
        .add_attribute("owner", owner_addr)
        .add_attribute("spender", info.sender)
        .add_attribute("amount", amount))
}

/// Mint enforces HARD_CAP. Only `minter` (mining_reward contract) may call.
fn execute_mint(
    deps: DepsMut,
    info: MessageInfo,
    recipient: String,
    amount: Uint128,
) -> Result<Response, ContractError> {
    let mut cfg = CONFIG.load(deps.storage)?;
    if info.sender != cfg.minter {
        return Err(ContractError::Unauthorized {});
    }
    if amount.is_zero() {
        return Err(ContractError::InvalidZeroAmount {});
    }
    let new_minted = cfg.total_minted.checked_add(amount)?;
    if new_minted.u128() > HARD_CAP {
        return Err(ContractError::SupplyCapExceeded {});
    }
    let rcpt = deps.api.addr_validate(&recipient)?;
    let bal = BALANCES.may_load(deps.storage, &rcpt)?.unwrap_or_default();
    BALANCES.save(deps.storage, &rcpt, &(bal + amount))?;
    cfg.total_minted = new_minted;
    cfg.total_supply = cfg.total_supply.checked_add(amount)?;
    CONFIG.save(deps.storage, &cfg)?;
    Ok(Response::new()
        .add_attribute("action", "mint")
        .add_attribute("to", rcpt)
        .add_attribute("amount", amount))
}

fn execute_update_minter(
    deps: DepsMut,
    info: MessageInfo,
    new_minter: String,
) -> Result<Response, ContractError> {
    let mut cfg = CONFIG.load(deps.storage)?;
    let owner = cfg.owner.clone().ok_or(ContractError::Unauthorized {})?;
    if info.sender != owner {
        return Err(ContractError::Unauthorized {});
    }
    cfg.minter = deps.api.addr_validate(&new_minter)?;
    CONFIG.save(deps.storage, &cfg)?;
    Ok(Response::new().add_attribute("action", "update_minter").add_attribute("new_minter", new_minter))
}

fn execute_change_allowance(
    deps: DepsMut,
    info: MessageInfo,
    spender: String,
    amount: Uint128,
    increase: bool,
) -> Result<Response, ContractError> {
    let spender_addr = deps.api.addr_validate(&spender)?;
    let cur = ALLOWANCES.may_load(deps.storage, (&info.sender, &spender_addr))?.unwrap_or_default();
    let new_val = if increase { cur.checked_add(amount)? } else { cur.checked_sub(amount)? };
    ALLOWANCES.save(deps.storage, (&info.sender, &spender_addr), &new_val)?;
    Ok(Response::new()
        .add_attribute("action", if increase { "increase_allowance" } else { "decrease_allowance" })
        .add_attribute("owner", info.sender)
        .add_attribute("spender", spender_addr)
        .add_attribute("amount", new_val))
}

#[entry_point]
pub fn query(deps: Deps, _env: Env, msg: QueryMsg) -> StdResult<Binary> {
    match msg {
        QueryMsg::TokenInfo {} => {
            let cfg = CONFIG.load(deps.storage)?;
            to_json_binary(&TokenInfoResponse {
                name: cfg.name,
                symbol: cfg.symbol,
                decimals: cfg.decimals,
                total_supply: cfg.total_supply,
            })
        }
        QueryMsg::Balance { address } => {
            let addr = deps.api.addr_validate(&address)?;
            let bal = BALANCES.may_load(deps.storage, &addr)?.unwrap_or_default();
            to_json_binary(&BalanceResponse { balance: bal })
        }
        QueryMsg::Minter {} => {
            let cfg = CONFIG.load(deps.storage)?;
            to_json_binary(&MinterResponse {
                minter: cfg.minter.to_string(),
                owner: cfg.owner.map(|o| o.to_string()),
                total_minted: cfg.total_minted,
                remaining_cap: Uint128::from(HARD_CAP).checked_sub(cfg.total_minted).unwrap_or_default(),
            })
        }
        QueryMsg::Allowance { owner, spender } => {
            let o = deps.api.addr_validate(&owner)?;
            let s = deps.api.addr_validate(&spender)?;
            let a = ALLOWANCES.may_load(deps.storage, (&o, &s))?.unwrap_or_default();
            to_json_binary(&AllowanceResponse {
                allowance: a,
                expires: cw20::Expiration::Never {},
            })
        }
    }
}
