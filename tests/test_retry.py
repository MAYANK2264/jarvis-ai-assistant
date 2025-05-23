"""Tests for retry and transaction functionality."""

import unittest
from unittest.mock import Mock, patch
import time
from utils.retry import retry, transactional, Transaction

class TestRetry(unittest.TestCase):
    def test_successful_execution(self):
        """Test successful function execution without retries."""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)
        
        result = decorated()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 1)

    def test_retry_on_exception(self):
        """Test retry behavior on exceptions."""
        mock_func = Mock(side_effect=[ValueError, ValueError, "success"])
        decorated = retry(max_attempts=3, delay_seconds=0.1)(mock_func)
        
        result = decorated()
        self.assertEqual(result, "success")
        self.assertEqual(mock_func.call_count, 3)

    def test_max_attempts_exceeded(self):
        """Test behavior when max retry attempts are exceeded."""
        mock_func = Mock(side_effect=ValueError("test error"))
        decorated = retry(max_attempts=3, delay_seconds=0.1)(mock_func)
        
        with self.assertRaises(ValueError):
            decorated()
        self.assertEqual(mock_func.call_count, 3)

    def test_retry_with_delay(self):
        """Test retry with delay between attempts."""
        mock_func = Mock(side_effect=[ValueError, "success"])
        decorated = retry(max_attempts=3, delay_seconds=0.1)(mock_func)
        
        start_time = time.time()
        result = decorated()
        elapsed_time = time.time() - start_time
        
        self.assertEqual(result, "success")
        self.assertGreaterEqual(elapsed_time, 0.1)

    def test_retry_with_specific_exceptions(self):
        """Test retry only on specific exceptions."""
        mock_func = Mock(side_effect=[ValueError, TypeError, "success"])
        decorated = retry(max_attempts=3, retry_on=[ValueError])(mock_func)
        
        with self.assertRaises(TypeError):
            decorated()
        self.assertEqual(mock_func.call_count, 2)

class TestTransaction(unittest.TestCase):
    def setUp(self):
        """Set up test environment."""
        self.transaction = Transaction()
        self.test_file = "test_file.txt"

    def test_transaction_commit(self):
        """Test successful transaction commit."""
        def forward():
            return True
            
        def backward():
            return True
            
        self.transaction.add_operation(forward, backward)
        self.assertTrue(self.transaction.commit())

    def test_transaction_rollback(self):
        """Test transaction rollback on failure."""
        forward_called = False
        backward_called = False
        
        def forward():
            nonlocal forward_called
            forward_called = True
            raise ValueError("Test error")
            
        def backward():
            nonlocal backward_called
            backward_called = True
            
        self.transaction.add_operation(forward, backward)
        
        with self.assertRaises(ValueError):
            self.transaction.commit()
            
        self.assertTrue(forward_called)
        self.assertTrue(backward_called)

    def test_transactional_decorator(self):
        """Test transactional decorator."""
        mock_operation = Mock(side_effect=[ValueError, "success"])
        
        @transactional
        def test_func(transaction=None):
            result = mock_operation()
            transaction.add_operation(
                lambda: True,
                lambda: False
            )
            return result
        
        # First call should fail and rollback
        with self.assertRaises(ValueError):
            test_func()
        
        # Second call should succeed
        result = test_func()
        self.assertEqual(result, "success")

    def test_nested_transactions(self):
        """Test nested transactions."""
        parent_trans = Transaction()
        child_trans = Transaction(parent=parent_trans)
        
        def forward():
            return True
            
        def backward():
            return True
            
        parent_trans.add_operation(forward, backward)
        child_trans.add_operation(forward, backward)
        
        self.assertTrue(child_trans.commit())
        self.assertTrue(parent_trans.commit())

    def test_transaction_context_manager(self):
        """Test transaction as context manager."""
        operations_called = []
        
        def forward():
            operations_called.append("forward")
            
        def backward():
            operations_called.append("backward")
            
        with Transaction() as transaction:
            transaction.add_operation(forward, backward)
            forward()
            
        self.assertIn("forward", operations_called)
        self.assertNotIn("backward", operations_called)

    def test_transaction_error_handling(self):
        """Test transaction error handling."""
        # Test with invalid operations
        with self.assertRaises(ValueError):
            self.transaction.add_operation(None, lambda: True)
        
        with self.assertRaises(ValueError):
            self.transaction.add_operation(lambda: True, None)
        
        # Test with operations that raise exceptions
        def bad_forward():
            raise ValueError("Forward error")
            
        def bad_backward():
            raise ValueError("Backward error")
        
        self.transaction.add_operation(bad_forward, bad_backward)
        
        with self.assertRaises(ValueError):
            self.transaction.commit() 