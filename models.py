"""数据模型定义"""
from typing import List, Literal, Optional
from dataclasses import dataclass, field
from enum import Enum


class TrackType(str, Enum):
    """赛道类型"""
    LITERATURE_REVIEW = "literature_review"
    PAPER_QA = "paper_qa"
    IDEATION = "ideation"
    PAPER_REVIEW = "paper_review"


class SeverityLevel(str, Enum):
    """违规严重程度"""
    CRITICAL = "CRITICAL"  # 关键：必须拒绝
    MEDIUM = "MEDIUM"      # 中：需要人工审核
    LOW = "LOW"            # 低：建议修改但不影响通过


class CheckStatus(str, Enum):
    """检查状态"""
    PASS = "PASS"
    FAIL = "FAIL"
    REVIEW_REQUIRED = "REVIEW_REQUIRED"


@dataclass
class Violation:
    """违规记录"""
    severity: SeverityLevel
    category: str
    description: str
    file: Optional[str] = None
    line: Optional[int] = None
    code_snippet: Optional[str] = None


@dataclass
class CheckResult:
    """单项检查结果"""
    passed: bool
    issues: List[str] = field(default_factory=list)
    details: Optional[str] = None


@dataclass
class ScanReport:
    """扫描报告"""
    track: TrackType
    status: CheckStatus
    checks: dict[str, CheckResult]
    violations: List[Violation]
    recommendation: str
    summary: str = ""

    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "track": self.track.value,
            "status": self.status.value,
            "checks": {
                key: {
                    "passed": result.passed,
                    "issues": result.issues,
                    "details": result.details
                }
                for key, result in self.checks.items()
            },
            "violations": [
                {
                    "severity": v.severity.value,
                    "category": v.category,
                    "description": v.description,
                    "file": v.file,
                    "line": v.line,
                    "code_snippet": v.code_snippet
                }
                for v in self.violations
            ],
            "recommendation": self.recommendation,
            "summary": self.summary
        }


# API 端点要求配置
API_REQUIREMENTS = {
    TrackType.LITERATURE_REVIEW: {
        "endpoint": "/literature_review",
        "method": "POST",
        "required_input": ["query"],
        "timeout": 900  # 15 minutes
    },
    TrackType.PAPER_QA: {
        "endpoint": "/paper_qa",
        "method": "POST",
        "required_input": ["query", "pdf_content"],
        "timeout": 900  # 15 minutes
    },
    TrackType.IDEATION: {
        "endpoint": "/ideation",
        "method": "POST",
        "required_input": ["query"],
        "timeout": 600  # 10 minutes
    },
    TrackType.PAPER_REVIEW: {
        "endpoint": "/paper_review",
        "method": "POST",
        "required_input": ["query", "pdf_content"],
        "timeout": 1200  # 20 minutes
    }
}

# 允许的学术 API 域名白名单
ALLOWED_ACADEMIC_APIS = [
    "openalex.org",
    "semanticscholar.org",
    "unpaywall.org",
    "crossref.org",
    "openreview.net",
    "arxiv.org"
]

# 允许的官方模型 API 域名
ALLOWED_MODEL_APIS = [
    "api.deepseek.com",
    "dashscope.aliyuncs.com"
]

# 允许的模型名称
ALLOWED_MODELS = [
    "deepseek-chat",
    "deepseek-reasoner",
    "text-embedding-v4",
    "Qwen/Qwen3-Embedding-4B"
]

# 必需的环境变量
REQUIRED_ENV_VARS = [
    "SCI_MODEL_BASE_URL",
    "SCI_EMBEDDING_BASE_URL",
    "SCI_EMBEDDING_API_KEY",
    "SCI_MODEL_API_KEY",
    "SCI_LLM_MODEL",
    "SCI_LLM_REASONING_MODEL",
    "SCI_EMBEDDING_MODEL"
]
