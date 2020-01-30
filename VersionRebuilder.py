import os
from pathlib import Path

from loguru import logger


class VersionRebuilder:
    def __init__(self):
        self.rebuildFile = Path('./.rebuild')
        self.versionsToRebuild = []

    def readFile(self):
        if not self.rebuildFile.exists():
            return

        with self.rebuildFile.open('r') as fileHandle:
            readLine = fileHandle.readline().strip()

            if readLine is not '':
                self.versionsToRebuild.append(readLine)

    def checkIfVersionNeedsRebuild(self, version: str) -> bool:
        return version in self.versionsToRebuild

    def finalize(self):
        if len(self.versionsToRebuild) == 0:
            return

        githubToken = os.getenv('GH_TOKEN', None)
        githubRepository = os.getenv('GH_REPOSITORY', 'YannickFricke/Docker-Shopware')

        if githubToken is None or githubToken.strip() is '':
            logger.error('No Github token found. Cannot reset the rebuild file')
            return

        if githubRepository is None or githubRepository.strip() is '':
            logger.error('No Github repository found. Cannot reset the rebuild file')
            return

        # Remove the .rebuild file
        self.rebuildFile.unlink()
        os.system(f'git rm --cached "{str(self.rebuildFile)}"')

        # Configure git to use a custom name
        os.system('git config --global user.name "Travis CI"')
        os.system('git config --global user.email "travis@travis-ci.org"')

        # Commit the changes
        os.system('git commit -m "Processed rebuild file [skip ci]"')

        # Add a new remote with the custom Github token
        os.system(
            f'git remote add travis-push https://{githubToken}@github.com/{githubRepository}.git > /dev/null 2>&1',
        )

        # Push the commit
        os.system('git push --quiet --set-upstream travis-push master')
