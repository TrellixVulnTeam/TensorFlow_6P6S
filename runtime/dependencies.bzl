# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Provides a workspace macro to load dependent repositories."""

load("@bazel_tools//tools/build_defs/repo:http.bzl", "http_archive")
load("@bazel_tools//tools/build_defs/repo:utils.bzl", "maybe")
load("@tf_runtime//third_party:repo.bzl", "tfrt_http_archive")
load("@tf_runtime//third_party/cuda:dependencies.bzl", "cuda_dependencies")

def tfrt_dependencies():
    """Loads TFRT external dependencies into WORKSPACE."""

    # Bazel rules to build CUDA targets.
    # TODO(csigg): move this to some public repo.
    maybe(
        name = "rules_cuda",
        repo_rule = native.local_repository,
        path = "third_party/rules_cuda",
    )

    cuda_dependencies()

    # LLVM and MLIR from llvm-project.
    LLVM_COMMIT = "5b29d26b21bb1cc60b7fe9c367a762fa8860f472"
    LLVM_SHA256 = "5a6b842c3066784930e061abda5fb6499ef99f846bdcf4b1f18e746c4148c3e2"
    LLVM_URLS = [
        "https://storage.googleapis.com/mirror.tensorflow.org/github.com/llvm/llvm-project/archive/{commit}.tar.gz".format(commit = LLVM_COMMIT),
        "https://github.com/llvm/llvm-project/archive/{commit}.tar.gz".format(commit = LLVM_COMMIT),
    ]
    maybe(
        name = "llvm-project",
        repo_rule = tfrt_http_archive,
        sha256 = LLVM_SHA256,
        strip_prefix = "llvm-project-" + LLVM_COMMIT,
        urls = LLVM_URLS,
        additional_build_files = {
            "@tf_runtime//third_party/llvm:llvm.autogenerated.BUILD": "llvm/BUILD",
            "@tf_runtime//third_party/mlir:BUILD": "mlir/BUILD",
            "@tf_runtime//third_party/mlir:test.BUILD": "mlir/test/BUILD",
        },
    )

    # https://github.com/bazelbuild/bazel-skylib/releases
    maybe(
        name = "bazel_skylib",
        repo_rule = http_archive,
        sha256 = "97e70364e9249702246c0e9444bccdc4b847bed1eb03c5a3ece4f83dfe6abc44",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/bazelbuild/bazel-skylib/releases/download/1.0.2/bazel-skylib-1.0.2.tar.gz",
            "https://github.com/bazelbuild/bazel-skylib/releases/download/1.0.2/bazel-skylib-1.0.2.tar.gz",
        ],
    )

    # Eigen3
    maybe(
        name = "eigen_archive",
        repo_rule = http_archive,
        build_file = "@tf_runtime//third_party:eigen/BUILD",
        sha256 = "924c7f85d5e2e40beb663489bf3f6908bb4c328dc81ab845c27bb6ce199b8698",  # SHARED_EIGEN_SHA
        strip_prefix = "eigen-3c02fefec53f21d9fad537ff0d62d8dcc8162466",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/gitlab.com/libeigen/eigen/-/archive/3c02fefec53f21d9fad537ff0d62d8dcc8162466/eigen-3c02fefec53f21d9fad537ff0d62d8dcc8162466.tar.gz",
            "https://gitlab.com/libeigen/eigen/-/archive/3c02fefec53f21d9fad537ff0d62d8dcc8162466/eigen-3c02fefec53f21d9fad537ff0d62d8dcc8162466.tar.gz",
        ],
    )

    maybe(
        name = "mkl_dnn",
        repo_rule = http_archive,
        build_file = "@tf_runtime//third_party/mkl_dnn:BUILD.mkl_dnn",
        sha256 = "ed56652dd237deb86ee9bf102c18de5f2625c059e5ab1d7512c8dc01e316b694",
        strip_prefix = "mkl-dnn-0.21.2",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/intel/mkl-dnn/archive/v0.21.2.tar.gz",
            "https://github.com/intel/mkl-dnn/archive/v0.21.2.tar.gz",
        ],
    )

    maybe(
        name = "com_google_googletest",
        repo_rule = tfrt_http_archive,
        sha256 = "ff7a82736e158c077e76188232eac77913a15dac0b22508c390ab3f88e6d6d86",
        strip_prefix = "googletest-b6cd405286ed8635ece71c72f118e659f4ade3fb",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/google/googletest/archive/b6cd405286ed8635ece71c72f118e659f4ade3fb.zip",
            "https://github.com/google/googletest/archive/b6cd405286ed8635ece71c72f118e659f4ade3fb.zip",
        ],
    )

    maybe(
        name = "com_github_google_benchmark",
        repo_rule = http_archive,
        strip_prefix = "benchmark-16703ff83c1ae6d53e5155df3bb3ab0bc96083be",
        sha256 = "59f918c8ccd4d74b6ac43484467b500f1d64b40cc1010daa055375b322a43ba3",
        urls = ["https://github.com/google/benchmark/archive/16703ff83c1ae6d53e5155df3bb3ab0bc96083be.zip"],
    )

    maybe(
        name = "com_google_protobuf",
        repo_rule = tfrt_http_archive,
        patch_file = "//third_party/protobuf:protobuf.patch",
        sha256 = "cfcba2df10feec52a84208693937c17a4b5df7775e1635c1e3baffc487b24c9b",
        strip_prefix = "protobuf-3.9.2",
        system_build_file = "//third_party/systemlibs:protobuf.BUILD",
        system_link_files = {
            "//third_party/systemlibs:protobuf.bzl": "protobuf.bzl",
        },
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/protocolbuffers/protobuf/archive/v3.9.2.zip",
            "https://github.com/protocolbuffers/protobuf/archive/v3.9.2.zip",
        ],
    )

    maybe(
        name = "cub_archive",
        repo_rule = tfrt_http_archive,
        build_file = "//third_party:cub/BUILD",
        patch_file = "//third_party:cub/pr170.patch",
        sha256 = "6bfa06ab52a650ae7ee6963143a0bbc667d6504822cbd9670369b598f18c58c3",
        strip_prefix = "cub-1.8.0",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/github.com/NVlabs/cub/archive/1.8.0.zip",
            "https://github.com/NVlabs/cub/archive/1.8.0.zip",
        ],
    )

    maybe(
        name = "zlib",
        repo_rule = tfrt_http_archive,
        build_file = "//third_party:zlib.BUILD",
        sha256 = "c3e5e9fdd5004dcb542feda5ee4f0ff0744628baf8ed2dd5d66f8ca1197cb1a1",
        strip_prefix = "zlib-1.2.11",
        system_build_file = "//third_party/systemlibs:zlib.BUILD",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/zlib.net/zlib-1.2.11.tar.gz",
            "https://zlib.net/zlib-1.2.11.tar.gz",
        ],
    )

    maybe(
        name = "py-cpuinfo",
        repo_rule = tfrt_http_archive,
        strip_prefix = "py-cpuinfo-0.2.3",
        sha256 = "f6a016fdbc4e7fadf2d519090fcb4fa9d0831bad4e85245d938e5c2fe7623ca6",
        urls = [
            "https://storage.googleapis.com/mirror.tensorflow.org/pypi.python.org/packages/source/p/py-cpuinfo/py-cpuinfo-0.2.3.tar.gz",
            "https://pypi.python.org/packages/source/p/py-cpuinfo/py-cpuinfo-0.2.3.tar.gz",
        ],
        build_file = "//third_party:py-cpuinfo.BUILD",
    )
