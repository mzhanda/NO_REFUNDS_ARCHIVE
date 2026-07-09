# NO REFUNDS ARCHIVE 项目交接汇总

> **生成时间**: 2026-07-09 12:41  
> **项目根目录**: `c:/Users/dan/CodeBuddy/20260706202534`  
> **项目主题**: "虚构已关闭店铺的复古收据" NFT 艺术收藏品

---

## 一、项目概述

**NO REFUNDS ARCHIVE** 是一个怀旧美学 NFT 系列，核心叙事是"商店已消失，但收据作为证据留存了下来"。包含 6 大虚构店铺系列、3333 个 NFT。

项目由三大部分组成：
1. **前端展示网站** - NFT 项目的营销落地页
2. **AI 图像生成工作流** - ComfyUI SDXL workflow
3. **Python 批量生产工具链** - 大规模 NFT 资产拼装系统

---

## 二、目录结构全貌

```
20260706202534/
├── index.html                    # 网站主页 (228KB, 397行)
├── script.js                     # 前端交互脚本 (17.96KB)
├── styles.css                    # 完整样式表 (100.11KB)
├── background.mp3                # 网站背景音乐
├── workflow_api.json             # ComfyUI SDXL 工作流模板
├── NoRefundsArchive.zip          # 项目归档包 (8.03MB)
├── assets/                       # 网站静态资源
│   └── no-refunds/               # 基础模型展示图 + trait 样张 (27张)
├── NO_REFUNDS_ARCHIVE_clone/     # 项目克隆副本
└── NRA_ComfyUI_Batch_Tools/      # ⭐ 核心生产工具链
    ├── assets/                   # 素材资源库
    │   ├── base_templates/       # 61 个底图变体 PNG
    │   ├── stamps/               # 26 个印章素材 (18红 + 8金)
    │   ├── handwritten/          # 30 个手写字素材
    │   ├── props/                # 71 个小物件素材
    │   ├── damage/               # 20 个纸张损伤素材
    │   ├── overlays/             # 15 个滤镜/噪点素材
    │   ├── material_pattern/     # 14 个材质/纹理素材
    │   ├── legendary_accent/     # 18 个传奇特征素材
    │   └── [其他参考图/测试图文件夹]
    ├── data/                     # CSV 数据文件
    │   ├── auto_compose_plan_0100_v2.csv  # 当前100张拼装计划 ⭐
    │   ├── auto_compose_plan_0100.csv     # v1 版计划
    │   ├── series_rules.md                # 系列匹配规则文档
    │   └── trait_review_list.csv          # trait 审查清单
    ├── output/                   # 输出产物
    │   ├── final_images_v2/      # ⭐ 175 张已生成 PNG
    │   ├── metadata_v2/          # ⭐ 175 个已生成 JSON metadata
    │   ├── final_images/         # v1 版 100 张
    │   ├── metadata/             # v1 版 100 个 metadata
    │   └── [报告CSV文件]
    ├── compose_nra_assets.py     # ⭐ 核心拼装引擎 v3.0
    ├── generate_plan_0100.py     # ⭐ 100张拼装计划生成器 v4.0
    ├── validate_compose_plan.py  # ⭐ 拼装计划校验器 v2.0
    ├── generate_base_variants.py # 底图变体生成器 (8→61张)
    ├── generate_trait_assets.py  # Trait素材生成器 v3.0
    ├── rebuild_props.py          # 道具重建脚本 v4
    └── preview.html              # 拼装结果本地预览页
```

---

## 三、六大街铺系列

| 系列 | 英文名 | 主题 | 底图类型 |
|------|--------|------|----------|
| 午夜餐厅 | Midnight Diner | 深夜餐厅收据 | B01 Standard Single Receipt |
| 夜猫视频 | Night Owl Video | 录像带出租店 | B02 Tabletop Narrative |
| 幸运8汽车旅馆 | Lucky 8 Gas & Motel | 公路加油站旅馆 | B03 Glass Display Case |
| B面唱片 | Side B Records | 黑胶唱片店 | B04 Archive Scan |
| 日落便利店 | Sunset Mart | 24小时便利店 | B05 Long Thermal Receipt |
| 代币当铺 | Token Pawn | 当铺/二手交易 | B06 Collage Evidence |

