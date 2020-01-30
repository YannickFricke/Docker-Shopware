import os
import shutil
from pathlib import Path

from loguru import logger


class DockerImageBuilder:
    def __init__(self):
        self.dockerUsername = os.getenv('DOCKER_USERNAME', 'yfricke')
        self.dockerRepository = os.getenv('DOCKER_REPOSITORY', 'shopware')

    def buildImage(
            self,
            version: str,
            assetsDirectory: Path,
            buildDirectory: Path
    ):
        """
        Builds the docker image
        Also copies the required files to the correct directory

        :param version: The Shopware version to build
        :param assetsDirectory:
        :param buildDirectory:
        :return:
        """

        self.copyDockerFile(version, assetsDirectory, buildDirectory)
        self.copyPHPConfigurationFile(version, assetsDirectory, buildDirectory)
        self.buildDockerImage(version, buildDirectory)

    def copyDockerFile(
            self,
            version: str,
            assetsDirectory: Path,
            buildDirectory: Path,
    ):
        """
        Copies the Dockerfile to the "extracted" directory

        :param version: The Shopware version
        :param assetsDirectory: The Path instance to the "assets" directory
        :param buildDirectory: The Path instance to the "extracted" directory
        """

        # Check if the version specific Dockerfile exists
        foundDockerfile = assetsDirectory.joinpath(
            'docker',
            f'{version}.Dockerfile',
        )

        if not foundDockerfile.exists():
            # The version specific Dockerfile does not exists
            # So we use the general Dockerfile
            foundDockerfile = assetsDirectory.joinpath(
                'docker',
                'all.Dockerfile',
            )

        if not foundDockerfile.exists():
            raise Exception('Could not find the general Dockerfile')

        shutil.copy(
            foundDockerfile,
            buildDirectory.joinpath('Dockerfile'),
        )

    def copyPHPConfigurationFile(
            self,
            version: str,
            assetsDirectory: Path,
            buildDirectory: Path,
    ) -> None:
        """
        Copies the php configuration file to the "extracted" directory

        :param version: The Shopware version
        :param assetsDirectory: The Path instance to the "assets" directory
        :param buildDirectory: The Path instance to the "extracted" directory
        """
        # Check if the version specific php configuration file exists
        foundPHPConfigurationFile = assetsDirectory.joinpath(
            'php',
            f'{version}.ini',
        )

        if not foundPHPConfigurationFile.exists():
            # The version specific Dockerfile does not exists
            # So we use the general Dockerfile
            foundPHPConfigurationFile = assetsDirectory.joinpath(
                'php',
                'all.ini',
            )

        if not foundPHPConfigurationFile.exists():
            raise Exception('Could not find the general php configuration file')

        shutil.copy(
            foundPHPConfigurationFile,
            buildDirectory.joinpath('php.ini'),
        )

    def buildDockerImage(
            self,
            version: str,
            buildDirectory: Path,
    ) -> None:
        """
        Builds the docker image
        :param version: The Shopware version of the image
        :param buildDirectory: The build directory
        """
        logger.debug(f'Building Docker image for version {version}')
        os.system(
            f'docker build -t {self.dockerUsername}/{self.dockerRepository}:{version} --file {str(buildDirectory.joinpath("Dockerfile"))} {str(buildDirectory)} > /dev/null 2>&1',
        )
        logger.info(f'Build Docker image for version {version}')

    def pushDockerImage(self, version: str) -> None:
        """
        Pushes the Docker image to the Docker registry
        :param version: The version to push
        """

        logger.debug(f'Pushing version {version} to the Docker registry')

        os.system(
            f"docker push {self.dockerUsername}/{self.dockerRepository}:{version} > /dev/null 2>&1",
        )

        logger.debug(f'Pushed version {version} to the Docker registry')
