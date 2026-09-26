// Package lightfee implements LightDAO §4.5 gas economics on a wasmd fork.
//
// Two mechanisms:
//
//	(a) USD-anchored dynamic min-gas-price:
//	    min_gas_price (Denom per gas) =
//	        (TransferUsdTarget / UsdPerToken) * 10^Decimals / RefTransferGas
//	    UsdPerToken is read from oracle_twap contract if configured; else static fallback.
//	    Enforced in the ante chain (MinGasPriceDecorator).
//
//	(b) Fee distribution 50% burn / 30% validators / 20% treasury:
//	    Runs at EndBlock, drains fee_collector module account accordingly.
//	    Validator share is left in fee_collector for x/distribution to sweep next block.
//
// Integration points in app.go:
//   - Add LightFeeKeeper field to WasmApp struct
//   - Initialize after BankKeeper (WasmKeeper optional for oracle)
//   - Call LightFeeKeeper.BeginBlock(ctx) in app.BeginBlocker (updates min gas)
//   - Call LightFeeKeeper.EndBlock(ctx)   in app.EndBlocker   (distributes fees)
//   - Pass LightFeeKeeper into ante.HandlerOptions and insert MinGasPriceDecorator
//     right before NewDeductFeeDecorator in app/ante.go
//
// CONSENSUS-BREAKING: any change to BeginBlock/EndBlock/AnteHandle logic requires
// a coordinated upgrade across all validators via x/upgrade governance proposal.
package lightfee

import (
	"encoding/json"
	"os"

	"cosmossdk.io/log"
	"cosmossdk.io/math"
	sdk "github.com/cosmos/cosmos-sdk/types"
	sdkerrors "github.com/cosmos/cosmos-sdk/types/errors"
	authtypes "github.com/cosmos/cosmos-sdk/x/auth/types"
	bankkeeper "github.com/cosmos/cosmos-sdk/x/bank/keeper"
	paramtypes "github.com/cosmos/cosmos-sdk/x/params/types"
)

const (
	// ModuleName identifies this package in logs and events.
	ModuleName = "lightfee"

	// BurnModuleLabel is used to derive a deterministic dead address for burn.
	// Funds sent here are functionally removed from circulation (no key can spend them).
	BurnModuleLabel = "lightdao_burn_v1"

	// TreasuryModuleLabel is the default treasury sink if LIGHTDAO_TREASURY_ADDR is unset.
	TreasuryModuleLabel = "lightdao_treasury_v1"
)

// WasmQuerier is the minimal wasm-keeper surface we need. Kept as an interface
// so lightfee can be built without a hard dep on wasmkeeper (and nil-safe when
// no oracle contract is wired yet).
type WasmQuerier interface {
	QuerySmart(ctx sdk.Context, contractAddr sdk.AccAddress, msg []byte) ([]byte, error)
}

// Config holds §4.5 parameters. All fields are runtime-tunable at Keeper
// construction; there is no on-chain governance for these yet (v1).
type Config struct {
	Denom             string         // native denom ("stake" on current mainnet; "ulight" after re-arch)
	Decimals          uint64         // exponent of the native denom (6 for both stake and ulight)
	TransferUsdTarget math.LegacyDec // whitepaper §4.5: reference tx USD target ($0.001)
	RefTransferGas    uint64         // typical gas for a bank send (100_000)
	BurnPct           math.LegacyDec // 0.5
	ValidatorPct      math.LegacyDec // 0.3 (kept implicit; residual after burn+treasury)
	TreasuryPct       math.LegacyDec // 0.2
	TreasuryAddr      sdk.AccAddress // where the 20% goes
	OracleContractAddr string        // bech32 wasm contract; empty => static fallback
	StaticPriceUsd    math.LegacyDec // fallback LIGHT/USD (e.g. 0.05)
}