每个系列有严格匹配的 stamps、handwritten、props、damages、overlays 规则。

---

## 四、当前进度状态

### ✅ 已完成

| 模块 | 状态 | 详情 |
|------|------|------|
| 前端网站 | ✅ 完成 | index.html + script.js + styles.css 完整可用 |
| 网站素材 | ✅ 完成 | 基础模型图、trait 样张、收据素材均已就位 |
| ComfyUI 工作流 | ✅ 完成 | `workflow_api.json` SDXL 模板可用 |
| 底图变体 | ✅ 完成 | 8 种构图 × 变体 = 61 张底图 PNG (1024x1024) |
| 印章素材 | ✅ 完成 | 18 红印章 + 8 金印章 = 26 个 |
| 手写字素材 | ✅ 完成 | 30 个手写笔记 |
| 小物件素材 | ✅ 完成 | 71 个道具 PNG |
| 纸张损伤素材 | ✅ 完成 | 20 个损伤纹理 |
| 滤镜素材 | ✅ 完成 | 15 个叠加滤镜 |
| 材质纹理素材 | ✅ 完成 | 14 个 MAT/PAT 素材 |
| 传奇特征素材 | ✅ 完成 | 18 个 legendary accent |
| 拼装计划生成器 | ✅ 完成 | `generate_plan_0100.py` v4.0 (含稀有度规则) |
| 拼装计划 CSV | ✅ 完成 | `auto_compose_plan_0100_v2.csv` (100条记录) |
| 核心拼装引擎 | ✅ 完成 | `compose_nra_assets.py` v3.0 (8层叠加) |
| 拼装校验器 | ✅ 完成 | `validate_compose_plan.py` v2.0 (14项检查) |
| 测试批次 20 张 | ✅ 完成 | 已归档在 `assets/05_Test_Batch_20/` |

### 🔄 进行中 / 需要继续

| 模块 | 状态 | 说明 |
|------|------|------|
| **100张批次拼装** | 🔄 部分完成 | `final_images_v2/` 有 **175 张**，但计划是 100 张。多出来的可能是重复运行或不同版本 |
| **拼装校验** | 🔄 待执行 | preview_check 显示所有记录"待校验"，需要用 `--files` 参数运行校验器 |
| **质量审查** | ⬜ 未开始 | 需要对生成的图片进行人工质量审查 |
| **批量扩展到3333** | ⬜ 未开始 | 当前只处理了100张的计划，需扩展到完整3333系列 |

### 📊 稀有度分布规则 (已编码在生成器中)

| 稀有度 | 数量 | 要求 |
|--------|------|------|
| Common | 60 | 无 material_pattern，无 legendary_accent |
| Uncommon | 25 | 30%概率有轻量 material_pattern |
| Rare | 10 | 至少1个高级 trait |
| Legendary | 4 | 至少2个高级 trait + 金印章 |
| Ultra Rare | 1 | 2-3个高级 trait + 独家金印章 + 传奇 overlay |

---

## 五、关键技术架构

### 拼装层级顺序 (compose_nra_assets.py)

```
1. base_template      → 底图 (RGB不透明, 1024x1024)
2. material_pattern   → 材质/纹理 (透明PNG叠加)
3. damage             → 纸张损伤 (透明PNG叠加)
4. props              → 小物件1+2 (透明PNG叠加)
5. stamp              → 印章 (透明PNG叠加)
6. handwritten        → 手写字 (透明PNG叠加)
7. overlay            → 滤镜/噪点 (透明PNG叠加)
8. legendary_accent   → 传奇特征 (透明PNG叠加)
→ 最终导出为 PNG
```

### CSV 拼装计划字段

