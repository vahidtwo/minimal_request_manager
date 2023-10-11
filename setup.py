from setuptools import setup

setup(
    name="reqeust_manager",
    version="0.0.1",
    entry_points={
        "console_scripts": [
            "rmcli=request_manager.cli:main",
        ],
    },
)