// DefaultConfig returns a config matching the current mainnet (denom=stake) with
// static price 0.05 USD. Treasury defaults to a deterministic dead-hold address
// (funds visible via query but not spendable) unless overridden.
func DefaultConfig(treasury sdk.AccAddress) Config {
	if treasury == nil || treasury.Empty() {
		treasury = authtypes.NewModuleAddress(TreasuryModuleLabel)
	}
	return Config{
		Denom:              "stake",
		Decimals:           6,
		TransferUsdTarget:  math.LegacyMustNewDecFromStr("0.001"),
		RefTransferGas:     100_000,
		BurnPct:            math.LegacyMustNewDecFromStr("0.5"),
		ValidatorPct:       math.LegacyMustNewDecFromStr("0.3"),
		TreasuryPct:        math.LegacyMustNewDecFromStr("0.2"),
		TreasuryAddr:       treasury,
		OracleContractAddr: "",
		StaticPriceUsd:     math.LegacyMustNewDecFromStr("0.05"),
	}
}

// ConfigFromEnv overlays DefaultConfig with env-var overrides:
//
//	LIGHTDAO_DENOM             - native denom (default "stake")
//	LIGHTDAO_STATIC_PRICE_USD  - fallback USD price (default "0.05")
//	LIGHTDAO_TREASURY_ADDR     - bech32 addr for the 20% share
//	LIGHTDAO_ORACLE_CONTRACT   - bech32 wasm contract for price queries
//	LIGHTDAO_TRANSFER_USD      - whitepaper transfer USD target (default "0.001")
func ConfigFromEnv() Config {
	var treasury sdk.AccAddress
	if v := os.Getenv("LIGHTDAO_TREASURY_ADDR"); v != "" {
		if a, err := sdk.AccAddressFromBech32(v); err == nil {
			treasury = a
		}
	}
	cfg := DefaultConfig(treasury)
	if v := os.Getenv("LIGHTDAO_DENOM"); v != "" {
		cfg.Denom = v
	}
	if v := os.Getenv("LIGHTDAO_STATIC_PRICE_USD"); v != "" {
		if d, err := math.LegacyNewDecFromStr(v); err == nil && d.IsPositive() {
			cfg.StaticPriceUsd = d
		}
	}
	if v := os.Getenv("LIGHTDAO_ORACLE_CONTRACT"); v != "" {
		cfg.OracleContractAddr = v
	}
	if v := os.Getenv("LIGHTDAO_TRANSFER_USD"); v != "" {
		if d, err := math.LegacyNewDecFromStr(v); err == nil && d.IsPositive() {
			cfg.TransferUsdTarget = d
		}
	}
	return cfg
}

// Keeper orchestrates min-gas-price updates and fee distribution.
type Keeper struct {
	cfg      Config
	bank     bankkeeper.Keeper
	wasm     WasmQuerier // may be nil
	logger   log.Logger
	burnAddr sdk.AccAddress
	ps       paramtypes.Subspace // on-chain governance-adjustable params (optional)

	// curMinGas is the per-gas minimum fee in Denom units, recomputed each BeginBlock.
	curMinGas math.LegacyDec
	// curPriceUsd is the last-used LIGHT/USD price (for query/debug).
	curPriceUsd math.LegacyDec
	// curPriceSrc records whether the last price came from "oracle" or "static".
	curPriceSrc string
}

