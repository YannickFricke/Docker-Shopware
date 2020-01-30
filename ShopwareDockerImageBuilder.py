from pathlib import Path

from loguru import logger
from requests import get

from ArchiveUnpacker import ArchiveUnpacker
from DockerImageBuilder import DockerImageBuilder
from ReleaseDownloader import ReleaseDownloader
from ReleaseInformationDownloader import ReleaseInformationDownloader


class ShopwareDockerImageBuilder:
    def __init__(self):
        self.data = []
        self.buildDirectory = Path('./build/')
        self.downloadDirectory = Path('./downloads/')
        self.assetsDirectory = Path('./assets/')

        self.releaseInformationDownloader = ReleaseInformationDownloader()
        self.releaseDownloader = ReleaseDownloader()
        self.archiveUnpacker = ArchiveUnpacker()
        self.dockerImageBuilder = DockerImageBuilder()

    @logger.catch
    def run(self):
        self.data = self.releaseInformationDownloader.fetchLatestInformations()

        for entry in self.data:
            version = entry['version']
            downloadURL = entry['uri']
            sha1Hash = entry['sha1']

            logger.info(f'Processing version {version}')

            if self.checkIfDockerTagExists(version):
                logger.info(f'Version {version} is already pushed to the Docker registry')
                continue

            if not self.releaseDownloader.downloadRelease(
                    self.downloadDirectory,
                    version,
                    downloadURL,
                    sha1Hash,
            ):
                continue

            downloadedArchive = self.downloadDirectory.joinpath(
                f'{version}.zip',
            )

            logger.debug(f'Unpacking archive {str(downloadedArchive.absolute())}')

            if not self.archiveUnpacker.unpackArchive(
                    downloadedArchive,
                    self.buildDirectory,
            ):
                logger.error(f"Could not unpack archive {str(downloadedArchive.absolute())}")
                continue

            logger.info(f'Unpacked archive {str(downloadedArchive.absolute())}')

            try:
                self.dockerImageBuilder.buildImage(
                    version,
                    self.assetsDirectory,
                    self.buildDirectory,
                )
            except Exception as e:
                logger.error(e)
                continue

            self.dockerImageBuilder.pushDockerImage(
                version,
            )

            if version == self.releaseInformationDownloader.latestVersion:
                logger.info('Pushing latest tag')
                self.dockerImageBuilder.buildDockerImage(
                    'latest',
                    self.buildDirectory,
                )
                self.dockerImageBuilder.pushDockerImage('latest')

    def checkIfDockerTagExists(self, version):
        response = get(
            f"https://index.docker.io/v1/repositories/yfricke/shopware/tags/{version}")

        return response.status_code is 200
