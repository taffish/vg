vg 1.78.0-r1

Purpose:
  VG variation-graph CLI, plus an optional Sequence Tube Map browser GUI.
  CLI remains the default; start the GUI only when you need interactive viewing.

Usage:
  taf-vg vg help
  taf-vg vg version
  taf-vg vg convert --help
  taf-vg vg giraffe --help
  Use "taf-vg vg SUBCOMMAND ...", not "taf-vg SUBCOMMAND ...".

Common tasks (run in a writable project directory):
  taf-vg vg construct -r reference.fa -v variants.vcf.gz > graph.vg
  taf-vg vg convert -g -x graph.gfa > graph.xg
  taf-vg vg stats -z graph.xg
  taf-vg vg paths -x graph.xg -L
  taf-vg vg viz -x graph.xg -o graph.svg
  Inputs: matching FASTA/VCF coordinates, graph paths and compatible indexes.
  Outputs: graph/index files, path lists, or an SVG; use explicit output paths.
  For map/call tasks, read the subcommand help and keep all indexes from one graph.

Open the GUI (built-in synthetic graph; no dataset download):
  Docker:
    TAFFISH_CONTAINER_BACKEND=docker TAFFISH_VG_GUI=1 taf-vg vg-tubemap
  Podman:
    TAFFISH_CONTAINER_BACKEND=podman TAFFISH_VG_GUI=1 taf-vg vg-tubemap
  Apptainer (native Linux):
    TAFFISH_CONTAINER_BACKEND=apptainer TAFFISH_VG_GUI=1 taf-vg vg-tubemap
  Open http://127.0.0.1:3000 after "ready". Ctrl-C stops and removes the session.
  Choose the synthetic graph, adjust the region, then use Download Image for SVG.
  Add --data-dir "'$PWD/graphs'" to select your physical graph/index directory.
  Uploads are limited to 5 MB; use --data-dir for larger XG/GBZ/graph/GAM files.
  Uploaded files and temporary results disappear when the session stops.
  Use TAFFISH_VG_GUI_PORT=8300 with TAFFISH_VG_GUI=1 for a different host port.
  Docker/Podman map that host port to container 3000; do not override --port.
  Apptainer listens directly on the selected host port; no Docker-style -p.
  Remote host: ssh -N -L 3000:127.0.0.1:3000 USER@HOST, then open localhost.
  No login/TLS: keep it private. Remote URL downloads are disabled unless
  --allow-remote is explicitly given for trusted URLs. Do not expose publicly.

Install one shared GFA resource (network and substantial disk space required):
  taf-vg vg-resources list
  base="$HOME/.local/share/taffish/resources/vg"; mkdir -p "$base"
  TAFFISH_VG_RESOURCE_INSTALL_ROOT="$base" taf-vg vg-resources install \
    --resource hprc-v1.0-mc-grch38-gfa --resource-root /resource-install --dry-run
  Replace --dry-run with --allow-network to download (~12 GB; ~24 GB free).
  Select Docker, Podman or Apptainer with TAFFISH_CONTAINER_BACKEND as above.
  An administrator may install once into /usr/local/share/taffish/resources/vg.
  Ordinary users reuse the readable member without downloading or writing it.
  The catalog is HPRC v1.0 raw GFA, not the latest HPRC release or ready VG indexes.

Use an installed member (all three backends):
  export TAFFISH_VG_RESOURCE_ID=hprc-v1.0-mc-grch38-gfa
  taf-vg vg-resources verify /vg-resource
  taf-vg sh -c "'gzip -dc /vg-resource/graph.gfa.gz | vg convert -g -x -'" > graph.xg
  Personal, /usr/local/share/taffish and /opt/taffish resource paths are searched.
  TAFFISH_VG_RESOURCE_PATH=/physical/member overrides discovery; ID must match.
  TAFFISH_VG_RESOURCE_AUTO_MOUNT=0 disables it; unset the ID when not needed.
  Selection needs host Python 3 and hashes the whole member (may take time).
  Without host Python, disable discovery and use in-image verify/manual bind.
  Manual read-only bind fallback (choose one; auto mount disabled):
  Docker:    TAFFISH_DOCKER_RUN_ARGS='-v /physical/member:/vg-resource:ro'
  Podman:    TAFFISH_PODMAN_RUN_ARGS='-v /physical/member:/vg-resource:ro'
  Apptainer: TAFFISH_APPTAINER_RUN_ARGS='--bind /physical/member:/vg-resource:ro'
  Export the matching variable before running taf-vg. Keep derived indexes and
  outputs in writable project storage, not in the shared resource.
  Custom compressed GFA: see "taf-vg vg-resources install --help".

Immediate notes:
  For a space-containing argument, preserve inner quotes: "'output graph.xg'".
  The same quoting is required for sh -c scripts; these paths cannot contain '.
  Native Linux amd64 and arm64; Apptainer requires Linux, not macOS.
  GPU/device access is not needed. GUI bind paths must contain trusted files,
  without symlinks. Never serve private genomic data to untrusted clients.
  VG 1.77 surject requires -i for paired input or -U for forced unpaired input.
  VG 1.78 deprecates viz; use Tube Map for interactive viewing.
  pack/call must use the same graph and indexes, not merely matching filenames.

More help:
  taf-vg vg-tubemap --help
  taf-vg --help       TAFFISH usage help
  taf-vg --version    Wrapper version, not the VG runtime version
  taf-vg --compile    Generated wrapper shell
  https://github.com/taffish/vg
