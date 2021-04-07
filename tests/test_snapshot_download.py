import os
import tempfile
import unittest

from huggingface_hub.snapshot_download import snapshot_download


SNAPSHOT_MODEL_ID = "lysandre/dummy-hf-hub"

# Commit at the top of main
SNAPSHOT_MODEL_ID_REVISION_MAIN = "4958076ba4a2f5b261e1ba190d343d21b844fc96"
# The `main` branch contains only a README.md file (and .gitattributes)

# Commit at the top of master
SNAPSHOT_MODEL_ID_REVISION_MASTER = "00c48906118a75ac112639c30e190d6a481acc7f"
# The `master` branch contains several files (and .gitattributes):
# | README.md
# | model_files
# | ---- config.json
# | ---- pytorch_model.bin
# | fast_tokenizer
# | ---- special_tokens_map.json
# | ---- tokenizer.json
# | ---- tokenizer_config.json
# | slow_tokenizer
# | ---- special_tokens_map.json
# | ---- vocab.txt
# | ---- tokenizer_config.json


class SnapshotDownloadTests(unittest.TestCase):
    def test_download_model(self):
        with tempfile.TemporaryDirectory() as tmpdirname:
            storage_folder = snapshot_download(
                SNAPSHOT_MODEL_ID, revision="main", cache_dir=tmpdirname
            )

            # folder contains two files and the README.md
            folder_contents = os.listdir(storage_folder)
            self.assertEqual(len(folder_contents), 2)
            self.assertTrue("README.md" in folder_contents)
            self.assertFalse("slow_tokenizer" in folder_contents)

            # folder name contains the revision's commit sha.
            self.assertTrue(SNAPSHOT_MODEL_ID_REVISION_MAIN in storage_folder)

            storage_folder = snapshot_download(
                SNAPSHOT_MODEL_ID, revision="master", cache_dir=tmpdirname
            )

            # folder contains two files and the README.md
            folder_contents = os.listdir(storage_folder)
            self.assertEqual(len(folder_contents), 5)
            self.assertTrue("README.md" in folder_contents)
            self.assertTrue("slow_tokenizer" in folder_contents)

            # folder name contains the revision's commit sha.
            self.assertTrue(SNAPSHOT_MODEL_ID_REVISION_MASTER in storage_folder)
