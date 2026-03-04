def get_reuse_command(use_uv: bool) -> list[str]:
    """Return the way in which REUSE should be invoked depending on the value of `use_uv`."""
    return ["uv", "run", "reuse"] if use_uv else ["reuse"]
