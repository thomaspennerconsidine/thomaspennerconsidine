# Profile configuration

`config/profile.json` is the canonical source of the public GitHub profile. `README.md` is a generated artifact that GitHub displays on the profile page. The schema at `config/profile.schema.json` documents the accepted JSON structure.

## Update the profile

1. Edit `config/profile.json` (do not edit the generated README directly).
2. Run `python3 scripts/profile.py render`.
3. Run `python3 scripts/profile.py check` and `python3 -m unittest discover -s tests -v`.
4. Commit the JSON and generated README together; the Actions workflow runs the same checks on pull requests and pushes to `main`.

The generator uses only the Python standard library. It validates required keys, lists, nonempty text, schema version, and duplicate specialization names. The JSON Schema is provided for IDEs and external validators, but the command does not require a JSON Schema package.

## Repository automation

- `.github/workflows/validate-profile.yml` checks the configuration and generated README; its token is read-only.
- `.github/dependabot.yml` requests monthly update pull requests for GitHub Actions.
- `.github/CODEOWNERS` declares the owner but **does not enforce review** without matching GitHub branch rules.
- `.editorconfig`, `.gitattributes`, and `.gitignore` standardize edits and reduce accidental generated-file commits.

These are profile-repository settings, not cloud-account or enterprise security controls. They do not enable MFA, branch protection, vulnerability reporting, or organization policies; configure those separately in GitHub's settings where supported.