// NewKeeper constructs a Keeper. wasm may be nil (static-price-only mode).
// ps may be an uninitialized subspace (params then fall back to cfg/env).
func NewKeeper(cfg Config, bank bankkeeper.Keeper, wasm WasmQuerier, logger log.Logger, ps paramtypes.Subspace) *Keeper {
	if cfg.Denom == "" {
		cfg.Denom = "stake"
	}
	if cfg.Decimals == 0 {
		cfg.Decimals = 6
	}
	if cfg.RefTransferGas == 0 {
		cfg.RefTransferGas = 100_000
	}
	if cfg.TransferUsdTarget.IsNil() || !cfg.TransferUsdTarget.IsPositive() {
		cfg.TransferUsdTarget = math.LegacyMustNewDecFromStr("0.001")
	}
	if cfg.BurnPct.IsNil() {
		cfg.BurnPct = math.LegacyMustNewDecFromStr("0.5")
	}
	if cfg.ValidatorPct.IsNil() {
		cfg.ValidatorPct = math.LegacyMustNewDecFromStr("0.3")
	}
	if cfg.TreasuryPct.IsNil() {
		cfg.TreasuryPct = math.LegacyMustNewDecFromStr("0.2")
	}
	if cfg.StaticPriceUsd.IsNil() || !cfg.StaticPriceUsd.IsPositive() {
		cfg.StaticPriceUsd = math.LegacyMustNewDecFromStr("0.05")
	}
	if cfg.TreasuryAddr == nil || cfg.TreasuryAddr.Empty() {
		cfg.TreasuryAddr = authtypes.NewModuleAddress(TreasuryModuleLabel)
	}
	k := &Keeper{
		cfg:         cfg,
		bank:        bank,
		wasm:        wasm,
		logger:      logger.With("module", ModuleName),
		burnAddr:    authtypes.NewModuleAddress(BurnModuleLabel),
		ps:          ps,
		curPriceUsd: cfg.StaticPriceUsd,
		curPriceSrc: "static",
	}
	k.curMinGas = computeMinGasPrice(cfg, cfg.StaticPriceUsd)
	return k
}

// Config returns a copy of the keeper config (for debug/query).
func (k *Keeper) Config() Config { return k.cfg }

// BurnAddress returns the deterministic dead address used for burning.
func (k *Keeper) BurnAddress() sdk.AccAddress { return k.burnAddr }

// CurrentMinGasPrice returns the min-gas-price as DecCoins (used by ante + tests).
func (k *Keeper) CurrentMinGasPrice() sdk.DecCoins {
	if k.curMinGas.IsNil() || !k.curMinGas.IsPositive() {
		return sdk.DecCoins{}
	}
	return sdk.NewDecCoins(sdk.NewDecCoinFromDec(k.cfg.Denom, k.curMinGas))
}

// CurrentMinGasPriceDec returns the raw decimal (per-gas units of Denom).
func (k *Keeper) CurrentMinGasPriceDec() math.LegacyDec { return k.curMinGas }

// CurrentPriceUsd returns the last-used LIGHT/USD price.
func (k *Keeper) CurrentPriceUsd() math.LegacyDec { return k.curPriceUsd }

// CurrentPriceSource returns "oracle" or "static" for the last update.
func (k *Keeper) CurrentPriceSource() string { return k.curPriceSrc }

// computeMinGasPrice derives min-gas-price (Denom per gas) from the USD price.
//
//	tokens_per_tx    = UsdTarget / UsdPerToken
//	native_per_tx    = tokens_per_tx * 10^Decimals
//	min_gas_price    = native_per_tx / RefTransferGas
func computeMinGasPrice(cfg Config, usdPerToken math.LegacyDec) math.LegacyDec {
	if usdPerToken.IsNil() || !usdPerToken.IsPositive() {
		return math.LegacyZeroDec()
	}
	tokensPerTx := cfg.TransferUsdTarget.Quo(usdPerToken)
	pow10 := math.LegacyNewDec(1)
	for i := uint64(0); i < cfg.Decimals; i++ {
		pow10 = pow10.Mul(math.LegacyNewDec(10))
	}
	nativePerTx := tokensPerTx.Mul(pow10)
	return nativePerTx.Quo(math.LegacyNewDec(int64(cfg.RefTransferGas)))
}

// oraclePriceResponse is the expected JSON shape from oracle_twap's get_price query.
// Contract returns {"price": "<integer string scaled 1e6>"} — e.g. "50000" means $0.05.
type oraclePriceResponse struct {
	Price string `json:"price"`
}

