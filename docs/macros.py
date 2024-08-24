from mkdocs_macros.plugin import MacrosPlugin


class MacroException(Exception):
    pass


def define_env(env: MacrosPlugin) -> None:
    @env.macro
    def exception(message: str) -> None:
        raise MacroException(message)
