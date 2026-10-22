# vg

`vg` packages **VG 1.78.0-r1** for TAFFISH, with the official optional
Sequence Tube Map browser service at a fixed, separately identified commit.

- Command: `taf-vg`; kind: `tool`.
- Packaging license: Apache-2.0. VG and Tube Map: MIT; dependencies retain their licenses.
- Upstream: [VG v1.78.0](https://github.com/vgteam/vg/releases/tag/v1.78.0).
- Install after publication: `taf install taf-vg-v1.78.0-r1`.
- This working candidate is not evidence that the release is published.

## What This App Packages

The unmodified official VG multiarch runtime is pinned to OCI index
`sha256:febc2401166d4acd81cbf07d89158feccee8c13de70613f72e641d48ceea4ca8`.
The VG tag resolves to `315509da9be8a4ca7c94631b471d0d835dbd7a33`;
runtime reports `vg version v1.78.0 "Sharptooth"`. This is a stable release, not a prerelease.

[Sequence Tube Map](https://github.com/vgteam/sequenceTubeMap) is the official
optional companion, fixed at `33b7a7e5df9f8052974ef8e6c689a031dac6e2c9`.
Its package.json version is 0.1.0, not VG's version. Its source, npm lock,
upstream WASI patch, license and original configuration are retained.
The production browser bundle uses that lock; npm update is not used.
TAFFISH changes only deployment configuration/default demo and adds lifecycle,
private scratch and explicit remote-download control around upstream `start()`.
It does not change graph algorithms or scientific defaults.

## Scope

Supported interfaces include VG construction, conversion, indexing, mapping,
genotyping/calling and visualization; explicit packaged helper commands remain
available through automatic command mode. Standard projects may use FASTA,
VCF, GFA/GFAz, PackedGraph, XG, GBZ, GBWT, GAM/GAF and related indexes.

The companion is a Node.js browser service, not a desktop/noVNC session.
It provides local graph/track selection, region navigation, small uploads,
display settings and SVG download. No GPU, X11, display manager or noVNC is needed.
This is a private single-user research viewer, not a public authenticated portal.
Developer benchmark scripts under /vg/scripts are retained, but their optional
R/Julia/site-specific benchmarking environments are not installed or validated.

## Container Contents and Dependency Closure

- `vg`: original upstream static binary; `samtools 1.22.1`, `bgzip`, `tabix`
  and the official image's scripts/runtime packages are preserved.
- `vg-tubemap`: explicit GUI helper; Node 22, fixed frontend assets and the
  production server dependency closure. Browser build tools/npm caches stay
  in build stages, not the final runtime.
- `vg-resources`: Python/stdlib and curl based fixed-member downloader/importer.
- GUI API calls resolve VG, Python 3, chunkix.py, tabix and cat from the image;
  WASM/JS/CSS/fonts and SVG export code are bundled locally.
- Original notices and their inventories live under /opt/vg/share/licenses
  and /opt/vg/tubemap/licenses. Full VG release source (including submodules)
  and the Tube Map source archive are retained under /opt/vg/share/sources.
  Their approximately 218 MB compressed payload is intentional source/provenance
  material, not disposable download cache.
- Image size measurements and runtime provider checks are recorded in release.md.
  Official-base layers are retained; deleting files in a later layer would not
  reduce those earlier layers and is not claimed as slimming.

## Usage and Command Mode

```sh
taf-vg vg help
taf-vg vg version
taf-vg vg construct -r reference.fa -v variants.vcf.gz > graph.vg
taf-vg vg convert -g -x graph.gfa > graph.xg
taf-vg vg stats -z graph.xg
taf-vg vg paths -x graph.xg -L
taf-vg vg viz -x graph.xg -o graph.svg
taf-vg samtools --version
```

Use the explicit executable form `taf-vg vg SUBCOMMAND ...`: a bare
`taf-vg SUBCOMMAND` can be interpreted as another container executable.
Wrapper `--help`, `--version` and `--compile` are TAFFISH-level operations.
Use matching coordinate systems and graph/index identities. Write derived
indexes, alignments, calls and visualizations to a writable project directory.

TAFFISH 0.11 reparses command arguments. Preserve literal inner quotes for a
space-containing value or a `sh -c` program, for example
`taf-vg vg paths -x "'output graph.xg'" -L` and
`taf-vg sh -c "'gzip -dc /vg-resource/graph.gfa.gz | vg convert -g -x -'"`.
For these examples, paths must not themselves contain a single quote.

## Browser GUI and Backend Usage

```sh
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_VG_GUI=1 taf-vg vg-tubemap
TAFFISH_CONTAINER_BACKEND=podman TAFFISH_VG_GUI=1 taf-vg vg-tubemap
TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_VG_GUI=1 taf-vg vg-tubemap
```

Open http://127.0.0.1:3000 after the separate ready message. The default is an
artificial 12-base graph; startup never downloads human data. Add
`--data-dir "'$PWD/graphs'"` for your trusted physical graph/index directory.
Uploads are capped at the upstream 5 MB limit; large data should be mounted.
The built-in upstream example files are retained, but remote/real-data demos
are not automatically selected. A raw GFA resource must be converted/indexed
into your working directory before use by the GUI.

| Capability | Docker | Podman | Apptainer |
| --- | --- | --- | --- |
| Native platforms declared | Linux amd64/arm64 | Linux amd64/arm64 | Native Linux only |
| GUI activation | `TAFFISH_VG_GUI=1` | Same | Same |
| GUI transport | host 127.0.0.1:PORT -> container 3000 | Same | direct host 127.0.0.1:PORT |
| Output ownership | caller UID:GID | keep-id and caller UID:GID | caller UID:GID |
| Shared resource analysis | automatic read-only volume | automatic read-only volume | automatic read-only bind |
| Persistent resource installation | actual writable bind | actual writable bind | actual writable bind |
| GPU/X11/noVNC | N/A: CPU browser service | Same | Same |

Set `TAFFISH_VG_GUI_PORT=8300` together with GUI=1 for an alternate **host**
port. For Docker/Podman do not additionally change helper `--port`; its
container port remains 3000. The app-specific mapping and UID flags are encoded
in src/main.taf, not delegated to global per-user run-argument configuration.
Apptainer on macOS is unavailable; use a native Linux host, such as via SSH.

For a remote host: `ssh -N -L 3000:127.0.0.1:3000 USER@HOST`.
No authentication or TLS is supplied; never expose it publicly or use untrusted
clients/graph directories. Default host mapping/bind is loopback. The helper
prints starting, URL, SSH, Ctrl-C and its private log before launching Node;
ready requires upstream HTTP/WebSocket/watch initialization plus live HTTP/API.
A component exit is an error with a log tail. Ctrl-C returns 130; TERM returns
143 through the attached runtime-client path (Apptainer: the foreground process
group). Terminal hangup is also handled for cleanup; standalone HUP returns 129.
It cleans its owned process group and unique scratch directory with bounded waits. This is foreground use,
not a promise that killing only an outer launcher PID acts as a service manager.

Uploads, request chunks and URL cache live in a mode-0700 temporary session,
never /opt or the shared dataset. They disappear on stop. Downloads selected in
the browser are saved by the browser on the client. Symlinks inside --data-dir
are refused because upstream path authorization is lexical. Remote URL fetch is
disabled unless `--allow-remote` is explicitly requested for trusted URLs;
that opt-in is not an SSRF-safe public service or a guarantee of remote datasets.

## Resources, Databases and Shared Installation

VG has no mandatory pretrained model. Project graphs/reads/variants are explicit
inputs; large public pangenome graphs are reusable selectable resources.
The fixed catalog covers two portable **raw GFA.gz HPRC v1.0 minigraph-cactus**
members (GRCh38 or CHM13), approximately 11.95/12.13 GB. It deliberately does
not silently install old binary indexes, the whole family, or a newer scientific
reference chosen for the user. Catalog hashes come from upstream indexes at
`c9a487dc5745a7d26b64f8252fff4df4b45515db`. HPRC has newer releases;
these identities are reproducible legacy source graphs, not a "latest" alias.
Use a separately chosen, verified local-* compressed GFA import for another
reference; build compatible VG indexes in writable project storage.

```sh
taf-vg vg-resources list
base="$HOME/.local/share/taffish/resources/vg"
mkdir -p "$base"
TAFFISH_VG_RESOURCE_INSTALL_ROOT="$base" taf-vg vg-resources install \
  --resource hprc-v1.0-mc-grch38-gfa --resource-root /resource-install --dry-run
# Review the dry-run, then replace --dry-run with --allow-network to download.
export TAFFISH_VG_RESOURCE_ID=hprc-v1.0-mc-grch38-gfa
taf-vg vg-resources verify /vg-resource
taf-vg sh -c "'gzip -dc /vg-resource/graph.gfa.gz | vg convert -g -x -'" > graph.xg
```

The same commands use Docker, Podman or Apptainer via TAFFISH_CONTAINER_BACKEND.
An administrator can instead create /usr/local/share/taffish/resources/vg
(or /opt/taffish/resources/vg) and run the installer once with that install
root. No ordinary user needs root or a duplicate download afterward. This is an
administrator-once installation with read-only ordinary-user reuse; analysis
and verify are offline. Installation needs --source or explicit --allow-network;
without either it fails before creating a lock, cache or stage.
Do not change shared caches/permissions merely to run analysis.

Each member contains graph.gfa.gz, resource.json, SHA256SUMS and READY. The helper
requires explicit selection, rejects corrupt/extra/symlink members, checks
size/SHA and gzip/GFA type, keeps resumable .downloads partials, takes a kernel flock,
stages privately and promotes with Linux no-replace rename. Existing identical members are
verified without writes; conflicting content is never overwritten. The persistent .vg-resources.lock file is not a stale lock: the kernel releases
ownership when the process exits. Legacy per-member .ID.lock directories require
owner inspection before manual recovery; they are not silently deleted.
INT/TERM/HUP stop the owned download child and remove only the owned staging
path, never an old or newly promoted member. Interrupted partials are retained;
empty and nonempty partials are resumed on explicit retry. A completed but wrong
partial fails checksum verification and is retained for diagnosis. Quarantine
only that verified-bad partial before retrying; never delete installed members. Allow about twice the payload
size plus headroom during install. Direct Index smoke uses only unique /tmp;
a top-level /resource-install is writable only when an actual bind is supplied.

Installed member directories/files are 0755/0644. Administrators must also make
their parent directories traversable/readable, while preserving their own site
security policy. Analysis mounts are read-only and never chmod/chown resources.
The installer does not infer scientific suitability or validate complete
production graphs; the full HPRC payloads are not downloaded as packaging tests.

Discovery (only after an explicit ID) checks:
1. ${TAFFISH_USER_HOME:-$HOME/.local/share/taffish}/resources/vg/ID
2. /usr/local/share/taffish/resources/vg/ID
3. /opt/taffish/resources/vg/ID

TAFFISH_VG_RESOURCE_PATH selects a specific member and takes precedence;
if RESOURCE_ID is also set, the identities must match (unset it when selecting a
different path). An explicitly empty override is invalid, not a fallback.
TAFFISH_VG_RESOURCE_AUTO_MOUNT=0 disables analysis auto-mount. Install-root mode
is separate and higher priority. Selected members undergo full checksum/inventory
checks, including fixed-catalog SHA binding; large graphs incur hashing time.
Automatic validation uses host Python 3 and the exact same validator/catalog as
the in-image helper. Without host Python, disable automatic discovery, perform
in-image verify, then use the manual read-only bind below. Physical paths may
contain spaces; colon/comma are refused as backend bind delimiters.
An explicit root symlink may resolve to a physical directory; member symlinks
and corrupt inventories are refused. Missing/corrupt selected resources fail
closed instead of falling through to an unverified dataset.

For manual fallback, disable auto-mount and export one matching variable:

```sh
export TAFFISH_VG_RESOURCE_AUTO_MOUNT=0
export TAFFISH_DOCKER_RUN_ARGS='-v /physical/member:/vg-resource:ro'
# Podman: TAFFISH_PODMAN_RUN_ARGS='-v /physical/member:/vg-resource:ro'
# Apptainer: TAFFISH_APPTAINER_RUN_ARGS='--bind /physical/member:/vg-resource:ro'
taf-vg vg-resources verify /vg-resource
```

For another authorized compressed GFA:
`vg-resources install --resource local-NAME --resource-root /resource-install
--source FILE.gfa.gz --sha256 SHA256 --assembly ID --license-note TEXT`
through the same wrapper/install-root binding. Use a new immutable ID for changed
data. Project-specific binary indexes remain explicitly version-bound user inputs.

## Version Migration and Troubleshooting

- 1.78.0 deprecates `vg viz` (still available); prefer Tube Map for interactive viewing.
- SAM/BAM M5 checksums are no longer calculated or checked upstream; do not rely
  on the old M5 behavior for independent input identity verification.
- Since 1.77, surject requires explicit -i for paired reads or -U for forced unpaired.
- giraffe --min-chains is renamed --target-alignment-attempts; chain is removed.
  mcmc/genotype are deprecated; snarls --pathnames is removed.
- GBZ v3 can be read; output defaults and index compatibility follow upstream.
  pack/call require the same graph representation, not just equivalent paths.
- Empty GUI: check the local ready/log output, graph format and selected region;
  use --data-dir for large files, not browser upload.
- A .gfa.gz is ordinary gzip, not GFAz. Decompress it before VG's GFA reader,
  as in the streaming example above; passing the gzip bytes directly can yield
  an empty graph instead of the intended graph.
- Port occupied: choose another TAFFISH_VG_GUI_PORT; the helper will not kill
  another process. If storage is read-only, bind a writable output/install root.
- Upstream-help commands may use nonzero help exit status; build-time checks
  assert stable markers without demanding terminal rendering or full GUI startup.

## Testing and Publication Boundary

The 1.78.0-r1 candidate passed native root-context builds on amd64 (xjp) and
arm64 (Docker Desktop Linux VM), with current image identities in release.md.
Docker and Podman passed fresh/offline normal and read-only-root exact probes
on both architectures; the same amd64 OCI passed as a real read-only Apptainer
SIF. Real wrappers passed CLI, persistent output, resource negative/recovery/
idempotence, and GUI startup/ready INT/TERM checks on all five combinations.
Browser rendering, help, display controls and SVG download were checked at
1280x720 and 768x900; both native images have identical frontend assets.
ARM64 Apptainer is not separately validated; the native platform and backend
axes are separate, not a claim that all six combinations were tested.
No backend exception was used. Detailed receipts and image sizes are in release.md.
Only synthetic engineering fixtures are used; tests do not validate scientific
accuracy, clinical use, complete HPRC datasets or production performance.
The existing canonical Action matches a fresh taf new --tool --docker template
byte-for-byte and is unchanged in this update. It builds from
app root on native amd64/arm64 runners. Full rendering is runtime-only.
Publication remains a separate maintainer action after the checklist passes.

For a source checkout, build and run the generated wrapper:

```sh
taf build
TAFFISH_CONTAINER_BACKEND=docker TAFFISH_VG_GUI=1 TAFFISH_VG_GUI_PORT=8300 \
  ./target/taf-vg-v1.78.0-r1 vg-tubemap
```

Use `podman` or `apptainer` in the same backend selector on native Linux.
Do not use the development `taf run` command for this long-running service:
the tested TAFFISH 0.11 path buffered startup output until the service exited.
The diagnostic explicitly stopped its own container; it does not certify
development-launcher signal management. That path is not a supported GUI launch
method. Installed users use `taf-vg`; no local build is needed.

For short CLI development, `taf run` can generate a named output file in
writable project storage, but its tested TAFFISH 0.11 stdout capture is not
binary-safe: streaming XG to the host produced a UTF-8 decoding error.
Use the generated target wrapper (or installed `taf-vg`) for binary stdout.
Both explicit file generation and binary streaming through the generated
wrapper were verified with the same synthetic graph; this is a development
launcher limitation, not a VG format or installed-wrapper failure.

## License and Citation

TAFFISH packaging is Apache-2.0; VG and Sequence Tube Map are MIT. Dependencies,
Node and the official Ubuntu runtime retain their respective notices/licenses.
The image preserves original available dependency notices plus full fixed VG
source with submodules and build recipes. The npm lock and notice inventory
identify frontend/server providers; this is not a fabricated full binary SBOM.
HPRC data are separate from software licensing: see the
[official data-use guidance](https://humanpangenome.org/data-use/), including
public-domain status, acknowledgement and ethical/privacy expectations.
No real human data are redistributed as a default demo.

Cite VG: Garrison et al. (2018), *Variation graph toolkit improves read mapping
by representing genetic variation in the reference*, Nature Biotechnology,
[doi:10.1038/nbt.4227](https://doi.org/10.1038/nbt.4227).
See the fixed Tube Map README and HPRC guidance for companion/resource attribution.