// QueryOraclePrice tries to fetch LIGHT/USD from the oracle_twap contract.
// Mainnet oracle_twap (code6) QueryMsg variants are: external_median, twap30d,
// anomaly (NOT get_price). Per §4.10: external_median = 3+ DEX/CEX median
// (validators submit in rotation); twap30d = on-chain LIGHT/USDC 30d TWAP.
// We prefer external_median, fall back to twap30d.
// Returns (price_dec, true) on success; (zero, false) on any failure or
// non-positive price, so the caller falls back to StaticPriceUsd. Never panics.
// NOTE: response is assumed 1e6-scaled (e.g. "50000" = $0.05); confirm the scale
// against oracle_twap source before relying on dynamic pricing in production.
func (k *Keeper) QueryOraclePrice(ctx sdk.Context) (math.LegacyDec, bool) {
	if k.cfg.OracleContractAddr == "" || k.wasm == nil {
		return math.LegacyZeroDec(), false
	}
	addr, err := sdk.AccAddressFromBech32(k.cfg.OracleContractAddr)
	if err != nil {
		k.logger.Debug("oracle addr parse failed", "err", err)
		return math.LegacyZeroDec(), false
	}
	for _, q := range []string{`{"external_median":{}}`, `{"twap30d":{}}`} {
		var bz []byte
		var qerr error
		func() {
			defer func() {
				if r := recover(); r != nil {
					k.logger.Debug("oracle query panicked", "recover", r, "q", q)
					bz, qerr = nil, nil
				}
			}()
			bz, qerr = k.wasm.QuerySmart(ctx, addr, []byte(q))
		}()
		if qerr != nil || bz == nil {
			continue
		}
		raw, ok := parseOraclePrice(bz)
		if ok && raw.IsPositive() {
			return math.LegacyNewDecFromInt(raw).Quo(math.LegacyNewDec(1_000_000)), true
		}
	}
	return math.LegacyZeroDec(), false
}

// parseOraclePrice extracts a 1e6-scaled integer from the contract response,
// tolerating: {"price":"50000"}, bare string "50000", or bare number 50000.
// Float responses (e.g. 0.05) are rejected (scale ambiguity) -> caller uses static.
func parseOraclePrice(bz []byte) (math.Int, bool) {
	var obj struct {
		Price json.Number `json:"price"`
	}
	if err := json.Unmarshal(bz, &obj); err == nil && obj.Price.String() != "" {
		if i, ok := math.NewIntFromString(obj.Price.String()); ok {
			return i, true
		}
	}
	var s string
	if err := json.Unmarshal(bz, &s); err == nil {
		if i, ok := math.NewIntFromString(s); ok {
			return i, true
		}
	}
	var n json.Number
	if err := json.Unmarshal(bz, &n); err == nil {
		if i, ok := math.NewIntFromString(n.String()); ok {
			return i, true
		}
	}
	return math.ZeroInt(), false
}

