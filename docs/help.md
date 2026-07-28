taf-vg 1.76.0-r1

Purpose:
  VG constructs, indexes, maps, genotypes, calls, and converts variation
  graphs and pangenome graph data. It supports graph formats and indexes used
  by VG workflows, including .vg, GFA, GBZ, XG, GCSA2, GAM, and related files.

Usage:
  taf-vg vg
  taf-vg vg help
  taf-vg vg version
  taf-vg vg construct -r ref.fa -v variants.vcf.gz > graph.vg
  taf-vg vg index -x graph.xg graph.vg
  taf-vg vg stats -z graph.vg
  taf-vg vg view -g graph.vg > graph.gfa
  taf-vg vg stats -z graph.gfaz
  taf-vg vg convert -g -f graph.gfaz > graph.gfa

Common workflows:
  taf-vg vg construct -r ref.fa -v variants.vcf.gz > graph.vg
  taf-vg vg autoindex --workflow giraffe -r ref.fa -v variants.vcf.gz -p idx
  taf-vg vg giraffe -Z idx.giraffe.gbz -m idx.min -d idx.dist -f reads.fq > aln.gam
  taf-vg vg pack -x graph.xg -g aln.gam -o aln.pack
  taf-vg vg call graph.xg -k aln.pack > calls.vcf
  taf-vg vg deconstruct graph.gbz -P refpath > graph.vcf

Packaged commands:
  vg        Upstream VG command suite.
  samtools  Helper from the official upstream runtime image.
  bgzip     VCF compression helper from the official upstream runtime image.
  tabix     VCF indexing helper from the official upstream runtime image.

Selected VG subcommands:
  construct    Build a graph from FASTA and optional VCF input.
  autoindex    Build mapping/calling indexes from interchange formats.
  index        Build XG, GCSA2, GBWT/GBZ, minimizer, or related indexes.
  giraffe      Fast haplotype-aware read mapping.
  map/mpmap    MEM-based and splice-aware mapping modes.
  pack         Convert alignments to compact coverage indexes.
  call         Genotype or call variants from graph-alignment evidence.
  deconstruct  Convert graph variation back to VCF.
  stats/view   Inspect and convert graph or alignment files.

Command-mode note:
  VG uses subcommands such as construct, index, stats, call, and giraffe.
  Prefer:
    taf-vg vg construct ...
  to run the explicit vg executable inside the container. Do not use
  taf-vg construct ... or taf-vg -- construct ... because TAFFISH command mode
  may treat construct as a container executable name. VG's main help is printed
  by vg help or vg with no subcommand; upstream vg --help is not the main help.

Inputs:
  FASTA/FAI      Reference sequences and samtools faidx indexes.
  VCF/VCF.GZ     Variant calls for graph construction and genotyping workflows.
  GFA/GFAz/GBZ   Graph interchange and compressed/native graph containers.
  FASTQ/BAM/GAM  Reads or graph alignments for mapping and calling workflows.

Key outputs:
  .vg, GFA, GBZ  Graph containers and interchange files.
  .xg, .gcsa     Query and mapping indexes.
  .gam, .gaf     Graph alignment outputs.
  .pack          Coverage indexes for calling.
  VCF/BCF        Variant calling or graph deconstruction outputs.

Platform and resources:
  Native container builds are requested for linux/amd64 and linux/arm64 from
  the official upstream VG image. No external database, network service, GPU,
  or license server is required by the packaged CPU runtime. Memory, CPU, and
  disk use can be very large for whole-genome pangenome graphs and GCSA/GBWT
  index construction.

Boundaries:
  This app packages the official upstream VG 1.76.0 runtime image with TAFFISH
  metadata, docs, and smoke checks. It does not bundle reference genomes,
  sample data, prebuilt pangenome indexes, or workflow-specific databases.
  VG 1.76.0 adds GFAz input and deconstruct --cluster-min-len. Upstream also
  removed the deprecated sift, join, explode, and msga subcommands; their
  absence is intentional. Independent smoke paths use a tiny synthetic
  FASTA/VCF graph with SVG rendering and an upstream GFAz fixture. They do not
  validate production-scale mapping accuracy, calling quality, or graph biology.

Detailed documentation:
  https://github.com/vgteam/vg
  https://github.com/vgteam/vg#usage
  https://github.com/vgteam/vg/releases/tag/v1.76.0

Wrapper options:
  taf-vg --help       Show this TAFFISH help.
  taf-vg --version    Show TAFFISH wrapper version.
  taf-vg --compile    Compile the TAFFISH wrapper.
  taf-vg vg help      Show upstream VG command overview.
