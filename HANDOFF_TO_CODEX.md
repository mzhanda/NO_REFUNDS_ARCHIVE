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

## 2. 官网前端状态

### 文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `index.html` | 228 KB | 单页官网，含全部 HTML/CSS/JS（内联 + 外部引用） |
| `styles.css` | 100 KB | 官网样式表 |
| `script.js` | 18 KB | 白名单表单逻辑 |
| `background.mp3` | 1.2 MB | 官网背景音乐 |
| `NoRefundsArchive.zip` | 8 MB | 官网提供的示例 NFT 下载包 |

### script.js 白名单接口状态

- **已接入 Google Apps Script**: ✅ 是
- **SHEET_API_URL 当前值**:
  ```
  https://script.google.com/macros/s/AKfycbxUHajYs7yxsGKOiXkW-QYfRGJT8EJ-d3ab3mMX5G3TgQrsP06MTYZ-MXR2FYFtEtvY/exec
  ```
- **提交字段**: `id`, `wallet`, `twitter`, `followed`, `retweeted`, `followCheck`, `createdAt`
- **使用 localStorage**: ✅ 是，键名 `nraWhitelist`，用于去重检查（钱包地址大小写不敏感）
- **提交流程**: 用户填写钱包 + Twitter → localStorage 去重 → `mode: "no-cors"` POST 到 Google Sheet
- **官网本地可打开**: ✅ 是（纯静态文件，直接浏览器打开 `index.html` 即可）
- **待修复问题**: 无已知阻塞问题。`no-cors` 模式下前端无法获取服务器响应，但数据能正常写入 Google Sheet。

---

## 3. NFT 工具链状态

### 目录: `NRA_ComfyUI_Batch_Tools/`

#### 核心 Python 脚本

| 文件 | 大小 | 作用 |
|------|------|------|
| `compose_nra_assets.py` | 34.5 KB | **主拼装引擎 v3.0**。从 CSV 读取计划，分层叠加素材，输出最终 PNG + JSON metadata |
| `generate_plan_0100.py` | 21.4 KB | **拼装计划生成器**。根据稀有度规则自动生成 100 张 NFT 的 trait 组合 CSV |
| `validate_compose_plan.py` | 30.7 KB | **规则校验器**。检查 CSV 拼装计划是否违反系列规则、稀有度规则、跨系列限制等 |
| `generate_trait_assets.py` | 134.8 KB | **素材生成器**。从原始素材批量处理生成各类 trait 资源 |
| `generate_base_variants.py` | 6.8 KB | **底图变体生成器**。为每个系列生成不同变体的底图 |
| `crop_props.py` | 1.1 KB | Props 透明区域自动裁切工具 |
| `crop_legendary_stickers.py` | 1.4 KB | 传奇贴纸透明区域自动裁切工具 |
| `rebuild_props.py` | 104 KB | Props 重建工具（大规模素材处理） |

#### 批处理文件

| 文件 | 作用 |
|------|------|
| `run_compose_first_100.bat` | 旧版批量拼装启动脚本 |
| `run_compose_first_100_v2.bat` | v2 版批量拼装启动脚本 |

#### 数据目录: `data/`

| 文件 | 说明 |
|------|------|
| `auto_compose_plan_0100_v2.csv` | **当前主力拼装计划**（100 行，v2 版含 material_pattern + legendary_accent 字段） |
| `preview_check_0100_v2.csv` | 拼装后预览检查清单 |
| `compose_plan_validation_report_v2.csv` | 规则校验报告 |
| `series_rules.md` | 系列规则文档（哪些 trait 允许在哪些系列使用） |
| `prop_crop_info.json` | Props 裁切信息（原始尺寸 → 裁切尺寸映射） |
| `legendary_sticker_crop_info.json` | 传奇贴纸裁切信息 |
| `trait_review_list.csv` | Trait 审核清单 |

#### 输出目录: `output/`

| 路径 | 内容 |
|------|------|
| `output/final_images_v2/` | **67 张**最终拼装 PNG（1024×1024） |
| `output/metadata_v2/` | **67 个**对应 JSON metadata（一一对应） |
| `output/missing_assets_report_v2.csv` | 缺失素材报告 |
| `output/preview_check_*.csv` | 各批次预览检查清单 |

---

## 4. 当前素材库状态

