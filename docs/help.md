vg 1.75.0-r1

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
  GFA/GBZ/.vg    Graph interchange and native graph containers.
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
  This app packages the official upstream VG 1.75.0 runtime image with TAFFISH
  metadata, docs, and smoke checks. It does not bundle reference genomes,
  sample data, prebuilt pangenome indexes, or workflow-specific databases.
  Upstream notes a known VG 1.75.0 issue where one single-command haplotype
  sampling mode of vg giraffe can write KMC logs into alignment output files.
  Avoid that affected mode or follow upstream guidance when using it.
  The smoke test uses a tiny synthetic FASTA/VCF graph and does not validate
  production-scale mapping accuracy, calling quality, or graph biology.

Detailed documentation:
  https://github.com/vgteam/vg
  https://github.com/vgteam/vg#usage
  https://github.com/vgteam/vg/releases/tag/v1.75.0

Wrapper options:
  taf-vg --help       Show this TAFFISH help.
  taf-vg --version    Show TAFFISH wrapper version.
  taf-vg --compile    Compile the TAFFISH wrapper.
  taf-vg vg help      Show upstream VG command overview.
