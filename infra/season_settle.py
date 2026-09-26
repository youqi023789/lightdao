#!/usr/bin/env python3
"""
LightDAO Season 1 结算脚本(治理提案 #4 授权,赛季末运行)
读网关每日数据(day_*.json),计算:
  season_score[miner] = Σ 每日 weighted_score(带宽40/会话30/验证20/稳定10)
  referral_bonus[inviter] += 10% × Σ 被邀人首周(first_day..first_day+6) weighted_score
  share = POOL × (season_score + referral_bonus) / Σ(all)
输出 /home/ubuntu/season1_settlement.json = [{address, amount_ulight}] 供 treasury_multisig(5/7)执行发放。
用法: python3 season_settle.py <start_day> <end_day> [pool_light]
"""
import json, os, sys, glob

DATA = os.environ.get("GW_DATA", os.path.expanduser("~/lightdao_gateway/data"))
WEIGHTS = {"bandwidth": 40, "session": 30, "verification": 20, "stability": 10}
SCALE = 1_000_000


def weighted(s):
    return (s.get("bandwidth", 0) * 40 + s.get("session", 0) * 30 +
            s.get("verification", 0) * 20 + s.get("stability", 0) * 10) // 100


def main():
    start = int(sys.argv[1]); end = int(sys.argv[2])
    pool_light = float(sys.argv[3]) if len(sys.argv) > 3 else 5_000_000.0
    pool = int(pool_light * 10**6)

    season = {}
    firstweek = {}   # invitee -> {referrer, first_day}
    referrals = {}   # from day files
    for day in range(start, end + 1):
        p = os.path.join(DATA, f"day_{day}.json")
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        if not d.get("finalized"):
            continue
        scores = d.get("scores", {})
        for m, s in scores.items():
            season[m] = season.get(m, 0) + weighted(s)
            # first-week per-invitee accumulation
            for ite, r in (d.get("referrals") or {}).items():
                referrals.setdefault(ite, r)
        for ite, r in (d.get("referrals") or {}).items():
            referrals.setdefault(ite, r)

    # referral bonus: 10% of invitee's first-week weighted score
    bonus = {}
    for ite, r in referrals.items():
        ref = r.get("referrer"); fd = r.get("first_day", start)
        if not ref:
            continue
        fw = 0
        for day in range(fd, fd + 7):
            p = os.path.join(DATA, f"day_{day}.json")
            if not os.path.exists(p):
                continue
            dd = json.load(open(p))
            if dd.get("finalized") and ite in (dd.get("scores") or {}):
                fw += weighted(dd["scores"][ite])
        if fw > 0:
            bonus[ref] = bonus.get(ref, 0) + fw // 10

    eff = {}
    for m in set(list(season) + list(bonus)):
        eff[m] = season.get(m, 0) + bonus.get(m, 0)
    total = sum(eff.values())
    if total <= 0:
        print("NO_SCORES: 赛季内无已定稿贡献"); sys.exit(0)

    plan = []
    for m, sc in sorted(eff.items(), key=lambda kv: -kv[1]):
        amt = pool * sc // total
        if amt > 0:
            plan.append({"address": m, "amount_ulight": amt,
                         "season_score": season.get(m, 0), "referral_bonus": bonus.get(m, 0)})
    out = {"season": [start, end], "pool_ulight": pool, "total_score": total,
           "miners": len(plan), "distribution": plan}
    op = os.path.expanduser("~/season1_settlement.json")
    json.dump(out, open(op, "w"), indent=2)
    print(f"结算完成: {len(plan)} 矿工, pool={pool} ulight, total_score={total}")
    print(f"输出: {op}")
    for row in plan[:10]:
        print(f"  {row['address']}  {row['amount_ulight']/1e6:,.2f} LIGHT (score={row['season_score']} bonus={row['referral_bonus']})")


if __name__ == "__main__":
    main()
