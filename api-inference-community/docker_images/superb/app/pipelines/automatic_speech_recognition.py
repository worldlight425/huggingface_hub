import os
import subprocess
import sys
from typing import Dict

import numpy as np
from app.pipelines import Pipeline
from huggingface_hub import snapshot_download


class AutomaticSpeechRecognitionPipeline(Pipeline):
    def __init__(self, model_id: str):
        # IMPLEMENT_THIS
        # Preload all the elements you are going to need at inference.
        # For instance your model, processors, tokenizer that might be needed.
        # This function is only called once, so do all the heavy processing I/O here
        # IMPLEMENT_THIS : Please define a `self.sampling_rate` for this pipeline
        # to automatically read the input correctly
        filepath = snapshot_download(model_id)
        sys.path.append(filepath)
        if "requirements.txt" in os.listdir(filepath):
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "pip",
                    "install",
                    "-r",
                    os.path.join(filepath, "requirements.txt"),
                ]
            )

        from model import PreTrainedModel

        self.model = PreTrainedModel(filepath)
        self.sampling_rate = 16000

    def __call__(self, inputs: np.array) -> Dict[str, str]:
        """
        Args:
            inputs (:obj:`np.array`):
                The raw waveform of audio received. By default at 16KHz.
                Check `app.validation` if a different sample rate is required
                or if it depends on the model
        Return:
            A :obj:`dict`:. The object return should be liked {"text": "XXX"} containing
            the detected langage from the input audio
        """
        return self.model(inputs)
