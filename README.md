# vg

TAFFISH tool app for [VG](https://github.com/vgteam/vg), the variation graph
toolkit for constructing, indexing, mapping, genotyping, calling, and converting
variation graphs and pangenome graph data.

Package identity:

- TAFFISH app: `vg`
- Command: `taf-vg`
- TAFFISH version: `1.76.1-r1`
- TAFFISH app license: `Apache-2.0`
- Upstream tag: `v1.76.1`
- Upstream release: [VG v1.76.1](https://github.com/vgteam/vg/releases/tag/v1.76.1)
- Runtime version string: `vg version v1.76.1`
- Container image: `ghcr.io/taffish/vg:1.76.1-r1`

This package wraps upstream VG `1.76.1` and publishes it as:

```bash
taf-vg vg version
taf-vg vg help
```

## What Is Packaged

- `vg`: upstream VG command suite.
- `samtools`, `bgzip`, `tabix`: helper commands available in the official
  upstream runtime image and useful for FASTA/VCF preparation.
- TAFFISH metadata, terminal help, a synthetic graph smoke, and the tiny GFAz
  fixture shipped in the upstream VG source tree.
- The exact upstream top-level license notice from tag `v1.76.1`, installed at
  `/opt/vg/share/licenses/vg/LICENSE` and bound to its recorded SHA256.

The container is based on the official upstream image
`quay.io/vgteam/vg:v1.76.1` pinned by the multi-architecture manifest digest
`sha256:e62d087d6ee64a302f1703046bc556892b530163b0dc44824b291571e8f11d9b`.

At packaging time, GitHub marks the `v1.76.1` release page as a prerelease, as
it also does for the already packaged `v1.76.0`. This app intentionally follows
VG's official semantic-version tags and digest-pinned official images; the tag,
release assets, and native amd64/arm64 image manifests are all present.

## Basic Usage

Show the upstream version and command overview:

```bash
taf-vg vg version
taf-vg vg help
```

Construct a small graph from FASTA and VCF:

```bash
taf-vg samtools faidx ref.fa
taf-vg bgzip -c variants.vcf > variants.vcf.gz
taf-vg tabix -p vcf variants.vcf.gz
taf-vg vg construct -r ref.fa -v variants.vcf.gz > graph.vg
```

Inspect and convert a graph:

```bash
taf-vg vg stats -z graph.vg
taf-vg vg view -g graph.vg > graph.gfa
taf-vg vg index -x graph.xg graph.vg
taf-vg vg paths -x graph.xg -L
```

Read a GFAz graph introduced in VG 1.76.0:

```bash
taf-vg vg stats -z graph.gfaz
taf-vg vg convert -g -f graph.gfaz > graph.gfa
```

Build indexes for a Giraffe workflow:

```bash
taf-vg vg autoindex --workflow giraffe \
  -r ref.fa \
  -v variants.vcf.gz \
  -p sample-index
```

Run a typical mapping and calling outline:

```bash
taf-vg vg giraffe \
  -Z sample-index.giraffe.gbz \
  -m sample-index.min \
  -d sample-index.dist \
  -f reads.fq > aln.gam

taf-vg vg pack -x graph.xg -g aln.gam -o aln.pack
taf-vg vg call graph.xg -k aln.pack > calls.vcf
```

## Command-Mode Notes

VG has many subcommands, such as `construct`, `index`, `stats`, `giraffe`,
`pack`, `call`, and `deconstruct`. With TAFFISH command mode, prefer the explicit
form:

```bash
taf-vg vg construct ...
```

Do not use `taf-vg construct ...` or `taf-vg -- construct ...`; those forms can
be interpreted as requests to run a container executable named `construct`.
Upstream VG also does not use `vg --help` as its main help entry. Use
`taf-vg vg help` or `taf-vg vg` for the upstream overview.

## Inputs And Outputs

Common inputs:

- FASTA and `.fai` reference indexes.
- VCF/BCF, usually bgzip-compressed and tabix-indexed.
- VG graph files, GFA, GBZ, XG, GCSA2, GBWT, GAM, GAF, and related VG formats.
- FASTQ/BAM/GAM read or alignment inputs for mapping and calling workflows.

Common outputs:

- `.vg`, GFA, and GBZ graph containers.
- `.xg`, `.gcsa`, `.gbwt`, `.dist`, `.min`, and related index files.
- `.gam` or `.gaf` graph alignments.
- `.pack` coverage indexes.
- VCF/BCF calls and graph deconstruction outputs.

## Runtime Boundaries

This app does not bundle reference genomes, sample data, prebuilt graph indexes,
or workflow-specific databases. Provide those files explicitly from the working
directory or mounted paths.

No network service, external database, GPU, or license server is required by the
packaged CPU runtime. Whole-genome pangenome workflows can still require large
amounts of memory, CPU time, and temporary disk space, especially during GCSA,
GBWT/GBZ, Giraffe, and variant-calling workflows.

VG 1.76.1 carries forward the 1.76.0 GFAz input,
`vg deconstruct --cluster-min-len`, minimizer fixes, and stricter Giraffe option
validation. The patch release restores the bundled `elfutils` build for static
binaries, corrects gref VCF `LV` semantics for `vcfbub`, and omits unused
contigs from generated VCF headers. Upstream intentionally removed the
deprecated `vg sift`, `vg join`, `vg explode`, and `vg msga` commands in
1.76.0, as well as `vg paths -N` and `vg circularize --describe`; their absence
is not a TAFFISH packaging omission.

The smoke test constructs a tiny FASTA/VCF graph, compresses and indexes the VCF
with `bgzip`/`tabix`, builds a VG graph, reports graph stats, converts to GFA,
builds an XG index, lists embedded paths, and renders an SVG with `vg viz`. A
separate smoke reads and converts the upstream tiny GFAz fixture. These checks
verify packaging and basic runtime behavior, not biological correctness or
production-scale performance.

Local release builds measure about 837 MB for arm64 and 819 MB for amd64, only
12,727 bytes above the corresponding official base images. VG itself is
statically linked, while the official image also supplies helper commands and
runtime support used by established VG workflows. The TAFFISH layer adds only
small docs and fixtures; no independent package manager environment or cache is
added, and no clearly safe large deletion was identified without narrowing
upstream functionality.

## Platforms

The upstream official image provides native `linux/amd64` and `linux/arm64`
manifests. This TAFFISH app requests both platforms.

## License And Citation

The TAFFISH wrapper metadata and documentation are distributed under
`Apache-2.0`. Upstream VG is distributed under the `MIT` license; its complete
top-level license notice is retained in the image and verified during build and
offline smoke.

Primary citation:

> Garrison et al. 2018. Variation graph toolkit improves read mapping by
> representing genetic variation in the reference. Nature Biotechnology.
> DOI: `10.1038/nbt.4227`.

VG includes subcommand-specific methods and papers. For publication work, also
follow the upstream README's citation guidance for the exact VG mode used, such
as Giraffe, GBZ, VG Call, or graph construction workflows.

## Upstream Resources

- Homepage and source: <https://github.com/vgteam/vg>
- Usage overview: <https://github.com/vgteam/vg#usage>
- Release notes: <https://github.com/vgteam/vg/releases/tag/v1.76.1>
