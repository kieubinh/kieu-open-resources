from setuptools import find_packages, setup

setup(
    name="kieu-open-resources",
    version="0.2.0",
    description="Kieu Open Resources: registry, discovery CLI and SDK for coding agents (plus the legacy kieu-resource service)",
    python_requires=">=3.9",
    package_dir={"": "src"},
    packages=find_packages("src"),
    package_data={
        "kieu_resource": ["catalogue.html", "skills/*/SKILL.md"],
        "kieu_open_resources": ["skills/kieu-resource-discovery/SKILL.md", "skills/kieu-resource-discovery/references/*.md"],
    },
    include_package_data=True,
    entry_points={"console_scripts": [
        "kieu-open-resources=kieu_open_resources.cli:main",
        # legacy v1 remote-first service, kept working until it is rebuilt on the core SDK (P1)
        "kieu-resource=kieu_resource.cli:main",
        "kieu-resource-api=kieu_resource.http:main",
        "kieu-resource-mcp=kieu_resource.mcp:main",
    ]},
)
