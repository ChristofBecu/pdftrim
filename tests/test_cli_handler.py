from src.ui.cli_handler import CLIHandler


def test_cli_search_batch_mode() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", "--search", "hello"])  # no -f => batch
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "search"
    assert result.parsed_args.is_batch_mode is True


def test_cli_search_with_file_single_mode() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--file", "in.pdf", "--delete", "--search", "hello"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.is_batch_mode is False
    assert result.parsed_args.input_path == "in.pdf"


def test_cli_rejects_conflicting_operations() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", "1", "--search", "hello"])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_requires_one_operation() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result([])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_allows_before_after_combination() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", "--before", "3", "--after", "5"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "before_after"


def test_cli_delete_empty_spec_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", ""])  # explicit empty
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_keep_sets_invert_selection() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--keep", "1-2"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "delete"
    assert result.parsed_args.invert_selection is True
    assert result.parsed_args.delete_spec == "1-2"


def test_cli_keep_short_flag_sets_invert_selection() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["-k", "3"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.invert_selection is True
    assert result.parsed_args.delete_spec == "3"


def test_cli_keep_empty_spec_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--keep", ""])  # explicit empty
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_rejects_keep_with_delete() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--keep", "--delete"])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_keep_modifier_allows_before_after_inversion() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--keep", "--before", "10"])
    assert result.should_exit is False
    assert result.parsed_args is not None
    assert result.parsed_args.operation == "before_after"
    assert result.parsed_args.invert_selection is True
    assert result.parsed_args.before_page == 10


def test_cli_search_empty_string_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--delete", "--search", ""])  # explicit empty
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_before_without_mode_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--before", "3"])
    assert result.should_exit is True
    assert result.exit_code == 1


def test_cli_search_without_mode_is_error() -> None:
    handler = CLIHandler(debug=False)
    result = handler.handle_arguments_with_result(["--search", "hello"])
    assert result.should_exit is True
    assert result.exit_code == 1
