#!/usr/bin/env python3

import argparse
import os
import re
import sys

import rich
from cloudflare import Cloudflare


DEST: str = "135.181.131.150"


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


def add_record(record: str, cf: Cloudflare):
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
    if ssl_setting is not None and ssl_setting.value != "strict":
        cf.zones.settings.edit(zone_id=zone.id, setting_id="ssl", value="strict")

    return

    if dns_records:
        print("Overlapping record already present, use web interface to remove it")
        rich.print(dns_records)
        return

    print("Record not present, proceeding to add")
    cf.dns.records.create(
        zone_id=zone.id,
        type="A",
        name=fqdn,
        content=DEST,
        proxied=True,
        comment="Auto-added by magic",
    )


def main():
    parser = argparse.ArgumentParser(description="Cloudflare DNS helper")
    subparsers = parser.add_subparsers(dest="command")

    parser_add = subparsers.add_parser("add-record", help="Add a DNS record")
    parser_add.add_argument("record", help="Record to add")

    args = parser.parse_args()

    if args.command == "add-record":
        cf = get_cf_client()
        add_record(args.record, cf)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
