load("@rules_python//python:defs.bzl", "py_library")
load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "cli",
    srcs = glob(["**/*.py"]),
    imports = [".."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("typer"),
        requirement("requests"),
        requirement("kubernetes"),
        requirement("python-dotenv"),
    ],
)
