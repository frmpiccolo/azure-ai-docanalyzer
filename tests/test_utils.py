import pytest
from unittest.mock import patch
from modules.utils import get_env_variable

@patch.dict("os.environ", {"AZURE_STORAGE_ACCOUNT_NAME": "bootcamp102storage"})
def test_get_env_variable_present():
    """
    Test that `get_env_variable` correctly fetches an environment variable when it exists.
    """
    result = get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
    assert result == "bootcamp102storage"


@patch.dict("os.environ", {}, clear=True)
def test_get_env_variable_missing():
    """
    Test that `get_env_variable` raises an error when the variable is missing.
    """
    with pytest.raises(EnvironmentError, match="Environment variable AZURE_STORAGE_ACCOUNT_NAME is missing."):
        get_env_variable("AZURE_STORAGE_ACCOUNT_NAME")
