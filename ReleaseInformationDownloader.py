from json import loads, JSONDecodeError
from os import getenv

from loguru import logger
from requests import get


class ReleaseInformationDownloader:
    def __init__(self):
        self.updateURL = getenv(
            'SHOPWARE_RELEASES_URL',
            'https://update-api.shopware.com/v1/releases/install',
        )
        self.latestVersion = None

    def fetchLatestInformations(self):
        """
        Downloads the latest informations, parses the JSON and extracts if possible the latest Shopware version
        :return: The parsed JSON contents
        """
        logger.debug("Fetching release informations")
        response = get(self.updateURL)
        logger.info("Fetched release informations")

        if response.status_code is not 200:
            raise Exception("Could not download the release informations")

        try:
            logger.debug('Trying to parse the release informations')
            content = loads(response.content, encoding='UTF-8')
            logger.info('Parsed the release informations')
        except JSONDecodeError as e:
            raise Exception(f"Could not parse JSON: {e}")
        except Exception as e:
            raise Exception(f"Unknown error while trying to parse JSON: {e}")

        if len(content) > 0:
            latestVersion = content[0]['version']
            logger.info(f'Found latest version: {latestVersion}')
            self.latestVersion = latestVersion

        return content
