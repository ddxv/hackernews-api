"""Track your API hits with umami (optional)."""

from config import get_logger
from my_app import UMAMI_SETTINGS

logger = get_logger(__name__)


def send_page_view(list_type: str, ip:str|None) -> None:
    """Send page hit to an ummami instance."""
    if not UMAMI_SETTINGS:
        logger.info("no umami settings")
        return
    import umami

    umami.set_url_base(UMAMI_SETTINGS["umami_base_url"])
    # Skip the need to pass the target website in subsequent calls.
    umami.set_website_id(UMAMI_SETTINGS["umami_website_id"])
    umami.set_hostname(UMAMI_SETTINGS["umami_hostname"])
    umami.new_page_view(page_title="Umami-Log", url=f"/articles/list/{list_type}", ip_address=ip)
    logger.info("umami page view sent")
