# Khalid Editing Creatives

**مونتاج فيديو عمودي بالكامل بالكود — لصنّاع المحتوى بالعربي.**
A [Claude Code](https://claude.com/claude-code) skill that edits vertical 9:16 Arabic talking-head videos end to end with no editing app. You give it a raw clip, and it gives back a finished reel with word-timed Arabic captions, motion graphics, paper-cut animation, real photos and videos from the internet, a cut-out speaker, and sound effects.

Everything is code: **ffmpeg** cuts, **Whisper** transcribes with per-word timing, and **Remotion** (React) renders the graphics over the video.

---

## What it does

| | |
|---|---|
| ✂️ **Silence cutting** | Measures pauses and removes them. A 98s take becomes a tight 46s. |
| 📝 **Word-timed Arabic captions** | large-v3 Whisper, dialect correction, highlighted keywords, your font and colors. |
| 🗒️ **Edit by script** | Delete a sentence from the transcript and it disappears from the video. Repeated sentences are flagged. |
| 🎨 **Mixed styles in one video** | Paper-cut stop-motion, motion graphics, investigation-board collage, documentary, dark-board diagrams. Each moment uses whatever serves it, tied together by your brand. |
| 🧍 **Speaker cutout** | Cuts you out of the frame to swap the background (a city photo, a video, your brand), or shrinks and moves you so graphics can sit beside you. With a 5-second empty-room shot, your real room stays behind you. |
| 🔦 **Selective light and timed grading** | For a second or two, you (or an object in the frame) glow in your accent color while the rest of the frame darkens and desaturates. Also moving spotlight areas and short black-and-white or high-contrast beats. Only when you ask. |
| 🌐 **Assets from the internet** | Searches free, licensed sources for photos, stock video, and icons. Builds one numbered contact sheet to choose from, downloads full resolution, removes backgrounds, and logs licenses and credits. |
| 📄 **Paper-cut animation** | A code toolkit (torn edges, fiber grain, hard shadows, 12 fps stop-motion, back-to-front assembly), plus a 3-prompt workflow for AI-generated paper-cut clips. |
| 🔊 **Sound effects, always** | 30+ synthesized sounds or your own library, placed on the exact word, with a governor that keeps them tasteful. |
| ✅ **Pre-render checks** | Gaps longer than 4s, coverage under 70%, graphics over the face, frozen scenes, cut alignment, sound spacing, and color and voice fidelity after render. |

**Hard rules:** your picture and voice come out exactly as they went in (measured, not eyeballed). No music unless you ask. Nothing is ever published; you get a file.

---

## Install

```bash
git clone https://github.com/khalidstark/khalid-editing-creatives ~/.claude/skills/khalid-editing-creatives
```

Then just talk to Claude Code: *«عدّل هذا الفيديو»*, *«مونتج المقطع»*, *«شيّل السكتات وركّب كابشن»*, *«صغّرني وحط ورايي صورة دبي»*, *«ابي أنيميشن ورق»*, or *"edit this video"* with a file path.

On first run the skill checks your machine and offers to install what's missing (it asks first):

| | macOS (Apple Silicon / Intel) | Windows |
|---|---|---|
| ffmpeg · Node · Python | Homebrew | winget |
| Transcription | `mlx-whisper` (GPU) | `faster-whisper` |
| Face and person detection | Apple Vision (Xcode tools) | `mediapipe` |
| Person cutout | `opencv-python` | `opencv-python` |
| Render engine | Remotion (~500 MB, downloaded on the first project) | same |

Downloads use `curl`, which uses system certificates. That avoids the common macOS Python `CERTIFICATE_VERIFY_FAILED` issue.

---

## How a video gets made

```
0  setup check            scripts/00_setup.sh
0.5 onboarding (once)     brand colors, font, style, captions, restrictions → profile.json
1  project folder         ~/Documents/khalid-editing-creatives/projects/<name>/
3  silence cut            01_cut_plan.py
4  transcription          01b_transcribe.py  (word-level timing)
5  corrections+captions   fixes.json → 02_captions.py
5.5 edit by script        10_script_edit.py show / dupes / drop / keep / undo
6  cut + zoom             03_cut_zoom.py · 12_face_guard.js
7  scenes                 Scenes.tsx (mix any toolkit) · assets · person cutout · paper
8  sound effects          05_sfx.py / mix_sfx.py → 05b_sfx_audit.py
9  checks + render        22_preflight.py → 04b_remotion.sh render
10 loudness               06b_master.sh (-14 LUFS)
11 subtitles + text       09_srt.py
```

Three modes: **quick** (cut + captions), **light** (+ zoom and sound effects), and **full** (everything).

---

## The new toolkits

### Assets from the internet (`scripts/28_assets.py`)
```bash
python3 scripts/28_assets.py <work> search "dubai skyline"              # photos (vertical first)
python3 scripts/28_assets.py <work> search "city traffic" --kind video  # stock video
python3 scripts/28_assets.py <work> search "trophy" --kind icon         # SVG icons (color sets first)
python3 scripts/28_assets.py <work> pick dubai-skyline 3 --name dubai --cut
python3 scripts/28_assets.py <work> icon twemoji:flag-egypt noto:trophy
python3 scripts/28_assets.py <work> credits                             # attribution lines for CC BY
```
Key-free sources: Wikimedia Commons, Openverse, and Iconify. You can add free Pexels or Pixabay keys in `~/Documents/khalid-editing-creatives/keys.json` for more stock video.

### Speaker cutout (`scripts/27_person_layer.py` + `Person.tsx`)
```json
{"windows": [
  {"a": 0.0,  "b": 2.6, "bg": "dubai.jpg", "scale": 1.0,  "y": 1.25, "in": 0},
  {"a": 5.4,  "b": 8.0, "bg": "theme",     "scale": 0.62, "x": 0.27, "y": 1.16},
  {"a": 24.4, "b": 29.9,"bg": "plate",     "scale": 0.6,  "x": 0.73}
]}
```
`bg` can be `plate` (your empty room), `theme` (your brand background), or any image or video file. The transition swaps the background first and then moves the person, so you never see two copies. Graphics can go **behind** the person via `export const BehindPerson` in `Scenes.tsx`. See `references/person-cutout.md`.

### Selective light (`scripts/29_spotlight.py` + `Spotlight.tsx`)
```json
{"windows": [
  {"a": 10.0, "b": 12.0, "target": "person", "pulse": true},
  {"a": 13.0, "b": 15.0, "target": "area", "area": {"x":0.36,"y":0.45,"rx":0.2,"ry":0.09}},
  {"a": 16.0, "b": 17.5, "target": "frame", "desat": 1.0, "contrast": 1.15, "in": 0},
  {"a": 21.3, "b": 23.0, "target": "object", "point": [0.72, 0.64]}
]}
```
`person` cuts you out frame by frame. `object` tracks whatever is under `point` using Apple Vision (macOS only). `area` is a soft elliptical spotlight that can move to `to`. `frame` is a timed grade of the whole frame with no target. The target is brightened and glows in your accent color, while the rest is dimmed and desaturated. It is drawn inside the video window with the same zoom, so it works full-screen or in a card. The color check skips these windows, because the change is intentional. See `references/spotlight.md`.

### Paper-cut (`styles/paper/kit/paper.tsx`)
`Piece` · `PaperWord` · `PaperBG` · `assemble` · `PaperClip` · `stepT` · `muted`. Everything is stepped at 12 fps, so pieces slide, drop, and rotate like real stop-motion, never morph. For hero moments, `references/paper-motion.md` writes the three prompts (paper-cut image → 9-panel sheet → animation) to run in your own AI tools.

---

## Repository layout

```
SKILL.md                    the skill (Arabic, read by Claude)
references/                 rules.md (130+ lessons) · scenes · sfx · onboarding · assets · person-cutout · paper-motion
scripts/                    pipeline (00–29) · remotion-template/ · personmask / subjectcut (Vision) · checks
styles/
  simple/                   clean brand shapes
  collage/                  kit/vox · editorial · board + real paper textures, hand, Ruqaa font
  paper/                    kit/paper.tsx (paper-cut stop-motion toolkit)
```

Your data never lives in the skill folder. It goes in `~/Documents/khalid-editing-creatives` (or `$KEC_HOME`): profile, dialect dictionary, sound library, and projects. An existing `~/Documents/video-editor-bassam` folder is picked up automatically.

---

## Credits and licenses

- Bundled textures are Pexels photos (Pexels License); the Aref Ruqaa font is SIL OFL 1.1. Details are in `styles/collage/assets/SOURCES.md`.
- Downloaded assets are logged per project in `assets/SOURCES.json`. CC BY items need a credit line (`28_assets.py credits`).
- Sound libraries are **not** included (their licenses forbid redistribution). Build your own with `styles/collage/sound_add.py`, or use the synthesized sounds.
- The paper-cut prompt workflow is adapted from the *motion-design* prompt pack.
- `k_hand_pen.png` and `k_hand_stamp.png` are AI-generated.

## License

[MIT](LICENSE) for the code and docs. Bundled third-party assets keep their own licenses (above).
