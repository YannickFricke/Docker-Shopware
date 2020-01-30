import hashlib
import shutil
from pathlib import Path

from loguru import logger
from requests import get


class ReleaseDownloader:
    def __init__(self):
        self.maxAttemps = 3

    def downloadRelease(
            self,
            downloadDirectory: Path,
            version: str,
            downloadURL: str,
            sha1Hash: str,
    ):
        if not downloadDirectory.exists():
            logger.info("Created download directory")
            downloadDirectory.mkdir(parents=True)

        localPath = downloadDirectory.joinpath(
            f'{version}.zip',
        )

        if localPath.exists() and self.sha1HashFile(localPath) == sha1Hash:
            logger.info(f"Installation archive for version {version} was already downloaded and the checksums matched")

            return True

        logger.debug(f"Downloading {downloadURL} to {str(localPath.absolute())}")
        attemps = 0

        while attemps < self.maxAttemps:
            response = get(downloadURL, stream=True)

            if response.status_code is not 200:
                logger.error(
                    f"Could not download version {version}. Expected status code 200 but got {response.status_code} instead"
                )
                continue

            with localPath.open('wb') as fileHandle:
                response.raw.decode = True
                shutil.copyfileobj(response.raw, fileHandle)

            fileHash = self.sha1HashFile(localPath)
            if fileHash == sha1Hash:
                break

            attemps = attemps + 1

            if attemps == self.maxAttemps:
                logger.error(f"Could not download installation archive for version {version}: Checksum mismatch")

                return False

            else:
                logger.warning(
                    f"Trying to redownload the installation archive for version {version}: Checksum mismatch"
                )
                logger.warning(f"Expected checksum {sha1Hash} got checksum {fileHash}")

        fileHash = self.sha1HashFile(localPath)

        if attemps >= self.maxAttemps and fileHash != sha1Hash:
            return False

        logger.debug("Download finished")

        return True

    def sha1HashFile(self, filename: Path):
        """
        Hashes the file and returns the SHA1 hash for it
        :param filename: The file to hash
        :return: The computed SHA1 hash
        """
        bufferSize = 65536
        sha1Hash = hashlib.sha1()

        with filename.open('rb') as f:
            while True:
                data = f.read(bufferSize)

                if not data:
                    break

                sha1Hash.update(data)

        return str(sha1Hash.hexdigest())
