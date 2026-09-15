# KTAI

**KTAI** = **K**hánh **T**iển **AI** — Personal AI Engineering Agent của **Nguyễn Khánh Tiển**.

KTAI là một agent kỹ thuật cá nhân độc lập: lệnh riêng (`ktai`), home riêng (`~/.ktai`),
bản sắc riêng (persona, banner, branding), và một đội 6 engineering agent chuyên trách.
Nó chạy trên **Hermes core architecture** (Nous Research) nên kế thừa toàn bộ năng lực:
vòng lặp agent tự trị, 253 tool, delegation đa agent, cron, gateway 30 nền tảng, desktop/TUI.

## Bắt đầu

```bash
ktai                                   # phiên tương tác
ktai chat -q "câu hỏi"                 # một lượt
ktai identity                          # thẻ bản sắc + home + đội agent
ktai agents                            # 6 engineering agent
ktai team debug "lỗi khi chạy X"       # giao việc cho một agent chuyên trách
ktai selfcheck                         # kiểm tra cài đặt (10 check)
ktai doctor                            # health check của core (passthrough)
```

Mọi subcommand của core dùng được y nguyên qua `ktai` (`ktai cron`, `ktai gateway`,
`ktai config`, `ktai tools`, …) — `ktai` chỉ chèn lớp bản sắc ở trên.

## Cấu trúc

```
~/KTAI/
├── core/         # source runtime (fork Hermes core, git repo + remote upstream)
├── ktai/         # package CLI: identity · agents · team · selfcheck · passthrough
├── identity/     # nguồn bản sắc: SOUL.md · AGENTS.md · agents/*.md · skins/ · skills/ktai
├── bin/ktai      # launcher (resolve symlink, set KTAI_HOME, exec venv)
├── scripts/      # clone · rebrand · setup_venv · seed_home · verify · rebuild
├── patches/      # rebrand.patch + manifest (bản sắc KTAI vs upstream)
├── venv/         # runtime riêng của KTAI
└── docs/         # ARCHITECTURE · KTAI-IDENTITY · REBRAND · AGENT-ROLES

~/.ktai/          # dữ liệu: config.yaml .env SOUL.md AGENTS.md agents/ skins/ skills/
                  #          memories/ plugins/ state.db logs/ sessions/
```

## Tài liệu

| Đọc | Nội dung |
|---|---|
| `docs/ARCHITECTURE.md` | Bản đồ kiến trúc đo từ code: entry point, agent loop, tool, đa agent, memory, runtime, build/test |
| `docs/KTAI-IDENTITY.md` | Định nghĩa bản sắc KTAI + chuẩn hành vi đã cài |
| `docs/AGENT-ROLES.md` | 6 engineering agent, cách gọi, hợp đồng đầu ra |
| `docs/REBRAND.md` | **Quan trọng**: đổi gì, giữ gì, vì sao, cách áp lại sau khi merge upstream |

## Vận hành

```bash
bash scripts/verify.sh                  # kiểm chứng toàn bộ (không tốn API call)
bash scripts/verify.sh --with-chat      # thêm smoke test identity (1 API call)
bash scripts/rebuild.sh                 # dựng lại từ đầu (idempotent)
bash scripts/rebuild.sh --force-seed    # ghi đè config/skills trong ~/.ktai
python3 scripts/rebrand_core.py         # áp lại lớp bản sắc (idempotent, fail loudly)
```

**Quy tắc sắt:** `core/` là runtime đang chạy — không sửa tay. Sửa bản sắc thì thêm mục vào
manifest trong `scripts/rebrand_core.py` rồi chạy lại; sửa năng lực thì viết ở lớp `ktai/`
(CLI/skill/plugin) để giữ core gần upstream và còn merge được fix.

## Ghi công

KTAI là bản phái sinh (derived work) từ **Hermes Agent** của **Nous Research**, giấy phép MIT
(`core/LICENSE`). Bản sắc, lớp điều phối, đội agent và tài liệu KTAI thuộc Nguyễn Khánh Tiển.
