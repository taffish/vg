ARG VG_VERSION=1.78.0
# Digests/checksums identify upstream bytes, not permanent hosting guarantees.
# On registry/release removal, recheck the official release; never disable verification.
ARG VG_UPSTREAM_IMAGE=quay.io/vgteam/vg@sha256:febc2401166d4acd81cbf07d89158feccee8c13de70613f72e641d48ceea4ca8
ARG NODE_IMAGE=mirror.gcr.io/library/node@sha256:83f487e0a63425e5b4d146fb5e5be574bcbe1b7b843d3ebafdd95eaf7767a7e5
FROM ${NODE_IMAGE} AS node
FROM ${VG_UPSTREAM_IMAGE} AS gui-build
USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
COPY --from=node /usr/local/ /usr/local/
# Locked websocket addons need native compilation where prebuilt binaries are absent.
# Compilers stay in the builder; use Node's matching local headers.
# apt indexes are mutable. If a package disappears, refresh/review this builder
# against the same base and rerun both native builds; no availability guarantee.
RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*
ENV npm_config_nodedir=/usr/local
ARG TUBEMAP_COMMIT=33b7a7e5df9f8052974ef8e6c689a031dac6e2c9
ARG TUBEMAP_SHA256=a133a4d79dafafce6f67d0ea8dd90ab11f8ac893c63deed401c8d7a924df9b1f
WORKDIR /build
RUN set -eux; \
    curl -fL --retry 3 --connect-timeout 30 --max-time 1800 \
      "https://codeload.github.com/vgteam/sequenceTubeMap/tar.gz/${TUBEMAP_COMMIT}" -o tubemap.tar.gz; \
    echo "${TUBEMAP_SHA256}  tubemap.tar.gz" | sha256sum -c -; \
    mkdir tubemap; tar -xzf tubemap.tar.gz --strip-components=1 -C tubemap
COPY docker/prepare-tubemap.py /build/
RUN python3 /build/prepare-tubemap.py
WORKDIR /build/tubemap
# The upstream lockfile and patch-package patch are preserved, not npm update.
# npm tarball availability is external; integrity failure requires source review,
# not a silent lockfile refresh or disabled checksum.
# Front-end compilation is not a browser/rendering or graph-analysis smoke.
RUN npm ci --no-audit --no-fund && GENERATE_SOURCEMAP=false npm run build
COPY docker/package-tubemap.py /build/
RUN python3 /build/package-tubemap.py

FROM ${VG_UPSTREAM_IMAGE} AS source-material
USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
ARG VG_VERSION
ARG VG_SOURCE_SHA256=2462a063cfdeeef328fb8053d8f1b140fc6b0039a88f3b4a74d8ab7f0b610bc0
RUN set -eux; \
    mkdir -p /out/sources /out/licenses/vg-dependencies /unpack; \
    curl -fL --retry 3 --connect-timeout 30 --max-time 1800 \
      "https://github.com/vgteam/vg/releases/download/v${VG_VERSION}/vg-v${VG_VERSION}.tar.gz" \
      -o /out/sources/vg-v${VG_VERSION}.tar.gz; \
    echo "${VG_SOURCE_SHA256}  /out/sources/vg-v${VG_VERSION}.tar.gz" | sha256sum -c -; \
    tar -xzf /out/sources/vg-v${VG_VERSION}.tar.gz -C /unpack --strip-components=1
COPY docker/collect-vg-notices.py /unpack/
RUN python3 /unpack/collect-vg-notices.py

