# Google Gemini Omni Flash Video Generation

Use this reference when the user asks Codex to generate video through Google Gemini Omni Flash (instead of Seedance 2.0).

## Overview

Google Gemini 2.0 Flash ("Omni Flash") supports native video generation through the standard Gemini API by setting `responseModalities` to include `"VIDEO"`. This allows image-to-video generation using product images and storyboard frames as reference.

## Security

- Never write the Google API key into SKILL.md, prompt files, generated reports, Git commits, or shared outputs.
- `scripts/gemini_omni_submit.py` reads `GOOGLE_API_KEY` from the environment, from a private env file passed by `--env-file`, or automatically from `$HOME/.codex/secrets/google_omni.env` when that file exists.
- Get your API key from: https://aistudio.google.com/apikey
- Each user must use their own API key. Do not share keys.

## API Details

- Endpoint: `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent`
- Default model: `gemini-2.0-flash-exp`
- Auth: API key as `?key=` query parameter
- Video generation requires `generationConfig.responseModalities: ["TEXT", "VIDEO"]`
- Reference images are passed as `inlineData` parts with base64-encoded image data
- Response contains video as base64-encoded `inlineData` with video MIME type

## Usage

```bash
# Basic usage with product images and storyboard
python scripts/gemini_omni_submit.py \
  --prompt-file path/to/prompt.txt \
  --reference-image product1.png \
  --reference-image product2.png \
  --reference-image storyboard.png \
  --output-dir output/ \
  --env-file scripts/google_omni.env.example

# Dry run (preview request without submitting)
python scripts/gemini_omni_submit.py \
  --prompt-file path/to/prompt.txt \
  --reference-image storyboard.png \
  --output-dir output/ \
  --dry-run

# Nine-grid direct submission mode
python scripts/gemini_omni_submit.py \
  --prompt-file path/to/prompt.txt \
  --reference-image nine_grid.png \
  --reference-mode grid-storyboard \
  --output-dir output/
```

## Key Differences from Seedance

| Feature | Seedance 2.0 | Gemini Omni Flash |
|---------|-------------|-------------------|
| API | Volcano Ark (async task) | Google Gemini (sync with base64 response) |
| Auth | ARK_API_KEY in header | GOOGLE_API_KEY as query param |
| Response | Long-running operation, poll for status | Immediate response with inline video data |
| Audio | Built-in audio generation | No built-in audio |
| Duration | 4-15 seconds | Model-dependent |
| Resolution | 480p/720p/1080p | Model-dependent |

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Yes | - | Google AI Studio API key |
| `GOOGLE_OMNI_MODEL` | No | `gemini-2.0-flash-exp` | Model ID to use |
| `GOOGLE_API_BASE_URL` | No | `https://generativelanguage.googleapis.com` | API base URL |

## Limitations

- Video length is controlled by the model, not by a duration parameter
- No built-in audio generation (unlike Seedance's `audio_mode`)
- For audio, post-process with a separate audio generation tool
- Model availability and capabilities may change; check Google AI Studio for current status

## Troubleshooting

- **403 Forbidden**: Check that your API key is valid and has access to the model
- **No video in response**: The model may not support video for the given input; try a different model or simpler prompt
- **Rate limiting**: Add delays between requests or upgrade your API quota
