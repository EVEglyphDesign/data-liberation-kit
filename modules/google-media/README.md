# Google media parallel path

Same idea as the Apple module, for Google Photos. Automated Takeout with the wait-and-download loop handled for you, plus a lighter continuous path via the Google Photos Library API for accounts where it's still available.

## What it does

- **Continuous mode** — uses the Google Photos Library API to pull new photos/videos into your repo shortly after they're synced to Google Photos.
- **Bulk mode** — automates a Google Takeout request (Photos-only), polls until the export is ready, downloads and unpacks it into the base-model layout.
- **Format handling** — Google Photos generally returns JPEG for photos and MP4 for videos; no conversion needed most of the time. Live-photo pairs are preserved.

## Extraction paths

- **Google Photos Library API** — documented, requires OAuth consent. Well-supported until deprecation notice announced in 2025 for some surfaces; module gracefully degrades to Takeout when API access is unavailable.
- **Google Takeout automation** — documented user-facing surface; the module drives the browser through the request-and-download loop using the same session cookies the user is already logged in with.

No jailbreak. No ToS violation.

## Configuration

```yaml
google-media:
  enabled: true
  modes:
    continuous: true
    bulk: true
  continuous:
    poll_interval_seconds: 900
  bulk:
    schedule_cron: "0 3 1 * *"   # first of every month at 3am local
    include_metadata_json: true
```

## Storage layout

Same as Apple module: `media/photos/YYYY/MM/DD/` and `media/videos/YYYY/MM/DD/`, keyed by capture time, manifest entries in `media/manifests/YYYY-MM.jsonl`.

## Running

```bash
./modules/google-media/run-continuous.sh
./modules/google-media/run-bulk.sh
```

## Known limitations

- Google Takeout can take hours (occasionally days) to prepare a large archive. The bulk script backgrounds while waiting.
- The Library API returns "base URLs" that expire after 60 minutes; the module downloads immediately.
- If a user has both Google Photos and legacy Picasa content, only Google Photos is in scope for now. Picasa content is on the WANTED list.

## References

- Google Photos Library API — https://developers.google.com/photos
- Google Takeout — https://takeout.google.com/
