from setuptools import setup

setup(
    name="your_package",
    version="1.0.0",
    entry_points={
        "console_scripts": [
            "rmcli=request_manager.main:main",
        ],
    },
)
