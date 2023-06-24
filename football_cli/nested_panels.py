from collections import defaultdict
from rich.console import RenderableType, Group
from rich.panel import Panel
from rich.align import AlignMethod
from nested_defaultdict import NestedDefaultDict
from typing import Optional


class NestedPanels:
    """Handle nested panels construction using `NestedDefaultDict`."""

    PANEL_COLORS = ["cyan", "yellow", "green"]

    def __init__(self):
        self.panels = NestedDefaultDict()

    def get(self, keys: list, default: RenderableType) -> RenderableType:
        """If all (sub-)keys are in the nested panels dictionary, return the value. Otherwise insert `default` value and return it."""
        return self.panels.setdefault(keys, default)

    def sort_panels(self, dict_: defaultdict, keywords: tuple[str] = ("matchday", "group")) -> list[tuple]:
        """Sort panels dictionary at some level if its keys start with some keywords."""
        items_ = list(dict_.items())
        if None in dict_.keys():
            return items_

        key = str(items_[0][0]).lower()
        if key.startswith(keywords) and key != "group_stage":
            items_.sort()

        return items_

    def construct(
        self, panels_dict: Optional[NestedDefaultDict | RenderableType] = None,
        align: AlignMethod = "left", level=0
    ) -> tuple[RenderableType, str]:
        """Construct panels recursively from a nested dictionary.

        :param panels_dict: nested dictionary containing panels info at some level,or renderable object if it's the last level (leaf)
        :param align: align method of the panel title
        :param level: nesting level

        :return: renderable nested panels as well as title
        """
        if panels_dict is None:     # level == 0 (root)
            panels_dict = self.panels

        if isinstance(panels_dict, RenderableType):     # Leaf value
            return panels_dict, ""

        panels = []
        return_title = ""
        items_ = self.sort_panels(panels_dict)
        for title, dict_ in items_:
            if not dict_:
                continue

            sub_panels, sub_title = self.construct(dict_, level=level+1)

            full_title = self.get_full_title(title, sub_title)

            # If it's the only panel, don't create it and delegate the creation responsibility to the parent,
            # in order not to create redundant panels (exept for the root panel)
            if len(panels_dict) == 1 and level:
                return sub_panels, full_title

            if not full_title:
                return_title = full_title
                panels.append(sub_panels)
                continue

            # Create a panel containing all sub-panels
            containing_panel = Panel(
                Group(sub_panels, fit=True),
                title=full_title,
                title_align=align,
                border_style=f"{self.PANEL_COLORS[level % len(self.PANEL_COLORS)]}"
            )
            panels.append(containing_panel)

        return Group(*panels, fit=True), return_title

    @staticmethod
    def get_full_title(title: str, sub_title: str) -> str:
        """Return full panel title by concatenating the panel title and the title of the sub panel in case it's the only one, hence, it wasn't created."""
        full_title = title or ""
        full_title += " | " if title and sub_title else ""
        full_title += sub_title or ""

        return full_title
