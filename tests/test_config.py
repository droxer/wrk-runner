from wrk_runner.core.config import Config, TestConfig


class TestTestConfig:
    """Tests for TestConfig."""

    def test_test_config_basic(self):
        """Test basic test configuration."""
        config = TestConfig(name="test_api", url="http://localhost:8000/api")
        assert config.name == "test_api"
        assert config.url == "http://localhost:8000/api"

    def test_test_config_with_overrides(self):
        """Test test config with parameter overrides."""
        config = TestConfig(
            name="test_api",
            url="http://localhost:8000/api",
            duration=60,
            connections=5000,
        )
        assert config.duration == 60
        assert config.connections == 5000


class TestMainConfig:
    """Tests for main Config."""

    def test_config_basic(self):
        """Test basic configuration."""
        config = Config(
            tests=[
                TestConfig(name="test1", url="http://localhost:8000"),
                TestConfig(name="test2", url="http://localhost:8001"),
            ]
        )
        assert len(config.tests) == 2
        assert config.duration == 30  # default
        assert config.connections == 1000  # default

    def test_config_custom_values(self):
        """Test configuration with custom values."""
        config = Config(
            duration=60,
            connections=2000,
            threads=16,
            warmup=10,
            output_dir="test_results",
            tests=[TestConfig(name="test", url="http://localhost:8000")],
        )
        assert config.duration == 60
        assert config.connections == 2000
        assert config.threads == 16
        assert config.warmup == 10
        assert config.output_dir == "test_results"

    def test_get_test_config(self):
        """Test getting effective configuration for a test."""
        base_config = Config(
            duration=30,
            connections=1000,
            tests=[
                TestConfig(
                    name="test",
                    url="http://localhost:8000",
                    duration=60,  # override
                    connections=2000,  # override
                )
            ],
        )

        test_config = base_config.tests[0]
        effective_config = base_config.get_test_config(test_config)

        assert effective_config["duration"] == 60
        assert effective_config["connections"] == 2000
        assert effective_config["threads"] == 8  # from base config
