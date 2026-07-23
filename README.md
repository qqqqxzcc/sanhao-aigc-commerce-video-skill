# sanhao-aigc-commerce-video-skill

Reusable Codex skill for ecommerce AI video production, optimized for Douyin-style benchmark replication, storyboard generation, Seedance 2.0 prompting, and API-ready video workflows.

## What This Repository Contains

This repository exposes one installable skill:

```text
skills/
  sanhao-aigc-commerce-video-skill/
```

That folder contains:

- `SKILL.md`: the main workflow and trigger rules
- `agents/`: optional agent config
- `references/`: supporting workflow, QA, and API docs
- `scripts/`: helper scripts
- `tests/`: basic route and prompt contract tests

## Main Capabilities

- benchmark video replication
- strong-hook material-to-video workflows
- 9-grid storyboard generation
- 16:9 production-board generation
- Seedance 2.0 video prompting
- voiceover-aware prompt planning
- no-subtitle video planning
- stable product and model locking

## Function 1 Highlights

`功能1` is the benchmark replication workflow. It is now designed for this exact input pattern:

- benchmark video
- product image
- model image
- selling-point text or selling-point images
- target generation count

### Function 1 Flow

1. Extract the benchmark video structure first:
   - shot order
   - action rhythm
   - scene progression
   - dialogue / voiceover / speaking scenes if present
2. If the user provides selling-point images instead of text, extract and organize the selling points first, then show them to the user for confirmation.
3. Replace the benchmark video's original product messaging with the user's confirmed selling points.
4. Lock product identity and model identity as P0:
   - no product drift
   - no face drift
   - no clothing drift
   - no logo-position drift
5. Generate only `分镜图1` first as a preview.
6. Wait for user confirmation.
7. After confirmation, generate the remaining storyboard images up to the user-requested count.
8. Wait for full storyboard confirmation.
9. Generate the corresponding Seedance 2.0 prompts.
10. Ask whether to:
   - call the API directly
   - or let the user generate on the website manually
11. If API generation is requested, ask the user for the required API credentials before submitting.

### Important Function 1 Rule

If the benchmark video contains dialogue, voiceover, or visible speaking content, the skill must not ignore it. The speaking rhythm and script structure must be preserved and rewritten with the user's product selling points.

## Installability Checklist

Other agents can install this skill only when all four conditions are true:

1. This repository has been pushed to a real GitHub repository.
2. The shared link points to the real branch name.
3. The skill folder exists at `skills/sanhao-aigc-commerce-video-skill`.
4. The shared link uses the real `owner/repo`, not placeholder text.

If any of the above is missing, the install link can fail.

## Correct GitHub Tree Link

After you publish this repository to GitHub, share the real tree URL in this format:

```text
https://github.com/YOUR_GITHUB_NAME/YOUR_REPO_NAME/tree/main/skills/sanhao-aigc-commerce-video-skill
```

Example:

```text
https://github.com/sanhao-aigc/sanhao-aigc-commerce-video-skill/tree/main/skills/sanhao-aigc-commerce-video-skill
```

Do not share:

```text
https://github.com/<owner>/<repo>/tree/main/skills/sanhao-aigc-commerce-video-skill
```

because that is only a placeholder.

## Install For Codex

### Option 1: Install from a GitHub tree URL

Publish the repo first, then share the real GitHub tree URL.

### Option 2: Install from a cloned repo

PowerShell:

```powershell
git clone <YOUR_GIT_REPOSITORY_URL>
Set-Location .\sanhao-aigc-commerce-video-skill-repo
New-Item -ItemType Directory -Force "$HOME\.codex\skills" | Out-Null
Copy-Item -Recurse -Force ".\skills\sanhao-aigc-commerce-video-skill" "$HOME\.codex\skills\"
```

macOS / Linux:

```bash
git clone <YOUR_GIT_REPOSITORY_URL>
cd sanhao-aigc-commerce-video-skill-repo
mkdir -p "$HOME/.codex/skills"
cp -R "./skills/sanhao-aigc-commerce-video-skill" "$HOME/.codex/skills/"
```

After install, restart Codex if needed, then invoke the skill by context or by name:

```text
$sanhao-aigc-commerce-video-skill
```

## Suggested Share Text

```text
安装链接：
https://github.com/YOUR_GITHUB_NAME/YOUR_REPO_NAME/tree/main/skills/sanhao-aigc-commerce-video-skill

安装后在 Codex 中可直接按场景触发，或手动输入：
$sanhao-aigc-commerce-video-skill
```
