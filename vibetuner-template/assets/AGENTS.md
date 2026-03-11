# Assets Directory

Place project icons and branding assets here.

## Conductor Integration

[Conductor](https://conductor.build) displays a repo icon in its sidebar.
It searches for icon files at the repository root in a fixed order
([docs](https://docs.conductor.build/faq#where-does-conductor-get-the-repo-icon)).

A `favicon.svg` symlink at the repo root points here. To enable the
Conductor icon, place your `favicon.svg` in this directory:

```text
assets/favicon.svg    <-- your icon goes here
favicon.svg           <-- symlink (already set up)
```

### Supported filenames (checked in order)

1. `public/apple-touch-icon.png`
2. `apple-touch-icon.png`
3. `public/favicon.svg`
4. `favicon.svg`
5. `public/favicon.png`
6. `public/icon.png`
7. `public/logo.png`
8. `favicon.png`
9. `app/icon.png`
10. `src/app/icon.png`
11. `public/favicon.ico`
12. `favicon.ico`
13. `app/favicon.ico`
14. `static/favicon.ico`
15. `src-tauri/icons/icon.png`
16. `assets/icon.png`
17. `src/assets/icon.png`
