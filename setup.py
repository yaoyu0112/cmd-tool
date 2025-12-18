from setuptools import setup, find_packages

with open("read.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cmd-gui-tool",
    version="1.0.0",
    author="開發者",
    author_email="your.email@example.com",
    description="CMD 控制工具 - 具備 SFTP 功能的 GUI 工具",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yaoyu0112/cmd-tool",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.0.0",
        "paramiko>=2.7.0",
    ],
    extras_require={
        "dev": [
            "pyinstaller>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "cmd-tool=cmd_tool:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.json", "*.md"],
    },
)