import pkg_resources
import os

# FORMAT: 1.x.x
pypi_config = {
    "version_target": "1.0.0",
    "package_name": "cloudevents",
}


def createTag():
    from git import Repo

    # Get local pypi cloudevents version
    published_pypi_version = pkg_resources.get_distribution(
        pypi_config["package_name"]
    ).version

    # Ensure pypi and local package versions match
    if pypi_config["version_target"] == published_pypi_version:
        # Create local git tag
        repo = Repo(os.getcwd())
        repo.create_tag(pypi_config["version_target"])

        # Push git tag to remote master
        origin = repo.remote()
        origin.push(pypi_config["version_target"])

    else:
        # PyPI publish likely failed
        print(
            f"Expected {pypi_config['package_name']}=={pypi_config['version_target']} "
            f"but found {pypi_config['package_name']}=={published_pypi_version}"
        )
        exit(1)


if __name__ == "__main__":
    createTag()
