from fastapi import APIRouter
from gemini_pool import get_gemini_pool
import asyncio

router = APIRouter()

@router.get("/api/pool/status")
async def get_pool_status():
    """Get current status of Gemini API pool"""
    try:
        pool = get_gemini_pool()
        status = pool.get_pool_status()
        return {
            "success": True,
            "pool_status": status,
            "performance": {
                "total_capacity": f"{status['total_keys'] * 60} requests/minute",
                "current_availability": f"{status['available_keys']} keys available",
                "rate_limited": f"{status['rate_limited_keys']} keys cooling down"
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Pool not initialized or no API keys configured"
        }

@router.post("/api/pool/test")
async def test_pool_performance():
    """Test pool performance with concurrent requests"""
    try:
        pool = get_gemini_pool()
        
        # Test concurrent requests
        test_prompts = [
            "What is AI?",
            "Explain machine learning",
            "What is Python?",
            "Define cloud computing",
            "What is FastAPI?"
        ]
        
        start_time = asyncio.get_event_loop().time()
        
        # Run concurrent requests
        tasks = [pool.generate_content_with_retry(prompt) for prompt in test_prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = asyncio.get_event_loop().time()
        
        successful_requests = sum(1 for r in results if not isinstance(r, Exception))
        failed_requests = len(results) - successful_requests
        
        return {
            "success": True,
            "test_results": {
                "total_requests": len(test_prompts),
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "total_time": f"{end_time - start_time:.2f} seconds",
                "requests_per_second": f"{len(test_prompts) / (end_time - start_time):.2f}",
                "average_response_time": f"{(end_time - start_time) / len(test_prompts):.2f} seconds"
            },
            "pool_status": pool.get_pool_status()
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }