# 快速开始

现在仓库里已经有 ComfyUI 批量出图脚本。

## 第一步：生成前100张CSV

在仓库根目录打开 PowerShell 或 CMD，运行：

```bash
python generate_batch_csv.py
```

运行后会生成：

```text
data/nra_batch_0001_0100.csv
```

## 第二步：导出ComfyUI工作流

在 ComfyUI 里：

```text
设置 → 开启 Developer mode / Dev mode
右上角 → Save(API Format)
保存为 workflows/workflow_api.json
```

## 第三步：先跑前10张

```bash
python comfyui_batch_runner.py --csv data/nra_batch_0001_0100.csv --workflow workflows/workflow_api.json --start 1 --limit 10
```

## 第四步：确认没问题后跑前100张

```bash
python comfyui_batch_runner.py --csv data/nra_batch_0001_0100.csv --workflow workflows/workflow_api.json --start 1 --limit 100
```

## 第五步：生成metadata

```bash
python generate_metadata.py
```

metadata 会生成到：

```text
metadata/
```

## 注意

不要一开始直接跑3333张。先跑10张，确认文件名和画面都对，再跑100张。
