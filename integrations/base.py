from abc import ABC, abstractmethod


class NoteApp(ABC):
    """Base class for all note-taking app integrations."""

    @property
    @abstractmethod
    def app_id(self) -> str:
        """Unique identifier (e.g. 'obsidian', 'logseq', 'notion')."""
        pass

    @property
    @abstractmethod
    def nome(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    def configurado(self) -> bool:
        """Returns True if the integration has all required settings."""
        pass

    @abstractmethod
    def formatar(self, texto: str, callbacks: dict) -> None:
        """Format plain text for this app via AI. Results delivered through callbacks:
        on_status(msg), on_formatado(md), on_erro(msg)."""
        pass

    @abstractmethod
    def salvar(self, conteudo: str, nome_inteligente: str, nome_custom: str, callbacks: dict) -> None:
        """Save formatted content to this app. Results delivered through callbacks:
        on_status(msg), on_salvar_concluido(path_or_url, nome), on_erro(msg)."""
        pass
