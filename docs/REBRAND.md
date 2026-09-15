# KTAI rebrand — cái gì đã đổi, vì sao, và cách áp lại

## 1. Phạm vi đã chốt: **scoped rebrand**

Đổi **toàn bộ bề mặt bản sắc** (lệnh, home, banner, persona, branding, identity trong
system prompt) và **giữ nguyên tên module nội bộ + biến môi trường runtime**.

Lý do (đo trên code thật, không phải phỏng đoán):

| Nếu rename toàn bộ | Hệ quả |
|---|---|
| `hermes_cli` → `ktai_cli`, `hermes_state` → `ktai_state`, … | phải sửa **4264 file `.py`** |
| 626 biến `HERMES_*` | là API runtime: plugins ngoài, compat layer (`COMPAT_MANIFEST.md`), hook gateway, docker, nix, CI đều đọc |
| Suite ~39k test / ~3.7k file | mọi test upstream chết theo → mất khả năng phát hiện hồi quy khi merge upstream |
| `scripts/check_compat_pointers.py` (CI) + `PLUGIN-COMPAT` blocks | gãy compat cho plugin bên thứ ba |
| `hermes update` / release pipeline | mất khả năng nhận fix từ upstream |

Kết luận kỹ thuật: rename toàn bộ **mua được tính thẩm mỹ ở tên symbol**, đổi lại là mất
khả năng merge upstream + rủi ro hồi quy không đo được. KTAI chọn đổi bản sắc ở nơi người
dùng thực sự thấy và giữ core gần upstream.

## 2. 28 sửa đổi trên 13 file + 1 file mới (toàn bộ nằm trong manifest)

Manifest (nguồn sự thật, có thể áp lại / kiểm tra): `patches/rebrand-manifest.json`
Diff đầy đủ so với upstream: `patches/rebrand.patch` (13 file)
Cơ cấu: **22 sửa đổi sản phẩm** + **6 sửa đổi test-alignment** (chỉ chuỗi identity).

**Identity & prompt (4 file)**
- `agent/prompt_builder.py` — `DEFAULT_AGENT_IDENTITY` → "You are KTAI (Khánh Tiển AI)…"; hai
  biến thể self-guidance trỏ về skill `ktai` + docs core. *Phần behavior spec
  (reply-sizing, cấm filler, "depth is earned") giữ nguyên verbatim — KTAI thừa hưởng hợp
  đồng trả lời của core.*
- `agent/system_prompt.py` — điều kiện chọn bản guidance đầy đủ nay nhận cả skill `ktai`.
- `agent/skill_utils.py` — `ESSENTIAL_SKILLS` thêm `"ktai"`: skill của KTAI được ghim như
  `hermes-agent`, không thể bị disable/xoá (slot guidance trong system prompt phụ thuộc nó).
- `hermes_cli/default_soul.py` — persona seed mặc định + scaffold → KTAI.

**Branding & hiển thị (3 file)**
- `core/ktai_branding.py` **(file mới)** — nguồn sự thật duy nhất cho identity: tên, chủ sở
  hữu, version, logo wordmark, hero art, branding dict, spinner, `version_label()`.
- `hermes_cli/banner.py` — import branding; **hero art** + **wordmark** + **nhãn version**
  đều lấy từ `ktai_branding` (hero: motif "chip"; logo: wordmark ANSI-shadow "KTAI").
- `hermes_cli/skin_engine.py` — branding fallback của skin mặc định → KTAI.
- `cli.py` — 7 chuỗi user-facing: tiny line, nhãn version fast-startup, welcome fallback,
  docstring module, docstring class, help text, import `_ktai_version_label`.

**Runtime (1 file)**
- `hermes_constants.py` — `get_hermes_home()` ưu tiên `KTAI_HOME` trước `HERMES_HOME`.
  (Default platform path `~/.hermes` **cố ý không đổi**: nó dùng chung cho profile
  resolution; KTAI dựa vào `KTAI_HOME` do launcher set, nên không có rủi ro đổi hành vi
  của bản Hermes đang cài.)

**Test alignment (5 file, 6 sửa)**
- `tests/hermes_cli/test_banner.py`, `test_skin_engine.py`, `test_startup_fast_guards.py` (2),
  `tests/agent/test_prompt_builder.py`, `tests/agent/test_phantom_tool_references.py` — chỉ sửa
  **kỳ vọng chuỗi identity** (tên agent, nhãn version, tên skill trong guidance pointer).
  Không đụng assertion hành vi, không nới lỏng assertion nào.

