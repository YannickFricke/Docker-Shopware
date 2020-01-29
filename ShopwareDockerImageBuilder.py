import json
import os
import shutil
from pathlib import Path

from requests import get


class ShopwareDockerImageBuilder:
    def __init__(self):
        self.data = []
        self.updateURL = 'https://update-api.shopware.com/v1/releases/install'
        self.extractedFolder = Path('./extracted/')
        self.downloadFolder = Path('./downloads/')
        self.defaultDirectoryPermissions = 0o744

    def run(self):
        if not self.updateData():
            return

        if not self.extractedFolder.exists():
            self.extractedFolder.mkdir()

        if not self.downloadFolder.exists():
            self.downloadFolder.mkdir()

        self.processData()

    def updateData(self):
        response = get(self.updateURL)

        if response.status_code is not 200:
            return False

        self.data = json.loads(response.content)

        return True

    def processData(self):
        for entry in self.data:
            version = entry['version']
            uri = entry['uri']

            print(f"Processing version: {version}")

            try:
                fileName = self.download(uri, version)
            except Exception as e:
                print(f"Could not download version {version}: {e}")
                continue

            print("Unpacking archive")
            self.unpack(fileName)
            print("Unpacked archive")

            print("Copying dockerfile")
            self.copyDockerFile(version)
            print("Copied dockerfile")

            print("Copying php settings file")
            self.copyPHPSettingsFile(version)
            print("Copied php settings file")

            print("Building Docker image")
            self.buildDockerImage(
                version,
            )
            print("Built Docker image")

            print("Pushing Docker image")
            self.pushDockerImage(version)
            print("Pushed Docker image")

    def download(self, url, version):
        if not self.downloadFolder.exists():
            self.downloadFolder.mkdir(
                self.defaultDirectoryPermissions
            )

        downloadedFile = self.downloadFolder.joinpath(f'{version}.zip')

        if downloadedFile.exists():
            return str(downloadedFile)

        response = get(url)

        if response.status_code is not 200:
            raise Exception("Download not ok")

        # if not self.extractedFolder.exists():
        #     self.extractedFolder.mkdir(self.defaultDirectoryPermissions)

        downloadedFile.write_bytes(response.content)

        return str(downloadedFile)

    def unpack(self, fileName):
        shopwareFolder = self.extractedFolder.joinpath(
            'shopware'
        )

        if shopwareFolder.exists():
            print("Removing existing shopware directory")
            shutil.rmtree(shopwareFolder)
            print("Removed existing shopware directory")

        shopwareFolder.mkdir(self.defaultDirectoryPermissions)

        os.system(
            f"unzip {fileName} -d {str(shopwareFolder)} > /dev/null 2>&1"
        )

    def copyDockerFile(self, version):
        dockerFile = Path(
            f"./assets/docker/{version}.Dockerfile"
        )

        if not dockerFile.exists():
            dockerFile = Path(
                f"./assets/docker/all.Dockerfile"
            )

        print(f"Using the following Dockerfile: {str(dockerFile)}")

        shutil.copyfile(
            dockerFile,
            './extracted/Dockerfile'
        )

    def copyPHPSettingsFile(self, version):
        phpSettingsFile = Path(
            f"./assets/php/{version}.ini"
        )

        if not phpSettingsFile.exists():
            phpSettingsFile = Path(
                f"./assets/php/all.ini"
            )

        print(f"Using the following php settings file: {str(phpSettingsFile)}")

        shutil.copyfile(
            phpSettingsFile,
            './extracted/php.ini'
        )

    def buildDockerImage(
        self,
        version: str
    ):
        os.system(
            f"docker build -t yfricke/shopware:{version} --file ./extracted/Dockerfile ./extracted/ > /dev/null 2>&1"
        )

    def pushDockerImage(
        self,
        version: str
    ):
        os.system(
            f"docker push yfricke/shopware:{version}"
        )
