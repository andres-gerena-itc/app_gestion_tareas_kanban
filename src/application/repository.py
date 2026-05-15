import abc
from src.domain.workspace import Workspace

class WorkspaceRepository(abc.ABC):
    """
    Puerto (interfaz) para el repositorio de persistencia.
    Ahora operamos sobre el Aggregate Root principal: Workspace.
    """
    @abc.abstractmethod
    def get_workspace(self) -> Workspace:
        """Recupera el Workspace actual (por ahora asumimos uno solo por defecto)."""
        pass

    @abc.abstractmethod
    def save_workspace(self, workspace: Workspace) -> None:
        """Persiste el estado completo del Workspace."""
        pass
