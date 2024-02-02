import jsonsubschema
import jsonschema

__all__ = ["__patch_version__"]
__patch_version__ = "0.0.1"


def _post_init(func, execute):
    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)
        execute(self)
        return result

    return wrapper


def _cast_numeric_to_draft4(self):
    if isinstance(self.exclusiveMaximum, (int, float)):
        self.maximum = self.exclusiveMaximum
        self.exclusiveMaximum = True
    if isinstance(self.exclusiveMinimum, (int, float)):
        self.minimum = self.exclusiveMinimum
        self.exclusiveMinimum = True


jsonsubschema._checkers.JSONTypeNumeric.__init__ = _post_init(jsonsubschema._checkers.JSONTypeNumeric.__init__, _cast_numeric_to_draft4)  # type: ignore
jsonsubschema.config.set_json_validator_version(jsonschema.Draft202012Validator)  # type: ignore
