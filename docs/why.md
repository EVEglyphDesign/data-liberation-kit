# Why this exists

The long version of the note in the README.

## The current situation

Every global platform you interact with holds a full-text, timestamped record of everything you did on it. Every message you sent, every search you ran, every photo you uploaded, every keystroke sequence that produced a comment or an edit. They have it. They use it. It's how their products work, how their recommendations work, how their training data is assembled.

You do not have that record.

You have whatever fragments the platform decided to give you back:

- A photos app that shows you thumbnails but makes the originals hard to move.
- A chat app whose export function truncates, delays, or omits.
- An email account whose IMAP surface is technically open but whose modern data lives in web-only APIs.
- A phone whose default storage tier is designed to fill up so that the platform can sell you a bigger one, and whose exit ramps use proprietary formats.

The asymmetry has consequences. When you switch phones, most of your history stays behind or gets partially copied. When you switch platforms, the same. When a platform loses, corrupts, or misrepresents something you did, you have no way to check. When a model gets trained on the full record of your behaviour, you have no way to audit what it learned.

The most concrete example: Apple sells you a phone with 256 GB of storage. Their default apps and default sync behaviours will fill that 256 GB. Their export paths for what fills it are proprietary formats. When the phone is full, the option they offer is to buy a bigger phone. The 256 GB was never really yours; it was leased space for their formats.

Half the storage would be plenty if you could stream your own history off the device as it happens, into a repository you own, in open formats. That is what this kit does.

## What the platforms should be doing

If any of the global platforms wanted to close the asymmetry, they already know how. They already have the record. Giving the user a mirror of the record they already have is a small engineering task compared to building the record in the first place.

They should be continually making it *less* complicated to access your data rights and extract everything you've ever done with them. Not more complicated.

A platform that shipped natively:

- One-click delivery of every ASCII stroke you made on their surface, full text, timestamped.
- Full-fidelity binary for every non-text upload.
- The platform's own reactions bracketing each of your actions.
- Cryptographic integrity so you can verify the extract wasn't tampered with.

...would be meeting the standard we describe in [`standards/FTTE.md`](../standards/FTTE.md).

We think several platforms will get there eventually. This kit is the interim tool that gets people the record while the platforms catch up.

## What "data will replace gold" means in practice

The valuation of a person's data record is currently captured almost entirely by the platforms. That is a temporary condition. The tools that let individuals hold, verify, and use their own data record are catching up. When individuals hold auditable, complete, portable records of their own lives — text, media, interactions — those records become the foundation of a lot of things: retrospective search, personal AI, cross-platform continuity, evidence in disputes, legacy for family.

A record you cannot extract is not really yours. This kit is about making the record yours in fact, not just in principle.

## Balance of control, not opposition

We are not opposed to platforms. We use their surfaces. We benefit from what they built. The kit does not break their locks; it uses the existing extraction paths they document or tolerate, and it does so within the law in every jurisdiction it's used.

What we are doing is rebalancing control. Currently the individual is exploited: the individual carries the burden of protecting data the platform is holding, while the platform reaps the benefits of the data it holds. This kit shifts a small part of that balance back — not by taking anything from the platform, but by ensuring the individual has the same record the platform already has.

That is not an attack on the platform. That is the standard the platforms should already be meeting.

## Why open-source and forkable

Because no single team can cover every platform, every format, every extraction path. The Apple photo path is different from the Google Photos path is different from the iMessage archive path is different from the Google Drive path. Every one of them has quirks that only someone who works with that platform daily really understands.

The kit is designed to be forked, extended, improved, and merged back. If you have a better Apple exporter than the one in this repo, send us a PR — if it's better, it becomes the base and everyone gets the improvement. If you have a module for a platform we haven't covered, send us a PR. If you find a new extraction path that works better than what we ship, send us a PR.

The base model is expected to evolve monthly. Nobody is required to update. Everyone can if they want to.

## Non-goals

- We are not building a data-collection service. Nothing here reports to us.
- We are not building an "everything app." The kit is a utility, not a platform.
- We are not tied to any specific LLM, storage vendor, or platform.
- We are not carrying any theoretical framework or ideology inside this repo. The utility does the work; other repositories carry the frameworks.
- We are not encouraging anyone to break any law or any platform's terms of service. Every extraction path in the kit uses documented or tolerated surfaces.

## Getting involved

Fork the repo. Improve it. Send a PR. Or just use it and tell us what breaks. See [`CONTRIBUTING.md`](../CONTRIBUTING.md).
