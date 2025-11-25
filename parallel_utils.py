"""
Fast parallel processing utilities for NovaX AI Platform
Optimized for free hosting environments like Render
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import List, Callable, Any
import time

class FastParallelProcessor:
    """Lightweight parallel processor for concurrent operations"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.semaphore = asyncio.Semaphore(10)
    
    async def run_parallel(self, tasks: List[Callable], *args, **kwargs) -> List[Any]:
        """Run multiple tasks in parallel with semaphore control"""
        async def run_task(task):
            async with self.semaphore:
                return await asyncio.get_event_loop().run_in_executor(
                    self.executor, task, *args, **kwargs
                )
        
        return await asyncio.gather(*[run_task(task) for task in tasks])
    
    async def batch_process(self, items: List[Any], processor: Callable, batch_size: int = 5) -> List[Any]:
        """Process items in parallel batches"""
        results = []
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            batch_tasks = [lambda item=item: processor(item) for item in batch]
            batch_results = await self.run_parallel(batch_tasks)
            results.extend(batch_results)
        return results

# Global processor instance
processor = FastParallelProcessor()

async def parallel_ai_requests(prompts: List[str], model_func: Callable) -> List[str]:
    """Process multiple AI requests in parallel"""
    tasks = [lambda prompt=p: model_func(prompt) for p in prompts]
    return await processor.run_parallel(tasks)

async def concurrent_database_ops(operations: List[Callable]) -> List[Any]:
    """Execute database operations concurrently"""
    return await processor.run_parallel(operations)

def optimize_for_render():
    """Optimize settings for Render free tier"""
    return {
        "max_workers": 2,  # Conservative for free tier
        "semaphore_limit": 5,  # Prevent overwhelming
        "batch_size": 3,  # Small batches
        "timeout": 30  # Quick timeout
    }
