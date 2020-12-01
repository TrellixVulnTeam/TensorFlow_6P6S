# Placeholder google/other-text-embedding-model/1
The placeholder is used to group different deployment formats of a model (TF.js,
TFLite) when the TF model itself is not present. Deployment formats are grouped
to the same placeholder by adding the parent-model tag in their markdown file.

The placeholder file should contain short description and metadata tags. For
example:

Token based text embedding trained on English Wikipedia corpus[1].

<!-- module-type: text-embedding -->
<!-- network-architecture: skip-gram -->
<!-- network-architecture: word2vec -->
<!-- dataset: Wikipedia -->
<!-- language: en -->
