#!/usr/bin/env python3
"""AI Scientist Challenge 代码审查工具 - 主程序"""
import asyncio
import json
import sys
import argparse
from pathlib import Path
from claude_agent_sdk import query, ClaudeAgentOptions
from claude_agent_sdk.types import AssistantMessage, TextBlock


async def scan_submission(submission_dir: str, track: str, output_file: str = None) -> dict:
    """
    扫描参赛代码

    Args:
        submission_dir: 参赛代码目录（绝对路径）
        track: 参赛赛道 (literature_review | paper_qa | ideation | paper_review)
        output_file: JSON 报告输出路径（可选）

    Returns:
        审查报告字典
    """
    # 验证目录
    submission_path = Path(submission_dir).resolve()
    if not submission_path.exists():
        raise FileNotFoundError(f"代码目录不存在: {submission_dir}")

    if not submission_path.is_dir():
        raise NotADirectoryError(f"不是有效的目录: {submission_dir}")

    # 验证赛道
    valid_tracks = ["literature_review", "paper_qa", "ideation", "paper_review"]
    if track not in valid_tracks:
        raise ValueError(f"无效的赛道: {track}。有效值: {', '.join(valid_tracks)}")

    # 读取提示词模板
    prompt_template_path = Path(__file__).parent / "prompts" / "code_review_prompt.md"
    prompt_template = prompt_template_path.read_text(encoding='utf-8')

    # 替换变量
    prompt = prompt_template.format(
        track=track,
        submission_dir=str(submission_path)
    )

    # 配置 Claude Agent
    options = ClaudeAgentOptions(
        system_prompt="你是一个严谨、专业的代码审查专家，擅长分析代码合规性和安全性。",
        permission_mode='bypassPermissions',  # 允许读取所有文件
        cwd=str(submission_path)  # 工作目录设为提交代码目录
    )

    print(f"\n{'='*70}")
    print(f"开始代码审查")
    print(f"{'='*70}")
    print(f"目录: {submission_path}")
    print(f"赛道: {track}")
    print(f"{'='*70}\n")

    # 收集 Agent 输出
    full_response = ""

    async for message in query(prompt=prompt, options=options):
        # 处理 AssistantMessage 中的文本内容
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    # 直接输出文本内容
                    print(block.text, end='', flush=True)
                    full_response += block.text

        # 检查是否完成
        elif hasattr(message, 'subtype') and message.subtype in ['success', 'error']:
            print(f"\n\n{'─'*70}")
            if hasattr(message, 'total_cost_usd') and message.total_cost_usd:
                print(f"审查完成 | 成本: ${message.total_cost_usd:.4f}")
            else:
                print(f"审查完成")
            print(f"{'─'*70}\n")
    print("\n正在提取 JSON 报告...\n")

    # 提取 JSON 报告
    report = extract_json_report(full_response)

    if report is None:
        raise RuntimeError(
            "无法从 Agent 响应中提取有效的 JSON 报告。"
            "请检查 Agent 输出是否包含正确的 JSON 代码块。"
        )

    # 保存报告
    if output_file:
        output_path = Path(output_file)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
        print(f"JSON 报告已保存: {output_file}\n")

    return report


def extract_json_report(response: str) -> dict:
    """
    从 Agent 响应中提取 JSON 报告

    优先查找 ```json 代码块，如果没有则尝试解析整个响应
    """
    import re

    # 查找 JSON 代码块
    json_pattern = r'```json\s*(\{.*?\})\s*```'
    matches = re.findall(json_pattern, response, re.DOTALL)

    if matches:
        # 取最后一个 JSON 块（可能 Agent 重试过）
        json_str = matches[-1]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"[!] 警告: JSON 代码块解析失败: {e}", file=sys.stderr)

    # 尝试查找任何 JSON 对象
    json_obj_pattern = r'\{[^{}]*"track"[^{}]*"status"[^{}]*\}'
    matches = re.findall(json_obj_pattern, response, re.DOTALL)

    for match in reversed(matches):  # 从后往前尝试
        try:
            # 尝试扩展匹配到完整的 JSON
            start = response.rfind('{', 0, response.index(match))
            end = response.find('}', response.index(match) + len(match)) + 1

            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except (json.JSONDecodeError, ValueError):
            continue

    return None


async def main():
    parser = argparse.ArgumentParser(
        description='AI Scientist Challenge 代码审查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python scan.py /path/to/submission literature_review
  python scan.py /path/to/submission paper_qa -o report.json
  python scan.py /path/to/submission ideation --output result.json

赛道选项:
  literature_review  - 文献综述
  paper_qa           - 论文问答
  ideation           - 创意生成
  paper_review       - 论文评审
        """
    )

    parser.add_argument(
        'submission_dir',
        help='参赛代码目录路径'
    )

    parser.add_argument(
        'track',
        choices=['literature_review', 'paper_qa', 'ideation', 'paper_review'],
        help='参赛赛道'
    )

    parser.add_argument(
        '-o', '--output',
        help='JSON 报告输出文件路径（默认不保存）'
    )

    args = parser.parse_args()

    try:
        report = await scan_submission(
            submission_dir=args.submission_dir,
            track=args.track,
            output_file=args.output
        )

        # 输出最终判定
        status = report.get('status', 'UNKNOWN')
        status_display = {
            'PASS': '通过',
            'FAIL': '拒绝',
            'REVIEW_REQUIRED': '需要人工审核',
            'UNKNOWN': '未知'
        }.get(status, status)

        print(f"{'='*70}")
        print(f"最终审查结果")
        print(f"{'='*70}")
        print(f"状态: {status_display}")
        print(f"{'='*70}\n")

        summary = report.get('summary', '')
        if summary:
            print(f"摘要:")
            print(f"{summary}\n")

        recommendation = report.get('recommendation', '')
        if recommendation:
            print(f"建议:")
            print(f"{recommendation}\n")

        print(f"{'='*70}\n")

        # 返回状态码
        if status == 'PASS':
            sys.exit(0)
        elif status == 'REVIEW_REQUIRED':
            sys.exit(1)
        else:  # FAIL
            sys.exit(2)

    except Exception as e:
        print(f"\n[错误] {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    asyncio.run(main())
