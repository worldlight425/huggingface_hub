import os
import shutil
import time
import unittest
import uuid

from huggingface_hub import HfApi
from huggingface_hub.file_download import is_torch_available
from huggingface_hub.hub_mixin import PyTorchModelHubMixin
from huggingface_hub.utils import logging

from .testing_constants import ENDPOINT_STAGING, PASS, USER
from .testing_utils import set_write_permission_and_retry


def repo_name(id=uuid.uuid4().hex[:6]):
    return "mixin-repo-{0}-{1}".format(id, int(time.time() * 10e3))


logger = logging.get_logger(__name__)
WORKING_REPO_SUBDIR = "fixtures/working_repo_2"
WORKING_REPO_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), WORKING_REPO_SUBDIR
)

if is_torch_available():
    import torch.nn as nn


def require_torch(test_case):
    """
    Decorator marking a test that requires PyTorch.

    These tests are skipped when PyTorch isn't installed.

    """
    if not is_torch_available():
        return unittest.skip("test requires PyTorch")(test_case)
    else:
        return test_case


if is_torch_available():

    class DummyModel(nn.Module, PyTorchModelHubMixin):
        def __init__(self, **kwargs):
            super().__init__()
            self.config = kwargs.pop("config", None)
            self.l1 = nn.Linear(2, 2)

        def forward(self, x):
            return self.l1(x)

else:
    DummyModel = None


@require_torch
class HubMixingCommonTest(unittest.TestCase):
    _api = HfApi(endpoint=ENDPOINT_STAGING)


@require_torch
class HubMixingTest(HubMixingCommonTest):
    def tearDown(self) -> None:
        if os.path.exists(WORKING_REPO_DIR):
            shutil.rmtree(WORKING_REPO_DIR, onerror=set_write_permission_and_retry)
        logger.info(
            f"Does {WORKING_REPO_DIR} exist: {os.path.exists(WORKING_REPO_DIR)}"
        )

    @classmethod
    def setUpClass(cls):
        """
        Share this valid token in all tests below.
        """
        cls._token = cls._api.login(username=USER, password=PASS)

    def test_save_pretrained(self):
        REPO_NAME = repo_name("save")
        model = DummyModel()

        model.save_pretrained(f"{WORKING_REPO_DIR}/{REPO_NAME}")
        files = os.listdir(f"{WORKING_REPO_DIR}/{REPO_NAME}")
        self.assertTrue("pytorch_model.bin" in files)
        self.assertEqual(len(files), 1)

        model.save_pretrained(
            f"{WORKING_REPO_DIR}/{REPO_NAME}", config={"num": 12, "act": "gelu"}
        )
        files = os.listdir(f"{WORKING_REPO_DIR}/{REPO_NAME}")
        self.assertTrue("config.json" in files)
        self.assertTrue("pytorch_model.bin" in files)
        self.assertEqual(len(files), 2)

    def test_rel_path_from_pretrained(self):
        model = DummyModel()
        model.save_pretrained(
            f"tests/{WORKING_REPO_SUBDIR}/FROM_PRETRAINED",
            config={"num": 10, "act": "gelu_fast"},
        )

        model = DummyModel.from_pretrained(
            f"tests/{WORKING_REPO_SUBDIR}/FROM_PRETRAINED"
        )
        self.assertTrue(model.config == {"num": 10, "act": "gelu_fast"})

    def test_abs_path_from_pretrained(self):
        REPO_NAME = repo_name("FROM_PRETRAINED")
        model = DummyModel()
        model.save_pretrained(
            f"{WORKING_REPO_DIR}/{REPO_NAME}",
            config={"num": 10, "act": "gelu_fast"},
        )

        model = DummyModel.from_pretrained(f"{WORKING_REPO_DIR}/{REPO_NAME}")
        self.assertDictEqual(model.config, {"num": 10, "act": "gelu_fast"})

    def test_push_to_hub(self):
        REPO_NAME = repo_name("PUSH_TO_HUB")
        model = DummyModel()
        model.push_to_hub(
            repo_path_or_name=f"{WORKING_REPO_DIR}/{REPO_NAME}",
            api_endpoint=ENDPOINT_STAGING,
            use_auth_token=self._token,
            git_user="ci",
            git_email="ci@dummy.com",
            config={"num": 7, "act": "gelu_fast"},
        )

        model_info = self._api.model_info(
            f"{USER}/{REPO_NAME}",
        )
        self.assertEqual(model_info.modelId, f"{USER}/{REPO_NAME}")

        self._api.delete_repo(repo_id=f"{REPO_NAME}", token=self._token)
