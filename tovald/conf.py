"""Tovald configuration module."""

import os

extensions = [
    "myst_parser",
    "sphinxcontrib.confluencebuilder",
]

confluence_publish = True
confluence_publish_force = True
confluence_page_hierarchy = True
confluence_disable_notifications = True
confluence_disable_autogen_title = True

confluence_server_url = os.environ.get("CONFLUENCE_SERVER_URL")
confluence_space_key = os.environ.get("CONFLUENCE_SPACE_KEY")
confluence_parent_page = os.environ.get("CONFLUENCE_PARENT_PAGE")
confluence_publish_token = os.environ.get("CONFLUENCE_PAT")
