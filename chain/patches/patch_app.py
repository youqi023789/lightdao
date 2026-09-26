#!/usr/bin/env python3
"""
Surgical patch of wasmd v0.55.0 app/app.go to wire in x/lightfee.

Idempotent: each step checks if the change already exists before applying.
Fails loudly if an anchor is not found (so wasmd version drift is caught).
"""
import sys
import re
from pathlib import Path

APP_GO = Path("/home/ubuntu/wasmd-src/app/app.go")

src = APP_GO.read_text()
orig = src

def must_replace(s, old, new, label):
    if new in s and old not in s:
        print(f"[skip] {label} (already patched)")
        return s, False
    if old not in s:
        print(f"[FAIL] {label}: anchor not found")
        sys.exit(2)
    n = s.count(old)
    if n != 1:
        print(f"[FAIL] {label}: anchor matches {n} times (expected 1)")
        sys.exit(3)
    print(f"[ok]   {label}")
    return s.replace(old, new, 1), True

changes = 0

# --- 1. Import lightfee package ---
old_imp = '\twasmkeeper "github.com/CosmWasm/wasmd/x/wasm/keeper"\n'
new_imp = '\t"github.com/CosmWasm/wasmd/x/lightfee"\n\twasmkeeper "github.com/CosmWasm/wasmd/x/wasm/keeper"\n'
src, ch = must_replace(src, old_imp, new_imp, "import lightfee")
changes += int(ch)

# --- 2. Struct field LightFeeKeeper ---
old_field = '\tWasmKeeper          wasmkeeper.Keeper\n\n\t// the module manager\n'
new_field = '\tWasmKeeper          wasmkeeper.Keeper\n\n\t// LightDAO §4.5 gas economics keeper (ante min-gas-price + fee 50/30/20)\n\tLightFeeKeeper      *lightfee.Keeper\n\n\t// the module manager\n'
src, ch = must_replace(src, old_field, new_field, "struct field LightFeeKeeper")
changes += int(ch)

# --- 3. Init LightFeeKeeper right after ModuleManager block, before RegisterInvariants ---
# Anchor: 'app.ModuleManager.RegisterInvariants(app.CrisisKeeper)'
old_init = '\tapp.ModuleManager.RegisterInvariants(app.CrisisKeeper)\n'
new_init = '''\t// Initialize LightDAO §4.5 lightfee keeper (config from env, static-price fallback).
\t// Placed after ModuleManager so BankKeeper and logger are ready. WasmQuerier is nil
\t// for now; oracle_twap wiring is a separate follow-up (see lightfee.QueryOraclePrice).
\t{
\t\tlightfeeCfg := lightfee.ConfigFromEnv()
\t\tapp.LightFeeKeeper = lightfee.NewKeeper(lightfeeCfg, app.BankKeeper, nil, logger)
\t}

\tapp.ModuleManager.RegisterInvariants(app.CrisisKeeper)
'''
src, ch = must_replace(src, old_init, new_init, "init LightFeeKeeper")
changes += int(ch)

# --- 4. setAnteHandler: pass LightFeeKeeper into HandlerOptions ---
old_ante = '''\t\t\tTXCounterStoreService: runtime.NewKVStoreService(txCounterStoreKey),
\t\t\tCircuitKeeper:         &app.CircuitKeeper,
\t\t},
\t)
\tif err != nil {
\t\tpanic(fmt.Errorf("failed to create AnteHandler: %s", err))
\t}'''
new_ante = '''\t\t\tTXCounterStoreService: runtime.NewKVStoreService(txCounterStoreKey),
\t\t\tCircuitKeeper:         &app.CircuitKeeper,
\t\t\tLightFeeKeeper:        app.LightFeeKeeper,
\t\t},
\t)
\tif err != nil {
\t\tpanic(fmt.Errorf("failed to create AnteHandler: %s", err))
\t}'''
src, ch = must_replace(src, old_ante, new_ante, "setAnteHandler wiring")
changes += int(ch)

# --- 5. BeginBlocker override ---
old_bb = '''// BeginBlocker application updates every begin block
func (app *WasmApp) BeginBlocker(ctx sdk.Context) (sdk.BeginBlock, error) {
\treturn app.ModuleManager.BeginBlock(ctx)
}
'''
new_bb = '''// BeginBlocker application updates every begin block
func (app *WasmApp) BeginBlocker(ctx sdk.Context) (sdk.BeginBlock, error) {
\t// LightDAO §4.5: refresh USD-anchored min-gas-price before any module runs.
\tif app.LightFeeKeeper != nil {
\t\tapp.LightFeeKeeper.BeginBlock(ctx)
\t}
\treturn app.ModuleManager.BeginBlock(ctx)
}
'''
src, ch = must_replace(src, old_bb, new_bb, "BeginBlocker hook")
changes += int(ch)

# --- 6. EndBlocker override ---
old_eb = '''// EndBlocker application updates every end block
func (app *WasmApp) EndBlocker(ctx sdk.Context) (sdk.EndBlock, error) {
\treturn app.ModuleManager.EndBlock(ctx)
}
'''
new_eb = '''// EndBlocker application updates every end block
func (app *WasmApp) EndBlocker(ctx sdk.Context) (sdk.EndBlock, error) {
\tresp, err := app.ModuleManager.EndBlock(ctx)
\tif err != nil {
\t\treturn resp, err
\t}
\t// LightDAO §4.5: split accumulated fee_collector balance 50% burn / 20% treasury /
\t// 30% left for x/distribution to sweep to validators on next BeginBlock.
\tif app.LightFeeKeeper != nil {
\t\tapp.LightFeeKeeper.EndBlock(ctx)
\t}
\treturn resp, nil
}
'''
src, ch = must_replace(src, old_eb, new_eb, "EndBlocker hook")
changes += int(ch)

if src == orig:
    print("no changes written (already patched)")
else:
    APP_GO.write_text(src)
    print(f"wrote {APP_GO} ({changes} patches applied)")
