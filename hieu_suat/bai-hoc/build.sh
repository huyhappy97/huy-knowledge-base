#!/usr/bin/env bash
# ./build.sh          -> hieu-suat.pdf (bản gộp)
# ./build.sh all      -> thêm PDF riêng cho từng chương
# ./build.sh <file>   -> dựng riêng một file
set -e
cd "$(dirname "$0")"
build() {
  local f="$1" d b
  d="$(dirname "$f")"; b="$(basename "$f")"
  (cd "$d" && latexmk -xelatex -interaction=nonstopmode -halt-on-error "$b" >build.log 2>&1 \
     && latexmk -c "$b" >/dev/null 2>&1 && rm -f ./*.xdv ./*.run.xml ./*.bbl build.log \
     && echo "   ok  $f  ($(pdfinfo "${b%.tex}.pdf" | awk '/Pages/{print $2}') trang)" \
     || { echo "   !!  $f  THẤT BẠI — xem $d/build.log"; exit 1; })
}
case "$1" in
  "")   build hieu-suat.tex ;;
  all)  build hieu-suat.tex; build 00-map.tex; build 99-ket-luan.tex
        for f in [0-9][0-9]-*/*.tex; do build "$f"; done ;;
  *)    build "$1" ;;
esac
