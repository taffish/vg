#!/usr/bin/env bash
set -euo pipefail
# 独占目录，不接受调用者提供的递归删除目标。stdout/stderr 在失败时带步骤回放。
scratch=$(mktemp -d "${TMPDIR:-/tmp}/taf-vg-smoke.XXXXXX")
stage=initialize
finish() {
  rc=$?
  if test "$rc" != 0; then
    printf >&2 'vg-smoke failed: stage=%s exit=%s\n' "$stage" "$rc"
    for log in "$scratch"/*.log; do test ! -f "$log" || tail -c 4000 "$log" >&2; done
  fi
  rm -rf -- "$scratch"
  exit "$rc"
}
trap finish EXIT
cd "$scratch"
stage=construct
printf '>ref\nACGTTGCAACGT\n' > ref.fa
samtools faidx ref.fa > samtools.log 2>&1
printf '##fileformat=VCFv4.2\n##contig=<ID=ref,length=12>\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\nref\t3\t.\tG\tA\t.\tPASS\t.\n' > tiny.vcf
bgzip -c tiny.vcf > tiny.vcf.gz 2> bgzip.log
tabix -p vcf tiny.vcf.gz > tabix.log 2>&1
vg construct -t 1 -r ref.fa -v tiny.vcf.gz > graph.vg 2> construct.log
test -s graph.vg
stage=stats-convert-index
vg stats -z graph.vg > graph.stats.tsv 2> stats.log
grep -F nodes graph.stats.tsv >/dev/null
grep -F edges graph.stats.tsv >/dev/null
vg convert -t 1 -f graph.vg > graph.gfa 2> convert.log
grep -F $'S\t' graph.gfa >/dev/null
vg index -t 1 -x graph.xg graph.vg > index.log 2>&1
vg paths -x graph.xg -L > paths.txt 2> paths.log
grep -Fx ref paths.txt >/dev/null
stage=svg
vg viz -x graph.xg -o graph.svg > viz.log 2>&1
test -s graph.svg
grep -F '<svg' graph.svg >/dev/null
stage=gfaz
vg convert -t 1 -g -f /opt/vg/share/testdata/tiny.gfaz > tiny.gfa 2> gfaz.log
grep -F $'S\t' tiny.gfa >/dev/null
vg stats -z /opt/vg/share/testdata/tiny.gfaz > gfaz.stats.tsv 2>> gfaz.log
grep -F nodes gfaz.stats.tsv >/dev/null
printf 'vg-smoke PASS: construct, index, paths, SVG, GFAz\n'
