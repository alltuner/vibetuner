#!/usr/bin/env uv run --script --with cloudflare --with click

# vim: filetype=python

import os
import re
import sys

import click
import rich
from cloudflare import Cloudflare


DEST: str = "135.181.131.150"


@click.group()
def cli():
    """Cloudflare DNS helper"""
    pass


def get_cf_client():
    api_token = os.getenv("CF_API_TOKEN")
    if not api_token:
        print("Error: CF_API_TOKEN environment variable not set.")
        sys.exit(1)
    return Cloudflare(api_token=api_token)


def split_fqdn(fqdn: str) -> tuple[str | None, str]:
    parts = fqdn.split(".")
    if len(parts) < 3:
        return None, fqdn
    return ".".join(parts[:-2]), ".".join(parts[-2:])


def is_valid_domain(domain: str) -> bool:
    domain = domain.strip()
    if len(domain) > 253:
        return False
    pattern = r"^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}$"
    return bool(re.match(pattern, domain))


@cli.command()
@click.argument("record")
def add_dns_record(record: str, dest: str = DEST):
    cf = get_cf_client()
    stem, domain = split_fqdn(record)

    if not is_valid_domain(domain):
        print("Invalid domain")
        return

    print(f"Identified {domain=} and {stem=} for {record=}")

    # Get zones and find matching domain
    zones = {z.name: z for z in cf.zones.list()}
    if domain not in zones:
        print("Zone not found")
        return

    zone = zones[domain]
    fqdn = f"{stem}.{domain}" if stem else domain

    # Check existing records
    dns_records = [
        record
        for record in cf.dns.records.list(zone_id=zone.id, name={"exact": fqdn}).result
        if record.type in ("A", "CNAME", "AAAA")
    ]

    ssl_setting = cf.zones.settings.get(zone_id=zone.id, setting_id="ssl")
    if ssl_setting is not None and ssl_setting.value != "strict":  # type: ignore
        cf.zones.settings.edit(zone_id=zone.id, setting_id="ssl", value="strict")

    if dns_records:
        print("Overlapping record already present, use web interface to remove it")
        rich.print(dns_records)
        return

    print("Record not present, proceeding to add")
    cf.dns.records.create(
        zone_id=zone.id,
        type="A",
        name=fqdn,
        content=dest,
        proxied=True,
        comment="Auto-added by magic",
    )


if __name__ == "__main__":
    cli()
