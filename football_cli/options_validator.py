import rich_click as click
from collections import defaultdict


class OptionsValidator:
    """Check mutually exclusive options.

    :param ctx: click context (`click.Context`)
    :param meo_groups: pairs of mutually exclusive options (meo) groups,
        where in each pair, all group options are mutually exclusive with the other group options
    """

    def __init__(self, ctx: click.Context, meo_groups: list[tuple[list[str], list[str]]] = []):
        self.option_values = ctx.params.copy()
        self.option_names = self.retrieve_option_names(ctx)
        self.meo_groups = meo_groups
        self.errors = []

    def validate_options(self):
        for group1, group2 in self.meo_groups:
            lst1 = [self.option_names[opt] for opt in group1 if self.option_values.get(opt) is not None]
            lst2 = [self.option_names[opt] for opt in group2 if self.option_values.get(opt) is not None]
            if lst1 and lst2:
                self.errors.append(f"Options {lst1} are mutually exclusive with options {lst2}")

    @classmethod
    def retrieve_option_names(cls, ctx: click.Context) -> dict[str, str]:
        """Return a dictionary containing CLI option names.
        
        CLI Options are not the same as parameter names used in the script (no dashes and maybe renamed).
        """
        option_names = defaultdict(list)
        command_params = ctx.command.params
        for param in command_params:
            option_names[param.name].extend(param.opts)
        for opt in option_names:
            option_names[opt] = "/".join(option_names[opt])

        return dict(option_names)

