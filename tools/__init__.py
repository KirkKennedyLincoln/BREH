from smolagents import DuckDuckGoSearchTool, VisitWebpageTool  # type: ignore[import-untyped]

from .scaling_tool import ScalingPredictorTool
from .etcd_tool import GetGraphTool, ListGraphsTool, PutGraphTool


def build_step_tools(models_dir: str = "models") -> dict:
    """Tool registry indexed by the name a graph step references in `step["tool"]`.
    Used by both the host executor (inline path) and the in-container entrypoint.
    Keys are taken from each tool's `.name` so they stay in sync if smolagents
    renames a built-in.
    """
    search = DuckDuckGoSearchTool()
    webpage = VisitWebpageTool()
    scaler = ScalingPredictorTool(models_dir=models_dir)
    return {
        scaler.name: scaler,
        search.name: search,
        webpage.name: webpage,
    }


__all__ = [
    'ScalingPredictorTool',
    'GetGraphTool',
    'ListGraphsTool',
    'PutGraphTool',
    'DuckDuckGoSearchTool',
    'VisitWebpageTool',
    'build_step_tools',
]
