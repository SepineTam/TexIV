import sys
import types
import shutil
from pathlib import Path
import importlib.util
import pytest
import importlib.metadata

# Ensure package root is importable
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# Load numpy stub and insert into sys.modules before project imports
spec = importlib.util.spec_from_file_location("numpy", Path(__file__).parent / "numpy_stub.py")
numpy_stub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(numpy_stub)
sys.modules.setdefault("numpy", numpy_stub)

# Stub tomlkit using local implementation
spec_tomlkit = importlib.util.spec_from_file_location("tomlkit", Path(__file__).parent / "tomlkit_stub.py")
tomlkit_stub = importlib.util.module_from_spec(spec_tomlkit)
spec_tomlkit.loader.exec_module(tomlkit_stub)
sys.modules.setdefault("tomlkit", tomlkit_stub)

# Provide a dummy version function for importlib.metadata
importlib.metadata.version = lambda name: "0.0"

@pytest.fixture(scope="session", autouse=True)
def prepare_env(tmp_path_factory):
    # Stub jieba
    jieba_stub = types.SimpleNamespace(lcut=lambda text: text.split())
    sys.modules.setdefault("jieba", jieba_stub)
    # Stub ollama
    class OllamaResp:
        def __init__(self, embeddings):
            self.embeddings = embeddings
    def embed(model=None, input=None):
        return OllamaResp([[float(i)] * 3 for i, _ in enumerate(input)])
    sys.modules.setdefault("ollama", types.SimpleNamespace(embed=embed))
    # Stub openai
    class FakeClient:
        def __init__(self, api_key=None, base_url=None):
            pass
        class EmbeddingsEndpoint:
            def create(self, model=None, input=None):
                return types.SimpleNamespace(
                    data=[types.SimpleNamespace(embedding=[float(i)] * 3) for i, _ in enumerate(input)]
                )
        @property
        def embeddings(self):
            return self.EmbeddingsEndpoint()
    sys.modules.setdefault("openai", types.SimpleNamespace(OpenAI=FakeClient))
    # Ensure config file exists
    config_dir = Path.home() / ".texiv"
    config_dir.mkdir(exist_ok=True)
    dst = config_dir / "config.toml"
    example = Path(__file__).resolve().parents[1] / "texiv" / "config" / "example.config.toml"
    shutil.copy(example, dst)
    yield

