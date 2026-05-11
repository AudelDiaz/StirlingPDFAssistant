import abc
from typing import Any, Dict, List, Optional, Tuple


class BaseTool(abc.ABC):
    """
    Abstract base class for all Stirling PDF tools.
    Designed for alignment with the Model Context Protocol (MCP).
    """

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """The machine-readable name of the tool."""
        pass

    @property
    @abc.abstractmethod
    def description(self) -> str:
        """A detailed description of what the tool does."""
        pass

    @property
    @abc.abstractmethod
    def endpoint(self) -> str:
        """The API endpoint for this tool."""
        pass

    @property
    @abc.abstractmethod
    def input_schema(self) -> Dict[str, Any]:
        """JSON Schema defining the tool's input parameters."""
        pass

    @abc.abstractmethod
    def prepare_payload(self, **kwargs) -> Tuple[List[tuple], Dict[str, Any]]:
        """
        Processes raw arguments into a (files, data) tuple for multipart/form-data.

        Returns:
            Tuple[List[tuple], Dict[str, Any]]: (files, form_data)
        """
        pass
