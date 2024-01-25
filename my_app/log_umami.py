"""Track your API hits with umami (optional)."""

from my_app import UMAMI_SETTINGS


def send_page_view(list_type: str) -> None:
    """Send page hit to an ummami instance."""
    if not UMAMI_SETTINGS:
        return
    import umami

    umami.set_url_base(UMAMI_SETTINGS["umami_base_url"])
    # Skip the need to pass the target website in subsequent calls.
    umami.set_website_id(UMAMI_SETTINGS["umami_website_id"])
    umami.set_hostname(UMAMI_SETTINGS["umami_hostname"])
    umami.new_page_view(page_title="Umami-Test", url=f"/test/{list_type}")
