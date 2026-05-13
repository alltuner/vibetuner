#!/usr/bin/env bun
// ABOUTME: Re-exposes the `tailwindcss` CLI bin from @tailwindcss/cli so scaffolded
// ABOUTME: projects can `bun tailwindcss ...` without declaring it as a direct dep.
import { createRequire } from "node:module";
import { dirname, join } from "node:path";

const require = createRequire(import.meta.url);
const pkgPath = require.resolve("@tailwindcss/cli/package.json");
const { bin } = require("@tailwindcss/cli/package.json");

await import(join(dirname(pkgPath), bin.tailwindcss));
