#!/bin/bash
# 已废弃（2026-10-15）：本脚本假设能在 HK 网关上直接 scp 到 sg-old，实测 HK→sg-old 无互信密钥、scp 直接被拒。
# 正确做法见 infra/ld_push_from_workstation.sh —— 由本机（可同时 ssh 到 HK 与 sg-old）编排仅快进推送。
# 保留此文件作为踩坑记录，不要执行。
echo "ld_push_via_old.sh 已废弃：请在【本机】运行 infra/ld_push_from_workstation.sh main" >&2
exit 78
