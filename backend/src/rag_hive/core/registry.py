"""Name → class registry for pipeline components.

Each component kind owns one registry (`parser_registry`, `chunker_registry`...). An
implementation registers itself with the `@registry.register` class decorator, and the
Planner later turns a benchmark config such as `{"parser": "pymupdf"}` into an instance
with `registry.create("pymupdf", {...})`.
"""

from collections.abc import Mapping

from rag_hive.core.component import Component


class RegistryError(Exception):
    """Base class for registry errors."""


class UnknownComponentError(RegistryError, LookupError):
    """No component is registered under the requested name."""


class DuplicateComponentError(RegistryError, ValueError):
    """A different class is already registered under that name."""


class InvalidComponentError(RegistryError, TypeError):
    """The class cannot be registered (missing or empty `name`)."""


class Registry[T: Component]:
    """Registry of the component classes of one kind."""

    def __init__(self, kind: str) -> None:
        """Create an empty registry.

        Args:
            kind: Human-readable component kind, used in error messages (e.g. "parser").
        """
        self.kind = kind
        self._classes: dict[str, type[T]] = {}

    def register(self, cls: type[T]) -> type[T]:
        """Register `cls` under its `name`. Usable as a class decorator.

        Re-registering the same class is a no-op, so module reloads are harmless.

        Raises:
            InvalidComponentError: If `cls.name` is missing or empty.
            DuplicateComponentError: If another class already uses that name.
        """
        name = getattr(cls, "name", None)
        if not isinstance(name, str) or not name:
            msg = f"{cls.__name__} must define a non-empty `name` to be registered as a {self.kind}"
            raise InvalidComponentError(msg)
        existing = self._classes.get(name)
        if existing is not None and existing is not cls:
            msg = f"{self.kind} {name!r} is already registered by {existing.__name__}"
            raise DuplicateComponentError(msg)
        self._classes[name] = cls
        return cls

    def get(self, name: str) -> type[T]:
        """Return the class registered under `name`.

        Raises:
            UnknownComponentError: If nothing is registered under `name`.
        """
        try:
            return self._classes[name]
        except KeyError:
            known = ", ".join(self.names()) or "none"
            msg = f"unknown {self.kind} {name!r} (registered: {known})"
            raise UnknownComponentError(msg) from None

    def create(self, name: str, config: Mapping[str, object] | None = None) -> T:
        """Instantiate the component `name`, validating `config` against its `config_model`.

        Raises:
            UnknownComponentError: If nothing is registered under `name`.
            pydantic.ValidationError: If `config` does not match the component's options.
        """
        cls = self.get(name)
        return cls(cls.config_model.model_validate(config or {}))

    def names(self) -> list[str]:
        """Return the registered names, sorted."""
        return sorted(self._classes)

    def __contains__(self, name: object) -> bool:
        """Return whether a component is registered under `name`."""
        return name in self._classes
