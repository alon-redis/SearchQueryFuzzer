import redis
import asyncio
from typing import List, Dict, Optional, Set, Tuple, Any, Union
from ..config.fuzzer_config import FuzzerConfig


class RedisExecutor:
    """Executes Redis Search queries against a Redis server."""
    
    def __init__(self, config: FuzzerConfig):
        """Initialize the Redis executor.
        
        Args:
            config: Fuzzer configuration instance.
        """
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get_redis_host(),
            port=config.get_redis_port(),
            password=config.get_redis_password(),
            decode_responses=True
        )
        self.execution_history: Dict[str, Dict[str, Any]] = {}
    
    async def execute_query(self, query: str, index_name: str = "idx") -> Dict[str, Any]:
        """Execute a Redis Search query.
        
        Args:
            query: The query to execute.
            index_name: Name of the index to search.
            
        Returns:
            Dictionary containing execution results and metadata.
        """
        try:
            # Execute the query with timeout
            result = await asyncio.wait_for(
                self._execute_query_async(query, index_name),
                timeout=self.config.get_timeout_ms() / 1000
            )
            
            execution_info = {
                "success": True,
                "result": result,
                "error": None,
                "execution_time": result.get("execution_time", 0)
            }
            
        except asyncio.TimeoutError:
            execution_info = {
                "success": False,
                "result": None,
                "error": "Query execution timed out",
                "execution_time": self.config.get_timeout_ms()
            }
            
        except redis.RedisError as e:
            execution_info = {
                "success": False,
                "result": None,
                "error": str(e),
                "execution_time": 0
            }
            
        except Exception as e:
            execution_info = {
                "success": False,
                "result": None,
                "error": f"Unexpected error: {str(e)}",
                "execution_time": 0
            }
        
        # Record execution history
        self.execution_history[query] = execution_info
        
        return execution_info
    
    async def _execute_query_async(self, query: str, index_name: str) -> Dict[str, Any]:
        """Execute a query asynchronously.
        
        Args:
            query: The query to execute.
            index_name: Name of the index to search.
            
        Returns:
            Dictionary containing query results and metadata.
        """
        start_time = asyncio.get_event_loop().time()
        
        # Execute the query
        result = self.redis_client.ft(index_name).search(query)
        
        end_time = asyncio.get_event_loop().time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        return {
            "result": result,
            "execution_time": execution_time
        }
    
    async def execute_query_batch(self, queries: List[str], index_name: str = "idx") -> List[Dict[str, Any]]:
        """Execute a batch of queries.
        
        Args:
            queries: List of queries to execute.
            index_name: Name of the index to search.
            
        Returns:
            List of execution results.
        """
        tasks = [self.execute_query(query, index_name) for query in queries]
        return await asyncio.gather(*tasks)
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get statistics about query execution.
        
        Returns:
            Dictionary with execution statistics.
        """
        total_queries = len(self.execution_history)
        if total_queries == 0:
            return {
                "total_queries": 0,
                "successful_queries": 0,
                "failed_queries": 0,
                "success_rate": 0,
                "average_execution_time": 0
            }
        
        successful_queries = sum(1 for info in self.execution_history.values() if info["success"])
        failed_queries = total_queries - successful_queries
        
        execution_times = [
            info["execution_time"]
            for info in self.execution_history.values()
            if info["success"]
        ]
        
        return {
            "total_queries": total_queries,
            "successful_queries": successful_queries,
            "failed_queries": failed_queries,
            "success_rate": successful_queries / total_queries,
            "average_execution_time": sum(execution_times) / len(execution_times)
            if execution_times else 0
        }
    
    def clear_history(self) -> None:
        """Clear the execution history."""
        self.execution_history.clear()
    
    def get_error_queries(self) -> List[Dict[str, Any]]:
        """Get information about queries that failed.
        
        Returns:
            List of dictionaries containing failed query information.
        """
        return [
            {"query": query, "error": info["error"]}
            for query, info in self.execution_history.items()
            if not info["success"]
        ]
    
    def get_slow_queries(self, threshold_ms: int = 1000) -> List[Dict[str, Any]]:
        """Get information about slow queries.
        
        Args:
            threshold_ms: Execution time threshold in milliseconds.
            
        Returns:
            List of dictionaries containing slow query information.
        """
        return [
            {
                "query": query,
                "execution_time": info["execution_time"]
            }
            for query, info in self.execution_history.items()
            if info["success"] and info["execution_time"] > threshold_ms
        ]
    
    def get_query_result(self, query: str) -> Optional[Dict[str, Any]]:
        """Get the execution result for a specific query.
        
        Args:
            query: The query to look up.
            
        Returns:
            Execution result dictionary, or None if not found.
        """
        return self.execution_history.get(query)
