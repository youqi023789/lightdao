use cosmwasm_std::{DivideByZeroError, OverflowError, StdError};
use thiserror::Error;

#[derive(Error, Debug, PartialEq)]
pub enum ContractError {
    #[error("{0}")]
    Std(#[from] StdError),

    #[error("overflow: {0}")]
    Overflow(#[from] OverflowError),

    #[error("divide by zero: {0}")]
    DivideByZero(#[from] DivideByZeroError),

    #[error("Unauthorized: sender is not authorized for this action")]
    Unauthorized {},

    #[error("Supply cap exceeded: minting would surpass HARD_CAP of 2.5B LIGHT")]
    SupplyCapExceeded {},

    #[error("Insufficient balance")]
    InsufficientBalance {},

    #[error("Insufficient allowance")]
    InsufficientAllowance {},

    #[error("Invalid zero amount")]
    InvalidZeroAmount {},
}