// loadParams refreshes governance-adjustable params from the on-chain subspace.
// Falls back to env/config values for any key not present. Never panics (params
// read must not break consensus).
func (k *Keeper) loadParams(ctx sdk.Context) {
	defer func() { _ = recover() }()
	if k.ps.Name() == "" {
		return
	}
	// self-initialize defaults on first block so governance can adjust thereafter
	if !k.ps.Has(ctx, []byte(KeyBurnPct)) {
		d := DefaultParams()
		k.ps.SetParamSet(ctx, &d)
	}
	var b, t, u, s math.LegacyDec
	var oc string
	if k.ps.Has(ctx, []byte(KeyBurnPct)) {
		k.ps.Get(ctx, []byte(KeyBurnPct), &b)
		if b.IsPositive() {
			k.cfg.BurnPct = b
		}
	}
	if k.ps.Has(ctx, []byte(KeyTreasuryPct)) {
		k.ps.Get(ctx, []byte(KeyTreasuryPct), &t)
		if t.IsPositive() {
			k.cfg.TreasuryPct = t
		}
	}
	if k.ps.Has(ctx, []byte(KeyTransferUsd)) {
		k.ps.Get(ctx, []byte(KeyTransferUsd), &u)
		if u.IsPositive() {
			k.cfg.TransferUsdTarget = u
		}
	}
	if k.ps.Has(ctx, []byte(KeyStaticPrice)) {
		k.ps.Get(ctx, []byte(KeyStaticPrice), &s)
		if s.IsPositive() {
			k.cfg.StaticPriceUsd = s
		}
	}
	if k.ps.Has(ctx, []byte(KeyOracleContract)) {
		k.ps.Get(ctx, []byte(KeyOracleContract), &oc)
		k.cfg.OracleContractAddr = oc
	}
}

// BeginBlock updates the min gas price. MUST be called from app.BeginBlocker
// before the module manager runs.
func (k *Keeper) BeginBlock(ctx sdk.Context) {
	k.loadParams(ctx)
	var price math.LegacyDec
	var src string
	if p, ok := k.QueryOraclePrice(ctx); ok {
		price, src = p, "oracle"
	} else {
		price, src = k.cfg.StaticPriceUsd, "static"
	}
	if !price.IsPositive() {
		return
	}
	k.curMinGas = computeMinGasPrice(k.cfg, price)
	k.curPriceUsd = price
	k.curPriceSrc = src

	ctx.EventManager().EmitEvent(sdk.NewEvent(
		ModuleName+"_price_update",
		sdk.NewAttribute("price_usd", price.String()),
		sdk.NewAttribute("source", src),
		sdk.NewAttribute("min_gas_price", k.curMinGas.String()),
		sdk.NewAttribute("denom", k.cfg.Denom),
	))
}

// EndBlock drains fee_collector and splits 50% burn / 20% treasury / 30% validators.
// MUST be called from app.EndBlocker AFTER the module manager (so x/distribution's
// BeginBlocker sweep hasn't happened yet this block — it runs next block).
//
// Note: the 30% validator share is left in fee_collector; x/distribution sweeps
// the residual into the validator reward pool on next BeginBlock. This means the
// effective validator share is exactly 30% (assuming no other module touches
// fee_collector between our EndBlock and next BeginBlock).
func (k *Keeper) EndBlock(ctx sdk.Context) {
	feeCollector := authtypes.NewModuleAddress(authtypes.FeeCollectorName)
	bal := k.bank.GetBalance(ctx, feeCollector, k.cfg.Denom)
	total := bal.Amount
	if !total.IsPositive() {
		return
	}
	totalDec := math.LegacyNewDecFromInt(total)
	burnAmt := totalDec.Mul(k.cfg.BurnPct).TruncateInt()
	treAmt := totalDec.Mul(k.cfg.TreasuryPct).TruncateInt()
	valAmt := total.Sub(burnAmt).Sub(treAmt) // residual => validators

	if burnAmt.IsPositive() {
		coins := sdk.NewCoins(sdk.NewCoin(k.cfg.Denom, burnAmt))
		if err := k.bank.SendCoins(ctx, feeCollector, k.burnAddr, coins); err != nil {
			k.logger.Error("burn transfer failed", "err", err, "amount", burnAmt.String())
		} else {
			ctx.EventManager().EmitEvent(sdk.NewEvent(
				ModuleName+"_burn",
				sdk.NewAttribute("amount", burnAmt.String()),
				sdk.NewAttribute("denom", k.cfg.Denom),
				sdk.NewAttribute("to", k.burnAddr.String()),
			))
		}
	}
	if treAmt.IsPositive() && k.cfg.TreasuryAddr != nil && !k.cfg.TreasuryAddr.Empty() {
		coins := sdk.NewCoins(sdk.NewCoin(k.cfg.Denom, treAmt))
		if err := k.bank.SendCoins(ctx, feeCollector, k.cfg.TreasuryAddr, coins); err != nil {
			k.logger.Error("treasury transfer failed", "err", err, "amount", treAmt.String())
		} else {
			ctx.EventManager().EmitEvent(sdk.NewEvent(
				ModuleName+"_treasury",
				sdk.NewAttribute("amount", treAmt.String()),
				sdk.NewAttribute("denom", k.cfg.Denom),
				sdk.NewAttribute("to", k.cfg.TreasuryAddr.String()),
			))
		}
	}
	ctx.EventManager().EmitEvent(sdk.NewEvent(
		ModuleName+"_summary",
		sdk.NewAttribute("total_fee", total.String()),
		sdk.NewAttribute("burn", burnAmt.String()),
		sdk.NewAttribute("treasury", treAmt.String()),
		sdk.NewAttribute("validators", valAmt.String()),
		sdk.NewAttribute("denom", k.cfg.Denom),
	))
}