```
编号, 最终文件名, 系列, 底图变体, 材质/纹理, 印章素材, 手写素材,
小物件1, 小物件2, 纸张痕迹, 叠加滤镜/噪点, 传奇特征, 稀有度,
拼装状态, metadata状态, 备注
```

### Metadata JSON 格式

```json
{
  "name": "NO REFUNDS ARCHIVE #0001",
  "description": "A layered archival receipt NFT...",
  "image": "NRA_0001_...png",
  "attributes": [
    {"trait_type": "Series", "value": "Token Pawn"},
    {"trait_type": "Stamp", "value": "UNCLAIMED"},
    ...
  ]
}
```

---

## 六、常用命令速查

```bash
# 1. 生成100张拼装计划 CSV
cd NRA_ComfyUI_Batch_Tools
python generate_plan_0100.py

# 2. 预检查素材是否存在 (不生成图)
python compose_nra_assets.py --csv data/auto_compose_plan_0100_v2.csv --check

# 3. 生成前100张 NFT (图片+metadata)
python compose_nra_assets.py --csv data/auto_compose_plan_0100_v2.csv --limit 100

# 4. 生成全部100张
python compose_nra_assets.py --csv data/auto_compose_plan_0100_v2.csv

# 5. 校验拼装计划 (规则层面)
python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv

# 6. 校验拼装计划 (含文件存在性+metadata一致性)
python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv --files

# 7. 生成底图变体 (8→61)
python generate_base_variants.py

# 8. 生成 trait 素材
python generate_trait_assets.py
```

---

## 七、当前状态总结与下一步建议

### 当前里程碑
- **v2 批次**: 100 张拼装计划已生成，`final_images_v2/` 中有 175 张图片和 175 个 metadata JSON（可能是多次运行产生）
- 所有素材资源 (stamps/handwritten/props/damage/overlays/material_pattern/legendary_accent) 均已完整就位
- 前端网站完全可用

### 建议的下一步
1. **运行完整校验**: `python validate_compose_plan.py --csv data/auto_compose_plan_0100_v2.csv --files` 检查所有100张的规则符合性和文件完整性
2. **清理重复输出**: `final_images_v2/` 有175张但计划只有100张，需要去重
3. **人工质量审查**: 打开 `preview.html` 在浏览器中审查生成的图片质量
4. **扩展到完整集合**: 修改 `generate_plan_0100.py` 的 `n` 参数从 100 扩展到 3333
5. **NFT 上链准备**: 准备 metadata 上 IPFS，部署智能合约

### 重要注意事项
- 所有素材的 seed 固定为 `42`，保证可复现性
- `compose_nra_assets.py` 使用 `--limit` 参数控制批次大小
- CSV 中 `拼装状态` 为"待拼装"的行会被处理，`已完成`/`已拼装`的会被跳过
- `archive_bad_0100/` 目录保存的是不符合规则的图片（106张）
- `archive_v1_0100/` 是 v1 版本的存档

---

## 八、文件依赖关系图

```
workflow_api.json ──────────────────────────────────────┐
  (ComfyUI SDXL 模板, 生成初始概念图)                     │
                                                         │
generate_base_variants.py ──→ base_templates/ (61张)     │
generate_trait_assets.py ──→ stamps/handwritten/         │
                              props/damage/overlays/     ├──→ compose_nra_assets.py ──→ final_images_v2/
                              material_pattern/          │         (核心拼装引擎)          metadata_v2/
                              legendary_accent/          │
                                                         │
generate_plan_0100.py ──→ auto_compose_plan_0100_v2.csv ─┘
  (拼装计划生成器)                                         │
                                                         │
validate_compose_plan.py ←── 校验 CSV + 图片 + metadata ─┘

index.html + script.js + styles.css  →  前端展示网站
  (引用 assets/no-refunds/ 中的 webp/jpg 素材)
```

---

**此文档已保存至**: `PROJECT_HANDOFF_SUMMARY.md`