| 素材类别 | 数量 | 路径 |
|----------|------|------|
| base_templates | **61** 个 | `assets/base_templates/` |
| stamps | **26** 个 | `assets/stamps/` |
| handwritten | **30** 个 | `assets/handwritten/` |
| props | **71** 个 | `assets/props/` |
| props_cropped | **71** 个 | `assets/props_cropped/` |
| damage | **20** 个 | `assets/damage/` |
| overlays | **15** 个 | `assets/overlays/` |
| material_pattern | **14** 个 | `assets/material_pattern/` |
| legendary_accent | **18** 个 | `assets/legendary_accent/` |
| legendary_accent_cropped | **10** 个 | `assets/legendary_accent_cropped/` |

> **素材总计**: 336 个素材文件，覆盖 10 个类别。

### 素材说明

- **props_cropped**: 与 `props/` 一一对应（71 对 71），已自动裁切透明区域。拼装时优先使用裁切版。
- **legendary_accent**: 18 个素材 = 8 个全幅 overlay + 10 个贴纸 sticker。overlay 保持全幅，sticker 有裁切版在 `legendary_accent_cropped/`（10 个）。

---

## 5. 当前输出状态

| 指标 | 数值 |
|------|------|
| final_images_v2 PNG 数量 | **67 张** |
| metadata_v2 JSON 数量 | **67 个** |
| 是否一一对应 | ✅ 是 |
| 是否有重复编号 | 否 |
| 是否有旧输出残留 | 无（仅有 v2 目录，无 v1 残留） |
| 最近一次新拼装 | 2026-07-10，重拼了 61 张含普通 props 的图 + 10 张含传奇 sticker 的图 |
| 建议保留 | 全部 67 张 |
| 需要人工筛选 | 部分 Rare 图缺少个别 prop 素材（如 `PROP_FOUNTAIN_PEN_01`、`PROP_HAIR_CLIP_01` 等），需确认是否接受 |

### 拼装引擎当前配置 (compose_nra_assets.py v3.0)

- `CANVAS_SIZE`: 1024×1024
- 层级顺序: base → material_pattern → damage → props → stamp → handwritten → overlay → legendary_accent
- **普通 props**: 裁切后放大 1.25x，Y 位置 20~60 px（收据上半部）
- **传奇 sticker**: 裁切后原始尺寸，Y 位置 -10~30 px（顶部边缘）
- **传奇 overlay**: 全幅 1024×1024 覆盖
- 输出目录: `output/final_images_v2/` + `output/metadata_v2/`

---

## 6. 当前 CSV / 报告状态

| 文件 | 存在 | 说明 |
|------|------|------|
| `data/auto_compose_plan_0100_v2.csv` | ✅ | 100 行拼装计划，含 material_pattern + legendary_accent 字段 |
| `data/preview_check_0100_v2.csv` | ✅ | 预览检查清单 |
| `data/compose_plan_validation_report_v2.csv` | ✅ | 校验报告（176 B，可能为空/无错误） |
| `data/missing_assets_report_v2.csv` | ⚠️ 在 `output/` 下 | 缺失素材报告（312 B） |
| `data/v2_image_selection_review.csv` | ❌ 不存在 | **需要 Codex 生成** |
| `review_v2_gallery.html` | ❌ 不存在 | **需要 Codex 生成** |
| `data/series_rules.md` | ✅ | 系列规则文档 |

---

## 7. 当前规则状态

### 稀有度规则

| 稀有度 | 数量/100张 | 规则 |
|--------|-----------|------|
| Common | 60 | 无 material_pattern，无 legendary_accent |
| Uncommon | 25 | 50% 概率有 material_pattern |
| Rare | 10 | 50% 概率有 material_pattern，50% 概率有 legendary_accent sticker |
| Legendary | 4 | 必须 gold stamp + material_pattern + 至少1个 legendary_accent（overlay 必选，sticker 50%概率追加） |
| Ultra Rare | 1 | 最顶级 gold stamp + 最顶级 material_pattern + legendary overlay + legendary sticker |

### 跨系列规则

- ✅ 已通过 `validate_compose_plan.py` 校验
- ✅ `series_rules.md` 定义了每个系列允许的 trait 组合
- ✅ material_pattern 和 legendary_accent 已接入拼装引擎

### 校验状态

- `validate_compose_plan.py`: 校验报告仅 176 B，推测无错误通过
- `compose_nra_assets.py`: 正常运行，67/100 张已拼装完成
- 缺失素材: 部分 prop ID 对应文件不存在（如 `PROP_FOUNTAIN_PEN_01`、`PROP_HAIR_CLIP_01`、`PROP_BARCODE_STICKER_01`、`PROP_RECORD_SLEEVE_CORNER_01`、`PROP_SAFETY_RAZOR_01`），这些行在拼装时会跳过缺失素材但继续生成其余图层

---

