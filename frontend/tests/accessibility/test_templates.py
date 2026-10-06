from html.parser import HTMLParser
from pathlib import Path


TEMPLATE_ROOT = Path(__file__).parents[2] / "templates"
BASE_TEMPLATE = TEMPLATE_ROOT / "base.html"
PRIMARY_PAGES = (
    TEMPLATE_ROOT / "auth/login.html",
    TEMPLATE_ROOT / "auth/register.html",
    TEMPLATE_ROOT / "auth/recovery.html",
    TEMPLATE_ROOT / "auth/inactive.html",
    TEMPLATE_ROOT / "workspace.html",
    TEMPLATE_ROOT / "organization/index.html",
    TEMPLATE_ROOT / "tasks/index.html",
    TEMPLATE_ROOT / "follow-up/index.html",
    TEMPLATE_ROOT / "reports/index.html",
)


class _AccessibilityParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.controls: list[dict[str, str]] = []
        self.labels: set[str] = set()
        self.heading_levels: list[int] = []
        self.invalid_click_targets: list[str] = []
        self.label_depth = 0
        self.labeled_controls: set[int] = set()

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "label":
            self.label_depth += 1
        if tag == "label" and attributes.get("for"):
            self.labels.add(attributes["for"])
        if tag in {"input", "select", "textarea"}:
            self.controls.append(attributes)
            if self.label_depth:
                self.labeled_controls.add(len(self.controls) - 1)
        if tag.startswith("h") and len(tag) == 2 and tag[1].isdigit():
            self.heading_levels.append(int(tag[1]))
        if tag == "div" and "onclick" in attributes:
            self.invalid_click_targets.append(tag)

    def handle_endtag(self, tag):
        if tag == "label":
            self.label_depth = max(0, self.label_depth - 1)


def test_primary_templates_have_headings_and_labeled_controls():
    for page in PRIMARY_PAGES:
        parser = _AccessibilityParser()
        parser.feed(page.read_text(encoding="utf-8"))
        assert 1 in parser.heading_levels, page
        for index, control in enumerate(parser.controls):
            if control.get("type") == "hidden":
                continue
            assert (
                control.get("aria-label")
                or control.get("id") in parser.labels
                or index in parser.labeled_controls
            ), (page, control)


def test_templates_do_not_use_noninteractive_click_targets():
    for page in PRIMARY_PAGES:
        parser = _AccessibilityParser()
        parser.feed(page.read_text(encoding="utf-8"))
        assert parser.invalid_click_targets == [], page


def test_base_template_exposes_accessible_user_control():
    source = BASE_TEMPLATE.read_text(encoding="utf-8")

    assert 'aria-label="Menú de usuario"' in source
    assert 'id="logout-button"' in source
    assert 'type="button"' in source
    assert 'role="status"' in source
