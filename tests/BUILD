load("@rules_python//python:defs.bzl", "py_test")

py_test(
    name = "api_test",
    srcs = ["test_api.py"],
    deps = [
        "//backend",
    ],
)

py_test(
    name = "cli_test",
    srcs = ["test_cli.py"],
    deps = [
        "//cli",
    ],
)

py_test(
    name = "job_runner_test",
    srcs = ["test_job_runner.py"],
    deps = [
        "//cli",
    ],
)
