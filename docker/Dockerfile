ARG VG_VERSION=1.76.0
ARG VG_TAG_COMMIT=e2547e979d86a446e8151c5489850b6176a82c0c
ARG VG_UPSTREAM_IMAGE=quay.io/vgteam/vg@sha256:fe3a0d6dcd5a0544de862b06b50c9744a5aed769069da61d62b27c30d4b14e10
FROM ${VG_UPSTREAM_IMAGE}

ARG VG_VERSION
ARG VG_TAG_COMMIT
ARG VG_UPSTREAM_IMAGE
ARG VG_UPSTREAM_AMD64_MANIFEST=sha256:fc176981cd4717ad37de4ea63aa3d3cef07ec5022ffb8c273f770d615adc95a3
ARG VG_UPSTREAM_ARM64_MANIFEST=sha256:3235b2cc44b94962ce89b84f2d752d90fb943f8b1c3c38738690118d27f65934
ARG GFAZ_FIXTURE_SHA256=809752f1e0569842e8a44620411c9b897c2bcc606acf7baa0b1b8a2f0e60185e

USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

LABEL org.opencontainers.image.title="TAFFISH vg" \
      org.opencontainers.image.description="VG ${VG_VERSION} runtime packaged for TAFFISH" \
      org.opencontainers.image.source="https://github.com/vgteam/vg" \
      org.opencontainers.image.version="${VG_VERSION}" \
      org.opencontainers.image.licenses="Apache-2.0 AND MIT"

RUN set -eux; \
    mkdir -p /opt/vg/share/doc/vg /opt/vg/share/licenses/vg /opt/vg/share/testdata; \
    ln -sf /vg/bin/vg /usr/local/bin/vg; \
    { \
      printf '%s\n' "version=${VG_VERSION}"; \
      printf '%s\n' "tag=v${VG_VERSION}"; \
      printf '%s\n' "tag_commit=${VG_TAG_COMMIT}"; \
      printf '%s\n' "upstream_image=quay.io/vgteam/vg:v${VG_VERSION}"; \
      printf '%s\n' "upstream_manifest=${VG_UPSTREAM_IMAGE#*@}"; \
      printf '%s\n' "upstream_amd64_manifest=${VG_UPSTREAM_AMD64_MANIFEST}"; \
      printf '%s\n' "upstream_arm64_manifest=${VG_UPSTREAM_ARM64_MANIFEST}"; \
      printf '%s\n' "source=https://github.com/vgteam/vg"; \
      printf '%s\n' "release=https://github.com/vgteam/vg/releases/tag/v${VG_VERSION}"; \
      printf '%s\n' "gfaz_fixture_source=https://raw.githubusercontent.com/vgteam/vg/${VG_TAG_COMMIT}/test/tiny/tiny.gfaz"; \
      printf '%s\n' "gfaz_fixture_sha256=${GFAZ_FIXTURE_SHA256}"; \
    } > /opt/vg/share/doc/vg/source.txt; \
    { \
      printf '%s\n' "VG and its packaged tiny GFAz test fixture are distributed upstream under the MIT license."; \
      printf '%s\n' "See https://github.com/vgteam/vg/blob/${VG_TAG_COMMIT}/LICENSE for the upstream license text."; \
      printf '%s\n' "This TAFFISH wrapper metadata and documentation are distributed under Apache-2.0."; \
    } > /opt/vg/share/licenses/vg/LICENSE-note.txt

COPY docker/testdata/tiny.gfaz.b64 /tmp/tiny.gfaz.b64

RUN set -eux; \
    base64 -d /tmp/tiny.gfaz.b64 > /opt/vg/share/testdata/tiny.gfaz; \
    printf '%s  %s\n' "${GFAZ_FIXTURE_SHA256}" /opt/vg/share/testdata/tiny.gfaz | sha256sum -c -; \
    rm -f /tmp/tiny.gfaz.b64

RUN cat > /opt/vg/share/testdata/vg-smoke.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

tmp="${1:-/tmp/taf-vg-smoke}"
rm -rf "$tmp"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

printf ">ref\nACGTTGCAACGT\n" > ref.fa
samtools faidx ref.fa

cat > tiny.vcf <<'VCF'
##fileformat=VCFv4.2
##contig=<ID=ref,length=12>
#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO
ref	3	.	G	A	.	PASS	.
VCF

bgzip -c tiny.vcf > tiny.vcf.gz
tabix -p vcf tiny.vcf.gz

vg construct -r ref.fa -v tiny.vcf.gz > graph.vg
test -s graph.vg

vg stats -z graph.vg > graph.stats.tsv
grep -F "nodes" graph.stats.tsv >/dev/null
grep -F "edges" graph.stats.tsv >/dev/null

vg view -g graph.vg > graph.gfa
grep -F "VN:Z" graph.gfa >/dev/null
grep -F $'S\t' graph.gfa >/dev/null

vg index -x graph.xg graph.vg
test -s graph.xg

vg paths -x graph.xg -L > paths.txt
grep -Fx "ref" paths.txt >/dev/null

vg viz -x graph.xg -o graph.svg
test -s graph.svg
grep -F "<svg" graph.svg >/dev/null
EOF

RUN cat > /opt/vg/share/testdata/vg-gfaz-smoke.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

tmp="${1:-/tmp/taf-vg-gfaz-smoke}"
fixture="${2:-/opt/vg/share/testdata/tiny.gfaz}"
expected_sha256="809752f1e0569842e8a44620411c9b897c2bcc606acf7baa0b1b8a2f0e60185e"

rm -rf "$tmp"
mkdir -p "$tmp"
trap 'rm -rf "$tmp"' EXIT
cd "$tmp"

test -s "$fixture"
printf '%s  %s\n' "$expected_sha256" "$fixture" | sha256sum -c - >/dev/null

vg convert -g -f "$fixture" > tiny.gfa
test -s tiny.gfa
grep -F $'S\t' tiny.gfa >/dev/null

vg stats -z "$fixture" > tiny.stats.tsv
grep -F "nodes" tiny.stats.tsv >/dev/null
grep -F "edges" tiny.stats.tsv >/dev/null
EOF

# Keep build-time checks lightweight for QEMU arm64 builds. Full graph,
# rendering, and GFAz paths run as independent runtime/index smoke tests.
RUN set -eux; \
    chmod 0755 /opt/vg/share/testdata/vg-smoke.sh /opt/vg/share/testdata/vg-gfaz-smoke.sh; \
    test "$(vg version 2>&1 | sed -n '1p')" = "vg version v${VG_VERSION} \"Chomper\""; \
    { vg help 2>&1 || true; } | grep -F "usage: vg <command> [options]" >/dev/null; \
    { vg convert --help 2>&1 || true; } | grep -F "GFAZ format" >/dev/null; \
    { vg deconstruct --help 2>&1 || true; } | grep -F -- "--cluster-min-len" >/dev/null; \
    command -v samtools >/dev/null; \
    command -v bgzip >/dev/null; \
    command -v tabix >/dev/null; \
    printf '%s  %s\n' "${GFAZ_FIXTURE_SHA256}" /opt/vg/share/testdata/tiny.gfaz | sha256sum -c -; \
    ldd "$(command -v vg)" > /tmp/taf-vg-ldd.txt 2>&1 || true; \
    grep -F "not a dynamic executable" /tmp/taf-vg-ldd.txt >/dev/null; \
    rm -f /tmp/taf-vg-ldd.txt

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=vg
