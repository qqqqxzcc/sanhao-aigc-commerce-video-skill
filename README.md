# sanhao-aigc-commerce-video-skill

Reusable Codex skill for ecommerce AI video production.

Main capabilities:

- benchmark video replication
- strong-hook material-to-video workflows
- 9-grid storyboard generation
- 16:9 production-board generation
- voiceover-first video prompting
- no-subtitle video planning
- stable model and product locking

## Repository Layout

```text
skills/
  sanhao-aigc-commerce-video-skill/
    SKILL.md
    agents/
    references/
    scripts/
    tests/
```

## Installability Checklist

Other agents can install this skill only when all four conditions are true:

1. This repository has been pushed to a real GitHub repo.
2. The branch in the shared link matches the real default branch.
3. The skill folder exists at `skills/sanhao-aigc-commerce-video-skill`.
4. The shared link uses the real `owner/repo`, not placeholder text.

If any of the above is missing, the install link will fail.

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

because that is only a placeholder template.

## Install For Codex

### Option 1: Install from a GitHub tree URL

Share the real GitHub tree URL after the repo is published.

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

After install:

```text
$sanhao-aigc-commerce-video-skill
```

Restart Codex if the skill does not appear immediately.

## Share Text

```text
安装链接：
https://github.com/YOUR_GITHUB_NAME/YOUR_REPO_NAME/tree/main/skills/sanhao-aigc-commerce-video-skill

安装后重启 Codex，然后直接输入：
$sanhao-aigc-commerce-video-skill
```