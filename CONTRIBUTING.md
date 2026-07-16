# Contributing

Fork it. Improve any part. Send a PR.

## Ground rules

1. **No ToS violations.** Every extraction path must use documented or tolerated surfaces.
2. **No jailbreaks or security exploits.** Ever.
3. **No secrets in commits.** Credentials go in `.liberation-kit/credentials.enc`, which is `.gitignore`d.
4. **Manifest schema compliance.** Every new module must emit manifest entries per [`docs/design.md`](docs/design.md).
5. **Timezone-correct timestamps.** UTC canonical, local preserved.
6. **Idempotent.** Running the same module twice does nothing the second time.
7. **No inference in base layout.** Store what platforms gave; put derived indices in optional side directories.
8. **Portable without the kit.** A user should be able to navigate the output with `jq`, `sqlite3`, and standard image tools.

## PR flow

1. Fork.
2. Branch from `main`. Name the branch after the module or the item: `module/apple-notes`, `wanted/fitbit-history`, `fix/ical-timezone-bug`.
3. Write code + tests + a short module README.
4. Update `WANTED.md` if you're completing an item there.
5. Open the PR. Include: what you built, what extraction path you used, what platforms/versions you tested on, any gotchas.

## What "better" means

The base model swaps in your version if any of these hold:

- Wider platform coverage (more OS versions, more account types, more regions).
- Faster (measurably, at reasonable scale).
- Cleaner (fewer dependencies, simpler code, better tests).
- More complete (more of what the platform actually has).
- Better documented.

We do not swap on style alone. Working code beats prettier code.

## Communication

Open an issue before starting a big module so we don't duplicate. For small fixes, just send the PR.

## Attribution

Contributors are listed in `CONTRIBUTORS.md` (created on first PR merge). Attribution is welcomed. It is not required — if you want to contribute anonymously or under a pseudonym, that's fine.

## Governance

This repo has no ideology and no governing framework. Decisions on what to merge are made by the maintainers based on the "what better means" list above. Disputes go to a rolling maintainers' vote. If you want to become a maintainer, contribute regularly and it happens.
