#!/bin/bash
# ld_chain_params.sh — G12: 链上参数漂移快照 diff 门。
# snap=建基线; check=对比; ack=接受当前为基线(治理提案主动改参后用)。
# 覆盖: x/gov, x/wasm, x/staking, x/mint, x/slashing, consensus params, 节点 min-gas-price。
# 设计与 ld_cfg.sh 相同(N2: 判定与调用身份无关, 始终 root)。
#
# LD-CHAINPARAMS-QUERYFAIL-20261016 修两个量具错（都会把"没查成"当成结论）：
#  1) 旧版查 consensus_params 不带高度 -> 节点正好在提交最新块时会回
#     "could not find consensus params for height #N"，那段错误 JSON 被写进指纹，
#     于是 2026-10-16 07:10 报了一次假 CHAINPARAM-DRIFT。现在固定查 tip-3 的稳定高度，
#     并且查不到就明确判 QUERY-FAIL（rc=5），绝不与"漂移"混为一谈。
#  2) 旧版整段 `2>/dev/null` 吞掉所有报错且没有空值校验 -> 任何模块查询失败都会被
#     当成"该模块没有这一项"。现在逐模块校验：空输出或含 "error" 即 QUERY-FAIL，
#     并且 snap/ack 也拒绝把失败查询写进基线（否则错误会被固化成"正常"）。
export PATH=/usr/local/bin:/usr/bin:/bin:$PATH
# 允许用环境变量指到别的节点（门禁自检/植入假故障时要能改目标，不动生产配置）
NODE=${LD_NODE_URL:-tcp://127.0.0.1:26657}
RPC=${LD_RPC_URL:-http://127.0.0.1:26657}
if [ "$(id -u)" != "0" ] && [ -z "${LD_CFG_ROOTED:-}" ]; then
  export LD_CFG_ROOTED=1
  # sudo 会吞掉未列入 env_keep 的变量（本机实测 sudo -E 也没保住 LD_REPO），
  # 所以这里把两个地址显式带过去，否则"可指向别的节点做自检"是句空话。
  exec env LD_NODE_URL="$NODE" LD_RPC_URL="$RPC" sudo -E "$0" "$@"
fi
B=/home/ubuntu/chainparams_baseline.txt
S=/home/ubuntu/chainparams_baseline.sha
ACK=/home/ubuntu/chainparams_ack
AL=/home/ubuntu/ld_alerts.log
QF=/home/ubuntu/ld_chainparams_queryfail
# LD-NOBASELINE-GUARD-20261015 基线缺失绝不能算"通过"
if [ "${1:-}" = "check" ] && { [ ! -s "$B" ] || [ ! -s "$S" ]; }; then
  echo "NO-BASELINE: 漂移门禁未生效（缺 $B 或 $S）——请先运行 $0 snap 重建基线"
  exit 1
fi

BAD=""
chk() {  # chk <模块名> <输出>  空、含报错、或不像 JSON 都算查询失败
  # 注意：`wasmd q xxx params` 连不上节点时打印的是 "Error: create client context..."
  # 这种纯文本——只查 "error" 会漏掉全部 5 个 CLI 模块（本机反向验证时暴露出来的）。
  case "$2" in
    "") BAD="$BAD $1(空输出)";;
    *"Error:"*|*'"error"'*) BAD="$BAD $1(RPC 报错)";;
    *"{"*) : ;;
    *) BAD="$BAD $1(输出不像 JSON)";;
  esac
}

gen() {
  local g w s m sl con mg H
  g=$(wasmd q gov params --node $NODE -o json 2>&1);      chk GOV "$g"
  w=$(wasmd q wasm params --node $NODE -o json 2>&1);     chk WASM "$w"
  s=$(wasmd q staking params --node $NODE -o json 2>&1);  chk STAKING "$s"
  m=$(wasmd q mint params --node $NODE -o json 2>&1);     chk MINT "$m"
  sl=$(wasmd q slashing params --node $NODE -o json 2>&1); chk SLASHING "$sl"
  # 用 tip-3 的稳定高度：最新高度的共识参数在出块瞬间可能查不到（旧版假漂移的根因）
  H=$(curl -s --max-time 10 $RPC/status | sed -n 's/.*"latest_block_height":"\([0-9]*\)".*/\1/p')
  if [ -n "$H" ] && [ "$H" -gt 4 ] 2>/dev/null; then
    con=$(curl -s --max-time 10 "$RPC/consensus_params?height=$((H-3))")
  else
    con=$(curl -s --max-time 10 $RPC/consensus_params)
  fi
  chk CONSENSUS "$con"
  mg=$(grep -E '^minimum-gas-prices' /home/ubuntu/.wasmd/config/app.toml 2>&1)
  [ -n "$mg" ] || BAD="$BAD MINGAS(读不到 app.toml)"
  printf -- '--GOV--\n%s\n--WASM--\n%s\n--STAKING--\n%s\n--MINT--\n%s\n--SLASHING--\n%s\n--CONSENSUS--\n%s\n--MINGAS--\n%s\n' \
    "$g" "$w" "$s" "$m" "$sl" \
    "$(printf '%s' "$con" | sed -E 's/"block_height":"[0-9]+",//; s/"height":"[0-9]+",//')" \
    "$mg"
}

run_gen() {  # 生成快照到 $1，返回 5 表示查询失败
  gen > "$1"
  if [ -n "$BAD" ]; then
    echo "$(date -u +%FT%TZ) QUERY-FAIL [chainparams] $BAD" >> $AL
    echo "$BAD" > $QF
    echo "QUERY-FAIL（不是漂移）:$BAD"
    return 5
  fi
  rm -f $QF
  return 0
}

case "$1" in
  snap)
    T=$(mktemp); run_gen $T || { rm -f $T; exit 5; }
    mv $T $B; sha256sum $B | cut -d" " -f1 > $S; echo "baseline $(cat $S)";;
  ack)
    T=$(mktemp); run_gen $T || { rm -f $T; exit 5; }
    mv $T $B; sha256sum $B | cut -d" " -f1 > $S; rm -f $ACK; echo "acked new baseline $(cat $S)";;
  check)
    T=$(mktemp); run_gen $T || { rm -f $T; exit 5; }
    CUR=$(sha256sum $T | cut -d" " -f1); OLD=$(cat $S 2>/dev/null)
    if [ "$CUR" != "$OLD" ]; then
      if [ -f $ACK ] && [ $ACK -nt $S ]; then
        mv $T $B; echo "$CUR" > $S; rm -f $ACK; echo "rebaselined (acked)"; exit 0
      fi
      echo "$(date -u +%FT%TZ) CHAINPARAM-DRIFT" >> $AL
      diff $B $T | head -40 >> /home/ubuntu/chainparams_diff.log 2>/dev/null
      /usr/bin/python3 /usr/local/bin/discord_bot.py send "⚠️ CHAIN PARAM DRIFT on $(hostname): see chainparams_diff.log (ack with ld_chain_params.sh ack after review)" >/dev/null 2>&1
      echo "DRIFT detected"; rm -f $T; exit 4
    fi
    rm -f $T; echo "chain params clean";;
  *) echo "usage: ld_chain_params.sh snap|check|ack  (rc: 0 干净/4 漂移/5 查询失败/1 无基线)";;
esac
