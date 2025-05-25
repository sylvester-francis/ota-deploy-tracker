load("@rules_python//python:defs.bzl", "py_binary", "py_library", "py_test")

package(default_visibility = ["//visibility:public"])

# Backend library
py_library(
    name = "backend_lib",
    srcs = glob(["backend/**/*.py"]),
    imports = ["."],
)

# CLI library
py_library(
    name = "cli_lib",
    srcs = glob(["cli/**/*.py"]),
    imports = ["."],
)

# Dashboard library
py_library(
    name = "dashboard_lib",
    srcs = glob(["dashboard/**/*.py"]),
    imports = ["."],
)

# API server binary
py_binary(
    name = "api_server",
    srcs = ["backend/main.py"],
    main = "backend/main.py",
    deps = [
        ":backend_lib",
    ],
)

# Dashboard binary
py_binary(
    name = "dashboard",
    srcs = ["dashboard/ota_dashboard.py"],
    main = "dashboard/ota_dashboard.py",
    deps = [
        ":dashboard_lib",
    ],
)

# CLI binary
py_binary(
    name = "cli",
    srcs = ["cli/client.py"],
    main = "cli/client.py",
    deps = [
        ":cli_lib",
    ],
)

# Job runner binary
py_binary(
    name = "job_runner",
    srcs = ["cli/job_runner.py"],
    main = "cli/job_runner.py",
    deps = [
        ":cli_lib",
    ],
)

# Tests
py_test(
    name = "api_test",
    srcs = ["tests/test_api.py"],
    deps = [
        ":backend_lib",
    ],
)

py_test(
    name = "cli_test",
    srcs = ["tests/test_cli.py"],
    deps = [
        ":cli_lib",
    ],
)

py_test(
    name = "job_runner_test",
    srcs = ["tests/test_job_runner.py"],
    deps = [
        ":cli_lib",
    ],
)
