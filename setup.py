import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="mtm",
    version="0.0.1",
    author="xy",
    description="MultiMedia Transport Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    include_package_data=True,
    zip_safe=True,
    url="https://github.com/firefirer1983/mtm.git",
    packages=setuptools.find_packages(exclude=["docs", "tests"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["requests", "pika", "sqlalchemy", "pymysql"],
    entry_points={
        "console_scripts": ["init_db = mtm.model.models:create_all_tables"]
    },
)