## 3. Cố ý KHÔNG đổi (và vì sao)

| Không đổi | Lý do |
|---|---|
| `HERMES_*` (626 biến), `HERMES_HOME` | API runtime; KTAI_HOME là alias ưu tiên ở lớp trên |
| Tên module `hermes_cli`, `hermes_state`, `hermes_constants`, … | 4264 file + plugin/compat phụ thuộc |
| Chuỗi hint `hermes --resume`, `hermes doctor`, … trong output | **test upstream assert trực tiếp** (9 chỗ trong `tests/`). Đổi → suite đỏ vĩnh viễn sau mỗi lần merge. Lệnh vẫn dùng được qua `ktai --resume` (passthrough) |
| Nội dung tài liệu `website/`, `docs/`, `AGENTS.md` của core | khối lượng lớn, không ảnh hưởng hành vi; muốn đổi thì dùng skill mới ở `~/.ktai/skills/ktai` |
| `hermes-agent.egg-info`, metadata package | sinh tự động; `ktai --version` tự in bản sắc KTAI |
| Tên skill `hermes-agent` (vẫn được copy vào home KTAI) | tài liệu core vẫn đúng và hữu ích; KTAI thêm skill `ktai` song song |

## 4. Verify (bằng chứng thật, chạy trên máy này)

`bash scripts/verify.sh` — kết quả lần dựng này:

```
ktai selfcheck                 → ALL GOOD (10/10 check)
rebrand idempotent             → "0 edits across 0 files" (chạy lại không đổi gì)
isolation                      → core resolve home = /Users/tiennk/.ktai
9 file test bị ảnh hưởng       → PASS (verify.sh: KTAI VERIFY: ALL GOOD)
tests/agent/ (toàn bộ)         → 6708 passed, 0 failed, 26 skipped (530 file, 71s)
banner (capture PTY thật)      → wordmark "KTAI" + hero chip + "KTAI v1.0.0 · core 0.21.1 (2026.9.7)"
ktai chat -q "<identity>"      → "em là KTAI (Khánh Tiển AI)… thuộc sở hữu của anh Nguyễn Khánh Tiển"
ktai team code "<task>"        → 10 tool call, tạo /tmp/ktai_team_demo/fib.py, tự chạy → fib(10)=55
                                 (KTAI tự báo phần chưa làm được thay vì bịa)
session storage                → ~/.ktai/state.db có 2 session KTAI; ~/.hermes/state.db nguyên vẹn
```

Ghi chú trung thực: `tests/agent/` có 1 file **FLAKY** (test timing về kill process tree —
`test_shell_hooks_tree_kill.py` / `test_codex_aux_timeout_fd_ownership`, khác nhau giữa các lần
chạy, pass khi retry). Runner tự gắn cờ flake; đây là test timing của môi trường, không liên
quan rebrand (rebrand không đụng vùng process/timeout).

## 5. Áp lại sau khi merge upstream

```bash
cd ~/KTAI/core
git fetch upstream && git merge upstream/main     # hoặc cherry-pick
cd ~/KTAI && python3 scripts/rebrand_core.py      # idempotent: chỉ vá chỗ bị mất
python3 scripts/rebrand_core.py                   # chạy lần 2 để chắc: "0 edits"
bash scripts/verify.sh
```

Cơ chế: mỗi sửa đổi là một cặp `(file, old, new)` tường minh. Nếu anchor không còn khớp
(upstream viết lại vùng đó), script **fail loudly và không ghi gì** — không bao giờ rebrand
nửa vời. Khi đó: đọc `patches/rebrand.patch`, cập nhật anchor trong
`scripts/rebrand_core.py`, chạy lại.

## 6. Thêm một thiết kế bản sắc mới

1. Chuỗi/identity mới → thêm vào `ktai_branding.py` (không rải hằng số khắp core).
2. Cần sửa core → thêm mục vào `REPLACEMENTS` trong `scripts/rebrand_core.py`.
3. Test upstream assert chuỗi đó → thêm mục vào `TEST_ALIGNMENT` (chỉ chuỗi identity).
4. Chạy `scripts/rebrand_core.py` → `bash scripts/verify.sh`.