FROM ${VG_UPSTREAM_IMAGE}
ARG VG_VERSION
ARG VG_UPSTREAM_IMAGE
ARG VG_TAG_COMMIT=315509da9be8a4ca7c94631b471d0d835dbd7a33
USER root
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
LABEL org.opencontainers.image.title="TAFFISH vg with Sequence Tube Map" \
      org.opencontainers.image.source="https://github.com/taffish/vg" \
      org.opencontainers.image.version="${VG_VERSION}-r1" \
      org.opencontainers.image.licenses="See /opt/vg/share/licenses and /opt/vg/tubemap/licenses"
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/LICENSE /opt/vg/share/licenses/node/LICENSE
COPY --from=gui-build /out/tubemap /opt/vg/tubemap
COPY --from=gui-build /build/tubemap.tar.gz /opt/vg/share/sources/sequenceTubeMap-33b7a7e.tar.gz
COPY --from=source-material /out/ /opt/vg/share/
COPY docker/licenses/vg-LICENSE /opt/vg/share/licenses/vg/LICENSE
COPY docker/testdata/ /opt/vg/share/testdata/
COPY docker/tubemap-launch.mjs /opt/vg/tubemap/tubemap-launch.mjs
COPY docker/vg-tubemap docker/vg-resources /usr/local/bin/
COPY src/resource_validation.py src/resource-catalog.json /usr/local/bin/
COPY src/resource-catalog.json /opt/vg/share/resource-catalog.json
RUN set -eux; \
    ln -sf /vg/bin/vg /usr/local/bin/vg; \
    chmod 0755 /usr/local/bin/vg-tubemap /usr/local/bin/vg-resources /opt/vg/share/testdata/*.sh; \
    base64 -d /opt/vg/share/testdata/tiny.gfaz.b64 > /opt/vg/share/testdata/tiny.gfaz; \
    echo '809752f1e0569842e8a44620411c9b897c2bcc606acf7baa0b1b8a2f0e60185e  /opt/vg/share/testdata/tiny.gfaz' | sha256sum -c -; \
    echo '7c3fe1c48ef0594c8d6728353d9325b5f4335eceea5bda3734820d7478bdeaef  /opt/vg/share/licenses/vg/LICENSE' | sha256sum -c -; \
    mkdir -p /opt/vg/tubemap/exampleData/taffish /opt/vg/share/doc/vg /vg-resource /resource-install; \
    vg convert -t 1 -g -x /opt/vg/share/testdata/tiny.gfa > /opt/vg/tubemap/exampleData/taffish/tiny.xg; \
    test -s /opt/vg/tubemap/exampleData/taffish/tiny.xg; \
    printf '%s\n' "version=${VG_VERSION}" "tag=v${VG_VERSION}" "tag_commit=${VG_TAG_COMMIT}" \
      "upstream_manifest=${VG_UPSTREAM_IMAGE#*@}" "github_release_prerelease_at_packaging=false" \
      "upstream_amd64_manifest=sha256:7a88081b74cad8918aca178c35c204c4daa53c3e2d59d4aca7efe970c3db0abd" \
      "upstream_arm64_manifest=sha256:d87bb10e676f848a79e64e357ad19fcebe517e144cc8081f7afe8e570c6cbbc2" \
      "source_sha256=2462a063cfdeeef328fb8053d8f1b140fc6b0039a88f3b4a74d8ab7f0b610bc0" \
      "tubemap_commit=33b7a7e5df9f8052974ef8e6c689a031dac6e2c9" \
      "tubemap_sha256=a133a4d79dafafce6f67d0ea8dd90ab11f8ac893c63deed401c8d7a924df9b1f" \
      > /opt/vg/share/doc/vg/source.txt
# Stable, small build probes only. Native runtime tests cover complete CLI and GUI.
RUN set -eux; \
    vg version > /tmp/vg-version.txt 2>&1; \
    grep -Fx 'vg version v1.78.0 "Sharptooth"' /tmp/vg-version.txt; \
    { vg help 2>&1 || true; } | grep -F 'usage: vg <command> [options]'; \
    node --version; vg-tubemap --help; vg-resources list; \
    node --check /opt/vg/tubemap/src/server.mjs; \
    test -s /opt/vg/tubemap/build/index.html; \
    test -s /opt/vg/tubemap/licenses/npm-inventory.json; \
    rm -f /tmp/vg-version.txt
WORKDIR /tmp
ENV TAFFISH_ENV=TAFFISH TAFFISH_NAME=vg PYTHONDONTWRITEBYTECODE=1
