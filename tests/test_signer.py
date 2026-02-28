import hashlib

from utils.signer import generate_sign, get_timestamp


class TestGenerateSign:
    def test_returns_md5_hex(self):
        result = generate_sign("/test", "1700000000000", "device123", "user456")
        expected = hashlib.md5("/test1700000000000device123user456".encode()).hexdigest()
        assert result == expected

    def test_without_user_id(self):
        result = generate_sign("/test", "1700000000000", "device123")
        expected = hashlib.md5("/test1700000000000device123".encode()).hexdigest()
        assert result == expected

    def test_empty_user_id(self):
        result = generate_sign("/test", "1700000000000", "device123", "")
        result_no_arg = generate_sign("/test", "1700000000000", "device123")
        assert result == result_no_arg

    def test_different_inputs_different_signs(self):
        sign_a = generate_sign("/a", "1000", "d1", "u1")
        sign_b = generate_sign("/b", "2000", "d2", "u2")
        assert sign_a != sign_b

    def test_output_is_32_char_hex(self):
        result = generate_sign("/path", "1234567890123", "dev", "usr")
        assert len(result) == 32
        assert all(c in "0123456789abcdef" for c in result)


class TestGetTimestamp:
    def test_returns_13_digit_string(self):
        ts = get_timestamp()
        assert isinstance(ts, str)
        assert len(ts) == 13
        assert ts.isdigit()

    def test_returns_increasing_values(self):
        ts1 = get_timestamp()
        ts2 = get_timestamp()
        assert int(ts2) >= int(ts1)
