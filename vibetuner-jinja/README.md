# @alltuner/vibetuner-jinja

The vibetuner framework's core jinja templates, packaged for npm so that
tailwind can scan them for class names at build time.

## Why this exists

The Python framework `vibetuner` ships its own jinja templates (base
layouts, auth pages, debug pages, the user menu, language picker, etc.).
When a project built on vibetuner runs `bun run dev` or `bun run
build-prod`, tailwind needs to scan these framework templates so that
classes used only there (e.g. the styling on the login page or the debug
toolbar) end up in the final `bundle.css`.

Having the bun-side build tooling shell out to the Python interpreter to
locate the templates inside the venv was painful — it broke in any context
where uv wasn't available (bun-only docker stages, sandboxed CI). This
package mirrors the templates so bun resolves them through normal node
module resolution.

## How to use it

You almost certainly don't install this package directly. It's pulled in
as a transitive dependency of `@alltuner/vibetuner`, and projects using
the vibetuner template `@import "@alltuner/vibetuner/core.css"` from
their `config.css` — that core file in turn imports this package's
`sources.css`, which contains the one-line `@source "./templates"`
directive needed for tailwind class scanning.

If you do need to wire it up manually (e.g. you're building a non-template
consumer):

```css
@import "@alltuner/vibetuner-jinja/sources.css";
```

## Source of truth

The canonical copy of the templates lives in
`vibetuner-py/src/vibetuner/templates/frontend/` in the
[vibetuner monorepo](https://github.com/alltuner/vibetuner). This package
is re-published whenever those templates change, in lockstep with the rest
of the framework via release-please.

`templates/` here is a generated mirror. It's not committed to git — the
package's `prepare` lifecycle hook (`scripts/sync.sh`) regenerates it from
the Python source whenever it runs (workspace `bun install` in the
monorepo, `npm pack`, `npm publish`). Consumers installing from the npm
registry get the templates baked into the published tarball, so no
post-install work happens on their end. Edit the Python copy; the mirror
follows automatically.
