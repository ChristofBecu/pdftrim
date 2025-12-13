"""Workflow management for PDF processing operations.

This module provides the WorkflowManager class for orchestrating PDF processing
workflows, handling both single file and batch processing with consistent
error handling, progress reporting, and output management.
"""

from __future__ import annotations

import os
import warnings
from typing import Optional, Tuple

from ..di.interfaces import IDisplayManager, IFileManager, IPDFProcessor, IConfig
from ..models.operation_request import OperationRequest, OperationType


class WorkflowManager:
    """
    Manages PDF processing workflows with centralized orchestration.
    
    This class eliminates duplication between single file and batch processing
    by providing consistent workflow orchestration, output directory handling,
    and progress reporting. Focuses purely on workflow coordination without
    CLI-specific concerns.
    """
    
    def __init__(self, 
                 display: IDisplayManager,
                 processor: IPDFProcessor,
                 file_manager: IFileManager,
                 config: IConfig,
                 debug: Optional[bool] = None):
        """
        Initialize the WorkflowManager with injected dependencies.
        
        Args:
            display: DisplayManager instance for output
            processor: PDFProcessor for handling PDF operations
            file_manager: FileManager for file operations
            config: Configuration instance
            debug: Enable debug mode (uses config default if None)
        """
        self.display = display
        self.processor = processor
        self.file_manager = file_manager
        self.config = config
        self.debug = debug if debug is not None else config.debug_mode
    
    def process_single_file(self, input_file: str, search_string: str, output_dir: str = "") -> bool:
        """Process a single PDF file (DEPRECATED).

        Deprecated in favor of :meth:`process_operation`.
        """
        warnings.warn(
            "WorkflowManager.process_single_file() is deprecated; use process_operation() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.process_operation(
            operation="search",
            input_path=input_file,
            output_dir=output_dir or "",
            is_batch_mode=False,
            search_string=search_string,
        )

    def _run_processor(
        self,
        *,
        operation: OperationType,
        input_file: str,
        output_dir: str,
        search_string: str = "",
        delete_spec: str = "",
        before_page: Optional[int] = None,
        after_page: Optional[int] = None,
    ):
        if operation == OperationType.SEARCH:
            return self.processor.process_pdf(input_file, search_string, output_dir)
        if operation == OperationType.DELETE:
            return self.processor.process_pdf_delete_pages(input_file, delete_spec, output_dir)
        if operation == OperationType.BEFORE_AFTER:
            return self.processor.process_pdf_delete_before_after(
                input_file,
                before_page,
                after_page,
                output_dir,
            )
        raise ValueError(f"Unknown operation: {operation}")

    def _display_operation_details(
        self,
        *,
        operation: OperationType,
        search_string: str,
        delete_spec: str,
        before_page: Optional[int],
        after_page: Optional[int],
    ) -> None:
        if operation == OperationType.SEARCH:
            self.display.info(f"Search string: '{search_string}'")
            return
        if operation == OperationType.DELETE:
            self.display.info(f"Delete spec: '{delete_spec}'")
            return
        if operation == OperationType.BEFORE_AFTER:
            if before_page is not None:
                self.display.info(f"Before page: {before_page}")
            if after_page is not None:
                self.display.info(f"After page: {after_page}")
            return
        raise ValueError(f"Unknown operation: {operation}")

    def _process_single_operation(
        self,
        *,
        operation: str,
        input_file: str,
        output_dir: str,
        search_string: str = "",
        delete_spec: str = "",
        before_page: Optional[int] = None,
        after_page: Optional[int] = None,
    ) -> bool:
        resolved_output_dir = self.file_manager.ensure_output_directory(output_dir or self.config.output_dir)

        self.display.info(f"Processing file: {input_file}")
        op = OperationType.from_string(operation)
        self._display_operation_details(
            operation=op,
            search_string=search_string,
            delete_spec=delete_spec,
            before_page=before_page,
            after_page=after_page,
        )

        self.display.info(f"Output directory: {resolved_output_dir}")

        result = self._run_processor(
            operation=op,
            input_file=input_file,
            output_dir=resolved_output_dir,
            search_string=search_string,
            delete_spec=delete_spec,
            before_page=before_page,
            after_page=after_page,
        )

        if result.success:
            self.display.info(f"Result: {result.message}")
            self.display.info(f"Output: {result.output_file}")
            self.display.success("Processing complete: 1 successful, 0 failed")
            return True

        self.display.error(f"Result: {result.message}")
        self.display.error("Processing complete: 0 successful, 1 failed")
        return False
    
    def process_batch(self, search_string: str, output_dir: Optional[str] = None) -> Tuple[int, int]:
        """Process all PDF files in the current directory (DEPRECATED).

        Deprecated in favor of :meth:`process_operation`.
        """
        warnings.warn(
            "WorkflowManager.process_batch() is deprecated; use process_operation() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self._process_batch_operation(
            operation="search",
            output_dir=output_dir,
            search_string=search_string,
        )

    def _process_batch_operation(
        self,
        *,
        operation: str,
        output_dir: Optional[str] = None,
        search_string: str = "",
        delete_spec: str = "",
        before_page: Optional[int] = None,
        after_page: Optional[int] = None,
    ) -> Tuple[int, int]:
        resolved_output_dir = output_dir or self.config.output_dir
        resolved_output_dir = self.file_manager.ensure_output_directory(resolved_output_dir)

        pdf_files = self.file_manager.find_pdf_files()
        if not pdf_files:
            self.display.info("No PDF files found in current directory.")
            return 0, 0

        self.display.info(f"Found {len(pdf_files)} PDF file(s) to process:")
        for pdf_file in pdf_files:
            self.display.info(f"  - {os.path.basename(pdf_file)}")

        self.display.info(f"Processing {len(pdf_files)} PDF files")
        op = OperationType.from_string(operation)
        self._display_operation_details(
            operation=op,
            search_string=search_string,
            delete_spec=delete_spec,
            before_page=before_page,
            after_page=after_page,
        )

        self.display.info(f"Output directory: {resolved_output_dir}")
        self.display.info("-" * 50)

        successful = 0
        failed = 0

        for pdf_file in pdf_files:
            result = self._run_processor(
                operation=op,
                input_file=pdf_file,
                output_dir=resolved_output_dir,
                search_string=search_string,
                delete_spec=delete_spec,
                before_page=before_page,
                after_page=after_page,
            )

            if result.success:
                successful += 1
            else:
                failed += 1
                self.display.error(f"Failed to process {pdf_file}: {result.message}")

        self.display.info("-" * 50)
        message = f"Processing complete: {successful} successful, {failed} failed"
        if failed == 0:
            self.display.success(message)
        elif successful == 0:
            self.display.error(message)
        else:
            self.display.warning(message)

        return successful, failed
    
    def process_workflow(self, input_path: Optional[str], search_string: str, 
                        output_dir: Optional[str] = None, is_batch_mode: bool = False) -> bool:
        """Process workflow based on input parameters (DEPRECATED).

        Deprecated in favor of :meth:`process_operation`.
        """
        warnings.warn(
            "WorkflowManager.process_workflow() is deprecated; use process_operation() instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return self.process_operation(
            operation="search",
            input_path=input_path,
            output_dir=output_dir,
            is_batch_mode=is_batch_mode,
            search_string=search_string,
        )

    def process_operation(
        self,
        *,
        operation: str,
        input_path: Optional[str],
        output_dir: Optional[str] = None,
        is_batch_mode: bool = False,
        search_string: str = "",
        delete_spec: str = "",
        before_page: Optional[int] = None,
        after_page: Optional[int] = None,
    ) -> bool:
        """Process a workflow for any supported operation.

        operation must be one of: 'search', 'delete', 'before_after'.
        """

        request = OperationRequest(
            operation=OperationType.from_string(operation),
            input_path=input_path,
            is_batch_mode=is_batch_mode or input_path is None,
            output_dir=output_dir,
            search_string=search_string,
            delete_spec=delete_spec,
            before_page=before_page,
            after_page=after_page,
        )

        return self.process_request(request)

    def process_request(self, request: OperationRequest) -> bool:
        """Process a workflow using a typed request object."""

        request.validate()

        if request.is_batch_mode or request.input_path is None:
            successful, failed = self._process_batch_operation(
                operation=request.operation.value,
                output_dir=request.output_dir,
                search_string=request.search_string,
                delete_spec=request.delete_spec,
                before_page=request.before_page,
                after_page=request.after_page,
            )
            return failed == 0

        return self._process_single_operation(
            operation=request.operation.value,
            input_file=request.input_path,
            output_dir=request.output_dir or "",
            search_string=request.search_string,
            delete_spec=request.delete_spec,
            before_page=request.before_page,
            after_page=request.after_page,
        )
    
    def get_processor_stats(self) -> dict:
        """
        Get processing statistics from the underlying PDFProcessor.
        
        Returns:
            Dictionary containing processing statistics
        """
        return {
            'files_processed': getattr(self.processor, '_files_processed', 0),
            'pages_removed': getattr(self.processor, '_pages_removed', 0),
            'blank_pages_removed': getattr(self.processor, '_blank_pages_removed', 0)
        }