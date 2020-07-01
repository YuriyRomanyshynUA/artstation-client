import setuptools


setuptools.setup(
    name="artstation-client-pkg-yuriy-romanyshyn",
    version="0.0.1",
    author="Yuriy Romanyshyn",
    author_email="yuriy.romanyshyn.lv.ua@gmail.com",
    description="artstation-client",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    install_requires=["fake_useragent", "aiohttp"],
    python_requires='>=3.6'
)
