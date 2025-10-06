from config import Config

def test_config_defaults():
    assert Config.SECRET_KEY == 'your-secret-key-here' or isinstance(Config.SECRET_KEY, str)
    assert Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///') or 'postgresql' in Config.SQLALCHEMY_DATABASE_URI
    assert Config.SQLALCHEMY_TRACK_MODIFICATIONS is False
