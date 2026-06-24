ARG VG_VERSION=1.75.0
ARG VG_UPSTREAM_IMAGE=quay.io/vgteam/vg@sha256:1982a810474ea1990a2ae21adc51b018c8eb709941fc38b6b0d3e83acfe2e0d6
FROM ${VG_UPSTREAM_IMAGE}

ARG VG_VERSION
ARG VG_UPSTREAM_IMAGE

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
      printf '%s\n' "VG version: ${VG_VERSION}"; \
      printf '%s\n' "Upstream image: ${VG_UPSTREAM_IMAGE}"; \
      printf '%s\n' "Upstream source: https://github.com/vgteam/vg"; \
      printf '%s\n' "Upstream release: https://github.com/vgteam/vg/releases/tag/v${VG_VERSION}"; \
    } > /opt/vg/share/doc/vg/source.txt; \
    { \
      printf '%s\n' "VG is distributed upstream under the MIT license."; \
      printf '%s\n' "See https://github.com/vgteam/vg/blob/master/LICENSE for the upstream license text."; \
      printf '%s\n' "This TAFFISH wrapper metadata and documentation are distributed under Apache-2.0."; \
    } > /opt/vg/share/licenses/vg/LICENSE-note.txt

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
grep -F "S	" graph.gfa >/dev/null

vg index -x graph.xg graph.vg
test -s graph.xg

vg paths -x graph.xg -L > paths.txt
grep -Fx "ref" paths.txt >/dev/null
EOF

RUN set -eux; \
    chmod 0755 /opt/vg/share/testdata/vg-smoke.sh; \
    vg version 2>&1 | grep -F "vg version v${VG_VERSION}" >/dev/null; \
    { vg help 2>&1 || true; } | grep -F "usage: vg <command> [options]" >/dev/null; \
    { vg construct --help 2>&1 || true; } | grep -F "usage: vg construct" >/dev/null; \
    { vg index --help 2>&1 || true; } | grep -F "usage: vg index" >/dev/null; \
    { vg stats --help 2>&1 || true; } | grep -F "usage: vg stats" >/dev/null; \
    command -v samtools >/dev/null; \
    command -v bgzip >/dev/null; \
    command -v tabix >/dev/null; \
    /opt/vg/share/testdata/vg-smoke.sh /tmp/taf-vg-build-smoke; \
    ldd "$(command -v vg)" > /tmp/taf-vg-ldd.txt 2>&1 || true; \
    grep -F "not a dynamic executable" /tmp/taf-vg-ldd.txt >/dev/null; \
    rm -f /tmp/taf-vg-ldd.txt

WORKDIR /root

ENV TAFFISH_ENV=TAFFISH
ENV TAFFISH_NAME=vg
