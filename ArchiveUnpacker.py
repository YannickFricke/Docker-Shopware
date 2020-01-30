import os
import shutil
from pathlib import Path

from loguru import logger


class ArchiveUnpacker:
    def unpackArchive(
            self,
            archivePath: Path,
            buildDirectory: Path,
    ) -> bool:
        if not archivePath.exists():
            logger.error(f"The given archive {str(archivePath.absolute())} does not exists")
            return False

        shopwareDirectory = buildDirectory.joinpath(
            "shopware",
        )

        if shopwareDirectory.exists():
            shutil.rmtree(shopwareDirectory)

        shopwareDirectory.mkdir(parents=True)

        exitCode = os.system(f'unzip {str(archivePath)} -d {str(shopwareDirectory)} > /dev/null 2>&1')

        return exitCode is 0
