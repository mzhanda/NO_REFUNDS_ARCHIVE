# HANDOFF TO CODEX — NO REFUNDS ARCHIVE 项目交接文档

> **交接时间**: 2026-07-10  
> **交接人**: CodeBuddy → Codex  
> **项目根目录**: `C:\Users\dan\CodeBuddy\20260706202534`

---

## 1. 项目总览

本项目分为 **两条独立产线**：

| 产线 | 说明 | 核心文件 |
|------|------|----------|
| **官网前端** | NFT 展示 + 白名单收集落地页 | `index.html` / `styles.css` / `script.js` |
| **NFT 分层拼装工具链** | 程序化批量生成 1024×1024 NFT 图像 | `NRA_ComfyUI_Batch_Tools/` |

两条线互不依赖。官网是静态前端，工具链是 Python 批量生产系统。

---

## 2. 当前最终状态（2026-07-10 最新）

### 缺失素材
- ✅ **0 缺失** — `missing_assets_report_v2.csv` 确认无缺失
- 20 个新 prop 已通过 AI 生成 + `rembg` 抠图补全（vintage 风格，RGBA 透明背景，最大边 80px）

### 素材数量
| 素材类别 | 数量 | 路径 |
|----------|------|------|
| base_templates | 61 | `assets/base_templates/` |
| stamps | 26 | `assets/stamps/` |
| handwritten | 30 | `assets/handwritten/` |
| props | 91 | `assets/props/` |
| props_cropped | 91 | `assets/props_cropped/` |
| damage | 20 | `assets/damage/` |
| overlays | 15 | `assets/overlays/` |
| material_pattern | 14 | `assets/material_pattern/` |
| legendary_accent | 18 | `assets/legendary_accent/` |
| legendary_accent_cropped | 10 | `assets/legendary_accent_cropped/` |
| **素材总计** | **376** | |

### 输出状态
| 指标 | 数值 |
|------|------|
| `final_images_v2/` PNG 数量 | **100 张** |
| `metadata_v2/` JSON 数量 | **100 个** |
| 是否一一对应 | ✅ 是 |
| 是否有重复编号 | 否 |
| 是否有旧输出残留 | 无 |

### 校验状态
| 文件 | 状态 |
|------|------|
| `compose_plan_validation_report_v2.csv` | ✅ 0 errors, 0 warnings, 全部通过 |
| `missing_assets_report_v2.csv` | ✅ 0 缺失 |
| `preview_check_0100_v2.csv` | ✅ 已同步（100行，全部标记"是/待人工确认"） |
| `v2_image_selection_review.csv` | ✅ 已生成（100行） |
| `review_v2_gallery.html` | ✅ 已生成（支持筛选、标记、导出） |

---

## 3. 关键文件路径速查

```
项目根目录: C:\Users\dan\CodeBuddy\20260706202534

├── index.html                          # 官网首页
├── styles.css                          # 官网样式
├── script.js                           # 白名单表单
├── background.mp3                      # 背景音乐
├── HANDOFF_TO_CODEX.md                 # ← 本文档
├── PROJECT_HANDOFF_SUMMARY.md          # 项目总览
│
└── NRA_ComfyUI_Batch_Tools/
    ├── compose_nra_assets.py           # 主拼装引擎 v3.0
    ├── generate_plan_0100.py           # 拼装计划生成器
    ├── validate_compose_plan.py        # 规则校验器 v2.0
    ├── generate_trait_assets.py        # 素材生成器
    ├── generate_base_variants.py       # 底图变体生成
    ├── crop_props.py                   # Props裁切
    ├── crop_legendary_stickers.py      # 传奇贴纸裁切
    │
    ├── data/
    │   ├── auto_compose_plan_0100_v2.csv              # 拼装计划（100行）
    │   ├── preview_check_0100_v2.csv                  # 预览检查（已同步）
    │   ├── compose_plan_validation_report_v2.csv      # 校验报告（0错误）
    │   ├── missing_assets_report_v2.csv               # 缺失报告（0缺失）
    │   ├── v2_image_selection_review.csv              # 图片筛选清单
    │   └── series_rules.md                            # 系列规则
    │
    ├── review_v2_gallery.html          # 图片审核页面
    ├── review_props.html               # 小物件预览页面
    │
    ├── assets/
    │   ├── base_templates/       (61个)
    │   ├── stamps/               (26个)
    │   ├── handwritten/          (30个)
    │   ├── props/                (91个)
    │   ├── props_cropped/        (91个)
    │   ├── damage/               (20个)
    │   ├── overlays/             (15个)
    │   ├── material_pattern/     (14个)
    │   ├── legendary_accent/     (18个)
    │   └── legendary_accent_cropped/ (10个)
    │
    └── output/
        ├── final_images_v2/      (100张PNG, 1024×1024)
        ├── metadata_v2/          (100个JSON)
        └── missing_assets_report_v2.csv
```