// -------- AnteDecorator --------

// MinGasPriceDecorator enforces fee >= CurrentMinGasPrice * gas.
type MinGasPriceDecorator struct {
	k *Keeper
}

// NewMinGasPriceDecorator returns a decorator backed by k. Safe with nil k
// (becomes a passthrough so misconfigured nodes don't hard-fail).
func NewMinGasPriceDecorator(k *Keeper) MinGasPriceDecorator {
	return MinGasPriceDecorator{k: k}
}

// AnteHandle implements sdk.AnteDecorator. Skips in simulation mode so gas
// estimation queries still work, and during genesis (BlockHeight==0) so gentxs
// with empty fees are not rejected — matching cosmos-sdk's own convention.
func (d MinGasPriceDecorator) AnteHandle(ctx sdk.Context, tx sdk.Tx, simulate bool, next sdk.AnteHandler) (sdk.Context, error) {
	if simulate || d.k == nil || ctx.BlockHeight() == 0 {
		return next(ctx, tx, simulate)
	}
	minCoins := d.k.CurrentMinGasPrice()
	if minCoins.IsZero() {
		return next(ctx, tx, simulate)
	}
	feeTx, ok := tx.(sdk.FeeTx)
	if !ok {
		return ctx, sdkerrors.ErrTxDecode.Wrap("tx must implement FeeTx")
	}
	gas := feeTx.GetGas()
	if gas == 0 {
		// zero-gas txs (unusual) bypass; standard ante handles gas==0 elsewhere
		return next(ctx, tx, simulate)
	}
	gasDec := math.LegacyNewDec(int64(gas))
	// Build required fees as Coins (SDK's IsAnyGTE expects Coins, not DecCoins).
	// Truncate each denom's amount down so we never over-charge by a fractional unit.
	required := sdk.NewCoins()
	for _, c := range minCoins {
		amt := c.Amount.Mul(gasDec).TruncateInt()
		if amt.IsPositive() {
			required = required.Add(sdk.NewCoin(c.Denom, amt))
		}
	}
	if required.Empty() {
		return next(ctx, tx, simulate)
	}
	feeCoins := feeTx.GetFee()
	if !feeCoins.IsAnyGTE(required) {
		return ctx, sdkerrors.ErrInsufficientFee.Wrapf(
			"USD-anchored min-gas-price not met: required >=%s, got %s (gas=%d, min_gas_price=%s/%s-gas)",
			required.String(), feeCoins.String(), gas, d.k.CurrentMinGasPriceDec().String(), d.k.cfg.Denom,
		)
	}
	return next(ctx, tx, simulate)
}

var _ sdk.AnteDecorator = MinGasPriceDecorator{}

// Suppress unused-import lint when sdkerrors is only referenced above.
var _ = sdkerrors.ErrInsufficientFee
