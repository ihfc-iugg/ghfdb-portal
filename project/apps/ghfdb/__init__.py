"""The database package contains all modules related to the creation of
schema specific to the Global Heat Flow Database. This includes database
models, administration classes, enumerators (choices), custom widgets, etc..."""
__version__ = "0.1.0"
__version_info__ = tuple(
    int(num) if num.isdigit() else num
    for num in __version__.replace("-", ".", 1).split(".")
)
