if [[ $(poetry version -s) =~ ^([0-9]+\.?)+-(alpha|beta)\.[0-9]+$  ]]; then
  echo "yes"
else
  echo "no"
fi
