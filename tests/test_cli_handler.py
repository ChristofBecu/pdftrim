from src.ui.cli_handler import CLIHandler


def test_cli_search_batch_mode() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--search", "hello"])  # no -f => batch
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "search"
    assert result.parsed_args.is_batch_mode is True


def test_cli_search_with_file_single_mode() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--file", "in.pdf", "--search", "hello"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.is_batch_mode is False
    assert result.parsed_args.input_path == "in.pdf"


def test_cli_rejects_conflicting_operations() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--search", "hello", "--delete", "1"])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_requires_one_operation() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result([])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_allows_before_after_combination() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--before", "3", "--after", "5"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "before_after"


def test_cli_delete_empty_spec_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", ""])  # explicit empty
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_search_empty_string_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--search", ""])  # explicit empty
    assert result.should_exit is True
    assert result.exit_code == 1
