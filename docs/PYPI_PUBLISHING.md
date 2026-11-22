# Publishing BAL to PyPI

The release workflow is `.github/workflows/publish.yml`. It runs only when a
version tag beginning with `v` is pushed. It checks that the tag exactly matches
the version in `pyproject.toml`, builds wheel and source distributions, runs
`twine check`, and publishes with PyPI Trusted Publishing (GitHub OIDC).

## One-time PyPI setup

1. Sign in to PyPI and open
   https://pypi.org/manage/account/publishing/
2. Register a pending publisher with:
   - PyPI project name: `bio-availability-language`
   - Owner: `utokyomedlee-lab`
   - Repository: `bio-availability-language`
   - Workflow filename: `publish.yml`
   - Environment name: `pypi`
3. In the GitHub repository, open Settings → Environments → New environment.
   Create an environment named exactly `pypi`.
4. Configure required reviewers / deployment protection for the `pypi`
   environment before production publishing.
5. Confirm the project name is available in PyPI. A pending publisher creates
   the project on the first successful trusted upload.

## Release

The current package version in `pyproject.toml` is `0.5.0.dev1`. For the
first development release, the matching Git tag is `v0.5.0.dev1`.

Only create and push that tag after the PyPI pending publisher and GitHub
environment are configured. The workflow validates the tag against the
package version; a mismatch fails before publishing.

From a local clone after one-time setup:

```bash
git checkout main
git pull
git tag v0.5.0.dev1
git push origin v0.5.0.dev1
```

Then inspect the Publish BAL to PyPI workflow in the GitHub Actions tab. The
build job should pass, and the publish job uses the `pypi` environment and
OIDC; no PyPI API token or GitHub secret is required.

## Important

The current version is a development pre-release. Users generally need
`pip install --pre bio-availability-language` to select a pre-release when no
stable release exists. A stable `0.5.0` release requires updating
`pyproject.toml` and tagging exactly `v0.5.0` instead.

BAL is a research software prototype, not a clinical dosing tool.
