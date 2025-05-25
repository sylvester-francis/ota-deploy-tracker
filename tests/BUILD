load("@rules_python//python:defs.bzl", "py_test")
load("@pip_deps//:requirements.bzl", "requirement")

py_test(
    name = "api_test",
    srcs = ["test_api.py"],
    deps = [
        "//backend",
        requirement("pytest"),
        requirement("httpx"),
    ],
)

py_test(
    name = "cli_test",
    srcs = ["test_cli.py"],
    deps = [
        "//cli",
        requirement("pytest"),
    ],
)

py_test(
    name = "job_runner_test",
    srcs = ["test_job_runner.py"],
    deps = [
        "//cli",
        requirement("pytest"),
    ],
)
