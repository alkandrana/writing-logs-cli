my-cli-app/
├── pyproject.toml      # Build system and dependency management
├── README.md
├── src/
│   └── my_cli/
│       ├── __init__.py
│       ├── main.py     # Entry point, initializes Click/Typer groups [6]
│       ├── config.py   # Configuration loading (env vars, files) [2]
│       ├── commands/   # Subcommands separated by functionality [3]
│       │   ├── __init__.py
│       │   ├── user.py # e.g., 'my-cli user create'
│       │   └── db.py   # e.g., 'my-cli db init'
│       └── utils/      # Shared utilities, helpers
│           ├── __init__.py
│           └── helpers.py
└── tests/