---

## 4. Git 状态

- 远程: `origin → https://github.com/mzhanda/NO_REFUNDS_ARCHIVE.git`
- 当前分支: `master`
- 本地领先 origin/master 1 commit
- `.gitignore` 已配置排除 `output/` 目录（final_images_v2 和 metadata_v2 不进 Git）

---

## 5. Codex 接手时应从哪个目录开始

**工作目录**: `C:\Users\dan\CodeBuddy\20260706202534\NRA_ComfyUI_Batch_Tools`

---

## 6. Codex 下一步应该做什么

### ⚠️ 不要直接生成 3333

请按以下顺序操作：

1. **接管检查**
   - 跑 `python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv --files`
   - 确认 0 errors, 0 warnings
   - 确认 `missing_assets_report_v2.csv` 为 0 缺失

2. **清点现有输出**
   - `final_images_v2/`: 100 PNG (NRA-0001 ~ NRA-0100)
   - `metadata_v2/`: 100 JSON，与 PNG 一一对应

3. **使用现有审核工具**
   - `review_v2_gallery.html` — 可视化浏览 100 张图，标记保留/重做/删除/传奇候选，导出 `review_decisions.csv`
   - `review_props.html` — 浏览 91 个小物件素材

4. **让用户人工筛选**
   - 用户通过 gallery 标记满意/不满意的图
   - 确认哪些 trait 组合效果好、哪些需要调整

5. **更新 v2_image_selection_review.csv**
   - 根据人工筛选结果更新 CSV

6. **再决定中批量**
   - 确认通过率后，决定是继续完善当前 100 张还是扩展到 333 张测试

---

## 7. 不要做的事

- ❌ 直接生成 3333
- ❌ 删除 `output/final_images_v2/` 中的现有图片
- ❌ 覆盖 `output/metadata_v2/` 中的现有 JSON
- ❌ 大改官网视觉风格
- ❌ 修改 Google Apps Script 白名单接口地址
- ❌ 回到纯 ComfyUI 整图生成路线

---

## 8. 拼装层级顺序

```
第1层: base_template       → 底图（收据模板）
第2层: material_pattern    → 材质/纹理（仅 Uncommon+）
第3层: damage              → 纸张痕迹（折痕、咖啡渍等）
第4层: prop1               → 小物件1（裁切后 1.25x，Y=20~60）
第5层: prop2               → 小物件2（裁切后 1.25x，Y=20~60）
第6层: stamp               → 印章（普通红色 / 传奇金色）
第7层: handwritten         → 手写便签
第8层: overlay             → 滤镜/噪点叠加
第9层: legendary_accent    → 传奇特征（overlay全幅 + sticker顶部边缘）
```

---

> **文档版本**: 3.0 (素材补齐 + 全量拼装 + 校验通过 + 审核工具就绪)  
> **最后更新**: 2026-07-10  
> **下一个接手者**: Codex
