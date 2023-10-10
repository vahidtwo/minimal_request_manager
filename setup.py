from setuptools import setup

setup(
    name="reqeust_manager",
    version="1.0.0",
    entry_points={
        "console_scripts": [
            "rmcli=request_manager.cli:main",
        ],
    },
)
