# Apple media off-ramp

Pulls photos and videos off your iPhone as fast as you take them. Original quality. Open formats. Your storage.

## What it does

- **Continuous mode** — uses the documented iCloud Photos API to pull each new photo/video into your repo within minutes of it being taken.
- **Bulk mode** — pulls the full archive on demand via USB (libimobiledevice) when the phone is plugged in.
- **Format normalisation** — HEIC → JPEG (both kept if you want), HEVC → MP4 (both kept if you want). Originals preserved by default so you have the platform-delivered fidelity.
- **Local processing only** — nothing leaves your machine except to whatever storage target you chose in setup.

## Why this exists

Apple's default is to fill your phone's storage with your own media in formats that make it hard to move off the device. Half the memory in most phones would be plenty if the platform actually let people stream their media off the phone as it's taken. This module makes the platform's own documented paths do exactly that.

## Extraction paths

This module uses:

- **iCloud Photos API** (documented) via the `pyicloud` library for continuous sync.
- **libimobiledevice** (open-source, mature) for USB bulk pulls.
- **CloudKit web endpoints** (documented, tolerated) as a fallback when iCloud Photos API is not available.

No jailbreak. No security exploits. No ToS violation.

## Configuration

Set at first-run via `./scripts/setup.sh`. Values land in `.liberation-kit/config.yaml` under the `apple-media:` key:

```yaml
apple-media:
  enabled: true
  modes:
    continuous: true
    bulk: true
  formats:
    keep_originals: true
    convert_heic_to_jpg: true
    convert_hevc_to_mp4: true
  continuous:
    poll_interval_seconds: 300
    device_hint: null   # optional device UDID to filter
  bulk:
    trigger_on_usb_connect: true
    require_confirmation: true
```

## Storage layout

Files land under your repo's `media/photos/YYYY/MM/DD/` and `media/videos/YYYY/MM/DD/`, keyed by capture time (not extract time), with the original filename plus a short content-hash suffix to prevent collisions.

Manifest entries land in `media/manifests/YYYY-MM.jsonl`.

## Running

```bash
# Continuous mode (daemon)
./modules/apple-media/run-continuous.sh

# Bulk mode (interactive, requires USB)
./modules/apple-media/run-bulk.sh
```

## Verified against

- iOS 18.x and iOS 19.x on iPhone 13/14/15/16 (community reports)
- macOS 15.x host (Sequoia)
- Linux hosts via libimobiledevice v1.3.x
- Windows 11 via libimobiledevice (WSL2 recommended)

## Known limitations

- The iCloud Photos API path requires two-factor authentication cooperation on first run. Once trusted, subsequent runs are non-interactive.
- Shared albums are supported but Shared Library (as distinct from Shared Albums) requires the CloudKit fallback and is slower.
- Live Photos are stored as their component photo + video pair; the "live" relationship is preserved in the manifest.
- If Apple changes the API in a way that breaks this module, we look for the next documented path. Community pickups welcome.

## References

- Apple: "Requesting a copy of your data" — https://privacy.apple.com/
- libimobiledevice project — https://libimobiledevice.org/
- iCloud Photos API documentation — via developer.apple.com/documentation/
