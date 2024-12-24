import os
import shutil
import subprocess
import tempfile

from loguru import logger

from llm_engineering.domain.documents import RepositoryDocument

from .base import BaseCrawler


class GithubCrawler(BaseCrawler):
    model = RepositoryDocument

    def __init__(self, ignore=(".git", ".toml", ".lock", ".png")) -> None:
        super().__init__()

        # Sets up a list of patterns to ignore standard files and 
        # directories found in GitHub repos
        self._ignore = ignore

    def extract(self, link: str, **kwargs) -> None:
        old_model = self.model.find(link=link)
        # checks if the repository has already been processed 
        # and stored in the database.
        if old_model is not None:
            logger.info(f"Repository already exists in the database: {link}")

            return

        logger.info(f"Starting scrapping GitHub repository: {link}")

        # extracts the repository name from the link
        repo_name = link.rstrip("/").split("/")[-1]
        
        # creates a temporary directory to clone the repository to ensure
        # that the cloned repository is cleaned up from the local disk 
        # after it’s processed.
        local_temp = tempfile.mkdtemp()

        try:

            # changes the current working directory to the temporary directory 
            # and executes the git clone command in a different process
            os.chdir(local_temp)
            subprocess.run(["git", "clone", link])

            # constructs the path to the cloned repository.
            repo_path = os.path.join(local_temp, os.listdir(local_temp)[0])  # noqa: PTH118

            # initializes an empty dictionary used to aggregate the content of 
            # the files in a standardized way.
            tree = {}

            # For each relevant file, it reads the content, removes any spaces,
            # and stores it in the dictionary with the file path as the key.
            for root, _, files in os.walk(repo_path):
                dir = root.replace(repo_path, "").lstrip("/")
                if dir.startswith(self._ignore):
                    continue

                for file in files:
                    if file.endswith(self._ignore):
                        continue
                    file_path = os.path.join(dir, file)  # noqa: PTH118
                    with open(os.path.join(root, file), "r", errors="ignore") as f:  # noqa: PTH123, PTH118
                        tree[file_path] = f.read().replace(" ", "")


            # creates a new instance of the RepositoryDocument model, populating 
            # it with the repository information.
            user = kwargs["user"]
            instance = self.model(
                content=tree,
                name=repo_name,
                link=link,
                platform="github",
                author_id=user.id,
                author_full_name=user.full_name,
            )
            instance.save()

        except Exception:
            raise
        finally:
           # temporary directory is removed to clean up any resources
           # used during the process
            shutil.rmtree(local_temp)

        logger.info(f"Finished scrapping GitHub repository: {link}")
