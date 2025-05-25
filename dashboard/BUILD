load("@rules_python//python:defs.bzl", "py_library")
load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "dashboard",
    srcs = glob(["**/*.py"]),
    imports = [".."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("streamlit"),
        requirement("pandas"),
        requirement("requests"),
        requirement("python-dotenv"),
    ],
)
