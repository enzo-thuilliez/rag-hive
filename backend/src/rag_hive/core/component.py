"""Common base for parsers, chunkers, embedders, retrievers and LLM providers."""

from abc import ABC
from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class ComponentConfig(BaseModel):
    """Base for a component's options. Subclass it to add typed, validated fields."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class Component(ABC):
    """A named, configurable pipeline component.

    Subclasses set `name` (the registry key, stable across releases since benchmark results
    reference it) and, when they take options, `config_model`.
    """

    name: ClassVar[str]
    config_model: ClassVar[type[ComponentConfig]] = ComponentConfig

    def __init__(self, config: ComponentConfig | None = None) -> None:
        """Store the validated config, or the defaults of `config_model` when none is given.

        Raises:
            TypeError: If `config` is not an instance of this component's `config_model`.
        """
        if config is None:
            config = self.config_model()
        if not isinstance(config, self.config_model):
            msg = (
                f"{type(self).__name__} expects {self.config_model.__name__}, "
                f"got {type(config).__name__}"
            )
            raise TypeError(msg)
        self.config = config
