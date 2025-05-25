load("@rules_python//python:defs.bzl", "py_library")
load("@pip_deps//:requirements.bzl", "requirement")

py_library(
    name = "backend",
    srcs = glob(["**/*.py"]),
    imports = [".."],
    visibility = ["//visibility:public"],
    deps = [
        requirement("fastapi"),
        requirement("uvicorn"),
        requirement("sqlalchemy"),
        requirement("pydantic"),
    ],
)
