package lightfee

import (
	"fmt"

	"cosmossdk.io/math"
	paramtypes "github.com/cosmos/cosmos-sdk/x/params/types"
)

// 链上可治理参数(§4.5)。通过 gov ParamChangeProposal 运行时调整,无需换二进制。
// subspace = "lightfee"
const (
	KeyBurnPct       = "BurnPct"
	KeyTreasuryPct   = "TreasuryPct"
	KeyTransferUsd   = "TransferUsd"
	KeyStaticPrice   = "StaticPrice"
	KeyOracleContract = "OracleContract"
)

// Params 为链上存储的 lightfee 可调参数。
type Params struct {
	BurnPct        math.LegacyDec `json:"burn_pct"`
	TreasuryPct    math.LegacyDec `json:"treasury_pct"`
	TransferUsd    math.LegacyDec `json:"transfer_usd"`
	StaticPrice    math.LegacyDec `json:"static_price"`
	OracleContract string         `json:"oracle_contract"`
}

// DefaultParams 与 env 默认一致(50/20、$0.001、$0.05、oracle 空=静态)。
func DefaultParams() Params {
	return Params{
		BurnPct:        math.LegacyMustNewDecFromStr("0.5"),
		TreasuryPct:    math.LegacyMustNewDecFromStr("0.2"),
		TransferUsd:    math.LegacyMustNewDecFromStr("0.001"),
		StaticPrice:    math.LegacyMustNewDecFromStr("0.05"),
		OracleContract: "",
	}
}

func validateDec(i interface{}) error {
	v, ok := i.(math.LegacyDec)
	if !ok {
		return fmt.Errorf("invalid parameter type: %T", i)
	}
	if v.IsNil() || v.IsNegative() {
		return fmt.Errorf("param must be non-negative: %s", v)
	}
	return nil
}
func validateStr(i interface{}) error {
	_, ok := i.(string)
	if !ok {
		return fmt.Errorf("invalid parameter type: %T", i)
	}
	return nil
}

// ParamKeyTable for lightfee subspace.
func ParamKeyTable() paramtypes.KeyTable {
	return paramtypes.NewKeyTable().RegisterParamSet(&Params{})
}

// ParamSetPairs implements params.ParamSet.
func (p *Params) ParamSetPairs() paramtypes.ParamSetPairs {
	return paramtypes.ParamSetPairs{
		paramtypes.NewParamSetPair([]byte(KeyBurnPct), &p.BurnPct, validateDec),
		paramtypes.NewParamSetPair([]byte(KeyTreasuryPct), &p.TreasuryPct, validateDec),
		paramtypes.NewParamSetPair([]byte(KeyTransferUsd), &p.TransferUsd, validateDec),
		paramtypes.NewParamSetPair([]byte(KeyStaticPrice), &p.StaticPrice, validateDec),
		paramtypes.NewParamSetPair([]byte(KeyOracleContract), &p.OracleContract, validateStr),
	}
}
