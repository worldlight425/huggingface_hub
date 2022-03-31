# Code generated by jtd-codegen for Python v0.3.1

from dataclasses import dataclass, field
from typing import Any, List, Optional

from typing_extensions import TypeAlias


ModelIndexSet: TypeAlias = "List[ModelIndex]"


@dataclass
class ModelIndex:
    name: str
    results: "List[SingleResult]"


@dataclass
class SingleMetric:
    type: str
    """
    Example: wer
    """

    value: Any
    """
    Example: 20.0 or "20.0 ± 1.2"
    """

    args: Any = field(default=None)
    name: Optional[str] = field(default=None)


@dataclass
class SingleResultTask:
    type: str
    """
    Example: automatic-speech-recognition Use task id from
    https://github.com/huggingface/huggingface_hub/blob/main/js/src/lib/int
    erfaces/Types.ts
    """

    name: Optional[str] = None
    """
    Example: Speech Recognition
    """


@dataclass
class SingleResultDataset:
    """
    This will switch to required at some point. in any case, we need them to
    link to PWC
    """

    name: str
    """
    Example: Common Voice zh-CN Also encode config params into the name if
    relevant.
    """

    type: str
    """
    Example: common_voice. Use dataset id from https://hf.co/datasets
    """

    args: Any = None
    """
    Example: zh-CN
    """


@dataclass
class SingleResult:
    metrics: "List[SingleMetric]"
    task: "SingleResultTask"
    dataset: "Optional[SingleResultDataset]"
    """
    This will switch to required at some point. in any case, we need them to
    link to PWC
    """
