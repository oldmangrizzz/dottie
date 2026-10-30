"""Explicit dependency wiring for the research cognitive stack.

Does not contact any provider during construction. Real connections require
configured exact model tags, network reachability and approved requests.
"""
from dataclasses import dataclass, field
from .lfm3_local import LFM3LocalAdapter
from .ollama_cloud import OllamaCloudAdapter
from .laya import LAYAAdvisory


@dataclass(repr=False)
class CognitiveStack:
    local: LFM3LocalAdapter
    remote: OllamaCloudAdapter
    laya: LAYAAdvisory | None = None

    def __repr__(self):
        return "<CognitiveStack local=LFM3 remote=OllamaCloud laya=%s>" % ("configured" if self.laya else "absent")


def build_cognitive_stack(config, laya_advisor=None):
    local = LFM3LocalAdapter(model=config.get("LFM3_MODEL", ""))
    remote = OllamaCloudAdapter(model=config.get("OLLAMA_CLOUD_MODEL", ""),
                               api_key=config.get("OLLAMA_API_KEY", ""))
    laya = LAYAAdvisory(laya_advisor) if laya_advisor is not None else None
    return CognitiveStack(local=local, remote=remote, laya=laya)
