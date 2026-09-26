#!/usr/bin/env python3
"""
Patch v2: fix lightfee event propagation.

cosmos-sdk v0.50 ModuleManager.BeginBlock/EndBlock internally calls
ctx.WithEventManager(sdk.NewEventManager()), discarding events emitted on the
outer ctx beforehand. Fix: run lightfee with its own fresh EventManager AFTER
the module manager, then append those events into the response. State writes
(bank transfers) still hit the same underlying MultiStore, so only event
capture changes — no consensus-state difference.

Idempotent.
"""
import sys
from pathlib import Path

APP_GO = Path("/home/ubuntu/wasmd-src/app/app.go")
src = APP_GO.read_text()
orig = src

def rep(s, old, new, label):
    if new in s and old not in s:
        print(f"[skip] {label} (already v2)")
        return s, False
    if old not in s:
        print(f"[FAIL] {label}: anchor not found")
        sys.exit(2)
    if s.count(old) != 1:
        print(f"[FAIL] {label}: {s.count(old)} matches")
        sys.exit(3)
    print(f"[ok]   {label}")
    return s.replace(old, new, 1), True

# --- BeginBlocker: current v1 (lightfee before module manager) -> v2 (after, with own EM) ---
old_bb = '''// BeginBlocker application updates every begin block
func (app *WasmApp) BeginBlocker(ctx sdk.Context) (sdk.BeginBlock, error) {
\t// LightDAO §4.5: refresh USD-anchored min-gas-price before any module runs.
\tif app.LightFeeKeeper != nil {
\t\tapp.LightFeeKeeper.BeginBlock(ctx)
\t}
\treturn app.ModuleManager.BeginBlock(ctx)
}
'''
new_bb = '''// BeginBlocker application updates every begin block
func (app *WasmApp) BeginBlocker(ctx sdk.Context) (sdk.BeginBlock, error) {
\tresp, err := app.ModuleManager.BeginBlock(ctx)
\tif err != nil {
\t\treturn resp, err
\t}
\t// LightDAO §4.5: refresh USD-anchored min-gas-price. ModuleManager.BeginBlock
\t// swaps in a fresh EventManager, so we run lightfee with our own EM and merge
\t// its events into the response (state is shared; only events are captured here).
\tif app.LightFeeKeeper != nil {
\t\temCtx := ctx.WithEventManager(sdk.NewEventManager())
\t\tapp.LightFeeKeeper.BeginBlock(emCtx)
\t\tresp.Events = append(resp.Events, emCtx.EventManager().ABCIEvents()...)
\t}
\treturn resp, nil
}
'''
src, _ = rep(src, old_bb, new_bb, "BeginBlocker v2 (event capture)")

# --- EndBlocker: v1 -> v2 with own EM ---
old_eb = '''// EndBlocker application updates every end block
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
new_eb = '''// EndBlocker application updates every end block
func (app *WasmApp) EndBlocker(ctx sdk.Context) (sdk.EndBlock, error) {
\tresp, err := app.ModuleManager.EndBlock(ctx)
\tif err != nil {
\t\treturn resp, err
\t}
\t// LightDAO §4.5: split accumulated fee_collector balance 50% burn / 20% treasury /
\t// 30% left for x/distribution to sweep to validators on next BeginBlock.
\t// Uses a fresh EventManager (module manager discarded the outer one) and merges
\t// events into the response; bank transfers still commit to the shared store.
\tif app.LightFeeKeeper != nil {
\t\temCtx := ctx.WithEventManager(sdk.NewEventManager())
\t\tapp.LightFeeKeeper.EndBlock(emCtx)
\t\tresp.Events = append(resp.Events, emCtx.EventManager().ABCIEvents()...)
\t}
\treturn resp, nil
}
'''
src, _ = rep(src, old_eb, new_eb, "EndBlocker v2 (event capture)")

if src == orig:
    print("no changes")
else:
    APP_GO.write_text(src)
    print("app.go updated to v2")
