#!/usr/bin/env bash
# ./build.sh          -> english.pdf (bản gộp toàn cây)
# ./build.sh all      -> thêm PDF riêng cho từng phần, từng chương
# ./build.sh <đường dẫn .tex>  -> dựng riêng một file
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
  "")   build english.tex ;;
  all)  build english.tex
        build 00-map.tex
        for f in [A-E]-*/*.tex [A-E]-*/*/*.tex; do build "$f"; done ;;
  *)    build "$1" ;;
esac
