"""nubivis setup"""
from setuptools import setup, find_packages

version = "0.0.1"
extra_compile_args = ["-O3", "-w"]
# extensions = [
#     Extension(
#         name="nubivis.parser",
#         sources=["source/parser.cpp"],
#         include_dirs=["source"],
#         extra_compile_args=extra_compile_args,
#         language="c++",
#     )
# ]
kwargs = {
    "name": "nubivis",
    "description": "Compute everywhere with units",
    "author": "Lee Johnston",
    "author_email": "lee.johnston.100@gmail.com",
    "version": version,
    "package_dir": {"": "source"},
    "packages": find_packages(),
    "install_requires": ["numpy"]
    # "ext_modules": extensions,
}
if __name__ == "__main__":
    setup(**kwargs)
