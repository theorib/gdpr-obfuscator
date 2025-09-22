import pytest

from gdpr_obfuscator import gdpr_obfuscator


@pytest.mark.describe("class description")
class TestClassName:
    # @pytest.mark.skip
    @pytest.mark.it("test description")
    def test_test_description(self):
        with pytest.raises(NotImplementedError):
            gdpr_obfuscator("tests/test_data.csv", ["name", "email"])
