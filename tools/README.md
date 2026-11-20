# tools

Static checks for this repository. They read files and parse them; they never run a lab,
start a container, call an API or need a secret.

## Run everything locally

```bash
python3 -m pip install pyyaml        # once; the only dependency
python3 -I tools/check_public.py     # about 3 seconds; exit 0 = clean, 1 = errors
```

`-I` is Python's isolated mode (ignores `PYTHON*` variables and the current directory),
the same way CI runs it. Every problem is printed as `path:line: error [rule] message`.
Warnings (`warning [rule]`) never fail the run.

`--root DIR` checks another checkout. `--extract-mermaid DIR` writes every Mermaid block
to `DIR/*.mmd` (plus `manifest.tsv` mapping each file back to `path:line`) and exits;
CI feeds those files to the Mermaid renderer.

## What `check_public.py` checks

| Rule | What it enforces |
|---|---|
| `front-matter`, `filename` | Every `course/*/*.md` lesson starts with YAML front matter holding `id`, `title`, `status`, `requirement`, `learning_objectives` (a list of strings) and `last_reviewed` (ISO date); no duplicate ids; `id` equals `SYSDESIGN-` plus the code in the file name (`04-…` gives `SYSDESIGN-04`, `C01-…` gives `SYSDESIGN-C01`). |
| `companion` | Each lesson has `slides/<name>.md` and `exercises/<name>.md`, and no slide or exercise file is an orphan. |
| `syllabus` | Every lesson code appears as a heading in `SYLLABUS.md`. |
| `link`, `anchor` | Every relative Markdown link, image and HTML `href`/`src` resolves to a file or directory that is part of the public repository, and every `#anchor` matches a heading in the target file (GitHub's slug rules, including `-1`/`-2` suffixes for repeated headings). Links are resolved inside the public surface only, so a link that works only in a bigger working tree still fails. |
| `fence`, `mermaid` | Every code fence is closed; no Mermaid block is empty. |
| `lab` | Every `labs/*/` directory has a `README.md` with a *Test status* section that states `illustrative`, `syntax-reviewed` or `runtime-tested`; every `labs/NN-name` path a lesson mentions exists. A lab that no lesson mentions is a warning. |
| `yaml`, `compose`, `json`, `course-yaml` | All `.yaml`/`.yml` files parse (multi-document aware, and duplicate keys are rejected, which plain PyYAML accepts silently); every `labs/*/compose.yaml` has a `services` mapping whose entries have `image` or `build`; all `.json` files parse; `course.yaml` has `course_id`. |
| `secret` | High-signal patterns only: private-key headers, GitHub tokens, `sk-` style API keys, AWS access key ids, Slack tokens, Google API keys, container-registry `auth` blobs, and credential-looking file names. Values are never echoed. Obvious placeholders (`EXAMPLE`, `REDACTED`) are ignored. |
| `attribution` | No AI-assistant co-author or "generated with" attribution strings. |
| `private-ref` | No reference to the private side of the project: private top-level directories, private tooling, the private repository name, or a path into someone's home directory. A mention of a private tool script outside `labs/` is a warning. |
| `references` | Every lesson has a `## References` section, and the first (primary) URL of each numbered entry is listed in `REFERENCES.md`. Extra URLs inside an entry's parenthetical note are exempt, because the generator of `REFERENCES.md` keeps only the primary source. |

Only the public surface is inspected: the root documents, `course.yaml`, `course/`,
`slides/`, `exercises/`, `labs/`, `tools/` and `.github/`.

## Checks that live in the workflows instead

| Check | Where | Local equivalent |
|---|---|---|
| Mermaid blocks render with `mermaid-cli` | `.github/workflows/ci.yml`, job `mermaid` | `python3 -I tools/check_public.py --extract-mermaid /tmp/mmd`, then `mmdc -i /tmp/mmd/<file>.mmd -o /tmp/out.svg` |
| `docker compose config -q` for each `labs/*/compose.yaml` | job `compose-and-scripts` | `docker compose -f labs/NN-name/compose.yaml config -q` (parses only; builds and pulls nothing) |
| `shellcheck` on `labs/**/*.sh` | job `compose-and-scripts` | `shellcheck --severity=warning labs/*/*.sh` |
| `python -m py_compile` on `labs/**/*.py` | job `compose-and-scripts` | `python3 -m py_compile labs/*/*.py labs/*/*/*.py` |
| External links (lychee), weekly and on demand | `.github/workflows/links.yml` | `lychee --accept '200..=299,403,429' README.md 'course/**/*.md'` |

None of these executes lab code.
