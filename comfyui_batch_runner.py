#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NO REFUNDS ARCHIVE - ComfyUI 批量出图脚本

用途：
1. 读取 data/nra_batch_0001_0100.csv
2. 把每一行 prompt 写入 ComfyUI workflow_api.json
3. 把 SaveImage 文件名前缀改成表格里的标准文件名
4. 通过 ComfyUI API 排队生成
5. 输出图片自动按 NRA_0001... 命名

使用前：
- 先启动 ComfyUI
- 在 ComfyUI 里打开你的工作流
- 右上角设置里开启 Dev mode / Developer mode
- 点击 Save(API Format)，保存为 workflows/workflow_api.json
"""

import argparse
import csv
import json
import time
import uuid
import urllib.request
from pathlib import Path


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def queue_prompt(server: str, workflow: dict, client_id: str) -> dict:
    payload = json.dumps({"prompt": workflow, "client_id": client_id}).encode("utf-8")
    req = urllib.request.Request(
        f"http://{server}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def find_positive_prompt_node(workflow: dict) -> str:
    """自动寻找第一个 CLIPTextEncode 节点。复杂工作流可在 config.json 手动指定。"""
    for node_id, node in workflow.items():
        if (
            node.get("class_type") == "CLIPTextEncode"
            and isinstance(node.get("inputs"), dict)
            and "text" in node["inputs"]
        ):
            return node_id
    raise RuntimeError("找不到 CLIPTextEncode 正向提示词节点。请在 config.json 里指定 positive_prompt_node_id。")


def find_save_image_node(workflow: dict) -> str:
    for node_id, node in workflow.items():
        if node.get("class_type") == "SaveImage" and isinstance(node.get("inputs"), dict):
            return node_id
    raise RuntimeError("找不到 SaveImage 节点。请检查 workflow_api.json。")


def apply_row_to_workflow(workflow_template: dict, row: dict, config: dict) -> dict:
    workflow = json.loads(json.dumps(workflow_template))

    positive_id = str(config.get("positive_prompt_node_id") or find_positive_prompt_node(workflow))
    save_id = str(config.get("save_image_node_id") or find_save_image_node(workflow))

    filename = row["filename"].strip()
    prefix = Path(filename).stem

    workflow[positive_id]["inputs"]["text"] = row["prompt"]

    # ComfyUI SaveImage 的 filename_prefix 不需要 .png
    workflow[save_id]["inputs"]["filename_prefix"] = prefix

    # 可选：如果工作流里有 EmptyLatentImage，则自动设定正方形尺寸
    width = int(config.get("width", 1024))
    height = int(config.get("height", 1024))
    for node_id, node in workflow.items():
        if node.get("class_type") == "EmptyLatentImage":
            node["inputs"]["width"] = width
            node["inputs"]["height"] = height

    return workflow


def read_csv(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="data/nra_batch_0001_0100.csv", help="CSV路径")
    parser.add_argument("--workflow", default="workflows/workflow_api.json", help="ComfyUI API格式workflow")
    parser.add_argument("--config", default="config.json", help="配置文件")
    parser.add_argument("--server", default="127.0.0.1:8188", help="ComfyUI服务器")
    parser.add_argument("--start", type=int, default=1, help="从第几行开始，1代表CSV第一条数据")
    parser.add_argument("--limit", type=int, default=10, help="本次最多生成多少张；先用10测试")
    parser.add_argument("--delay", type=float, default=1.0, help="每次提交之间停顿秒数")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    workflow_path = Path(args.workflow)
    config_path = Path(args.config)

    if not csv_path.exists():
        raise FileNotFoundError(f"找不到CSV：{csv_path}")
    if not workflow_path.exists():
        raise FileNotFoundError(
            f"找不到workflow：{workflow_path}\n"
            "请在ComfyUI里把工作流导出为 API Format，然后保存到 workflows/workflow_api.json"
        )

    config = load_json(config_path) if config_path.exists() else {}
    rows = read_csv(csv_path)
    workflow_template = load_json(workflow_path)
    client_id = str(uuid.uuid4())

    selected = rows[args.start - 1 : args.start - 1 + args.limit]
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_path = log_dir / "queue_log.csv"

    new_log = not log_path.exists()
    with log_path.open("a", encoding="utf-8-sig", newline="") as f:
        fieldnames = ["id", "filename", "prompt_id", "status"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if new_log:
            writer.writeheader()

        for row in selected:
            print(f"提交：{row['id']} -> {row['filename']}")
            workflow = apply_row_to_workflow(workflow_template, row, config)
            result = queue_prompt(args.server, workflow, client_id)
            prompt_id = result.get("prompt_id", "")
            writer.writerow(
                {
                    "id": row["id"],
                    "filename": row["filename"],
                    "prompt_id": prompt_id,
                    "status": "queued",
                }
            )
            f.flush()
            time.sleep(args.delay)

    print("\n提交完成。")
    print("如果ComfyUI正常运行，图片会保存到 ComfyUI/output 文件夹。")
    print("文件名前缀会按CSV里的 filename 设置。")


if __name__ == "__main__":
    main()
