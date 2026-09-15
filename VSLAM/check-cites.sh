#!/usr/bin/env bash
# Kiểm mọi \cite{...} trong cây có tồn tại trong refs.bib không.
cd "$(dirname "$0")"
grep -o '^@[a-z]*{[^,]*' refs.bib | sed 's/.*{//' | sort -u > /tmp/_bibkeys.txt
grep -rho '\\cite[a-z]*\(\[[^]]*\]\)\?{[^}]*}' --include='*.tex' . \
  | sed 's/.*{//; s/}//' | tr ',' '\n' | tr -d ' ' | sort -u > /tmp/_usedkeys.txt
missing=$(comm -23 /tmp/_usedkeys.txt /tmp/_bibkeys.txt)
if [ -n "$missing" ]; then echo "THIẾU trong refs.bib:"; echo "$missing"; exit 1
else echo "   ok  mọi bibkey đều có trong refs.bib ($(wc -l < /tmp/_usedkeys.txt) khoá được dùng)"; fi
