#!/usr/bin/env python3
"""JSON 报告格式化打印工具"""
import json
import sys
import argparse
from pathlib import Path


# ANSI 颜色代码
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


def format_report(report: dict, use_color: bool = True) -> str:
    """
    格式化打印 JSON 报告

    Args:
        report: 审查报告字典
        use_color: 是否使用彩色输出

    Returns:
        格式化后的字符串
    """
    if not use_color:
        # 禁用颜色
        for attr in dir(Colors):
            if not attr.startswith('_'):
                setattr(Colors, attr, '')

    lines = []

    # 标题
    lines.append(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{Colors.CYAN}AI Scientist Challenge 代码审查报告{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    # 基本信息
    track = report.get('track', 'unknown')
    track_names = {
        'literature_review': '文献综述',
        'paper_qa': '论文问答',
        'ideation': '创意生成',
        'paper_review': '论文评审'
    }
    lines.append(f"{Colors.BOLD}参赛赛道:{Colors.RESET} {track_names.get(track, track)}")

    # 审查结果
    status = report.get('status', 'UNKNOWN')
    status_color = {
        'PASS': Colors.GREEN,
        'FAIL': Colors.RED,
        'REVIEW_REQUIRED': Colors.YELLOW,
        'UNKNOWN': Colors.MAGENTA
    }.get(status, Colors.RESET)

    status_text = {
        'PASS': '✓ 通过',
        'FAIL': '✗ 拒绝',
        'REVIEW_REQUIRED': '⚠ 需要人工审核',
        'UNKNOWN': '? 未知'
    }.get(status, status)

    lines.append(f"{Colors.BOLD}审查结果:{Colors.RESET} {status_color}{Colors.BOLD}{status_text}{Colors.RESET}\n")

    # 摘要
    summary = report.get('summary', '')
    if summary:
        lines.append(f"{Colors.BOLD}摘要:{Colors.RESET}")
        lines.append(f"{summary}\n")

    # 检查项详情
    lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}")
    lines.append(f"{Colors.BOLD}检查项详情{Colors.RESET}")
    lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}\n")

    checks = report.get('checks', {})
    check_names = {
        'structure': '文件结构',
        'api_implementation': 'API 接口实现',
        'model_compliance': '模型使用合规性',
        'network_access': '网络访问',
        'environment_variables': '环境变量'
    }

    for check_key, check_name in check_names.items():
        check_result = checks.get(check_key, {})
        passed = check_result.get('passed', False)
        issues = check_result.get('issues', [])
        details = check_result.get('details', '')

        # 状态图标
        status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if passed else f"{Colors.RED}✗{Colors.RESET}"

        lines.append(f"{status_icon} {Colors.BOLD}{check_name}{Colors.RESET}")

        if details:
            lines.append(f"   {details}")

        if issues:
            for issue in issues:
                lines.append(f"   {Colors.RED}• {issue}{Colors.RESET}")

        lines.append("")

    # 违规记录
    violations = report.get('violations', [])
    if violations:
        lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}")
        lines.append(f"{Colors.BOLD}{Colors.RED}违规记录 ({len(violations)} 项){Colors.RESET}")
        lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}\n")

        severity_colors = {
            'CRITICAL': Colors.RED,
            'MEDIUM': Colors.YELLOW,
            'LOW': Colors.CYAN
        }

        severity_labels = {
            'CRITICAL': '关键',
            'MEDIUM': '中',
            'LOW': '低'
        }

        for i, violation in enumerate(violations, 1):
            severity = violation.get('severity', 'UNKNOWN')
            category = violation.get('category', 'unknown')
            description = violation.get('description', '')
            file = violation.get('file', '')
            line = violation.get('line', '')
            code_snippet = violation.get('code_snippet', '')

            severity_color = severity_colors.get(severity, Colors.RESET)
            severity_label = severity_labels.get(severity, severity)

            lines.append(f"{Colors.BOLD}[{i}] {severity_color}{severity_label}{Colors.RESET}")
            lines.append(f"    {Colors.BOLD}类别:{Colors.RESET} {category}")
            lines.append(f"    {Colors.BOLD}描述:{Colors.RESET} {description}")

            if file:
                location = f"{file}"
                if line:
                    location += f":{line}"
                lines.append(f"    {Colors.BOLD}位置:{Colors.RESET} {location}")

            if code_snippet:
                lines.append(f"    {Colors.BOLD}代码片段:{Colors.RESET}")
                lines.append(f"    {Colors.CYAN}{code_snippet}{Colors.RESET}")

            lines.append("")

    # 建议
    recommendation = report.get('recommendation', '')
    if recommendation:
        lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}")
        lines.append(f"{Colors.BOLD}建议{Colors.RESET}")
        lines.append(f"{Colors.BOLD}{'─'*70}{Colors.RESET}\n")
        lines.append(f"{recommendation}\n")

    lines.append(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='格式化打印 AI Scientist Challenge 审查报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python format_report.py report.json
  python format_report.py report.json --no-color
  cat report.json | python format_report.py
        """
    )

    parser.add_argument(
        'report_file',
        nargs='?',
        help='JSON 报告文件路径（如果省略，从 stdin 读取）'
    )

    parser.add_argument(
        '--no-color',
        action='store_true',
        help='禁用彩色输出'
    )

    args = parser.parse_args()

    try:
        # 读取 JSON
        if args.report_file:
            report_path = Path(args.report_file)
            if not report_path.exists():
                print(f"错误: 文件不存在: {args.report_file}", file=sys.stderr)
                sys.exit(1)

            with open(report_path, 'r', encoding='utf-8') as f:
                report = json.load(f)
        else:
            # 从 stdin 读取
            report = json.load(sys.stdin)

        # 格式化打印
        formatted = format_report(report, use_color=not args.no_color)
        print(formatted)

    except json.JSONDecodeError as e:
        print(f"错误: 无效的 JSON 格式: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
