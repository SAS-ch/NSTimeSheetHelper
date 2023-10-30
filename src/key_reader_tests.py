import unittest
import key_reader


class KeyReaderTests(unittest.TestCase):
    def test_read(self):
        assert (len(key_reader.read_key()) > 0)


if __name__ == '__main__':
    unittest.main()
