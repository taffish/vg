# vg

TAFFISH tool app for [VG](https://github.com/vgteam/vg), the variation graph
toolkit for constructing, indexing, mapping, genotyping, calling, and converting
variation graphs and pangenome graph data.

This package wraps upstream VG `1.75.0` and publishes it as:

```bash
taf-vg vg version
taf-vg vg help
```

## What Is Packaged

- `vg`: upstream VG command suite.
- `samtools`, `bgzip`, `tabix`: helper commands available in the official
  upstream runtime image and useful for FASTA/VCF preparation.
- TAFFISH metadata, terminal help, and a tiny offline smoke fixture.

The container is based on the official upstream image
`quay.io/vgteam/vg:v1.75.0` pinned by the multi-architecture manifest digest
`sha256:1982a810474ea1990a2ae21adc51b018c8eb709941fc38b6b0d3e83acfe2e0d6`.
Bioconda was not used for this release because its published VG recipe lagged
behind the current upstream VG release at packaging time.

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

Upstream VG `1.75.0` release notes mention a known issue in one single-command
haplotype sampling mode of `vg giraffe`: KMC log messages can be written into
alignment output files and corrupt them. Avoid that affected mode or follow
upstream guidance if you need it.

The smoke test constructs a tiny FASTA/VCF graph, compresses and indexes the VCF
with `bgzip`/`tabix`, builds a VG graph, reports graph stats, converts to GFA,
builds an XG index, and lists embedded paths. It verifies packaging and basic
runtime behavior, not biological correctness or production-scale performance.

## Platforms

The upstream official image provides native `linux/amd64` and `linux/arm64`
manifests. This TAFFISH app requests both platforms.

## License And Citation

The TAFFISH wrapper metadata and documentation are distributed under
`Apache-2.0`. Upstream VG is distributed under the `MIT` license.

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
- Release notes: <https://github.com/vgteam/vg/releases/tag/v1.75.0>
