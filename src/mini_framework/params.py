from dataclasses import dataclass


class Param:
    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover
        return f"{type(self).__name__}()"


class Path(Param):
    __slots__ = ()


class Query(Param):
    __slots__ = ()


class Body(Param):
    __slots__ = ()


@dataclass(frozen=True, slots=True, kw_only=True)
class BodyModel(Body):
    embed: bool = False


class Field(Param):
    __slots__ = ()


class File(Param):
    __slots__ = ()


class Header(Param):
    __slots__ = ()


class Cookie(Param):
    __slots__ = ()