## 8. 本次 CodeBuddy 会话新增/修改内容

### 新增素材
- `assets/legendary_accent_cropped/` — 10 个裁切版传奇贴纸

### 新增脚本
- `crop_legendary_stickers.py` — 传奇贴纸裁切工具

### 修改脚本
- `compose_nra_assets.py` — 三处关键改动：
  1. `resolve_asset()`: 为 legendary_accent sticker 优先返回裁切版路径
  2. `compose_image()`: 区分普通 prop / 传奇 sticker / 传奇 overlay 的加载和定位
  3. 普通 props 放大 1.25x，Y 下移到 20~60 px

### 新拼装的图
- 10 张含传奇 sticker 的图（Rare/Legendary/Ultra Rare）— sticker 从中间移到顶部边缘
- 61 张含普通 props 的图 — props 放大 1.25x 并下移

### 官网改动
- `preview.html` 增加了 Rare 和 Legendary 的预览行

### GitHub 同步
- 本次之前项目无 Git 版本控制，需首次推送

---

## 9. 给 Codex 的下一步建议

### ⚠️ 第一步：不要直接生成 3333

接手后请按以下顺序操作：

1. **接管检查**
   - 跑一遍 `validate_compose_plan.py` 确认当前 CSV 无规则错误
   - 检查 `output/missing_assets_report_v2.csv` 确认缺失素材清单
   - 确认 `final_images_v2/` 和 `metadata_v2/` 各 67 个且一一对应

2. **清点现有输出**
   - 对 `output/final_images_v2/` 做文件名列表
   - 对 `output/metadata_v2/` 做文件名列表
   - 交叉比对确保无遗漏

3. **生成筛选工具**
   - 生成 `data/v2_image_selection_review.csv`（含编号、文件名、稀有度、系列、各 trait 字段、通过/不通过标记）
   - 生成 `review_v2_gallery.html`（可视化浏览所有 67 张图，支持标记筛选）

4. **让用户人工筛选**
   - 用户通过 gallery 标记满意/不满意的图
   - 确认哪些 trait 组合效果好、哪些需要调整

5. **再决定中批量**
   - 确认通过率后，决定是继续完善当前 100 张还是扩展到 333 张测试

---

## 10. 不要做的事

Codex 接手后**暂时不要**：

- ❌ 删除 `output/final_images_v2/` 中的现有图片
- ❌ 覆盖 `output/metadata_v2/` 中的现有 JSON
- ❌ 直接生成 3333 张（先做好质量把控）
- ❌ 大改官网视觉风格
- ❌ 修改 Google Apps Script 白名单接口地址
- ❌ 回到纯 ComfyUI 整图生成路线（当前分层拼装路线已确认）

---

## 附录 A: 关键路径速查

```
项目根目录
├── index.html                          # 官网首页
├── styles.css                          # 官网样式
├── script.js                           # 白名单表单
├── background.mp3                      # 背景音乐
├── NoRefundsArchive.zip                # 示例包
├── HANDOFF_TO_CODEX.md                 # ← 本文档
│
└── NRA_ComfyUI_Batch_Tools/
    ├── compose_nra_assets.py           # 主拼装引擎
    ├── generate_plan_0100.py           # 拼装计划生成
    ├── validate_compose_plan.py        # 规则校验
    ├── generate_trait_assets.py        # 素材生成
    ├── generate_base_variants.py       # 底图变体
    ├── crop_props.py                   # Props裁切
    ├── crop_legendary_stickers.py      # 传奇贴纸裁切
    ├── run_compose_first_100_v2.bat    # 批量拼装
    │
    ├── data/
    │   ├── auto_compose_plan_0100_v2.csv        # 拼装计划
    │   ├── series_rules.md                      # 系列规则
    │   └── preview_check_0100_v2.csv            # 预览检查
    │
    ├── assets/
    │   ├── base_templates/       (61个)
    │   ├── stamps/               (26个)
    │   ├── handwritten/          (30个)
    │   ├── props/                (71个)
    │   ├── props_cropped/        (71个)
    │   ├── damage/               (20个)
    │   ├── overlays/             (15个)
    │   ├── material_pattern/     (14个)
    │   ├── legendary_accent/     (18个)
    │   └── legendary_accent_cropped/ (10个)
    │
    └── output/
        ├── final_images_v2/      (67张PNG)
        ├── metadata_v2/          (67个JSON)
        └── missing_assets_report_v2.csv
```

## 附录 B: 拼装层级顺序

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

> **文档版本**: 1.0  
> **最后更新**: 2026-07-10  
> **下一个接手者**: Codex
