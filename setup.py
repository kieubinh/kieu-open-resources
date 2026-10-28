from setuptools import find_packages, setup

setup(
    name="kieu-resource",
    version="0.1.0",
    description="Shared Kieu Resources discovery CLI, API and MCP server",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={"kieu_resource": ["catalogue.html", "skills/*/SKILL.md"]},
    include_package_data=True,
    entry_points={"console_scripts": [
        "kieu-resource=kieu_resource.cli:main",
        "kieu-resource-api=kieu_resource.http:main",
        "kieu-resource-mcp=kieu_resource.mcp:main",
    ]},
)
