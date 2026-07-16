# WANTED — community pickups

Locks and extraction paths we haven't broken yet. If you can knock one of these off, send a PR. If your implementation is better than what's in the base model, it replaces the base model.

**Ground rules:** every path must use documented or tolerated extraction surfaces. Nothing that breaks any platform's terms of service. Nothing that requires a jailbreak. Nothing that requires exploiting a security vulnerability. If a path is legally grey in a jurisdiction, note the jurisdiction.

---

## Apple ecosystem

| Item | Difficulty | Notes |
|---|---|---|
| Full iCloud backup extraction (not just Photos) | Hard | The full iCloud backup bundle is the big one. Documented paths exist for third-party backup extractors but the flow is fragile. |
| iMessage archive with attachments | Hard | Local Mac path via `~/Library/Messages/` works but is Mac-only. iOS-only users need a different path. |
| Apple Notes with rich content preserved | Medium | CloudKit-based export loses rich formatting. A cleaner path would preserve tables, links, and attachments. |
| Apple Health full record | Medium | Health export via iOS Settings works but is monolithic. A continuous incremental sync would be better. |
| Apple Fitness and Workout data | Easy–Medium | Falls out of Health export but the per-workout details are worth normalising. |
| Voice Memos with transcripts | Easy | The audio is easy; the transcripts (if generated) are harder to extract. |
| Safari bookmarks + reading list + history | Medium | Some pieces sync via iCloud; a unified extractor would be useful. |
| HomeKit device history | Hard | Not documented as extractable. Explore before we ship. |
| Continuity handoff history | Hard | May not be extractable at all. Community exploration welcome. |

## Google ecosystem

| Item | Difficulty | Notes |
|---|---|---|
| Gmail full extract with labels + threads intact | Medium | Takeout gives mbox; a normalised JSONL with labels and thread integrity is more useful. |
| Google Drive with folder structure + share history | Medium | Takeout preserves files; the share/permission history is harder. |
| Google Docs edit history per document | Hard | Rich edit history is not in Takeout. Documented but tedious to extract per-document. |
| YouTube: comments, likes, subscriptions, watch history in structured form | Easy | Falls out of Takeout; wants normalising. |
| Google Maps: timeline + saved places + reviews | Medium | Timeline export is available; consolidating with Places and Reviews is the work. |
| Google Search history in structured form | Easy | Falls out of Takeout; wants normalising. |
| Android device backup (non-Pixel) | Hard | Varies by manufacturer; may need per-OEM modules. |

## LLM chat history

| Item | Difficulty | Notes |
|---|---|---|
| Meta AI (WhatsApp integration) chat history | Medium–Hard | The WhatsApp assistant does not currently expose a clean export path. Community exploration welcome. |
| Grok chat history | Medium | Export is available but format is not stable. |
| DeepSeek chat history | Medium | Same as Grok — export exists, format is in flux. |
| Mistral, Cohere, other frontier model exports | Medium | Each needs its own module. |
| Copilot (GitHub) prompt-and-completion history | Medium | GitHub Copilot logs are not user-accessible in a documented way. Explore. |

## Social platforms

| Item | Difficulty | Notes |
|---|---|---|
| X / Twitter: full archive + DMs + likes | Medium | X provides an archive; the DM piece is the tricky part. |
| Instagram: full archive with DMs + Stories | Medium | Meta's data-download flow gets you most of it; normalising is the work. |
| Facebook: full archive with reactions + timeline | Medium | Same as Instagram. |
| LinkedIn: full archive with messaging + connections | Medium | LinkedIn's data-download flow is documented; consolidation is the work. |
| TikTok: full archive | Medium | Their data-download flow exists but is variable by region. |
| Reddit: full comment + post + saved-items history | Easy | Their export is decent; wants normalising. |
| Discord: DMs + server messages (own account) | Hard | Discord's data-download is slow and partial. |

## Financial platforms

Marked separately because extraction paths are usually well-documented (regulatory) but formatting is chaotic.

| Item | Difficulty | Notes |
|---|---|---|
| Bank transaction history normalisation across US/CA/UK/EU banks | Hard | Plaid coverage helps but doesn't solve normalisation. |
| Credit card statements with merchant categorisation preserved | Medium | Each issuer has its own format. |
| Investment account holdings + transaction history | Medium | Similar per-broker variation. |

## Health platforms

| Item | Difficulty | Notes |
|---|---|---|
| Fitbit full history | Medium | Export exists; wants normalising against Apple Health schema. |
| Garmin Connect full history | Medium | Same. |
| Oura Ring full history | Medium | Same. |
| Whoop full history | Medium | Same. |
| Peloton workout + strain history | Medium | Same. |

## Infrastructure / tooling

| Item | Difficulty | Notes |
|---|---|---|
| Encrypted per-repo credential store that survives reinstalls | Medium | Currently uses OS keychain; a cross-platform sealed store would be portable. |
| Web-based front-end for browsing an FTTE-shaped repo | Medium | Currently CLI-only; a local-only web viewer is a good community pickup. |
| iOS app that runs the kit's Apple paths natively | Hard | The paths work outside iOS; running inside iOS is a different animal. |
| Verification-only mode (compare platform-delivered FTTE against kit-assembled) | Medium | Would be useful once platforms start delivering. |

---

## How to claim an item

1. Fork the repo.
2. Open an issue titled `WANTED: <item>` so others know you're working on it.
3. Implement it in a `modules/<your-module-name>/` folder following the manifest schema in [`docs/design.md`](docs/design.md).
4. Send a PR. Include tests where practical. Include a note on which extraction path you used and any gotchas.

If two people work on the same item, we'll take the one that's cleaner, faster, or better tested. Sometimes we take both and let users pick.

---

## Adding items to this list

If you know a lock or extraction path that isn't on the list, open a PR against this file. Keep the ground rules in mind: documented or tolerated paths only, no ToS violations, no vulnerability exploitation.
