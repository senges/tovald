"""Tovald configuration module."""

import os


def getenv(env: str) -> str:
    """Environment variable grab convenience."""
    return os.environ.get(env, "")

extensions = [
    "myst_parser",
    "sphinxcontrib.confluencebuilder",
]

confluence_publish = True
confluence_publish_force = True
confluence_page_hierarchy = True
confluence_disable_notifications = True
confluence_disable_autogen_title = True

confluence_server_url = getenv("CONFLUENCE_SERVER_URL")
confluence_space_key = getenv("CONFLUENCE_SPACE_KEY")
confluence_parent_page = getenv("CONFLUENCE_PARENT_PAGE")
confluence_publish_token = getenv("CONFLUENCE_PAT")

confluence_page_generation_notice = True
confluence_sourcelink = {}
if sources := getenv("CONFLUENCE_SOURCES_URL"):
    confluence_sourcelink["url"] = sources

# Auto-generated heading anchors depth.
# Max value for ATX Headings according to Markdown spec.
# https://spec.commonmark.org/0.31.2/#atx-headings
myst_heading_anchors = 6
