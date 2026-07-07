# NO REFUNDS ARCHIVE - ComfyUI 批量生成工具

这个仓库用于 NO REFUNDS ARCHIVE 项目的正式批量生产流程：

```text
Google表格 3333组合表
↓
CSV / prompt / 文件名
↓
ComfyUI 批量出图
↓
自动统一文件名
↓
metadata JSON
```

## 当前阶段

已经准备好 **前100张测试批次** 的批量生产脚本。

建议执行顺序：

```text
先跑前10张
↓
检查风格和文件名
↓
再跑前100张
↓
生成metadata
↓
确认没问题后再扩展到300张、3333张
```

## 文件说明

```text
comfyui_batch_runner.py       批量提交prompt到ComfyUI
generate_metadata.py          根据CSV生成NFT metadata JSON
config.json                   ComfyUI节点配置和图片尺寸
requirements.txt              依赖说明，目前只用Python标准库
run_first_10.bat              Windows一键跑前10张
run_first_100.bat             Windows一键跑前100张
make_metadata.bat             Windows一键生成metadata
data/nra_batch_0001_0100.csv  前100张CSV数据
workflows/                    放ComfyUI API格式工作流
```

## 使用方法

### 1. 启动 ComfyUI

默认地址：

```text
http://127.0.0.1:8188
```

### 2. 导出 API Format 工作流

在 ComfyUI 里：

```text
设置 → 开启 Developer mode / Dev mode
右上角 → Save(API Format)
保存为：workflows/workflow_api.json
```

注意：文件名必须是：

```text
workflow_api.json
```

### 3. 先跑10张

Windows 双击：

```text
run_first_10.bat
```

成功后，ComfyUI 的 output 文件夹里会出现类似：

```text
NRA_0001_MidnightDiner_B01_AfterHours...
NRA_0002_MidnightDiner_B02_Closed...
```

### 4. 再跑前100张

确认前10张没问题后，双击：

```text
run_first_100.bat
```

### 5. 生成metadata

双击：

```text
make_metadata.bat
```

metadata 会生成到：

```text
metadata/
```

## 重要提醒

1. 先跑10张，不要直接跑3333。
2. 如果保存文件名不对，检查 ComfyUI 工作流里是否有 SaveImage 节点。
3. 如果提示找不到 CLIPTextEncode 节点，在 `config.json` 里手动填写 `positive_prompt_node_id`。
4. 生成速度取决于电脑显卡或云服务器，不取决于表格。
5. 后续我会继续帮你把 300张 / 3333张的CSV和metadata规则扩展出来。
