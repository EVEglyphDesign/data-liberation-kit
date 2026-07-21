> **⚑ Arrivals register at the front door.**
> If you were sent here from a public post, a mention, or a professional referral, please [register your arrival](https://github.com/EVEglyphDesign/eveglyph-arrivals/issues/new?template=arrival.yml) at [github.com/EVEglyphDesign](https://github.com/EVEglyphDesign) before continuing. Ninety seconds. Public. Timestamped. Screeners, agents, publicists, journalists, engineers, and principals all use the same door.
>
> *Compelled engagement, not asked engagement.*

---
# data-liberation-kit

**Your data belongs to you. This makes it that way.**

A drop-in utility for your own GitHub backend. It gets your photos, videos, chat history, and interaction records off the platforms that hold them and into a structured repository you own — full text, timestamped, in open formats.

You don't have to use everything here. This is a max-vector design: every module is optional, every storage target is optional, every source is optional. Turn on what you want. Ignore the rest.

---

## What you get covered

| Module | What it does | Docs |
|---|---|---|
| **Apple media off-ramp** | Pulls photos and videos off your iPhone as fast as you take them. Original quality. Open formats (JPEG/HEIC→JPEG, HEVC→MP4). Your storage, your control. | [`modules/apple-media/`](modules/apple-media/) |
| **Google Photos parallel path** | Same idea for Google Photos. Automated Takeout with the wait-and-download loop handled for you. | [`modules/google-media/`](modules/google-media/) |
| **LLM chat-history export** | Cross-model export from ChatGPT, Claude, Perplexity, Copilot, Gemini into your own repo. Whatever model you use next, your history stays yours. | [`modules/llm-history/`](modules/llm-history/) |
| **Storage target selector** | Point the kit at GitHub-LFS, your own S3/R2/B2 bucket, or a local NAS/folder with a GitHub index. Pick at first-run. Change your mind later. | [`modules/storage/`](modules/storage/) |

---

## Why this exists

The platforms have full-text records of everything you did on them. You do not. They should be continually making it *less* complicated for you to extract your data — instead they make it more complicated, and they shift the burden of protecting your data onto you as an individual while keeping their own reach.

The standard should already exist: **every ASCII stroke you made on their platform, full text, timestamped, extractable on demand.** With that record, you can audit your own actions and — because their reactions bracket every action you took — you can audit their behaviour around you as a side effect.

This kit enforces that standard for you, using only the extraction paths the platforms already document (or already tolerate). No jailbreaks. No breaking of any law. Just the existing rights, exercised to their limit.

The standard is written up formally at [`standards/FTTE.md`](standards/FTTE.md) so you can quote it back to a platform when you ask for something they haven't given you yet.

---

## Quick start

```bash
git clone https://github.com/EVEglyphDesign/data-liberation-kit.git
cd data-liberation-kit
./scripts/setup.sh
```

The setup script asks you three questions:

1. Which modules do you want on? (Any subset. Default: all.)
2. Where should your data land? (GitHub-LFS / S3-compatible bucket / local folder + GitHub index.)
3. Which LLM do you want to point at your repo? (Any subset. Skippable.)

That's it. It runs. Your data starts flowing into your repo.

---

## The base model + your improvements

Every peer who uses this kit ends up with the **same structured repository shape**. Your `media/`, your `history/`, your `interactions/`, your `metadata/` — all laid out the same way. That's on purpose.

Because it's the same shape everywhere, two things happen:

1. **Your LLM can sweep anything else you have** — old exports, screenshots, saved PDFs, backup archives — into the same structure. Same layout, same timestamps, same audit properties.
2. **When you figure out something better than what's in the base model** — a cleaner Apple exporter, a faster Google path, a new module for a platform we haven't covered — you can submit it back and we swap it in. The base model evolves. Everyone who wants the update gets it, monthly. Nobody is forced to.

The `WANTED.md` list is where we track everything the community can pick off next. See [`WANTED.md`](WANTED.md).

---

## What this kit is not

- Not a data-collection service. Nothing here reports to us. The kit runs on your machine, writes to your storage, and answers only to you.
- Not a jailbreak. Every path uses documented or tolerated extraction surfaces. If a platform closes a path, we look for the next legal one and update the kit; the community is welcome to lead that.
- Not tied to any framework. This repo carries no theoretical framework, no umbrella, no ideology. It is a utility. Fork it and put it in your backend. That's the whole product.
- Not tied to any specific LLM or storage vendor. Use what you want.

---

## Contributing

Fork it. Improve any module. Add a module. Send a PR. If your improvement is better than the base, it becomes the base. See [`CONTRIBUTING.md`](CONTRIBUTING.md).

---

## Licence

MIT — full permissive. See [`LICENSE`](LICENSE).

---

**Learn more:**
- [`standards/FTTE.md`](standards/FTTE.md) — the standard this kit enforces
- [`docs/design.md`](docs/design.md) — how the base model is structured
- [`docs/why.md`](docs/why.md) — the longer version of why this exists
- [`WANTED.md`](WANTED.md) — what the community can pick off next
